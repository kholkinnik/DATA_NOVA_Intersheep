from kafka import KafkaConsumer
import json
import clickhouse_connect
from datetime import datetime, date
#====== raw_purchases ==========
import os
from dotenv import load_dotenv
# загружаю переменные окружения
load_dotenv()
CLICKHOUSE_USER=os.getenv("CLICKHOUSE_USER")
CLICKHOUSE_PASSWORD= os.getenv("CLICKHOUSE_PASSWORD")

consumer = KafkaConsumer(
    "raw_purchases",
    bootstrap_servers="localhost:9092",
    group_id= None,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    consumer_timeout_ms=5000
    
)

client = clickhouse_connect.get_client(host='localhost', port=8123, username=CLICKHOUSE_USER, password=CLICKHOUSE_PASSWORD) 
print("\n⏳  читаю raw_purchases")

# вот сейчас будут изменения
for message in consumer:
    doc = message.value
    row = [(
        doc.get('purchase_id'),
        doc.get('customer_id'),
        doc.get('store_id'),
        doc.get('product_id'),
        doc.get('total_amount'),     
        doc.get('payment_method'),
        doc.get('is_delivery'),
        datetime.strptime(doc.get('purchase_datetime'), '%Y-%m-%dT%H:%M:%S.%f')       
    )]
    #print(row)
    client.insert(table='raw_purchases', 
                  data=row, 
                  column_names=['purchase_id', 'customer_id', 'store_id', 'product_id', 'total_amount', 'payment_method', 'is_delivery', 'purchase_datetime'])
    #print(f'✅ запись {row} вставлена в таблицу raw_customers')

consumer.close()
client.close()
print(f'✅ Топик raw_purchases прочитан')


