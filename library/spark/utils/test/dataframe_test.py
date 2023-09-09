from pyspark import sql
from pyspark.sql import types as T
import pytest

from library.spark.utils.test import dataframe as df_test_utils


def test_simple_equal(spark_session: sql.SparkSession):
    df1 = spark_session.createDataFrame(
        [
            {
                "user_id": "user_1",
                "class": "class_1",
                "priority": 1,
                "date": "2022-08-11",
            },
            {
                "user_id": "user_1",
                "class": "class_2",
                "priority": 3,
                "date": "2022-08-12",
            },
        ]
    )
    df2 = spark_session.createDataFrame(
        [
            {
                "user_id": "user_1",
                "class": "class_1",
                "priority": 1,
                "date": "2022-08-11",
            },
            {
                "user_id": "user_1",
                "class": "class_2",
                "priority": 3,
                "date": "2022-08-12",
            },
        ]
    )
    df_test_utils.assert_dataframe_equals(df1, df2)


def test_type_equal(spark_session: sql.SparkSession):
    int_schema = T.StructType(
        [
            T.StructField("id", T.IntegerType(), True),
        ]
    )
    bigint_schema = T.StructType(
        [
            T.StructField("id", T.LongType(), True),
        ]
    )

    int_df = spark_session.createDataFrame(
        [
            {"col": 0},
        ],
        int_schema,
    )

    bigint_df = spark_session.createDataFrame(
        [
            {"col": 0},
        ],
        bigint_schema,
    )

    # pass test IFF AssertionError occurs
    with pytest.raises(AssertionError):
        df_test_utils.assert_dataframe_equals(int_df, bigint_df)


def test_null_equal(spark_session: sql.SparkSession):
    schema = T.StructType(
        [
            T.StructField("col", T.StringType(), True),
        ]
    )
    df1 = spark_session.createDataFrame(
        [
            {"col": None},
        ],
        schema,
    )

    df2 = spark_session.createDataFrame(
        [
            {"col": None},
        ],
        schema,
    )
    df_test_utils.assert_dataframe_equals(df1, df2)


def test_map_equal(spark_session: sql.SparkSession):
    schema = T.StructType(
        [
            T.StructField("name", T.StringType(), True),
            T.StructField(
                "properties", T.MapType(T.StringType(), T.IntegerType()), True
            ),
        ]
    )
    data1 = [("John", {"a": 1, "b": 2}), ("Jane", {"a": 3, "b": 4})]
    df1 = spark_session.createDataFrame(data1, schema)

    data2 = [
        ("John", {"b": 2, "a": 1}),
        ("Jane", {"b": 4, "a": 3}),
    ]
    df2 = spark_session.createDataFrame(data2, schema)
    df_test_utils.assert_dataframe_equals(df1, df2)

    data3 = [("John", {"a": 1, "b": 3}), ("Jane", {"a": 3, "b": 4})]
    df3 = spark_session.createDataFrame(data3, schema)

    # pass test IFF AssertionError occurs
    with pytest.raises(AssertionError):
        df_test_utils.assert_dataframe_equals(df1, df3)
