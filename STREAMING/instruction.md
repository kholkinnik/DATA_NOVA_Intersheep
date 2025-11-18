# создаю виртуальное окружение
python -m venv venv
# активировать виртуальное окружение
venv\Scripts\activate
_____________________________________________________
# создаем довер компос и запускаем командой
docker-compose up -d
# останавливаю контейнеры 
docker compose down
# останавливаю контейнеры и удаляю все тома
docker compose down -v
_____________________________________________________

# запускаем kafka-python
pip install kafka-python

# устанавливаю библиотеку для работы с postgres
pip install psycopg2

# устанавливаю библиотеку для работы с ClickHouse
pip install clickhouse-connect

# остановить процесс вставки и чтения данных
Ctrl+C

