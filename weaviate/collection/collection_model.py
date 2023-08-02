import uuid as uuid_package
from typing import Type, Optional, Any, List, Dict, Generic, Tuple, Union

from pydantic import create_model
from requests.exceptions import ConnectionError as RequestsConnectionError

from weaviate.collection.collection_base import (
    CollectionBase,
    CollectionObjectBase,
)
from weaviate.collection.collection_classes import Errors
from weaviate.collection.grpc import GrpcBuilderBase, HybridFusion, ReturnValues
from weaviate.connect import Connection
from weaviate.data.replication import ConsistencyLevel
from weaviate.exceptions import UnexpectedStatusCodeException
from weaviate.util import _capitalize_first_letter
from weaviate.weaviate_classes import (
    BaseProperty,
    BatchReference,
    CollectionModelConfig,
    Metadata,
    MetadataReturn,
    Model,
    UserModelType,
    _Object,
)
from weaviate.weaviate_types import UUID, UUIDS, BEACON, PYTHON_TYPE_TO_DATATYPE


class GrpcBuilderModel(Generic[Model], GrpcBuilderBase):
    def __init__(self, connection: Connection, name: str, model: Type[Model]):
        super().__init__(connection, name, model.get_non_optional_fields(model))
        self._model: Type[Model] = model

    def get(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        after: Optional[UUID] = None,
    ) -> List[_Object[Model]]:
        return [self.__dict_to_obj(obj) for obj in self._get(limit, offset, after)]

    def hybrid(
        self,
        query: str,
        alpha: Optional[float] = None,
        vector: Optional[List[float]] = None,
        properties: Optional[List[str]] = None,
        fusion_type: Optional[HybridFusion] = None,
    ) -> List[_Object[Model]]:
        objects = self._hybrid(query, alpha, vector, properties, fusion_type)
        return [self.__dict_to_obj(obj) for obj in objects]

    def bm25(self, query: str, properties: Optional[List[str]] = None) -> List[_Object[Model]]:
        return [self.__dict_to_obj(obj) for obj in self._bm25(query, properties)]

    def __dict_to_obj(self, obj: Tuple[Dict[str, Any], MetadataReturn]) -> _Object[Model]:
        return _Object[Model](data=self._model(**obj[0]), metadata=obj[1])


class CollectionObjectModel(CollectionObjectBase, Generic[Model]):
    @dataclass
    class __Data:
        __collection: "CollectionObjectModel[Model]"

        def insert(self, obj: Model) -> uuid_package.UUID:
            self.__collection._model.model_validate(obj)

            weaviate_obj: Dict[str, Any] = {
                "class": self.__collection._name,
                "properties": obj.props_to_dict(),
                "id": str(obj.uuid),
            }
            if obj.vector is not None:
                weaviate_obj["vector"] = obj.vector

            self.__collection._insert(weaviate_obj)
            return uuid_package.UUID(str(obj.uuid))

    def __init__(self, connection: Connection, name: str, model: Type[Model]) -> None:
        super().__init__(connection, name)
        self._model: Type[Model] = model
        self._default_props = model.get_non_optional_fields(model)
        self.data = self.__Data(self)

    def with_tenant(self, tenant: Optional[str] = None) -> "CollectionObjectModel":
        return self._with_tenant(tenant)

    def with_consistency_level(
        self, consistency_level: Optional[ConsistencyLevel] = None
    ) -> "CollectionObjectModel":
        return self._with_consistency_level(consistency_level)

    def insert_many(self, objects: List[Model]) -> List[Union[uuid_package.UUID, Errors]]:
        for obj in objects:
            self._model.model_validate(obj)

        weaviate_objs: List[Dict[str, Any]] = [
            {
                "class": self._name,
                "properties": obj.props_to_dict(),
                "id": str(obj.uuid),
            }
            for obj in objects
        ]
        return self._insert_many(weaviate_objs)

    def replace(self, obj: Model, uuid: UUID) -> None:
        self._model.model_validate(obj)

        weaviate_obj: Dict[str, Any] = {
            "class": self._name,
            "properties": obj.props_to_dict(),
        }
        if obj.vector is not None:
            weaviate_obj["vector"] = obj.vector

        self._replace(weaviate_obj, uuid)

    def update(self, obj: Model, uuid: UUID) -> None:
        self._model.model_validate(obj)

        weaviate_obj: Dict[str, Any] = {
            "class": self._name,
            "properties": obj.props_to_dict(update=True),
        }
        if obj.vector is not None:
            weaviate_obj["vector"] = obj.vector

        self._update(weaviate_obj, uuid)

    def get_by_id(
        self, uuid: UUID, metadata: Optional[Metadata] = None
    ) -> Optional[_Object[Model]]:
        ret = self._get_by_id(uuid=uuid, metadata=metadata)
        if ret is None:
            return None
        return self._json_to_object(ret)

    def get(self, metadata: Optional[Metadata] = None) -> Optional[List[_Object[Model]]]:
        ret = self._get(metadata=metadata)
        if ret is None:
            return None

        return [self._json_to_object(obj) for obj in ret["objects"]]

    @property
    def get_grpc(self) -> ReturnValues[GrpcBuilderModel[Model]]:
        return ReturnValues[GrpcBuilderModel[Model]](
            GrpcBuilderModel[Model](self._connection, self._name, self._model)
        )

    def reference_add(self, from_uuid: UUID, from_property: str, to_uuids: UUIDS) -> None:
        self._reference_add(
            from_uuid=from_uuid, from_property_name=from_property, to_uuids=to_uuids
        )

    def reference_delete(self, from_uuid: UUID, from_property: str, to_uuids: UUIDS) -> None:
        self._reference_delete(
            from_uuid=from_uuid, from_property_name=from_property, to_uuids=to_uuids
        )

    def reference_replace(self, from_uuid: UUID, from_property: str, to_uuids: UUIDS) -> None:
        self._reference_replace(
            from_uuid=from_uuid, from_property_name=from_property, to_uuids=to_uuids
        )

    def reference_batch_add(self, from_property: str, refs: List[BatchReference]) -> None:
        refs_dict = [
            {
                "from": BEACON + f"{self._name}/{ref.from_uuid}/{from_property}",
                "to": BEACON + str(ref.to_uuid),
            }
            for ref in refs
        ]
        self._reference_batch_add(refs_dict)

    def _json_to_object(self, obj: Dict[str, Any]) -> _Object[Model]:
        for ref in self._model.get_ref_fields(self._model):
            if ref not in obj["properties"]:
                continue

            beacons = obj["properties"][ref]
            uuids = []
            for beacon in beacons:
                uri = beacon["beacon"]
                assert isinstance(uri, str)
                uuids.append(uri.split("/")[-1])

            obj["properties"][ref] = uuids

        # weaviate does not save none values, so we need to add them to pass model validation
        for prop in self._default_props:
            if prop not in obj["properties"]:
                obj["properties"][prop] = None

        model_object = _Object[Model](
            data=self._model(**obj["properties"]), metadata=MetadataReturn(**obj)
        )
        model_object.data.uuid = model_object.metadata.uuid
        model_object.data.vector = model_object.metadata.vector
        return model_object


class CollectionModel(CollectionBase):
    def __init__(self, connection: Connection):
        super().__init__(connection)

    def create(self, config: CollectionModelConfig[Model]) -> CollectionObjectModel[Model]:
        name = super()._create(config)
        if config.name != name:
            raise ValueError(
                f"Name of created collection ({name}) does not match given name ({config.name})"
            )
        return CollectionObjectModel[Model](self._connection, config.name, config.model)

    def get(self, model: Type[Model], name: str) -> CollectionObjectModel[Model]:
        path = f"/schema/{_capitalize_first_letter(name)}"

        try:
            response = self._connection.get(path=path)
        except RequestsConnectionError as conn_err:
            raise RequestsConnectionError("Schema could not be retrieved.") from conn_err
        if response.status_code != 200:
            raise UnexpectedStatusCodeException("Get schema", response)

        response_json = response.json()
        model_props = model.type_to_dict(model)
        schema_props = [
            {"name": prop["name"], "dataType": prop["dataType"]}
            for prop in response_json["properties"]
        ]

        def compare(s: List[Any], t: List[Any]) -> bool:
            t = list(t)  # make a mutable copy
            try:
                for elem in s:
                    t.remove(elem)
            except ValueError:
                return False
            return not t

        if compare(model_props, schema_props):
            raise TypeError("Schemas not compatible")
        return CollectionObjectModel[Model](self._connection, name, model)

    def get_dynamic(self, name: str) -> Tuple[CollectionObjectModel[Model], UserModelType]:
        path = f"/schema/{_capitalize_first_letter(name)}"

        try:
            response = self._connection.get(path=path)
        except RequestsConnectionError as conn_err:
            raise RequestsConnectionError("Schema could not be retrieved.") from conn_err
        if response.status_code != 200:
            raise UnexpectedStatusCodeException("Get schema", response)

        response_json = response.json()
        fields: Dict[str, Any] = {
            prop["name"]: (PYTHON_TYPE_TO_DATATYPE[prop["dataType"][0]], None)
            for prop in response_json["properties"]
        }
        model = create_model(response_json["class"], **fields, __base__=BaseProperty)

        return CollectionObjectModel(self._connection, name, model), model

    def delete(self, name: str) -> None:
        return self._delete(name)

    def exists(self, name: str) -> bool:
        return self._exists(name)
