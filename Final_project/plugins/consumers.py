from airflow_clickhouse_plugin.hooks.clickhouse import ClickHouseHook
from kafka import KafkaConsumer
import json
import logging
from datetime import datetime, date

logger = logging.getLogger(__name__)

# ========= 1. данные из топика "raw-products-kbju"====================
def run_kafka_to_clickhouse_raw_products_kbju( ):
    logger.info("⬅️ Запуск consumer: Kafka → ClickHouse")

    # Получаем clickhouse_driver.Client через Hook
    client = ClickHouseHook(clickhouse_conn_id='clickhouse_default')
    consumer = KafkaConsumer(
        "raw-products-kbju",
        bootstrap_servers="kafka:29092",
        group_id="raw-products-kbju",
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode("utf-8")),
        consumer_timeout_ms=5000,
    )

    msg_count = 0
    batch = []  # Буфер для батча
    BATCH_SIZE = 10  # Размер батча для оптимизации (под данный проект - ок)

    for message in consumer:
        doc = message.value
        row = (                            # Tuple без внешнего списка
            doc.get("prod_id"),
            doc.get("calories"),
            doc.get("carbohydrates"),
            doc.get("fat"),
            doc.get("protein"),
        )
        batch.append(row)
        msg_count += 1

        if len(batch) >= BATCH_SIZE:
            client.execute(
                "INSERT INTO raw_products_kbju (product_id, calories, carbohydrates, fat, protein) VALUES",
                batch  # Список tuples — батч вставляется целиком
            )
            logger.info(f"📦 Вставлен батч из {len(batch)} записей")
            batch = []

    # Финальный батч( или остаток)
    if batch:
        client.execute(
            "INSERT INTO raw_products_kbju (product_id, calories, carbohydrates, fat, protein) VALUES",
            batch
        )
        logger.info(f"📦 Финальный батч: {len(batch)} записей")

    consumer.close()
    
    logger.info(f"✅ Всего вставлено {msg_count} записей в raw_products_kbju")

# ========= 2. данные из топика "raw-products"====================
def run_kafka_to_clickhouse_raw_products( ):
    logger.info("⬅️ Запуск consumer: Kafka → ClickHouse")

    # Получаем clickhouse_driver.Client через Hook
    client = ClickHouseHook(clickhouse_conn_id='clickhouse_default')

    consumer = KafkaConsumer(
        "raw-products",
        bootstrap_servers="kafka:29092",
        group_id= "raw-products",
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        consumer_timeout_ms=5000    
    )

    msg_count = 0
    batch = []  # Буфер для батча
    BATCH_SIZE = 10  # Размер батча для оптимизации (под данный проект - ок)

    for message in consumer:
        doc = message.value
        row = (
            doc.get('prod_id'),
            doc.get('name'),
            doc.get('group'),
            doc.get('description'),
            doc.get('price'),
            doc.get('unit'),
            doc.get('origin_country'),
            doc.get('expiry_days'),
            doc.get('is_organic'),
            doc.get('barcode'),
        )
        batch.append(row)
        msg_count += 1

        if len(batch) >= BATCH_SIZE:
            client.execute(
                "INSERT INTO raw_products (product_id, name, group, description, price, unit, origin_country, expiry_days, is_organic, barcode ) VALUES",
                batch  # Список tuples — батч вставляется целиком
            )
            logger.info(f"📦 Вставлен батч из {len(batch)} записей")
            batch = []

    # Финальный батч( или остаток)
    if batch:
        client.execute(
            "INSERT INTO raw_products (product_id, name, group, description, price, unit, origin_country, expiry_days, is_organic, barcode ) VALUES",
            batch
        )
    consumer.close()    

    logger.info(f"✅ Всего вставлено {msg_count} записей в raw_products")

# =========3. данные из топика "raw-customers"====================
def run_kafka_to_clickhouse_raw_customers( ):
    logger.info("⬅️ Запуск consumer: Kafka → ClickHouse")

    # Получаем clickhouse_driver.Client через Hook
    client = ClickHouseHook(clickhouse_conn_id='clickhouse_default')

    consumer = KafkaConsumer(
        "raw-customers",
        bootstrap_servers="kafka:29092",
        group_id= "raw-customers",
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        consumer_timeout_ms=5000    
    )

    msg_count = 0
    batch = []  # Буфер для батча
    BATCH_SIZE = 10  # Размер батча для оптимизации (под данный проект - ок)

    for message in consumer:
        doc = message.value
        row = ( doc.get('customer_id'),
                doc.get('first_name'),
                doc.get('last_name'),
                doc.get('email'),
                doc.get('phone'),
                datetime.strptime(doc.get('birth_date'), '%Y-%m-%d').date(),
                doc.get('gender'),
                datetime.strptime(doc.get('registration_date'), '%Y-%m-%dT%H:%M:%S.%f'), 
                doc.get('is_loyalty_member'),
                doc.get('loyalty_card_number'),
                )
        
        batch.append(row)
        msg_count += 1

        if len(batch) >= BATCH_SIZE:
            client.execute(
                "INSERT INTO raw_customers (customer_id, first_name, last_name, email, phone, birth_date, gender, registration_date, is_loyalty_member, loyalty_card_number) VALUES",
                batch  # Список tuples — батч вставляется целиком
            )
            logger.info(f"📦 Вставлен батч из {len(batch)} записей")
            batch = []

    # Финальный батч( или остаток)
    if batch:
        client.execute(
            "INSERT INTO raw_customers (customer_id, first_name, last_name, email, phone, birth_date, gender, registration_date, is_loyalty_member, loyalty_card_number) VALUES",
            batch
        )
    consumer.close()    

    logger.info(f"✅ Всего вставлено {msg_count} записей в raw-customers")


# =========4. данные из топика "raw_stores"====================
def run_kafka_to_clickhouse_raw_stores( ):
    logger.info("⬅️ Запуск consumer: Kafka → ClickHouse")

    # Получаем clickhouse_driver.Client через Hook
    client = ClickHouseHook(clickhouse_conn_id='clickhouse_default')

    consumer = KafkaConsumer(
        "raw-stores",
        bootstrap_servers="kafka:29092",
        group_id= "raw-stores",
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        consumer_timeout_ms=5000    
    )

    msg_count = 0
    batch = []  # Буфер для батча
    BATCH_SIZE = 10  # Размер батча для оптимизации (под данный проект - ок)

    for message in consumer:
        doc = message.value
        row = ( doc.get('store_id'),
                doc.get('store_name'),
                doc.get('store_network'),
                doc.get('store_type_description'),
                doc.get('type'),
            ) 
        
        batch.append(row)
        msg_count += 1

        if len(batch) >= BATCH_SIZE:
            client.execute(
                "INSERT INTO raw_stores (store_id, store_name, store_network, store_type_description, type) VALUES",
                batch  # Список tuples — батч вставляется целиком
            )
            logger.info(f"📦 Вставлен батч из {len(batch)} записей")
            batch = []

    # Финальный батч( или остаток)
    if batch:
        client.execute(
            "INSERT INTO raw_stores (store_id, store_name, store_network, store_type_description, type) VALUES",
            batch
        )
    consumer.close()    

    logger.info(f"✅ Всего вставлено {msg_count} записей в raw_stores")

# ========= 5. данные из топика "raw-purchases"====================
def run_kafka_to_clickhouse_raw_purchases( ):
    logger.info("⬅️ Запуск consumer: Kafka → ClickHouse")

    # Получаем clickhouse_driver.Client через Hook
    client = ClickHouseHook(clickhouse_conn_id='clickhouse_default')

    consumer = KafkaConsumer(
        "raw-purchases",
        bootstrap_servers="kafka:29092",
        group_id= "raw-purchases",
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        consumer_timeout_ms=5000    
    )

    msg_count = 0
    batch = []  # Буфер для батча
    BATCH_SIZE = 10  # Размер батча для оптимизации (под данный проект - ок)

    for message in consumer:
        doc = message.value
        row = (
            doc.get('purchase_id'),
            doc.get('customer_id'),
            doc.get('store_id'),
            doc.get('product_id'),
            doc.get('total_amount'),     
            doc.get('payment_method'),
            doc.get('is_delivery'),
            datetime.strptime(doc.get('purchase_datetime'), '%Y-%m-%dT%H:%M:%S.%f')
            )
        
        batch.append(row)
        msg_count += 1

        if len(batch) >= BATCH_SIZE:
            client.execute(
                "INSERT INTO raw_purchases (purchase_id, customer_id, store_id, product_id, total_amount, payment_method, is_delivery, purchase_datetime) VALUES",
                batch  # Список tuples — батч вставляется целиком
            )
            logger.info(f"📦 Вставлен батч из {len(batch)} записей")
            batch = []

    # Финальный батч( или остаток)
    if batch:
        client.execute(
            "INSERT INTO raw_customers (customer_id, first_name, last_name, email, phone, birth_date, gender, registration_date, is_loyalty_member, loyalty_card_number) VALUES",
            batch
        )
    consumer.close()    

    logger.info(f"✅ Всего вставлено {msg_count} записей в raw_purchases")
    

    
