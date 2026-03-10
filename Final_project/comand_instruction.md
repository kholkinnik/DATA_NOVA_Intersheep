#### Создание и Активация виртаального окружения
python -m venv venv
.\venv\Scripts\activate

#### Установка библиотек >> requirments.txt
pip install faker
pip install pymongo
pip install python-dotenv
pip install kafka-python
pip install clickhouse-connect


# Запуск и тест docker-compose.yaml
### Запуск Docker
docker compose up -d
<!-- ### Инициализация MongoDB Replica Set (выход из режима stanalone в репликационный) -->
<!-- docker exec -it mongo1 mongosh --eval "
rs.initiate({
  _id: 'rs0',
  members: [{ _id: 0, host: 'mongo1:27017' }]
})" -->
### проверка
### Проверка статусов
docker-compose ps
# Логи
docker-compose logs -f kafka
docker-compose logs -f mongo1
# Тест Kafka
# 1. Создать топик
docker exec -it kafka kafka-topics --create --topic test --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1
# 2. Посмотреть список
docker exec -it kafka kafka-topics --list --bootstrap-server kafka:9092
# 3. Отправить сообщение
echo "Hello from console!" | docker exec -i kafka kafka-console-producer --topic test --bootstrap-server kafka:9092
# 4. Прочитать сообщение 
docker exec -it kafka kafka-console-consumer --topic raw-purchases --bootstrap-server kafka:9092 --from-beginning

# 5. Удалить топик
docker exec -it kafka kafka-topics --delete --topic raw-products-kbju --bootstrap-server localhost:9092

# Тест ClickHouse
curl 'http://localhost:8123/?query=SELECT%201&user=default&password=password'

# Тест MongoDB
docker exec -it mongo_db mongosh
> show dbs

> use pikcha_market
  db.stats()
> db.products.find()


 # Работа с Grafana
 localhost:3000