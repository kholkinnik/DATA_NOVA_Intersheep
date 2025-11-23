# 1. Посмотреть список работающих контейнеров
docker ps

# 2. Зайти внутрь контейнера Kafka
docker exec -it <имя контейнера> bash
docker exec -it 26a4a5f52f87 bash

# 3. Проверить, где Kafka хранит логи (путь из config-файла)
grep log.dirs /etc/kafka/server.properties
# → Выдаст: log.dirs=/var/lib/kafka

# 4. Перейти в каталог с логами Kafka
cd /var/lib/kafka

# 5. Посмотреть, что там есть
ls -lah

# 6. Перейти в подкаталог с данными (это указанный log.dirs)
cd data

# 7. Посмотреть содержимое — там будет папка по топику
ls -lah

# 8. Перейти в папку раздела топика, например `user_events-0`
cd user_events-0

# 9. Посмотреть, какие файлы там есть (логи, индексы и т.д.)
ls -lah


# посмотреть какие есть топики( сначала зайди в контейнер)
kafka-topics --bootstrap-server localhost:9092 --list

# посомтерть какие сообщения в топике 
kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic user_events_01 \
  --from-beginning

# очистить топик от сообщений (через удаление)
# удалить топик
kafka-topics \
  --bootstrap-server localhost:9092 \
  --delete \
  --topic user_events_01
