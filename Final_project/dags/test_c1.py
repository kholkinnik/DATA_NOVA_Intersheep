from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from airflow.operators.empty import EmptyOperator 

# импорт бизнес‑логики из plugins/consumers
from consumers import run_kafka_to_clickhouse_raw_products_kbju
from consumers import run_kafka_to_clickhouse_raw_products
from consumers import run_kafka_to_clickhouse_raw_customers
from consumers import run_kafka_to_clickhouse_raw_stores
from consumers import run_kafka_to_clickhouse_raw_purchases

with DAG(
    dag_id="kafka_to_clickhouse_consumer",
    start_date=datetime(2026, 3, 2),
    schedule_interval=None,
    catchup=False,
) as dag:
    start = EmptyOperator(
        task_id = 'start'
    )

    consume_1 = PythonOperator(
        task_id="kafka_to_clickhouse_1",
        python_callable=run_kafka_to_clickhouse_raw_products_kbju      
    )

    consume_2 = PythonOperator(
        task_id="kafka_to_clickhouse_2",
        python_callable=run_kafka_to_clickhouse_raw_products    
    )

    consume_3 = PythonOperator(
        task_id="kafka_to_clickhouse_3",
        python_callable=run_kafka_to_clickhouse_raw_customers  
    )

    consume_4 = PythonOperator(
        task_id="kafka_to_clickhouse_4",
        python_callable=run_kafka_to_clickhouse_raw_stores 
    )

    consume_5 = PythonOperator(
        task_id="kafka_to_clickhouse_5",
        python_callable=run_kafka_to_clickhouse_raw_purchases
    )

    finish = EmptyOperator(
        task_id = 'finish'
    )
start >> consume_1 >> consume_2 >> consume_3 >> consume_4 >> consume_5 >> finish