# Собираем кастомный образ для Airflow с тегом в текущей директории -t airflow-with-java .
docker build -t airflow-with-java .

# Предзапуск
- создай 4 папки: dags, logs, plugins, data, scripts
- или в терминале mkdir -p ./dags ./logs ./plugins ./data ./scripts
- проверь наличие docker-compose.yaml

# проведи инициализацию
docker compose up airflow-init
Это необходимо для инициализации, а так же, как пишут в официальной документации, "чтобы запустить миграцию базы данных и создать первую учетную запись пользователя".

# Запуск 
docker compose up -d

# Открытие интерфейса Airflow через браузер
http://localhost:8080/
пароль: airflow
пользователь: airflow

# Настрйока "clickhouse_default" в Airflow через нативный порт(по умолчанию 9000)
Connection Id:clickhouse_default
пользователь: default
пароль: password
host: clickhouse (смотри docker)

# Настрйока "clickhouse_http" ClickHouse в Airflow через 8123 HTTP‑интерфейс, через JDBC‑драйвер Spark‑а
Connection Id:clickhouse_http
Connection Type: Generic
host: clickhouse (смотри docker)
пользователь: default
пароль: password
Port: 8123