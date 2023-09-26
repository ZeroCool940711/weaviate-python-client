import datetime
import uuid as uuid_package
from typing import (
    Dict,
    Any,
    Optional,
    List,
    Tuple,
    Union,
    Generic,
    Type,
    cast,
    get_type_hints,
    get_origin,
)

from google.protobuf.struct_pb2 import Struct
from requests.exceptions import ConnectionError as RequestsConnectionError

from weaviate.collection.classes.batch import _BatchDeleteResult
from weaviate.collection.classes.config import ConsistencyLevel
from weaviate.collection.classes.data import (
    BatchReference,
    DataObject,
    Error,
    _BatchReturn,
    RefError,
)
from weaviate.collection.classes.internal import (
    _Object,
    _metadata_from_dict,
    Reference,
    _Reference,
)
from weaviate.collection.classes.orm import (
    Model,
)
from weaviate.collection.classes.types import Properties, TProperties, _check_data_model
from weaviate.collection.classes.filters import _Filters
from weaviate.collection.grpc_batch import _BatchGRPC
from weaviate.collection.rest_batch import _BatchREST
from weaviate.connect import Connection
from weaviate.exceptions import (
    UnexpectedStatusCodeException,
    ObjectAlreadyExistsException,
    WeaviateInsertInvalidPropertyError,
)
from weaviate.util import (
    _datetime_to_string,
    _decode_json_response_dict,
    _decode_json_response_list,
)
from weaviate.types import BEACON, UUID
from weaviate_grpc import weaviate_pb2


class _Data:
    def __init__(
        self,
        connection: Connection,
        name: str,
        consistency_level: Optional[ConsistencyLevel],
        tenant: Optional[str],
    ) -> None:
        self._connection = connection
        self.name = name
        self._consistency_level = consistency_level
        self._tenant = tenant
        self._batch_grpc = _BatchGRPC(connection, consistency_level)
        self._batch_rest = _BatchREST(connection)

    def __validate_props(self, props: Dict[str, Any], clean_props: bool) -> None:
        should_throw = False
        if "id" in props:
            if clean_props:
                del props["id"]
            else:
                should_throw = True
        if "vector" in props:
            if clean_props:
                del props["vector"]
            else:
                should_throw = True
        if should_throw:
            raise WeaviateInsertInvalidPropertyError(props)

    def _insert(self, weaviate_obj: Dict[str, Any], clean_props: bool) -> uuid_package.UUID:
        path = "/objects"
        self.__validate_props(weaviate_obj["properties"], clean_props=clean_props)

        params, weaviate_obj = self.__apply_context_to_params_and_object({}, weaviate_obj)
        try:
            response = self._connection.post(path=path, weaviate_object=weaviate_obj, params=params)
        except RequestsConnectionError as conn_err:
            raise RequestsConnectionError("Object was not added to Weaviate.") from conn_err
        if response.status_code == 200:
            return uuid_package.UUID(weaviate_obj["id"])

        try:
            response_json = _decode_json_response_dict(response, "insert object")
            assert response_json is not None
            if "already exists" in response_json["error"][0]["message"]:
                raise ObjectAlreadyExistsException(weaviate_obj["id"])
        except KeyError:
            pass
        raise UnexpectedStatusCodeException("Creating object", response)

    def _insert_many(self, objects: List[Dict[str, Any]], clean_props: bool) -> _BatchReturn:
        weaviate_objs: List[weaviate_pb2.BatchObject] = [
            weaviate_pb2.BatchObject(
                class_name=self.name,
                vector=obj["vector"] if obj["vector"] is not None else None,
                uuid=str(obj["uuid"]) if obj["uuid"] is not None else str(uuid_package.uuid4()),
                properties=self.__parse_properties_grpc(obj["properties"], clean_props),
                tenant=self._tenant,
            )
            for obj in objects
        ]

        errors = self._batch_grpc.batch(weaviate_objs)

        all_responses: List[Union[uuid_package.UUID, Error]] = cast(
            List[Union[uuid_package.UUID, Error]], list(range(len(weaviate_objs)))
        )
        return_success: Dict[int, uuid_package.UUID] = {}
        return_errors: Dict[int, Error] = {}

        for idx, obj in enumerate(weaviate_objs):
            if idx in errors:
                error = Error(errors[idx], original_uuid=objects[idx].get("uuid"))
                return_errors[idx] = error
                all_responses[idx] = error
            else:
                success = uuid_package.UUID(obj.uuid)
                return_success[idx] = success
                all_responses[idx] = success

        return _BatchReturn(
            uuids=return_success,
            errors=return_errors,
            has_errors=len(errors) > 0,
            all_responses=all_responses,
        )

    def delete_by_id(self, uuid: UUID) -> bool:
        """Delete an object from the collection based on its UUID.

        Arguments:
            `uuid`
                The UUID of the object to delete, REQUIRED.
        """
        path = f"/objects/{self.name}/{uuid}"

        try:
            response = self._connection.delete(path=path, params=self.__apply_context({}))
        except RequestsConnectionError as conn_err:
            raise RequestsConnectionError("Object could not be deleted.") from conn_err
        if response.status_code == 204:
            return True  # Successfully deleted
        elif response.status_code == 404:
            return False  # did not exist
        raise UnexpectedStatusCodeException("Delete object", response)

    def delete_many(
        self, where: _Filters, verbose: bool = False, dry_run: bool = False
    ) -> _BatchDeleteResult:
        """Delete multiple objects from the collection based on a filter.

        Arguments:
            `where`
                The filter to apply. This filter is the same that is used when performing queries and has the same syntax, REQUIRED.
            `verbose`
                Whether to return the deleted objects in the response.
            `dry_run`
                Whether to perform a dry run. If set to `True`, the objects will not be deleted, but the response will contain the objects that would have been deleted.

        Raises:
            `requests.ConnectionError`:
                If the network connection to Weaviate fails.
            `weaviate.UnexpectedStatusCodeException`:
                If Weaviate reports a non-OK status.
        """
        return self._batch_rest.delete(
            self.name, where, verbose, dry_run, self._consistency_level, self._tenant
        )

    def _replace(self, weaviate_obj: Dict[str, Any], uuid: UUID) -> None:
        path = f"/objects/{self.name}/{uuid}"
        params, weaviate_obj = self.__apply_context_to_params_and_object({}, weaviate_obj)

        weaviate_obj["id"] = str(uuid)  # must add ID to payload for PUT request

        try:
            response = self._connection.put(path=path, weaviate_object=weaviate_obj, params=params)
        except RequestsConnectionError as conn_err:
            raise RequestsConnectionError("Object was not replaced.") from conn_err
        if response.status_code == 200:
            return
        raise UnexpectedStatusCodeException("Replacing object", response)

    def _update(self, weaviate_obj: Dict[str, Any], uuid: UUID) -> None:
        path = f"/objects/{self.name}/{uuid}"
        params, weaviate_obj = self.__apply_context_to_params_and_object({}, weaviate_obj)

        try:
            response = self._connection.patch(
                path=path, weaviate_object=weaviate_obj, params=params
            )
        except RequestsConnectionError as conn_err:
            raise RequestsConnectionError("Object was not updated.") from conn_err
        if response.status_code == 204:
            return
        raise UnexpectedStatusCodeException("Update object", response)

    def _get_by_id(self, uuid: UUID, include_vector: bool) -> Optional[Dict[str, Any]]:
        path = f"/objects/{self.name}/{uuid}"
        params: Dict[str, Any] = {}
        if include_vector:
            params["include"] = "vector"
        return self._get_from_weaviate(params=self.__apply_context(params), path=path)

    def _get(self, limit: Optional[int], include_vector: bool) -> Optional[Dict[str, Any]]:
        path = "/objects"
        params: Dict[str, Any] = {"class": self.name}
        if limit is not None:
            params["limit"] = limit
        if include_vector:
            params["include"] = "vector"
        return self._get_from_weaviate(params=self.__apply_context(params), path=path)

    def _get_from_weaviate(self, params: Dict[str, Any], path: str) -> Optional[Dict[str, Any]]:
        try:
            response = self._connection.get(path=path, params=params)
        except RequestsConnectionError as conn_err:
            raise RequestsConnectionError("Could not get object/s.") from conn_err
        if response.status_code == 200:
            response_json = _decode_json_response_dict(response, "get")
            assert response_json is not None
            return response_json
        if response.status_code == 404:
            return None
        raise UnexpectedStatusCodeException("Get object/s", response)

    def _reference_add(self, from_uuid: UUID, from_property: str, ref: Reference) -> None:
        params: Dict[str, str] = {}

        path = f"/objects/{self.name}/{from_uuid}/references/{from_property}"
        for beacon in ref._to_beacons():
            try:
                response = self._connection.post(
                    path=path,
                    weaviate_object=beacon,
                    params=self.__apply_context(params),
                )
            except RequestsConnectionError as conn_err:
                raise RequestsConnectionError("Reference was not added.") from conn_err
            if response.status_code != 200:
                raise UnexpectedStatusCodeException("Add property reference to object", response)

    def _reference_add_many(
        self, refs: List[Dict[str, str]]
    ) -> Optional[Dict[int, List[RefError]]]:
        params: Dict[str, str] = {}
        if self._consistency_level is not None:
            params["consistency_level"] = self._consistency_level

        if self._tenant is not None:
            for ref in refs:
                ref["tenant"] = self._tenant

        response = self._connection.post(
            path="/batch/references", weaviate_object=refs, params=params
        )

        error_return: Dict[int, List[RefError]] = {}
        if response.status_code == 200:
            response_json = _decode_json_response_list(response, "batch references")
            assert response_json is not None

            for i, resp in enumerate(response_json):
                if "errors" in resp["result"] and len(resp["result"]["errors"]["error"]) > 0:
                    error_return[i] = [
                        RefError(message=err["message"])
                        for err in resp["result"]["errors"]["error"]
                    ]

            if len(error_return) > 0:
                return error_return
            return None
        raise UnexpectedStatusCodeException("Send ref batch", response)

    def _reference_delete(self, from_uuid: UUID, from_property: str, ref: Reference) -> None:
        params: Dict[str, str] = {}

        path = f"/objects/{self.name}/{from_uuid}/references/{from_property}"
        for beacon in ref._to_beacons():
            try:
                response = self._connection.delete(
                    path=path,
                    weaviate_object=beacon,
                    params=self.__apply_context(params),
                )
            except RequestsConnectionError as conn_err:
                raise RequestsConnectionError("Reference was not added.") from conn_err
            if response.status_code != 204:
                raise UnexpectedStatusCodeException("Add property reference to object", response)

    def _reference_replace(self, from_uuid: UUID, from_property: str, ref: Reference) -> None:
        params: Dict[str, str] = {}

        path = f"/objects/{self.name}/{from_uuid}/references/{from_property}"
        try:
            response = self._connection.put(
                path=path,
                weaviate_object=ref._to_beacons(),
                params=self.__apply_context(params),
            )
        except RequestsConnectionError as conn_err:
            raise RequestsConnectionError("Reference was not added.") from conn_err
        if response.status_code != 200:
            raise UnexpectedStatusCodeException("Add property reference to object", response)

    def __apply_context(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if self._tenant is not None:
            params["tenant"] = self._tenant
        if self._consistency_level is not None:
            params["consistency_level"] = self._consistency_level
        return params

    def __apply_context_to_params_and_object(
        self, params: Dict[str, Any], obj: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        if self._tenant is not None:
            obj["tenant"] = self._tenant
        if self._consistency_level is not None:
            params["consistency_level"] = self._consistency_level
        return params, obj

    def _serialize_properties(self, data: Properties) -> Dict[str, Any]:
        return {
            key: val._to_beacons()
            if isinstance(val, _Reference)
            else self.__serialize_primitive(val)
            for key, val in data.items()
        }

    def __serialize_primitive(self, value: Any) -> Any:
        if isinstance(value, uuid_package.UUID):
            return str(value)
        if isinstance(value, datetime.datetime):
            return _datetime_to_string(value)
        if isinstance(value, list):
            return [self.__serialize_primitive(val) for val in value]
        return value

    def _deserialize_primitive(self, value: Any, type_value: Optional[Any]) -> Any:
        if type_value is None:
            return value
        if type_value == uuid_package.UUID:
            return uuid_package.UUID(value)
        if type_value == datetime.datetime:
            return datetime.datetime.fromisoformat(value)
        if isinstance(type_value, list):
            return [
                self._deserialize_primitive(val, type_value[idx]) for idx, val in enumerate(value)
            ]
        return value

    def __parse_properties_grpc(
        self, data: Dict[str, Any], clean_props: bool
    ) -> weaviate_pb2.BatchObject.Properties:
        self.__validate_props(data, clean_props)

        multi_target: List[weaviate_pb2.BatchObject.RefPropertiesMultiTarget] = []
        single_target: List[weaviate_pb2.BatchObject.RefPropertiesSingleTarget] = []
        non_ref_properties: Struct = Struct()
        bool_arrays: List[weaviate_pb2.BooleanArrayProperties] = []
        text_arrays: List[weaviate_pb2.TextArrayProperties] = []
        int_arrays: List[weaviate_pb2.IntArrayProperties] = []
        float_arrays: List[weaviate_pb2.NumberArrayProperties] = []
        for key, val in data.items():
            if isinstance(val, _Reference):
                if val.is_multi_target:
                    multi_target.append(
                        weaviate_pb2.BatchObject.RefPropertiesMultiTarget(
                            uuids=val.uuids_str,
                            target_collection=val.target_collection,
                            prop_name=key,
                        )
                    )
                else:
                    single_target.append(
                        weaviate_pb2.BatchObject.RefPropertiesSingleTarget(
                            uuids=val.uuids_str, prop_name=key
                        )
                    )
            elif isinstance(val, list) and isinstance(val[0], bool):
                bool_arrays.append(weaviate_pb2.BooleanArrayProperties(prop_name=key, values=val))
            elif isinstance(val, list) and isinstance(val[0], str):
                text_arrays.append(weaviate_pb2.TextArrayProperties(prop_name=key, values=val))
            elif isinstance(val, list) and isinstance(val[0], datetime.datetime):
                text_arrays.append(
                    weaviate_pb2.TextArrayProperties(
                        prop_name=key, values=[_datetime_to_string(x) for x in val]
                    )
                )
            elif isinstance(val, list) and isinstance(val[0], uuid_package.UUID):
                text_arrays.append(
                    weaviate_pb2.TextArrayProperties(prop_name=key, values=[str(x) for x in val])
                )
            elif isinstance(val, list) and isinstance(val[0], int):
                int_arrays.append(weaviate_pb2.IntArrayProperties(prop_name=key, values=val))
            elif isinstance(val, list) and isinstance(val[0], float):
                float_arrays.append(weaviate_pb2.NumberArrayProperties(prop_name=key, values=val))
            else:
                non_ref_properties.update({key: self.__serialize_primitive(val)})

        return weaviate_pb2.BatchObject.Properties(
            non_ref_properties=non_ref_properties,
            ref_props_multi=multi_target,
            ref_props_single=single_target,
            text_array_properties=text_arrays,
            number_array_properties=float_arrays,
            int_array_properties=int_arrays,
            boolean_array_properties=bool_arrays,
        )


class _DataCollection(Generic[Properties], _Data):
    def __init__(
        self,
        connection: Connection,
        name: str,
        consistency_level: Optional[ConsistencyLevel],
        tenant: Optional[str],
        type_: Optional[Type[Properties]] = None,
    ):
        super().__init__(connection, name, consistency_level, tenant)
        self.__type = type_

    def with_data_model(self, data_model: Type[TProperties]) -> "_DataCollection[TProperties]":
        _check_data_model(data_model)
        return _DataCollection[TProperties](
            self._connection, self.name, self._consistency_level, self._tenant, data_model
        )

    def __deserialize_properties(self, data: Dict[str, Any]) -> Properties:
        hints = (
            get_type_hints(self.__type)
            if self.__type and not get_origin(self.__type) == dict
            else {}
        )
        return cast(
            Properties,
            {key: self._deserialize_primitive(val, hints.get(key)) for key, val in data.items()},
        )

    def _json_to_object(self, obj: Dict[str, Any]) -> _Object[Properties]:
        props = self.__deserialize_properties(obj["properties"])
        return _Object(
            properties=cast(Properties, props),
            metadata=_metadata_from_dict(obj),
        )

    def insert(
        self,
        properties: Properties,
        uuid: Optional[UUID] = None,
        vector: Optional[List[float]] = None,
    ) -> uuid_package.UUID:
        """Insert a single object into the collection.

        Arguments:
            `properties`
                The properties of the object, REQUIRED.
            `uuid`
                The UUID of the object. If not provided, a random UUID will be generated.
            `vector`
                The vector of the object.
        """
        weaviate_obj: Dict[str, Any] = {
            "class": self.name,
            "properties": self._serialize_properties(properties),
            "id": str(uuid if uuid is not None else uuid_package.uuid4()),
        }

        if vector is not None:
            weaviate_obj["vector"] = vector

        return self._insert(weaviate_obj, False)

    def insert_many(
        self,
        objects: List[Union[Properties, DataObject[Properties]]],
    ) -> _BatchReturn:
        """Insert multiple objects into the collection.

        Arguments:
            `objects` REQUIRED
                The objects to insert. This can be either a list of `Properties` or `DataObject[Properties]`
                    If you didn't set `data_model` then `Properties` will be `Data[str, Any]` in which case you can insert simple dictionaries here.
                        If you want to insert vectors and UUIDs alongside your properties, you will have to use `DataObject` instead.

        Raises:
            `weaviate.exceptions.WeaviateGRPCException`:
                If the network connection to Weaviate fails.
            `weaviate.exceptions.WeaviateInsertInvalidPropertyError`:
                If a property is invalid. I.e., has name `id` or `vector`, which are reserved.
        """
        return self._insert_many(
            [
                {
                    "properties": obj.properties,
                    "vector": obj.vector,
                    "uuid": obj.uuid,
                }
                if isinstance(obj, DataObject)
                else {
                    "properties": obj,
                    "vector": None,
                    "uuid": None,
                }
                for obj in objects
            ],
            False,
        )

    def replace(
        self, properties: Properties, uuid: UUID, vector: Optional[List[float]] = None
    ) -> None:
        """Replace an object in the collection.

        This is equivalent to a PUT operation.

        Arguments:
            `properties`
                The properties of the object, REQUIRED.
            `uuid`
                The UUID of the object, REQUIRED.
            `vector`
                The vector of the object.

        Raises:
            `requests.ConnectionError`:
                If the network connection to Weaviate fails.
            `weaviate.UnexpectedStatusCodeException`:
                If Weaviate reports a non-OK status.
            `weaviate.exceptions.WeaviateInsertInvalidPropertyError`:
                If a property is invalid. I.e., has name `id` or `vector`, which are reserved.
        """
        weaviate_obj: Dict[str, Any] = {
            "class": self.name,
            "properties": self._serialize_properties(properties),
        }
        if vector is not None:
            weaviate_obj["vector"] = vector

        self._replace(weaviate_obj, uuid=uuid)

    def update(
        self, properties: Properties, uuid: UUID, vector: Optional[List[float]] = None
    ) -> None:
        """Update an object in the collection.

        This is equivalent to a PATCH operation.

        Arguments:
            `properties`
                The properties of the object, REQUIRED.
            `uuid`
                The UUID of the object, REQUIRED.
            `vector`
                The vector of the object.
        """
        weaviate_obj: Dict[str, Any] = {
            "class": self.name,
            "properties": self._serialize_properties(properties),
        }
        if vector is not None:
            weaviate_obj["vector"] = vector

        self._update(weaviate_obj, uuid=uuid)

    def reference_add(self, from_uuid: UUID, from_property: str, ref: Reference) -> None:
        """Create a reference between an object in this collection and any other object in Weaviate.

        Arguments:
            `from_uuid`
                The UUID of the object in this collection, REQUIRED.
            `from_property`
                The name of the property in the object in this collection, REQUIRED.
            `ref`
                The reference to add, REQUIRED. Use `ReferenceFactory.to` to generate the correct type.

        Raises:
            `requests.ConnectionError`:
                If the network connection to Weaviate fails.
            `weaviate.UnexpectedStatusCodeException`:
                If Weaviate reports a non-OK status.
        """
        self._reference_add(
            from_uuid=from_uuid,
            from_property=from_property,
            ref=ref,
        )

    def reference_add_many(
        self, from_property: str, refs: List[BatchReference]
    ) -> Optional[Dict[int, List[RefError]]]:
        """Create multiple references on a property in batch between objects in this collection and any other object in Weaviate.

        Arguments:
            `from_property`
                The name of the property in the object in this collection, REQUIRED.
            `refs`
                The references to add, REQUIRED.

        Raises:
            `requests.ConnectionError`:
                If the network connection to Weaviate fails.
            `weaviate.UnexpectedStatusCodeException`:
                If Weaviate reports a non-OK status.
        """
        refs_dict = [
            {
                "from": BEACON + f"{self.name}/{ref.from_uuid}/{from_property}",
                "to": BEACON + str(ref.to_uuid),
            }
            for ref in refs
        ]
        return self._reference_add_many(refs_dict)

    def reference_delete(self, from_uuid: UUID, from_property: str, ref: Reference) -> None:
        """Delete a reference from an object within the collection.

        Arguments:
            `from_uuid`
                The UUID of the object in this collection, REQUIRED.
            `from_property`
                The name of the property in the object in this collection from which the reference should be deleted, REQUIRED.
            `ref`
                The reference to delete, REQUIRED. Use `ReferenceFactory.to` to generate the correct type.
        """
        self._reference_delete(from_uuid=from_uuid, from_property=from_property, ref=ref)

    def reference_replace(self, from_uuid: UUID, from_property: str, ref: Reference) -> None:
        """Replace a reference of an object within the collection.

        Arguments:
            `from_uuid`
                The UUID of the object in this collection, REQUIRED.
            `from_property`
                The name of the property in the object in this collection from which the reference should be replaced, REQUIRED.
            `ref`
                The reference to replace, REQUIRED. Use `ReferenceFactory.to` to generate the correct type.
        """
        self._reference_replace(from_uuid=from_uuid, from_property=from_property, ref=ref)


class _DataCollectionModel(Generic[Model], _Data):
    def __init__(
        self,
        connection: Connection,
        name: str,
        model: Type[Model],
        consistency_level: Optional[ConsistencyLevel],
        tenant: Optional[str],
    ):
        super().__init__(connection, name, consistency_level, tenant)
        self.__model = model

    def _json_to_object(self, obj: Dict[str, Any]) -> _Object[Model]:
        for ref in self.__model.get_ref_fields(self.__model):
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
        for prop in self.__model.get_non_default_fields(self.__model):
            if prop not in obj["properties"]:
                obj["properties"][prop] = None

        metadata = _metadata_from_dict(obj)
        model_object = _Object[Model](
            properties=self.__model.model_validate(
                {
                    **obj["properties"],
                    "uuid": metadata.uuid,
                    "vector": metadata.vector,
                }
            ),
            metadata=metadata,
        )
        return model_object

    def insert(self, obj: Model) -> uuid_package.UUID:
        self.__model.model_validate(obj)
        weaviate_obj: Dict[str, Any] = {
            "class": self.name,
            "properties": self._serialize_properties(obj.props_to_dict()),
            "id": str(obj.uuid),
        }
        if obj.vector is not None:
            weaviate_obj["vector"] = obj.vector

        self._insert(weaviate_obj, False)
        return uuid_package.UUID(str(obj.uuid))

    def insert_many(self, objects: List[Model]) -> _BatchReturn:
        for obj in objects:
            self.__model.model_validate(obj)

        data_objects = [
            {
                "properties": obj.props_to_dict(),
                "uuid": obj.uuid,
                "vector": obj.vector,
            }
            for obj in objects
        ]

        return self._insert_many(data_objects, False)

    def replace(self, obj: Model, uuid: UUID) -> None:
        self.__model.model_validate(obj)

        weaviate_obj: Dict[str, Any] = {
            "class": self.name,
            "properties": self._serialize_properties(obj.props_to_dict()),
        }
        if obj.vector is not None:
            weaviate_obj["vector"] = obj.vector

        self._replace(weaviate_obj, uuid)

    def update(self, obj: Model, uuid: UUID) -> None:
        self.__model.model_validate(obj)

        weaviate_obj: Dict[str, Any] = {
            "class": self.name,
            "properties": self._serialize_properties(obj.props_to_dict()),
        }
        if obj.vector is not None:
            weaviate_obj["vector"] = obj.vector

        self._update(weaviate_obj, uuid)

    def get_by_id(self, uuid: UUID, include_vector: bool = False) -> Optional[_Object[Model]]:
        ret = self._get_by_id(uuid=uuid, include_vector=include_vector)
        if ret is None:
            return None
        return self._json_to_object(ret)

    def get(
        self, limit: Optional[int] = None, include_vector: bool = False
    ) -> List[_Object[Model]]:
        ret = self._get(limit=limit, include_vector=include_vector)
        if ret is None:
            return []

        return [self._json_to_object(obj) for obj in ret["objects"]]

    def reference_add(self, from_uuid: UUID, from_property: str, ref: Reference) -> None:
        self._reference_add(from_uuid=from_uuid, from_property=from_property, ref=ref)

    def reference_delete(self, from_uuid: UUID, from_property: str, ref: Reference) -> None:
        self._reference_delete(from_uuid=from_uuid, from_property=from_property, ref=ref)

    def reference_replace(self, from_uuid: UUID, from_property: str, ref: Reference) -> None:
        self._reference_replace(from_uuid=from_uuid, from_property=from_property, ref=ref)

    def reference_add_many(self, from_property: str, refs: List[BatchReference]) -> None:
        refs_dict = [
            {
                "from": BEACON + f"{self.name}/{ref.from_uuid}/{from_property}",
                "to": BEACON + str(ref.to_uuid),
            }
            for ref in refs
        ]
        self._reference_add_many(refs_dict)
