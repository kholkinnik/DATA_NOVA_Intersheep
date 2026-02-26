from kafka import KafkaConsumer
import json
import clickhouse_connect
import time
import os
from dotenv import load_dotenv

load_dotenv()
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD")

start_time = time.time()
MAX_RUNTIME = 30  # 30 секунд

consumer = KafkaConsumer(
    "raw-products",
    bootstrap_servers="localhost:9092",
    group_id=None,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    consumer_timeout_ms=30000  # Дополнительная защита
)

client = clickhouse_connect.get_client(
    host='localhost', 
    port=8123, 
    username=CLICKHOUSE_USER, 
    password=CLICKHOUSE_PASSWORD
)
print("✅ Подключение к Kafka(Consumer) и Clickhouse успешно!")
print(f"⏱️ Автоостановка через {MAX_RUNTIME} сек")

messages_processed = 0

try:
    for message in consumer:
        # ✅ ПРОВЕРКА ВРЕМЕНИ
        if time.time() - start_time > MAX_RUNTIME:
            print("\n⏰ 30 секунд истекло! Останавливаем...")
            break
            
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

        client.insert(
            table='raw_products', 
            data=row, 
            column_names=['product_id', 'name', 'group', 'description', 'price', 'unit', 'origin_country', 'expiry_days', 'is_organic', 'barcode']
        )
        messages_processed += 1
        print(f'✅ Запись {messages_processed} вставлена: {row}')

except KeyboardInterrupt:
    print("\n🛑 Остановка по Ctrl+C")
except Exception as e:
    print(f"❌ Ошибка: {e}")
finally:
    print(f"\n📊 Обработано сообщений: {messages_processed}")
    print(f"⏱️ Время работы: {time.time() - start_time:.1f} сек")
    consumer.close()
    client.close()
    print("🔒 Соединения закрыты")
