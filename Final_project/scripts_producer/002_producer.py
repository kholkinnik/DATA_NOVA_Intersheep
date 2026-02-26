#===== Producer: MongoDB → Kafka ===========
#===== raw_products

from kafka import KafkaProducer
import json
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# Подключение к MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["pikcha_market"] 
collection = db["products"]

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
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
    # print(f"Отправлен ID: {key}")
    


producer.flush()
producer.close()
client.close()

print("\n✅ Загрузка в топик raw_products завершена!")
