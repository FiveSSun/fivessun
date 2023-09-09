from pyspark import sql

from library.spark.utils.test import dataframe as df_test_utils


def test_sample(spark_session: sql.SparkSession):
    actual = spark_session.createDataFrame([{"a": 1, "b": 2}])
    expected = spark_session.createDataFrame([{"a": 1, "b": 2}])
    df_test_utils.assert_dataframe_equals(actual, expected)
