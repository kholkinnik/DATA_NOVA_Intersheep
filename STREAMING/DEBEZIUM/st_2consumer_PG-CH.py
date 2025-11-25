from kafka import KafkaConsumer
import json
import requests
from datetime import datetime

CLICKHOUSE_URL = "http://localhost:8123"
CLICKHOUSE_USER = "default"
CLICKHOUSE_PASSWORD = "clickhousepass"

# Функция для создания таблицы в CH, через URL
def create_clickhouse_table(): 
    query = """
    CREATE TABLE IF NOT EXISTS changes (
        id UInt32,
        name String,
        created_at DateTime,
        op String,
        ts DateTime DEFAULT now()
    ) ENGINE = MergeTree()
    ORDER BY (id, ts);
    """
    r = requests.post(
        CLICKHOUSE_URL,
        data=query,
        auth=(CLICKHOUSE_USER, CLICKHOUSE_PASSWORD)
    )

# Функция принимает список событий batch и массово вставляет в CH 
def insert_to_clickhouse(batch):
    values = []
    for row in batch:
        id = row.get("id", 0)
        name = row.get("name", "")
        created_at = row.get("created_at", datetime.now().isoformat())
        op = row.get("op", "u")
        values.append(f"({id}, '{name}', toDateTime('{created_at}'), '{op}')")

    if values:
        query = (
            "INSERT INTO changes (id, name, created_at, op) VALUES " +
            ", ".join(values)
        )
        r = requests.post(
            CLICKHOUSE_URL,
            data=query,
            auth=(CLICKHOUSE_USER, CLICKHOUSE_PASSWORD)
        )

# Функция SELECT последних 10 записей (что бы убедиться что данные в CH сохраняются)
def select_changes():
    query = "SELECT * FROM changes ORDER BY ts DESC LIMIT 10"
    r = requests.post(
        CLICKHOUSE_URL,
        data=query,
        auth=(CLICKHOUSE_USER, CLICKHOUSE_PASSWORD)
    )
    if r.status_code == 200:
        print("📥 Последние события из ClickHouse:")
        print(r.text)
    else:
        print(f"❌ Ошибка при выполнении SELECT: {r.text}")

# подключается k Kafka и слушает только новые сообщения
def consume_kafka_once():
    consumer = KafkaConsumer(
        'pgserver1.public.my_table', # Название топика откуда читаем данные в нашем случае DEBEZIUM
        bootstrap_servers='localhost:29092', # Адрес брокера Kafka
        auto_offset_reset='latest', # Если нет сохраненной позиции то читаем последнее ('earlist', 'later', 'none')
        enable_auto_commit=False, # не сохранять автоматически позицию чтения(offset), управляем этим вручную
        group_id='pg-consumer-once', #Идентификатор группы - нужен для отслеживания offset-ов и балансироки между несколькими Consumer- ами 
        value_deserializer=lambda m: json.loads(m.decode('utf-8')), # преобразуем байты сообщения в JSON
        consumer_timeout_ms= 60000 # завершение чтение, если в течении 20 сек не приходит ни одного сообщения
    )

    print("🟢 Чтение сообщений из Kafka...\n")

    buffer = []

    for message in consumer:
        payload = message.value
        op = payload.get("op")

        if op == "u":
            after = payload.get("after")
            after["op"] = "u"
            print(f"🔁 Обновление: {after}")
            buffer.append(after)
        else:
            print(f"ℹ️ Пропущено (op = {op}):", payload)

    consumer.close() 

    if buffer:
        insert_to_clickhouse(buffer) # после 1 мин. если в buffer (см. consumer_timeout_ms= 60000)
    else:
        print("⚠️ Нет новых событий для записи в ClickHouse.") # если buffer оказался пустой, не пришло ни одного сообщения


if __name__ == '__main__':
    create_clickhouse_table()
    consume_kafka_once()
    select_changes()
