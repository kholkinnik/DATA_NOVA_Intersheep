# ===Скрипт для теста подключения к БД CH и CH из SPARK с помощью connection ClickHouse=====
from airflow import DAG
from airflow.hooks.base import BaseHook  # для подключения к Spark
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow_clickhouse_plugin.hooks.clickhouse import ClickHouseHook
from pyspark.sql import SparkSession
from datetime import datetime
import logging


def check_clickhouse_connection():
    try:
        ch_hook = ClickHouseHook(clickhouse_conn_id='clickhouse_default')
        version = ch_hook.execute('SELECT version()')  # или get_first()
        logging.info(f"Успешное подключение к Clickhouse: {version}")
    except Exception as e:
        logging.error('ClickHouse Connection failed: %s', str(e))


def conn_from_spark():
    conn = BaseHook.get_connection("clickhouse_http")
    host = conn.host              # "clickhouse"
    port = conn.port              # 8123
    user = conn.login             # "default"
    password = conn.password      # "password"
    database = conn.schema or "default"

    url = f"jdbc:clickhouse://{host}:{port}/{database}"

    spark = SparkSession.builder \
        .appName("ReadFromClickHouse") \
        .master("local[*]") \
        .config("spark.jars", "/opt/spark/jars/clickhouse-jdbc-0.4.6.jar") \
        .getOrCreate()

    logging.info("Spark session opened")

    try:
        df = spark.read \
            .format("jdbc") \
            .option("url", url) \
            .option("query", "SELECT 1 AS test, now() AS time") \
            .option("user", user) \
            .option("password", password) \
            .option("driver", "com.clickhouse.jdbc.ClickHouseDriver") \
            .load()

        df.show(truncate=False)

        df_transformed = df.select("test", "time")
        df_transformed.show()

    except Exception as e:
        logging.error("Spark JDBC read failed: %s", str(e))
        raise
    finally:
        spark.stop()
        logging.info("Spark session stopped")


with DAG(
    'connection_test_CH',
    schedule_interval=None,
    start_date=datetime(2026, 2, 2),
    catchup=False,
    tags=['test_CH'],
) as dag:

    start = EmptyOperator(task_id='start')

    test_CH_connection_task = PythonOperator(
        task_id='test_CH_conn',
        python_callable=check_clickhouse_connection,
    )

    run_connectioon_from_Spark = PythonOperator(
        task_id="run_from_spark",
        python_callable=conn_from_spark,
    )

    start >> test_CH_connection_task >> run_connectioon_from_Spark
