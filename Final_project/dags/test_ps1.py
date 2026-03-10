from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator 
# from pyspark.sql import SparkSession
from datetime import datetime

# импорт бизнес‑логики из pySpark
from final_report_from_spark import run_spark_s3



with DAG(
        dag_id="test_ps1",
        start_date=datetime(2023, 10, 1),
        schedule_interval= None,
        catchup=False,
) as dag:
    
    start = EmptyOperator(
        task_id = 'start'
    ) 
    run_pyspark_task = PythonOperator(
        task_id="run_spark_s3",
        python_callable=run_spark_s3,
    )

start >> run_pyspark_task

