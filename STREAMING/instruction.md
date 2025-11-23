# создаю виртуальное окружение
python -m venv venv
# активировать виртуальное окружение
venv\Scripts\activate
_____________________________________________________

# Устанавливаю зависимости 
Хорошее правило все зависимости - библиоотеки лежат в файле requirments.txt
# "ЗамораживаюЭ зависимости 
pip freeze
# вывожу все в requirments.txt
pip freeze > requirments.txt
# устанавлию в терминала из файла
pip install -r requirements.txt
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

# устанавливаю библиотеку для переменных окружения
pip install python-dotenv

# остановить процесс вставки и чтения данных
Ctrl+C

