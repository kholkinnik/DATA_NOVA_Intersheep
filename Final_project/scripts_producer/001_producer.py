#===== Producer: MongoDB → Kafka ===========
#===== raw_products_kbju

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
    'kbju.calories': 1,
    'kbju.carbohydrates': 1,
    'kbju.fat': 1,
    'kbju.protein': 1
}))

for doc in docs:
    # Преобразование в плоский dict
    kbju = doc.get('kbju', {})
    filtered_doc = {
        'prod_id': doc.get('id'),
        'calories': kbju.get('calories'),
        'carbohydrates': kbju.get('carbohydrates'),
        'fat': kbju.get('fat'),
        'protein': kbju.get('protein')
    }
    key = filtered_doc.get('prod_id')
    producer.send('raw-products-kbju', key=key, value=filtered_doc)
    #print(f"Отправлен ID: {key}")

producer.flush()
producer.close()
client.close()

print("\n✅ Загрузка в топик raw_products_kbju завершена!")
