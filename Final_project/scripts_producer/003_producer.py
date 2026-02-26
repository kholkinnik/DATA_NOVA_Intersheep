#===== Producer: MongoDB → Kafka ===========
#===== raw_customers

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
collection = db["customers"]

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
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
    #print(f"Отправлен ID: {filtered_doc['customer_id']}")
    


producer.flush()
producer.close()
client.close()


print("\n✅ Загрузка в топик raw_customer завершена!")
