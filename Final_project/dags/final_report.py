from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

from airflow.operators.empty import EmptyOperator 

# импорт бизнес‑логики из plugins/producer
from producers import producer_mongo_to_raw_products_kbju
from producers import producer_mongo_to_raw_products
from producers import producer_mongo_to_raw_customer
from producers import producer_mongo_to_raw_stores
from producers import producer_mongo_to_raw_purchases

# импорт бизнес‑логики из plugins/consumers
from consumers import run_kafka_to_clickhouse_raw_products_kbju
from consumers import run_kafka_to_clickhouse_raw_products
from consumers import run_kafka_to_clickhouse_raw_customers
from consumers import run_kafka_to_clickhouse_raw_stores
from consumers import run_kafka_to_clickhouse_raw_purchases

# импорт бизнес‑логики из plugins/final_report_from_spark
from final_report_from_spark import run_spark_s3



with DAG(
    dag_id="final_report",
    start_date=datetime(2026, 3, 2),
    schedule_interval=None,
    #schedule_interval='0 10 * * *',
    catchup=False,
    tags=['analityc_result']
    
) as dag:
    start_producer = EmptyOperator(
        task_id = 'start_producer'
    )

    produce_1 = PythonOperator(
        task_id="producer_to_raw_products_kbju",
        python_callable=producer_mongo_to_raw_products_kbju,
    )

    produce_2 = PythonOperator(
        task_id="producer_to_raw_products",
        python_callable=producer_mongo_to_raw_products,
    )

    produce_3 = PythonOperator(
        task_id="producer_to_raw_customer",
        python_callable=producer_mongo_to_raw_customer,
    )

    produce_4 = PythonOperator(
        task_id="producer_to_raw_stores",
        python_callable=producer_mongo_to_raw_stores,
    )

    produce_5 = PythonOperator(
        task_id="producer_to_raw_purchases",
        python_callable=producer_mongo_to_raw_purchases,
    )

    start_consumer = EmptyOperator(
        task_id = 'start_consumer'
    )

    consume_1 = PythonOperator(
        task_id="consumer_raw_products_kbju",
        python_callable=run_kafka_to_clickhouse_raw_products_kbju      
    )

    consume_2 = PythonOperator(
        task_id="consumer_raw_products",
        python_callable=run_kafka_to_clickhouse_raw_products    
    )

    consume_3 = PythonOperator(
        task_id="consumer_raw_customers",
        python_callable=run_kafka_to_clickhouse_raw_customers  
    )

    consume_4 = PythonOperator(
        task_id="consumer_raw_stores",
        python_callable=run_kafka_to_clickhouse_raw_stores 
    )

    consume_5 = PythonOperator(
        task_id="consumer_raw_purchases",
        python_callable=run_kafka_to_clickhouse_raw_purchases
    )

    run_pyspark_task = PythonOperator(
        task_id="run_spark_s3",
        python_callable=run_spark_s3,
    )


    finish = EmptyOperator(
        task_id = 'finish'
    )
start_producer >> [produce_1, produce_2, produce_3, produce_4, produce_5] \
>> start_consumer \
>> [consume_1, consume_2, consume_3, consume_4] >> consume_5 \
>> run_pyspark_task \
>> finish