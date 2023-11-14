from typing import Callable, Generic, Iterable, Iterator, List, Optional, TypeVar
from uuid import UUID

from weaviate.collections.classes.internal import _Object
from weaviate.collections.classes.types import Properties


ITERATOR_CACHE_SIZE = 100

P = TypeVar("P")


class _ObjectIterator(Generic[Properties], Iterable[_Object[Properties]]):
    def __init__(
        self, fetch_objects_query: Callable[[int, Optional[UUID]], List[_Object[Properties]]]
    ) -> None:
        self.__query = fetch_objects_query

        self.__iter_object_cache: List[_Object[Properties]] = []
        self.__iter_object_last_uuid: Optional[UUID] = None

    def __iter__(self) -> Iterator[_Object[Properties]]:
        self.__iter_object_cache = []
        self.__iter_object_last_uuid = None
        return self

    def __next__(self) -> _Object[Properties]:
        if len(self.__iter_object_cache) == 0:
            objects = self.__query(
                ITERATOR_CACHE_SIZE,
                self.__iter_object_last_uuid,
            )
            self.__iter_object_cache = objects
            if len(self.__iter_object_cache) == 0:
                raise StopIteration

        ret_object = self.__iter_object_cache.pop(0)
        self.__iter_object_last_uuid = ret_object.metadata.uuid
        assert (
            self.__iter_object_last_uuid is not None
        )  # if this is None the iterator will never stop
        return ret_object
