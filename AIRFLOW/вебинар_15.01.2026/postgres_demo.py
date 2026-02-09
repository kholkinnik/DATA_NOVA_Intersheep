"""
POSTGRESQL + PYTHON - ИНТЕГРАЦИЯ С БАЗОЙ ДАННЫХ
Демонстрация работы с PostgreSQL через Airflow:

1. PostgresHook - для работы из Python кода
2. PostgresOperator - для выполнения SQL команд
3. Создание Connection в коде (если его нет в UI)
"""

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.python import PythonOperator
from datetime import datetime
import psycopg2

# =============== ФУНКЦИЯ: ПРОВЕРКА И СОЗДАНИЕ CONNECTION ===============
def setup_postgres_connection():
    """
    Создаем или обновляем Connection к PostgreSQL в Airflow.
    Это нужно сделать ОДИН РАЗ, потом Connection сохранится в UI.
    """
    try:
        # Подключаемся напрямую к PostgreSQL для проверки
        conn = psycopg2.connect(
            host='postgres',      # Имя сервиса из docker-compose
            database='airflow',   # База данных из конфигурации
            user='airflow',       # Пользователь из конфигурации
            password='airflow',   # Пароль из конфигурации
            port=5432            # Порт PostgreSQL
        )
        print("✅ PostgreSQL доступен!")
        conn.close()

        # Пытаемся создать Connection в Airflow (если нет прав - игнорируем)
        try:
            from airflow.models import Connection
            from airflow import settings

            session = settings.Session()

            # Проверяем, есть ли уже соединение
            existing_conn = session.query(Connection).filter(
                Connection.conn_id == 'postgres_default'
            ).first()

            if not existing_conn:
                # Создаем новое соединение
                new_conn = Connection(
                    conn_id='postgres_default',
                    conn_type='postgres',
                    host='postgres',
                    login='airflow',
                    password='airflow',
                    schema='airflow',
                    port=5432
                )
                session.add(new_conn)
                session.commit()
                print("✅ Connection 'postgres_default' создан в Airflow!")
            else:
                print("ℹ️ Connection 'postgres_default' уже существует")

        except Exception as e:
            print(f"⚠️ Не удалось создать Connection в Airflow: {e}")
            print("   Создайте Connection вручную в Airflow UI:")
            print("   Admin → Connections → Add")
            print("   Conn Id: postgres_default")
            print("   Conn Type: Postgres")
            print("   Host: postgres")
            print("   Login: airflow")
            print("   Password: airflow")
            print("   Schema: airflow")
            print("   Port: 5432")

    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {e}")
        raise


# =============== ФУНКЦИЯ: СОЗДАНИЕ ТЕСТОВЫХ ДАННЫХ ===============
def create_test_data(**context):
    """
    Создаем тестовые данные в памяти (без файлов)
    """
    # Тестовые данные - список словарей
    test_users = [
        {'id': 1, 'name': 'Анна', 'city': 'Москва', 'age': 25},
        {'id': 2, 'name': 'Борис', 'city': 'Санкт-Петербург', 'age': 32},
        {'id': 3, 'name': 'Виктория', 'city': 'Казань', 'age': 28},
        {'id': 4, 'name': 'Дмитрий', 'city': 'Новосибирск', 'age': 35},
        {'id': 5, 'name': 'Елена', 'city': 'Москва', 'age': 29},
    ]

    # Сохраняем в XCom для передачи другим задачам
    context['ti'].xcom_push(key='users_data', value=test_users)

    print(f"✅ Создано {len(test_users)} тестовых пользователей")
    return test_users


# =============== ФУНКЦИЯ: ВСТАВКА В БАЗУ POSTGRES ===============
def insert_to_postgres(**context):
    """
    Вставляем данные в PostgreSQL с использованием PostgresHook.
    Если Connection не настроен, используем прямое подключение.
    """
    # 1. Получаем данные из XCom
    users = context['ti'].xcom_pull(task_ids='create_data_task', key='users_data')

    try:
        # Пробуем использовать PostgresHook (если Connection настроен)
        hook = PostgresHook(postgres_conn_id='postgres_default')
        conn = hook.get_conn()
        print("✅ Используем PostgresHook с Connection 'postgres_default'")

    except Exception as e:
        print(f"⚠️ PostgresHook не сработал: {e}")
        print("   Использую прямое подключение...")

        # Прямое подключение через psycopg2
        conn = psycopg2.connect(
            host='postgres',
            database='airflow',
            user='airflow',
            password='airflow',
            port=5432
        )

    # 2. Получаем курсор и вставляем данные
    cursor = conn.cursor()

    for user in users:
        cursor.execute(
            """
            INSERT INTO test_users (id, name, city, age) 
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                city = EXCLUDED.city,
                age = EXCLUDED.age
            """,
            (user['id'], user['name'], user['city'], user['age'])
        )

    # 3. Сохраняем изменения
    conn.commit()
    cursor.close()
    conn.close()

    print(f"✅ Вставлено/обновлено {len(users)} записей в базу данных")


# =============== ФУНКЦИЯ: ЧТЕНИЕ ИЗ POSTGRES ===============
def read_from_postgres(**context):
    """
    Читаем данные из PostgreSQL и анализируем их
    """
    try:
        # Пробуем PostgresHook
        hook = PostgresHook(postgres_conn_id='postgres_default')
        df = hook.get_pandas_df("SELECT * FROM test_users ORDER BY id")

    except Exception as e:
        print(f"⚠️ PostgresHook не сработал: {e}")
        print("   Использую прямое подключение...")

        # Прямое подключение
        import pandas as pd
        conn = psycopg2.connect(
            host='postgres',
            database='airflow',
            user='airflow',
            password='airflow',
            port=5432
        )
        df = pd.read_sql_query("SELECT * FROM test_users ORDER BY id", conn)
        conn.close()

    print("\n📊 ДАННЫЕ ИЗ ТАБЛИЦЫ test_users:")
    print("=" * 40)
    print(df.to_string(index=False))

    # Аналитика данных
    if not df.empty:
        print("\n📈 СТАТИСТИКА:")
        print(f"   Всего пользователей: {len(df)}")
        print(f"   Средний возраст: {df['age'].mean():.1f} лет")

        # Группировка по городам
        city_stats = df.groupby('city').agg({
            'id': 'count',
            'age': 'mean'
        }).reset_index()

        print("\n🏙️  ПО ГОРОДАМ:")
        for _, row in city_stats.iterrows():
            print(f"   {row['city']}: {row['id']} чел., средний возраст {row['age']:.1f} лет")


# =============== ФУНКЦИЯ: АНАЛИЗ ДАННЫХ С PANDAS ===============
def analyze_with_pandas():
    """
    Дополнительный анализ данных с помощью pandas
    """
    try:
        hook = PostgresHook(postgres_conn_id='postgres_default')
        df = hook.get_pandas_df("SELECT * FROM test_users")

        print("\n🎯 PANDAS АНАЛИЗ:")
        print("=" * 40)

        # Самый молодой и самый старший
        youngest = df.loc[df['age'].idxmin()]
        oldest = df.loc[df['age'].idxmax()]

        print(f"   Самый молодой: {youngest['name']} ({youngest['age']} лет)")
        print(f"   Самый старший: {oldest['name']} ({oldest['age']} лет)")

        # Самые популярные города
        city_counts = df['city'].value_counts()
        print(f"\n   Самый популярный город: {city_counts.index[0]} ({city_counts.iloc[0]} чел.)")

    except Exception as e:
        print(f"⚠️ Ошибка при анализе: {e}")


# =============== СОЗДАНИЕ DAG С POSTGRES ===============
with DAG(
    'postgres_demo',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,      # Запуск только вручную
    catchup=False,              # Не запускать пропущенные задачи
    tags=['postgres', 'demo', 'вебинар'],
    default_args={
        'owner': 'airflow',
    }
) as dag:

    # ЗАДАЧА 0: Настройка подключения (выполняется первой)
    setup_connection = PythonOperator(
        task_id='setup_connection',
        python_callable=setup_postgres_connection,
        dag=dag
    )

    # ЗАДАЧА 1: Создание таблицы (PostgresOperator)
    create_table = PostgresOperator(
        task_id='create_table',
        postgres_conn_id='postgres_default',
        sql="""
        CREATE TABLE IF NOT EXISTS test_users (
            id INTEGER PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            city VARCHAR(100),
            age INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        # Если Connection не настроен, эта задача упадет
        # Но следующий код с PythonOperator будет работать
        dag=dag
    )

    # ЗАДАЧА 2: Создание тестовых данных (PythonOperator)
    create_data = PythonOperator(
        task_id='create_data_task',
        python_callable=create_test_data,
        dag=dag
    )

    # ЗАДАЧА 3: Вставка данных в базу (PythonOperator + PostgresHook)
    insert_data = PythonOperator(
        task_id='insert_data_task',
        python_callable=insert_to_postgres,
        dag=dag
    )

    # ЗАДАЧА 4: Чтение данных из базы
    read_data = PythonOperator(
        task_id='read_data_task',
        python_callable=read_from_postgres,
        dag=dag
    )

    # ЗАДАЧА 5: Анализ данных с pandas
    analyze_data = PythonOperator(
        task_id='analyze_data_task',
        python_callable=analyze_with_pandas,
        dag=dag
    )

    # ЗАДАЧА 6: Очистка таблицы (альтернатива)
    cleanup = PostgresOperator(
        task_id='cleanup_table',
        postgres_conn_id='postgres_default',
        sql="DELETE FROM test_users",  # Очищаем таблицу
        dag=dag
    )

    # =============== ПОРЯДОК ВЫПОЛНЕНИЯ ===============
    setup_connection >> create_table >> create_data >> insert_data
    insert_data >> read_data >> analyze_data >> cleanup