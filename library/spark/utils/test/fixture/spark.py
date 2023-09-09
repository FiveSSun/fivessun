import logging
import warnings

from pyspark import sql
import pytest

from library.spark.core import context


def _suppress_py4j_logging():
    logger = logging.getLogger("py4j")
    logger.setLevel(logging.WARN)


# Disable ResourceWarning logs. For the detail. please refer to
# https://stackoverflow.com/questions/26563711/disabling-python-3-2-resourcewarning.
def _add_warning_filter():
    warnings.simplefilter("ignore")


@pytest.fixture(scope="session")
def spark_session(tmp_path_factory: pytest.TempPathFactory) -> sql.SparkSession:
    """pytest fixture for pyspark unit tests.

    The scope of this fixture is 'session' which means a spark session will be created
    once per pytest run.

    Usage:
        `spark_session` fixture will be passed as an argument by pytest automatically.

        def test_sample(spark_session):
            actual_df = spark_session.createDataFrame([{'a': 1, 'b': 2}]).collect()
            expected_df = spark_session.createDataFrame([{'a': 1, 'b': 2}]).collect()
            assert actual_df == expected_df
    """

    _suppress_py4j_logging()
    _add_warning_filter()
    spark = context.create_spark_test_session(__name__, tmp_path_factory)

    yield spark
    spark.stop()
