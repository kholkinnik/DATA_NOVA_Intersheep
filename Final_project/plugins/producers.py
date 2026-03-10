from kafka import KafkaProducer
import json
from pymongo import MongoClient
#from airflow.hooks.base import BaseHook   
import logging

logger = logging.getLogger(__name__)

#================данные для топика raw-products-kbju ============================
def producer_mongo_to_raw_products_kbju():

    logger.info("➡️ Запуск producer: Mongo → Kafka")

    # MongoDB подключене к MongoDb
    client = MongoClient("mongodb://mongo:27017/", serverSelectionTimeoutMS=5000)
    db = client["pikcha_market"]
    logger.info("✅ Успешное подключение к MongoDb")


    collection = db["products"]
    # Kafka Producer
    producer = KafkaProducer(
        bootstrap_servers=["kafka:29092"],
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda k: k.encode("utf-8") if k else None,
    )

    docs = collection.find(
        {},
        {
            "id": 1,
            "kbju.calories": 1,
            "kbju.carbohydrates": 1,
            "kbju.fat": 1,
            "kbju.protein": 1,
        },
    )
    msg_count = 0
    for doc in docs:
        kbju = doc.get("kbju", {})
        filtered_doc = {
            "prod_id": doc.get("id"),
            "calories": kbju.get("calories"),
            "carbohydrates": kbju.get("carbohydrates"),
            "fat": kbju.get("fat"),
            "protein": kbju.get("protein"),
        }
        key = filtered_doc.get("prod_id")
        producer.send("raw-products-kbju", key=key, value=filtered_doc)
        msg_count += 1

    producer.flush()
    producer.close()
    client.close()

    print(f"✅ Mongo → Kafka: направлено {msg_count} сообщений в топик raw-products-kbju!")


#================данные для топика raw_products ============================
def producer_mongo_to_raw_products():

    logger.info("➡️ Запуск producer: Mongo → Kafka")

    # MongoDB подключене к MongoDb
    client = MongoClient("mongodb://mongo:27017/", serverSelectionTimeoutMS=5000)
    db = client["pikcha_market"]
    logger.info("✅ Успешное подключение к MongoDb")

    collection = db["products"]
    producer = KafkaProducer(
        bootstrap_servers="kafka:29092",
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8') if k else None
    )
    # выбор для сообщения только необходимых полей из коллекции
    docs = list(collection.find({}, {
        'id': 1,
        'name': 1,
        'group': 1,
        'description': 1,
        'price': 1,
        'unit':1,
        'origin_country': 1,
        'expiry_days': 1,
        'is_organic': 1,
        'barcode': 1
    }))
    msg_count = 0
    for doc in docs:
        # Преобразование в плоский dict
        filtered_doc = {
            'prod_id': doc.get('id'),
            'name': doc.get('name'),
            'group': doc.get('group')[2::], # убираю эмодзи 🍏, 🥩, 🥦
            'description': doc.get('description'),
            'price': doc.get('price'),
            'unit': doc.get('unit'),
            'origin_country': doc.get('origin_country'),
            'expiry_days': doc.get('expiry_days'),
            'is_organic': doc.get('is_organic'),
            'barcode': doc.get('barcode')

        }
        key = filtered_doc.get('prod_id')
        producer.send('raw-products', key=key, value=filtered_doc)
        msg_count += 1
        # print(f"Отправлен ID: {key}")
    producer.flush()
    producer.close()
    client.close()
    
    print(f"✅ Mongo → Kafka: направлено {msg_count} сообщений в топик raw-products!")

#================данные для топика raw_customer ============================
def producer_mongo_to_raw_customer():

    logger.info("➡️ Запуск producer: Mongo → Kafka")

    # MongoDB подключене к MongoDb
    client = MongoClient("mongodb://mongo:27017/", serverSelectionTimeoutMS=5000)
    db = client["pikcha_market"]
    logger.info("✅ Успешное подключение к MongoDb")
    
    import hashlib
    
    db = client["pikcha_market"] 
    collection = db["customers"]

    producer = KafkaProducer(
        bootstrap_servers="kafka:29092",
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8') if k else None
    )
    # выбор для сообщения только необходимых полей из коллекции
    docs = list(collection.find({}, {
        'customer_id': 1,
        'first_name': 1,
        'last_name': 1,
        'email': 1,
        'phone': 1,
        'birth_date': 1,
        'gender': 1,
        'registration_date': 1,
        'is_loyalty_member': 1,
        'loyalty_card_number': 1
        
    }))
    msg_count = 0
    for doc in docs:
        # Преобразование в плоский dict
        filtered_doc = {
            'customer_id': doc.get('customer_id'),
            'first_name': doc.get('first_name'),
            'last_name': doc.get('last_name'),
            'email': doc.get('email'),
            'phone': hashlib.md5(('+7'+''.join([i for i in doc.get('phone') if i.isdigit()])[-10::]).encode()).hexdigest(),
            'birth_date': doc.get('birth_date'),
            'gender': doc.get('gender'),
            'registration_date': doc.get('registration_date'),
            'is_loyalty_member': doc.get('is_loyalty_member'),
            'loyalty_card_number': doc.get('loyalty_card_number')
        }
        key = filtered_doc.get('customer_id')
        producer.send('raw-customers', key=key, value=filtered_doc)
        msg_count += 1
        #print(f"Отправлен ID: {filtered_doc['customer_id']}")
    producer.flush()
    producer.close()
    client.close()
   
    print(f"✅ Mongo → Kafka: направлено {msg_count} сообщений в топик raw_customer!")

#================данные для топика raw_stores ============================
def producer_mongo_to_raw_stores():

    logger.info("➡️ Запуск producer: Mongo → Kafka")

    client = MongoClient("mongodb://mongo:27017/", serverSelectionTimeoutMS=5000) 
    db = client["pikcha_market"] 
    collection = db["stores"]
    logger.info("✅ Успешное подключение к MongoDb")

    producer = KafkaProducer(
        bootstrap_servers="kafka:29092",
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8') if k else None
    )
    # выбор для сообщения только необходимых полей из коллекции
    docs = list(collection.find({}, {
        'store_id': 1,
        'store_name': 1,
        'store_network': 1,
        'store_type_description': 1,
        'type' : 1
        
    }))
    msg_count = 0 
    for doc in docs:
        # Преобразование в плоский dict
        filtered_doc = {
            'store_id': doc.get('store_id'),
            'store_name': doc.get('store_name'),
            'store_network': doc.get('store_network'),
            'store_type_description': doc.get('store_type_description'),
            'type': doc.get('type')
        }
        key = filtered_doc.get('store_id')
        producer.send('raw-stores', key=key, value=filtered_doc)
        msg_count += 1
        #print(f"Отправлен ID:", *[filtered_doc[i] for i in ['store_id', 'store_name']])
    producer.flush()
    producer.close()
    client.close()
    
    print(f"✅ Mongo → Kafka: направлено {msg_count} сообщений в топик raw-stores!")

#================данные для топика raw_purchases ============================
def producer_mongo_to_raw_purchases():
  
    logger.info("➡️ Запуск producer: Mongo → Kafka")

    client = MongoClient("mongodb://mongo:27017/", serverSelectionTimeoutMS=5000) 

    db = client["pikcha_market"] 
    collection = db["purchases"]
    logger.info("✅ Успешное подключение к MongoDb")

    producer = KafkaProducer(
        bootstrap_servers="kafka:29092",
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        key_serializer=lambda k: k.encode('utf-8') if k else None
    )
    # выбор для сообщения только необходимых полей из коллекции
    docs = list(collection.find({}, {
        'purchase_id': 1,
        'customer.customer_id': 1,
        'store.store_id': 1,
        'items.product_id': 1,
        'total_amount': 1,
        'payment_method': 1,
        'is_delivery' :1,
        'purchase_datetime':1
    }))
    msg_count = 0
    for doc in docs:
        # Преобразование в плоский dict
        customer = doc.get('customer', {})
        store = doc.get('store', {})
        items = doc.get('items', {})
   
        filtered_doc = {
            'purchase_id': doc.get('purchase_id'),
            'customer_id': customer.get('customer_id'),
            'store_id': store.get('store_id'),
            'product_id': items[0].get('product_id'),
            'total_amount' : doc.get('total_amount'),
            'payment_method': doc.get('payment_method'),
            'is_delivery' : doc.get('is_delivery'),
            'purchase_datetime': doc.get('purchase_datetime')
        }
        key = filtered_doc.get('purchase_id')
        producer.send('raw-purchases', key=key, value=filtered_doc)
        msg_count += 1
        #print(f"Отправлен ID: {filtered_doc}")

    producer.flush()
    producer.close()
    client.close()
    print(f"✅ Mongo → Kafka: направлено {msg_count} сообщений в топик raw-purchases!")