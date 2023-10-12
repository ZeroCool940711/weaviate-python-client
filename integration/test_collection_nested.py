from typing import List, Union

import pytest

import weaviate
from weaviate.collection.classes.config import (
    DataType,
    Property,
)


@pytest.fixture(scope="module")
def client():
    connection_params = weaviate.ConnectionParams(
        scheme="http", host="localhost", port=8080, grpc_port=50051
    )
    client = weaviate.Client(connection_params)
    client.schema.delete_all()
    yield client
    client.schema.delete_all()


@pytest.mark.parametrize(
    "property_,object_",
    [
        (
            Property(
                name="nested",
                data_type=DataType.OBJECT,
                nested_properties=Property(
                    name="text",
                    data_type=DataType.TEXT,
                ),
            ),
            {"text": "Hello World"},
        ),
        (
            Property(
                name="nested",
                data_type=DataType.OBJECT,
                nested_properties=[
                    Property(
                        name="text",
                        data_type=DataType.TEXT,
                    )
                ],
            ),
            {"text": "Hello World"},
        ),
        (
            Property(
                name="nested",
                data_type=DataType.OBJECT_ARRAY,
                nested_properties=Property(
                    name="text",
                    data_type=DataType.TEXT,
                ),
            ),
            [{"text": "Hello World"}, {"text": "Hello World"}],
        ),
        (
            Property(
                name="nested",
                data_type=DataType.OBJECT_ARRAY,
                nested_properties=[
                    Property(
                        name="text",
                        data_type=DataType.TEXT,
                    )
                ],
            ),
            [{"text": "Hello World"}, {"text": "Hello World"}],
        ),
        (
            Property(
                name="nested",
                data_type=DataType.OBJECT,
                nested_properties=[
                    Property(
                        name="text",
                        data_type=DataType.TEXT,
                    ),
                    Property(
                        name="texts",
                        data_type=DataType.TEXT_ARRAY,
                    ),
                    Property(
                        name="number",
                        data_type=DataType.NUMBER,
                    ),
                    Property(
                        name="numbers",
                        data_type=DataType.NUMBER_ARRAY,
                    ),
                    Property(
                        name="int",
                        data_type=DataType.INT,
                    ),
                    Property(
                        name="ints",
                        data_type=DataType.INT_ARRAY,
                    ),
                    Property(
                        name="bool",
                        data_type=DataType.BOOL,
                    ),
                    Property(
                        name="bools",
                        data_type=DataType.BOOL_ARRAY,
                    ),
                    Property(
                        name="date",
                        data_type=DataType.DATE,
                    ),
                    Property(
                        name="dates",
                        data_type=DataType.DATE_ARRAY,
                    ),
                    Property(
                        name="obj",
                        data_type=DataType.OBJECT,
                        nested_properties=Property(
                            name="text",
                            data_type=DataType.TEXT,
                        ),
                    ),
                    Property(
                        name="objs",
                        data_type=DataType.OBJECT_ARRAY,
                        nested_properties=Property(
                            name="text",
                            data_type=DataType.TEXT,
                        ),
                    ),
                ],
            ),
            {
                "text": "Hello World",
                "texts": ["Hello", "World"],
                "number": 42.0,
                "numbers": [42.0, 43.0],
                "int": 42,
                "ints": [42, 43],
                "bool": True,
                "bools": [True, False],
                "date": "2020-01-01T00:00:00Z",
                "dates": ["2020-01-01T00:00:00Z", "2020-01-02T00:00:00Z"],
                "obj": {"text": "Hello World"},
                "objs": [{"text": "Hello World"}, {"text": "Hello World"}],
            },
        ),
        (
            Property(
                name="nested",
                data_type=DataType.OBJECT_ARRAY,
                nested_properties=[
                    Property(
                        name="text",
                        data_type=DataType.TEXT,
                    ),
                    Property(
                        name="texts",
                        data_type=DataType.TEXT_ARRAY,
                    ),
                    Property(
                        name="number",
                        data_type=DataType.NUMBER,
                    ),
                    Property(
                        name="numbers",
                        data_type=DataType.NUMBER_ARRAY,
                    ),
                    Property(
                        name="int",
                        data_type=DataType.INT,
                    ),
                    Property(
                        name="ints",
                        data_type=DataType.INT_ARRAY,
                    ),
                    Property(
                        name="bool",
                        data_type=DataType.BOOL,
                    ),
                    Property(
                        name="bools",
                        data_type=DataType.BOOL_ARRAY,
                    ),
                    Property(
                        name="date",
                        data_type=DataType.DATE,
                    ),
                    Property(
                        name="dates",
                        data_type=DataType.DATE_ARRAY,
                    ),
                    Property(
                        name="obj",
                        data_type=DataType.OBJECT,
                        nested_properties=Property(
                            name="text",
                            data_type=DataType.TEXT,
                        ),
                    ),
                    Property(
                        name="objs",
                        data_type=DataType.OBJECT_ARRAY,
                        nested_properties=Property(
                            name="text",
                            data_type=DataType.TEXT,
                        ),
                    ),
                ],
            ),
            [
                {
                    "text": "Hello World",
                    "texts": ["Hello", "World"],
                    "number": 42.0,
                    "numbers": [42.0, 43.0],
                    "int": 42,
                    "ints": [42, 43],
                    "bool": True,
                    "bools": [True, False],
                    "date": "2020-01-01T00:00:00Z",
                    "dates": ["2020-01-01T00:00:00Z", "2020-01-02T00:00:00Z"],
                    "obj": {"text": "Hello World"},
                    "objs": [{"text": "Hello World"}, {"text": "Hello World"}],
                }
            ],
        ),
    ],
)
def test_insert_nested_properties(
    client: weaviate.Client, property_: Property, object_: Union[dict, List[dict]]
):
    name = "TestInsertNestedProperties"
    client.collection.delete(name)
    collection = client.collection.create(
        name=name,
        properties=[property_],
    )
    collection.data.insert_many([{"nested": object_}])
    result = collection.query.fetch_objects()
    import json

    print(json.dumps(result.objects[0].properties["nested"], indent=4))
    assert result.objects[0].properties["nested"] == object_
