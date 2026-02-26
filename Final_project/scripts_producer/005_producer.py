#===== Producer: MongoDB → Kafka ===========
#===== raw_purchases

from kafka import KafkaProducer
import json
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from pprint import pprint

load_dotenv()

# Подключение к MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["pikcha_market"] 
collection = db["purchases"]

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
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
    key = filtered_doc.get('id')
    producer.send('raw_purchases', key=key, value=filtered_doc)
    #print(f"Отправлен ID: {filtered_doc}")

producer.flush()
producer.close()
client.close()

print("\n✅ Загрузка в топик raw_purchases завершена!")
