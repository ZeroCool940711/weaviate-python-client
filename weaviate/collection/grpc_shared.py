from typing import Optional, Tuple, List

from weaviate.collection.classes.config import ConsistencyLevel
from weaviate.connect import Connection
from weaviate_grpc import weaviate_pb2


class _BaseGRPC:
    def __init__(self, connection: Connection, consistency_level: Optional[ConsistencyLevel]):
        self._connection = connection
        self._consistency_level = self._get_consistency_level(consistency_level)

    def _get_metadata(self) -> Optional[Tuple[Tuple[str, str], ...]]:

        metadata: Optional[Tuple[Tuple[str, str], ...]] = None
        access_token = self._connection.get_current_bearer_token()

        metadata_list: List[Tuple[str, str]] = []
        if len(access_token) > 0:
            metadata_list.append(("authorization", access_token))

        if len(self._connection.additional_headers):
            for key, val in self._connection.additional_headers.items():
                if val is not None:
                    metadata_list.append((key.lower(), val))

        if len(metadata_list) > 0:
            metadata = tuple(metadata_list)

        return metadata

    @staticmethod
    def _get_consistency_level(
        consistency_level: Optional[ConsistencyLevel],
    ) -> Optional["weaviate_pb2.ConsistencyLevel"]:
        if consistency_level is None:
            return None

        if consistency_level.value == ConsistencyLevel.ONE:
            return weaviate_pb2.ConsistencyLevel.CONSISTENCY_LEVEL_ONE
        elif consistency_level.value == ConsistencyLevel.QUORUM:
            return weaviate_pb2.ConsistencyLevel.CONSISTENCY_LEVEL_QUORUM
        else:
            assert consistency_level.value == ConsistencyLevel.ALL
            return weaviate_pb2.ConsistencyLevel.CONSISTENCY_LEVEL_ALL
