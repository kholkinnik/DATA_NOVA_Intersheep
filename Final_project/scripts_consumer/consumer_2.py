from kafka import KafkaConsumer
import json
import clickhouse_connect




import os
from dotenv import load_dotenv
# загружаю переменные окружения
load_dotenv()
CLICKHOUSE_USER=os.getenv("CLICKHOUSE_USER")
CLICKHOUSE_PASSWORD= os.getenv("CLICKHOUSE_PASSWORD")


consumer = KafkaConsumer(
    "raw-products",
    bootstrap_servers="localhost:9092",
    group_id= None,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    consumer_timeout_ms=5000
    
)

client = clickhouse_connect.get_client(host='localhost', port=8123, username=CLICKHOUSE_USER, password=CLICKHOUSE_PASSWORD) 
print("\n⏳  читаю raw_products")


for message in consumer:
    doc = message.value
    row = [(
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
    )]

    client.insert(table='raw_products', data=row, column_names=['product_id', 'name', 'group', 'description', 'price', 'unit', 'origin_country', 'expiry_days', 'is_organic', 'barcode' ])
    # print(f'✅ запись {row} вставлена в таблицу raw_products')

consumer.close()
client.close()
print(f'✅ Топик raw_products прочитан')
