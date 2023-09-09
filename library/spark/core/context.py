from typing import Literal

from pyspark import conf as spark_conf
from pyspark import sql
import pytest


def set_shuffle_partitions(spark: sql.SparkSession, num_partitions: int | str):
    spark.conf.set("spark.sql.shuffle.partitions", str(num_partitions))


def set_dynamic_partition_mode_enabled(spark: sql.SparkSession):
    spark.conf.set("hive.exec.dynamic.partition", "true")
    spark.conf.set("hive.exec.dynamic.partition.mode", "nonstrict")


def get_hadoop_conf(spark: sql.SparkSession) -> spark_conf.SparkConf:
    conf = (
        spark.sparkContext._jsc.hadoopConfiguration()
    )  # pylint:disable=protected-access
    conf.set("fs.s3a.endpoint", "s3-ap-northeast-2.amazonaws.com")
    conf.set("mapreduce.input.fileinputformat.input.dir.recursive", "true")
    return conf


def _create_spark_session(conf=spark_conf.SparkConf()) -> sql.SparkSession:
    builder = sql.SparkSession.builder.config(conf=conf).enableHiveSupport()
    return builder.getOrCreate()


def create_spark_batch_session(
    conf=spark_conf.SparkConf(), compression_codec: Literal["orc", "zsrd"] = "orc"
) -> sql.SparkSession:
    (
        conf.set("spark.sql.parquet.compression.codec", compression_codec)
        .set("spark.sql.orc.compression.codec", compression_codec)
        .set("spark.sql.parquet.binaryAsString", "true")
        .set("spark.sql.broadcastTimeout", "600")
        .set("spark.sql.parquet.outputTimestampType", "TIMESTAMP_MICROS")
    )

    return _create_spark_session(conf)


def create_spark_dump_session(
    use_speculation: bool,
    max_executors: int,
    compression_codec: Literal["orc", "zsrd"] = "orc",
    conf=spark_conf.SparkConf(),
) -> sql.SparkSession:
    (
        conf.set("spark.dynamicAllocation.maxExecutors", str(max_executors))
        .set("spark.sql.parquet.compression.codec", compression_codec)
        .set("spark.sql.orc.compression.codec", compression_codec)
        .set("spark.sql.parquet.outputTimestampType", "TIMESTAMP_MICROS")
    )
    if use_speculation is True:
        conf.set("spark.speculation", "true").set(
            "spark.speculation.multiplier", "2.5"
        ).set("spark.speculation.quantile", "0.9")

    return _create_spark_session(conf)


def create_spark_local_session(
    conf=spark_conf.SparkConf(),
    app_name: str = "local",
) -> sql.SparkSession:
    conf.setMaster("local[1]")
    conf.setAppName(app_name)
    conf.set("spark.driver.host", "localhost")
    conf.set("spark.sql.session.timeZone", "UTC")
    return _create_spark_session(conf)


def create_spark_stream_session(conf=spark_conf.SparkConf()) -> sql.SparkSession:
    (
        conf.set("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .set(
            "spark.sql.catalog.spark_catalog",
            "org.apache.spark.sql.delta.catalog.DeltaCatalog",
        )
        .set("spark.dynamicAllocation.enabled", "false")
        .set("spark.databricks.delta.retentionDurationCheck.enabled", "false")
        .set("spark.sql.files.maxRecordsPerFile", "1000000")
    )
    return _create_spark_session(conf)


def create_spark_test_session(
    conf=spark_conf.SparkConf(),
    app_name: str = "test",
    tmp_path_factory: pytest.TempPathFactory | None = None,
) -> sql.SparkSession:
    """Create Spark Session Only for pytest."""
    conf.setMaster("local[1]")
    conf.setAppName(app_name)
    conf.set("spark.driver.host", "localhost")
    conf.set("spark.sql.session.timeZone", "UTC")
    conf.set("spark.sql.warehouse.dir", str(tmp_path_factory.mktemp("warehouse")))
    conf.set("spark.jars.ivy", str(tmp_path_factory.mktemp("tmp_ivy")))

    spark = _create_spark_session(conf)

    hadoop_conf = spark._jsc.hadoopConfiguration()  # pylint: disable=protected-access
    hadoop_conf.set("fs.s3.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    hadoop_conf.set("fs.s3a.access.key", "testing")
    hadoop_conf.set("fs.s3a.secret.key", "testing")
    return spark
