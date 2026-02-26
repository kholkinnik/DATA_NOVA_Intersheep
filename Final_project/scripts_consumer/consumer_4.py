from kafka import KafkaConsumer
import json
import clickhouse_connect
from datetime import datetime, date

#======= raw_stores ======
import os
from dotenv import load_dotenv
# загружаю переменные окружения
load_dotenv()
CLICKHOUSE_USER=os.getenv("CLICKHOUSE_USER")
CLICKHOUSE_PASSWORD= os.getenv("CLICKHOUSE_PASSWORD")

consumer = KafkaConsumer(
    "raw-stores",
    bootstrap_servers="localhost:9092",
    group_id= None,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    consumer_timeout_ms=5000
    
)

client = clickhouse_connect.get_client(host='localhost', port=8123, username=CLICKHOUSE_USER, password=CLICKHOUSE_PASSWORD) 
print("\n⏳  читаю raw_stores")

# вот сейчас будут изменения
for message in consumer:
    doc = message.value
    row = [(
        doc.get('store_id'),
        doc.get('store_name'),
        doc.get('store_network'),
        doc.get('store_type_description'),
        doc.get('type')       
        

    )]
    
    client.insert(table='raw_stores', 
                  data=row, 
                  column_names=['store_id', 'store_name', 'store_network', 'store_type_description', 'type' ])
    # print(f'✅ запись {row} вставлена в таблицу raw_customers')

consumer.close()
client.close()
print(f'✅ Топик raw_stores прочитан')


