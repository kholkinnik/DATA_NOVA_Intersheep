# consumer_to_clickhouse.py
from kafka import KafkaConsumer
import json
import clickhouse_connect
from datetime import datetime

# библиотеки для переменных окружения
import os
from dotenv import load_dotenv
# загружаю переменные окружения
load_dotenv()
CLICKHOUSE_USER=os.getenv("CLICKHOUSE_USER")
CLICKHOUSE_PASSWORD= os.getenv("CLICKHOUSE_PASSWORD")

# подключение к Consumer
consumer = KafkaConsumer(
    "streaming_hw_kafka",
    bootstrap_servers="localhost:9092",
    group_id="streaming_hw_kafka_group_CH", # прописываю группу, что бы не было повторного чтения при запуске доп. консьюмера
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Подключение к ClickHouse
client = clickhouse_connect.get_client(host='localhost', port=8123, username= CLICKHOUSE_USER, password=CLICKHOUSE_PASSWORD)
# Создание таблицы для вставки данных
client.command("""
CREATE TABLE IF NOT EXISTS user_logins (
    id INTEGER,
    username String,
    event_type String,
    event_time DateTime
) ENGINE = MergeTree()
ORDER BY event_time
""")
# чтение данных из топика
for message in consumer:
    data = message.value
    print("Received:", data)
    try:
        # Использую client.insert для параметризированной вставки
        client.insert(
            table = "user_logins",
            data =[(
                data['id'],
                data['username'],
                data['event_type'],
                datetime.fromtimestamp(data['event_time'])  # преобразуем UNIX timestamp
            )]
        )
    except Exception as e:
        print (f"Ошибка вставки данных в Clickhouse: {e}")
    
