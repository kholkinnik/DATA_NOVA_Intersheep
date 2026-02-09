"""
DAG: simple_etl_postgres
Описание: Простейший ETL процесс с использованием PythonOperator и PostgresOperator
Время запуска: Вручную
Автор: Data Engineer
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from datetime import datetime
import psycopg2


# ФУНКЦИЯ 1: Создание таблицы с помощью PythonOperator
def create_table_with_python():
    """
    Эта функция создает таблицу в PostgreSQL используя чистый Python (psycopg2)
    Используется когда нужна более сложная логика создания таблиц
    """
    print("🔧 Начинаю создание таблицы...")

    # Шаг 1: Подключаемся к PostgreSQL
    # Здесь мы используем параметры подключения напрямую
    conn = psycopg2.connect(
        host='postgres',  # Имя хоста из docker-compose
        database='airflow',  # Название базы данных
        user='airflow',  # Имя пользователя
        password='airflow',  # Пароль
        port=5432  # Порт PostgreSQL
    )

    # Шаг 2: Создаем курсор для выполнения SQL команд
    cursor = conn.cursor()

    # Шаг 3: Выполняем SQL команду для создания таблицы
    cursor.execute("""
                   -- Создаем таблицу employees если ее еще нет
                   CREATE TABLE IF NOT EXISTS employees
                   (
                       id
                       SERIAL
                       PRIMARY
                       KEY, -- Уникальный ID (автоинкремент)
                       name
                       VARCHAR
                   (
                       100
                   ) NOT NULL, -- Имя сотрудника
                       department VARCHAR
                   (
                       100
                   ), -- Отдел
                       salary DECIMAL
                   (
                       10,
                       2
                   ), -- Зарплата
                       hire_date DATE, -- Дата приема на работу
                       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Когда создана запись
                       )
                   """)

    # Шаг 4: Сохраняем изменения в базе данных
    conn.commit()

    # Шаг 5: Закрываем соединение
    cursor.close()
    conn.close()

    print("✅ Таблица 'employees' создана успешно!")


# ФУНКЦИЯ 2: Вставка данных с помощью PythonOperator
def insert_data_with_python(**context):
    """
    Эта функция вставляет тестовые данные в таблицу
    Используем **context для работы с контекстом Airflow (например, дата запуска)
    """
    print("📝 Начинаю вставку данных...")

    # Тестовые данные для вставки
    employees = [
        ('Иван Петров', 'ИТ', 75000, '2023-01-15'),
        ('Мария Сидорова', 'Маркетинг', 65000, '2023-02-20'),
        ('Алексей Иванов', 'Продажи', 80000, '2023-03-10'),
        ('Ольга Смирнова', 'Финансы', 90000, '2023-04-05'),
    ]

    # Подключаемся к базе
    conn = psycopg2.connect(
        host='postgres',
        database='airflow',
        user='airflow',
        password='airflow',
        port=5432
    )

    cursor = conn.cursor()

    # Вставляем данные построчно
    for emp in employees:
        cursor.execute("""
                       INSERT INTO employees (name, department, salary, hire_date)
                       VALUES (%s, %s, %s, %s)
                       -- ON CONFLICT ничего не делаем, так как id автоинкрементный
                       """, emp)
        print(f"   ✅ Добавлен: {emp[0]} ({emp[1]})")

    # Сохраняем изменения
    conn.commit()

    # Закрываем соединение
    cursor.close()
    conn.close()

    print("✅ Данные успешно добавлены!")
    return f"Добавлено {len(employees)} сотрудников"


# ФУНКЦИЯ 3: Чтение и анализ данных
def analyze_data_with_python():
    """
    Эта функция читает данные из таблицы и проводит простой анализ
    """
    print("📊 Начинаю анализ данных...")

    conn = psycopg2.connect(
        host='postgres',
        database='airflow',
        user='airflow',
        password='airflow',
        port=5432
    )

    cursor = conn.cursor()

    # ЗАПРОС 1: Получаем всех сотрудников
    cursor.execute("SELECT * FROM employees ORDER BY id")
    all_employees = cursor.fetchall()

    print("\n👥 Все сотрудники:")
    print("-" * 60)
    for emp in all_employees:
        print(f"ID: {emp[0]:2} | {emp[1]:20} | {emp[2]:12} | {emp[3]:8} руб.")

    # ЗАПРОС 2: Считаем статистику по отделам
    cursor.execute("""
                   SELECT department,
                          COUNT(*) as count,
            AVG(salary) as avg_salary,
            SUM(salary) as total_salary
                   FROM employees
                   GROUP BY department
                   ORDER BY avg_salary DESC
                   """)

    dept_stats = cursor.fetchall()

    print("\n📈 Статистика по отделам:")
    print("-" * 60)
    for dept in dept_stats:
        print(f"{dept[0]:12} | {dept[1]:2} чел. | {dept[2]:8.0f} руб. | Итого: {dept[3]:10.0f} руб.")

    # ЗАПРОС 3: Общая статистика
    cursor.execute("SELECT COUNT(*), AVG(salary), SUM(salary) FROM employees")
    total_stats = cursor.fetchone()

    print("\n🎯 Общая статистика:")
    print(f"   Всего сотрудников: {total_stats[0]}")
    print(f"   Средняя зарплата: {total_stats[1]:.0f} руб.")
    print(f"   Общий фонд оплаты: {total_stats[2]:.0f} руб.")

    cursor.close()
    conn.close()


# СОЗДАЕМ DAG
with DAG(
        'simple_etl_postgres',  # Уникальное имя DAG
        start_date=datetime(2023, 1, 1),  # Дата начала работы
        schedule_interval=None,  # Запуск только вручную
        catchup=False,  # Не запускать прошлые задачи
        tags=['demo', 'postgres', 'etl']  # Теги для поиска
) as dag:
    # ЗАДАЧА 1: Создание таблицы с помощью PythonOperator
    # PythonOperator позволяет выполнять любые Python функции
    create_table_task = PythonOperator(
        task_id='create_table_task',  # Уникальный ID задачи
        python_callable=create_table_with_python  # Функция для выполнения
    )

    # ЗАДАЧА 2: Вставка данных с помощью PythonOperator
    insert_data_task = PythonOperator(
        task_id='insert_data_task',
        python_callable=insert_data_with_python,
        provide_context=True  # Передаем контекст Airflow в функцию
    )

    # ЗАДАЧА 3: Обновление данных с помощью PostgresOperator
    # PostgresOperator специализирован для выполнения SQL команд
    update_salaries_task = PostgresOperator(
        task_id='update_salaries_task',
        postgres_conn_id='postgres_default',  # Connection из Airflow UI
        sql="""
            -- Повышаем зарплату всем сотрудникам отдела ИТ на 10%
            UPDATE employees
            SET salary = salary * 1.10
            WHERE department = 'ИТ';

            -- Показываем обновленные данные
            SELECT name, salary
            FROM employees
            WHERE department = 'ИТ';
            """
    )

    # ЗАДАЧА 4: Анализ данных с помощью PythonOperator
    analyze_data_task = PythonOperator(
        task_id='analyze_data_task',
        python_callable=analyze_data_with_python
    )

    # ЗАДАЧА 5: Очистка таблицы с помощью PostgresOperator
    cleanup_task = PostgresOperator(
        task_id='cleanup_task',
        postgres_conn_id='postgres_default',
        sql="""
            -- Удаляем все данные из таблицы
            TRUNCATE TABLE employees;

            -- Показываем что таблица пуста
            SELECT COUNT(*) as remaining
            FROM employees;
            """
    )

    # ОПРЕДЕЛЯЕМ ПОРЯДОК ВЫПОЛНЕНИЯ ЗАДАЧ
    # Создаем таблицу → Вставляем данные → Обновляем зарплаты → Анализируем → Очищаем
    create_table_task >> insert_data_task >> update_salaries_task >> analyze_data_task >> cleanup_task