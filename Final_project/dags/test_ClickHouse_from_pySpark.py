from airflow import DAG
from airflow.operators.empty import EmptyOperator 
from airflow.operators.python import PythonOperator

# библиотеки для сессий и логирования
from pyspark.sql import SparkSession
from datetime import datetime
import logging


def connection_to_ch():

    spark = SparkSession.builder \
    .appName("Final_report_from_CH") \
    .master("local[*]") \
    .config("spark.jars", "/opt/spark/jars/clickhouse-jdbc-0.4.6.jar") \
    .getOrCreate()
    
    logging.info(f"Spark session открыта: {datetime.now()}")
    


    df_test = spark.read \
    .format("jdbc") \
    .option("url", "jdbc:clickhouse://clickhouse:8123/default") \
    .option("dbtable", "(SELECT 1 as test, now() as time) t") \
    .option("user", "default") \
    .option("password", "password") \
    .option("driver", "com.clickhouse.jdbc.ClickHouseDriver") \
    .load()

    df_test.show()
    # Остановка сессии Spark
    logging.info(f"Spark версия: {spark.version}")
    logging.info(f"SparkContext версия: {spark.sparkContext.version}")
    spark.stop()
    logging.info(f"✓ SparkSession остановлена {datetime.now()}")


with DAG(
        dag_id="test_CH_from_pySpark",
        start_date=datetime(2026, 3, 2),
        schedule_interval=None,
        catchup=False,
) as dag:
    
    start = EmptyOperator(
        task_id = 'start'
    )

    run_connectioon_to_ch = PythonOperator(
        task_id="run_connectioon_to_ch",
        python_callable= connection_to_ch,
    )

start >> run_connectioon_to_ch