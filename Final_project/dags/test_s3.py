from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from pyspark.sql import SparkSession

from datetime import datetime
import logging

def run_spark_s3():
    spark = SparkSession.builder \
        .appName("SUCCESS") \
        .config("spark.jars", 
            "/opt/spark/jars/hadoop-aws-3.3.4.jar,"
            "/opt/spark/jars/aws-java-sdk-bundle-1.12.262.jar,"
            "/opt/spark/jars/commons-compress-1.20.jar") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "admin") \
        .config("spark.hadoop.fs.s3a.secret.key", "StrongPassword123!") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")
    logging.info(f"✅ SparkSession готова {datetime.now()}")

    # Создание тестового DF с дальнейшей загрузкой в MiniO
    df = spark.createDataFrame([
        ("test1", 1, datetime.now()), 
        ("test2", 2, datetime.now())
    ], ["name", "value", "date"])

    df.write.mode("overwrite").parquet("s3a://report-clickhouse/FINAL-SUCCESS.parquet")
    logging.info(f"✅ ЗАПИСЬ УСПЕШНА!")

    # Чтение обратно
    logging.info(f"✅ пример чтениия из S3!")
    spark.read.parquet("s3a://report-clickhouse/FINAL-SUCCESS.parquet").show()

    spark.stop()
    logging.info(f"✓ SparkSession остановлена {datetime.now()}")


with DAG(
        dag_id="test_s3",
        start_date=datetime(2023, 10, 1),
        schedule_interval=None,
        catchup=False,
) as dag:
    
    start = EmptyOperator(
        task_id = 'start'
    )

    run_connectioon_to_s3 = PythonOperator(
        task_id="run_connectioon_to_s3",
        python_callable= run_spark_s3,
    )

start >> run_connectioon_to_s3