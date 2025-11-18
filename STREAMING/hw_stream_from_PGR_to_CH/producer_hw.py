# producer_pg_to_kafka.py
import psycopg2
from kafka import KafkaProducer
import json
import time

# Подключение к Kafka
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Подключаюсь к БД 
conn = psycopg2.connect(
    dbname="test_db", user="admin", password="admin", host="localhost", port=5432
)
cursor = conn.cursor()

# Получаем данные которые не передавались в Kafka, т.е. sent_to_kafka = FALSE
cursor.execute("SELECT id, username, event_type, extract(epoch FROM event_time) FROM user_logins WHERE sent_to_kafka = False")
events = cursor.fetchall()

# Сериализую и отправляю в Kafka
for event in events:
    data = {
        "id": event [0],
        "username": event[1],
        "event_type": event[2],
        "event_time": float(event[3])  # преобразуем Decimal → float
        
    }
    producer.send("streaming_hw_kafka", value=data) # указывается имя топика в который будут литься данные "user_events"
    print("Sent:", data)
    # После успешной отправки, выставляем sent_to_kafka = true
    cursor.execute("UPDATE user_logins SET sent_to_kafka = True WHERE id = %s", (event[0],))
    conn.commit()
    time.sleep(0.5)
