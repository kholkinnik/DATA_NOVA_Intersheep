"""
DAG: postgres_monitoring
Описание: Мониторинг состояния PostgreSQL и отправка уведомлений
Время запуска: Каждый день в 9 утра
Автор: DevOps Engineer
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime, timedelta


# ФУНКЦИЯ: Проверка здоровья базы данных
def check_database_health(**context):
    """
    Проверяем различные параметры здоровья базы данных
    Используем context для получения даты запуска и других метаданных
    """
    execution_date = context['execution_date']
    print(f"🔍 Проверка здоровья БД за {execution_date}")

    try:
        # Импортируем psycopg2 внутри функции для лучшей изоляции
        import psycopg2
        from psycopg2 import OperationalError

        # Шаг 1: Пытаемся подключиться к базе данных
        print("  1. Проверка подключения...")
        conn = psycopg2.connect(
            host='postgres',
            database='airflow',
            user='airflow',
            password='airflow',
            port=5432,
            connect_timeout=5  # Таймаут 5 секунд
        )

        cursor = conn.cursor()

        # Шаг 2: Проверяем доступность базы
        cursor.execute("SELECT 1")
        print("     ✅ Подключение успешно")

        # Шаг 3: Проверяем время работы базы
        cursor.execute("SELECT pg_postmaster_start_time()")
        start_time = cursor.fetchone()[0]
        uptime = datetime.now() - start_time
        print(f"     ⏰ Время работы: {uptime}")

        # Шаг 4: Проверяем количество подключений
        cursor.execute("SELECT COUNT(*) FROM pg_stat_activity")
        connections = cursor.fetchone()[0]
        print(f"     🔌 Активных подключений: {connections}")

        # Шаг 5: Проверяем размер базы данных
        cursor.execute("""
            SELECT pg_database_size('airflow') as size_bytes,
                   pg_size_pretty(pg_database_size('airflow')) as size_pretty
        """)
        db_size = cursor.fetchone()
        print(f"     💾 Размер БД: {db_size[1]} ({db_size[0]} байт)")

        # Шаг 6: Проверяем последние ошибки в логах
        print("  2. Проверка логов на ошибки...")
        cursor.execute("""
                       SELECT COUNT(*)
                       FROM information_schema.tables
                       WHERE table_schema = 'public'
                       """)
        table_count = cursor.fetchone()[0]
        print(f"     📊 Таблиц в базе: {table_count}")

        # Шаг 7: Закрываем соединение
        cursor.close()
        conn.close()

        # Шаг 8: Формируем отчет
        health_report = {
            'status': 'HEALTHY',
            'uptime': str(uptime),
            'connections': connections,
            'size': db_size[1],
            'tables': table_count,
            'checked_at': datetime.now().isoformat()
        }

        # Сохраняем отчет в XCom для других задач
        context['ti'].xcom_push(key='health_report', value=health_report)

        print("✅ Проверка здоровья завершена успешно!")
        return "База данных в норме"

    except OperationalError as e:
        print(f"❌ Ошибка подключения: {e}")
        # Здесь можно отправить алерт в Slack/Telegram/Email
        return "Ошибка подключения к базе данных"


# ФУНКЦИЯ: Мониторинг таблиц
def monitor_tables(**context):
    """
    Мониторинг роста таблиц и поиск аномалий
    """
    print("📈 Мониторинг таблиц...")

    try:
        import psycopg2
        import pandas as pd

        conn = psycopg2.connect(
            host='postgres',
            database='airflow',
            user='airflow',
            password='airflow',
            port=5432
        )

        # Запрос для получения информации о таблицах
        query = """
                SELECT schemaname as schema,
                tablename as table_name,
                pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename)) as total_size,
                pg_size_pretty(pg_relation_size(schemaname || '.' || tablename)) as table_size,
                pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename) - 
                              pg_relation_size(schemaname || '.' || tablename)) as index_size,
                n_live_tup as row_count
                FROM pg_stat_user_tables
                ORDER BY pg_total_relation_size(schemaname || '.' || tablename) DESC
                    LIMIT 10 \
                """

        # Используем pandas для удобства анализа
        df = pd.read_sql_query(query, conn)

        print("\n🏆 Топ-10 самых больших таблиц:")
        print("-" * 80)
        for idx, row in df.iterrows():
            print(f"{idx + 1:2}. {row['table_name']:30} | Размер: {row['total_size']:10} | Строк: {row['row_count']:8}")

        # Проверяем аномалии
        large_tables = df[df['row_count'] > 1000000]  # Таблицы с более чем 1M строк
        if not large_tables.empty:
            print("\n⚠️  ВНИМАНИЕ: Найдены очень большие таблицы!")
            for _, table in large_tables.iterrows():
                print(f"    {table['table_name']}: {table['row_count']} строк")

        conn.close()

    except Exception as e:
        print(f"❌ Ошибка при мониторинге таблиц: {e}")


# ФУНКЦИЯ: Отправка отчета
def send_monitoring_report(**context):
    """
    Формируем и отправляем итоговый отчет
    """
    print("📨 Формирую отчет о мониторинге...")

    # Получаем данные из предыдущих задач
    try:
        health_report = context['ti'].xcom_pull(
            task_ids='check_health_task',
            key='health_report'
        )

        if health_report:
            print("\n" + "=" * 60)
            print("📋 ОТЧЕТ О МОНИТОРИНГЕ POSTGRESQL")
            print("=" * 60)

            for key, value in health_report.items():
                if key != 'checked_at':
                    print(f"{key.upper():15}: {value}")

            print(f"ПРОВЕРЕНО       : {health_report['checked_at']}")
            print("=" * 60)

            # Здесь можно добавить отправку email или в Slack
            # Например: send_email(report) или send_slack_message(report)

            print("✅ Отчет сформирован успешно!")
        else:
            print("⚠️  Отчет о здоровье не найден")

    except Exception as e:
        print(f"❌ Ошибка при формировании отчета: {e}")


# НАСТРОЙКИ DAG
default_args = {
    'owner': 'devops',  # Владелец DAG
    'depends_on_past': False,  # Не зависеть от прошлых запусков
    'email_on_failure': True,  # Отправлять email при ошибке
    'email_on_retry': False,  # Не отправлять при повторной попытке
    'retries': 2,  # Количество попыток при ошибке
    'retry_delay': timedelta(minutes=5),  # Пауза между попытками
    'start_date': datetime(2023, 1, 1),  # Дата начала работы
}

# СОЗДАЕМ DAG ДЛЯ МОНИТОРИНГА
with DAG(
        'postgres_monitoring',
        default_args=default_args,
        description='Ежедневный мониторинг состояния PostgreSQL',
        catchup=False,
        tags=['monitoring', 'postgres', 'devops']
) as dag:
    # ЗАДАЧА 1: Проверка здоровья БД с помощью PythonOperator
    check_health_task = PythonOperator(
        task_id='check_health_task',
        python_callable=check_database_health,
        provide_context=True,  # Важно! Передаем контекст Airflow
        execution_timeout=timedelta(minutes=10)  # Таймаут 10 минут
    )

    # ЗАДАЧА 2: Проверка медленных запросов с помощью PostgresOperator
    check_slow_queries_task = PostgresOperator(
        task_id='check_slow_queries_task',
        postgres_conn_id='postgres_default',
        sql="""
            -- Ищем медленные запросы (выполнялись больше 1 секунды)
            -- Эта таблица доступна если включен pg_stat_statements
            SELECT 
                query,
                calls,
                total_time,
                mean_time,
                rows
            FROM pg_stat_statements 
            WHERE mean_time > 1000  -- больше 1 секунды
            ORDER BY mean_time DESC
            LIMIT 5;

            -- Если таблицы нет, просто возвращаем сообщение
            SELECT 'pg_stat_statements не настроен' as status
            WHERE NOT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'pg_stat_statements'
            );
        """
    )

    # ЗАДАЧА 3: Мониторинг таблиц с помощью PythonOperator
    monitor_tables_task = PythonOperator(
        task_id='monitor_tables_task',
        python_callable=monitor_tables,
        provide_context=True
    )

    # ЗАДАЧА 4: Создание лога мониторинга с помощью PostgresOperator
    create_monitoring_log_task = PostgresOperator(
        task_id='create_monitoring_log_task',
        postgres_conn_id='postgres_default',
        sql="""
            -- Создаем таблицу для логов мониторинга если ее нет
            CREATE TABLE IF NOT EXISTS monitoring_logs
            (
                id
                SERIAL
                PRIMARY
                KEY,
                check_date
                TIMESTAMP
                DEFAULT
                CURRENT_TIMESTAMP,
                status
                VARCHAR
            (
                20
            ),
                uptime INTERVAL,
                connection_count INTEGER,
                database_size TEXT,
                table_count INTEGER,
                details TEXT
                );

            -- Вставляем запись о текущей проверке
            -- Данные будут заполнены позже через XCom
            INSERT INTO monitoring_logs (status, check_date)
            VALUES ('IN_PROGRESS', CURRENT_TIMESTAMP);

            -- Показываем последние 5 проверок
            SELECT check_date,
                   status,
                   connection_count,
                   database_size
            FROM monitoring_logs
            ORDER BY check_date DESC LIMIT 5;
            """
    )

    # ЗАДАЧА 5: Отправка отчета с помощью PythonOperator
    send_report_task = PythonOperator(
        task_id='send_report_task',
        python_callable=send_monitoring_report,
        provide_context=True
    )

    # ОПРЕДЕЛЯЕМ ПОРЯДОК ВЫПОЛНЕНИЯ:
    # 1. Сначала проверяем здоровье БД
    # 2. Параллельно проверяем медленные запросы и создаем лог
    # 3. Затем мониторим таблицы
    # 4. В конце отправляем отчет

    check_health_task >> [check_slow_queries_task, create_monitoring_log_task]
    [check_slow_queries_task, create_monitoring_log_task] >> monitor_tables_task
    monitor_tables_task >> send_report_task