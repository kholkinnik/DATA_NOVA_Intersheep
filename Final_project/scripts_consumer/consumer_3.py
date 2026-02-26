from kafka import KafkaConsumer
import json
import clickhouse_connect
from datetime import datetime, date

import os
from dotenv import load_dotenv
# загружаю переменные окружения
load_dotenv()
CLICKHOUSE_USER=os.getenv("CLICKHOUSE_USER")
CLICKHOUSE_PASSWORD= os.getenv("CLICKHOUSE_PASSWORD")

consumer = KafkaConsumer(
    "raw-customers",
    bootstrap_servers="localhost:9092",
    group_id= None,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    consumer_timeout_ms=5000
    
)

client = clickhouse_connect.get_client(host='localhost', port=8123, username=CLICKHOUSE_USER, password=CLICKHOUSE_PASSWORD) 
print("\n⏳  читаю raw_customers")

# вот сейчас будут изменения
for message in consumer:
    doc = message.value
    row = [(
        doc.get('customer_id'),
        doc.get('first_name'),
        doc.get('last_name'),
        doc.get('email'),
        doc.get('phone'),
        datetime.strptime(doc.get('birth_date'), '%Y-%m-%d').date(),
        doc.get('gender'),
        datetime.strptime(doc.get('registration_date'), '%Y-%m-%dT%H:%M:%S.%f'), 
        doc.get('is_loyalty_member'),
        doc.get('loyalty_card_number'),
    )]
    
    client.insert(table='raw_customers', 
                  data=row, 
                  column_names=['customer_id', 'first_name', 'last_name', 'email', 'phone', 'birth_date', 'gender', 'registration_date', 'is_loyalty_member', 'loyalty_card_number' ])
    #print(f'✅ запись {row} вставлена в таблицу raw_customers')

consumer.close()
client.close()
print(f'✅ Топик raw_customers прочитан')


