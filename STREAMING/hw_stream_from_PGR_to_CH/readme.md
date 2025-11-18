#### В данном проекте реализуется pipeline передачи данных между БД Postgres и Clickhouse, с использованием Kafka
# 1. Смонтируй образ при помощи docker-compose
docker-compose up -d
* при первом запуске будет сформирован Датасет, в соответствии скрипта user_logins.sql
* проверь загрузилисьли данные

# Запусти producer запуска процесса записи в топик kafka
python producer.py - скрипт прочитает данные из БД и положит их в топик "streaming_hw_kafka"

# Запусти consumer для записи из kafka 
python consumer.py - скрипт прочитает данные из топика "streaming_hw_kafka"

# Проверка идемпотентности останови 
останови producer и consumer клавишами Сtrl+C
запусти producer и consumer заново

