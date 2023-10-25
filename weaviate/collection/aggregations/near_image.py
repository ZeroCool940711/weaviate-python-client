from io import BufferedReader
from pathlib import Path
from typing import List, Optional, Union

from weaviate.collection.aggregations.base import _Aggregate
from weaviate.collection.classes.aggregate import (
    PropertiesMetrics,
    _AggregateReturn,
    _AggregateGroupByReturn,
)
from weaviate.collection.classes.filters import _Filters


class _NearImage(_Aggregate):
    def near_image(
        self,
        near_image: Union[str, Path, BufferedReader],
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        object_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        limit: Optional[int] = None,
        total_count: bool = False,
        return_metrics: Optional[PropertiesMetrics] = None,
    ) -> _AggregateReturn:
        """Aggregate metrics over the objects returned by a near image vector search on this collection.

        At least one of `certainty`, `distance`, or `object_limit` must be specified here for the vector search.

        This method requires a vectoriser capable of handling base64-encoded images, e.g. `img2vec-neural`, `multi2vec-clip`, and `multi2vec-bind`.

        Arguments:
            `near_image`
                The image to search on.
            `certainty`
                The minimum certainty of the image search.
            `distance`
                The maximum distance of the image search.
            `object_limit`
                The maximum number of objects to return from the image search prior to the aggregation.
            `filters`
                The filters to apply to the search.
            `limit`
                The maximum number of aggregated objects to return.
            `total_count`
                Whether to include the total number of objects that match the query in the response.
            `return_metrics`
                A list of property metrics to aggregate together after the text search.

        Returns:
            A `_AggregateReturn` object that includes the aggregation objects.

        Raises:
            `weaviate.exceptions.WeaviateQueryException`:
                If an error occurs while performing the query against Weaviate.
        """
        builder = self._base(return_metrics, filters, limit, total_count)
        builder = self._add_near_image(builder, near_image, certainty, distance, object_limit)
        res = self._do(builder)
        return self._to_aggregate_result(res, return_metrics)


class _NearImageGroupBy(_Aggregate):
    def near_image(
        self,
        near_image: Union[str, Path, BufferedReader],
        group_by: str,
        certainty: Optional[float] = None,
        distance: Optional[float] = None,
        object_limit: Optional[int] = None,
        filters: Optional[_Filters] = None,
        limit: Optional[int] = None,
        total_count: bool = False,
        return_metrics: Optional[PropertiesMetrics] = None,
    ) -> List[_AggregateGroupByReturn]:
        """Aggregate metrics over the objects returned by a near image vector search on this collection grouping the results by a property.

        At least one of `certainty`, `distance`, or `object_limit` must be specified here for the vector search.

        This method requires a vectoriser capable of handling base64-encoded images, e.g. `img2vec-neural`, `multi2vec-clip`, and `multi2vec-bind`.

        Arguments:
            `near_image`
                The image to search on.
            `group_by`
                The property name to group the aggregation by.
            `certainty`
                The minimum certainty of the image search.
            `distance`
                The maximum distance of the image search.
            `object_limit`
                The maximum number of objects to return from the image search prior to the aggregation.
            `filters`
                The filters to apply to the search.
            `limit`
                The maximum number of aggregated objects to return.
            `total_count`
                Whether to include the total number of objects that match the query in the response.
            `return_metrics`
                A list of property metrics to aggregate together after the text search.

        Returns:
            A `_AggregateGroupByReturn` object that includes the aggregation objects.

        Raises:
            `weaviate.exceptions.WeaviateQueryException`:
                If an error occurs while performing the query against Weaviate.
        """
        builder = (
            self._base(return_metrics, filters, limit, total_count)
            .with_group_by_filter([group_by])
            .with_fields(" groupedBy { path value } ")
        )
        builder = self._add_near_image(builder, near_image, certainty, distance, object_limit)
        res = self._do(builder)
        return self._to_group_by_result(res, return_metrics)
