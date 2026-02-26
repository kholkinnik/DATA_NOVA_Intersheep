#===== Producer: MongoDB → Kafka ===========
#===== raw_stores

from kafka import KafkaProducer
import json
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime
load_dotenv()

import hashlib

# Подключение к MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["pikcha_market"] 
collection = db["stores"]

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
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
    #print(f"Отправлен ID:", *[filtered_doc[i] for i in ['store_id', 'store_name']])

    


producer.flush()
producer.close()
client.close()

print("\n✅ Загрузка в топик raw_stores завершена!")
