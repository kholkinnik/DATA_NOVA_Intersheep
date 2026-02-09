
"""
# Автоматический генератор DAG для ETL витрин данных (xDC_*)
## Назначение
Скрипт **динамически генерирует Airflow DAG** для каждой папки из `SCRIPTS_FOLDER`.
Каждый DAG выполняет полный **ETL цикл** для одной витрины данных: {NAME}
Нейминг внутри папок внутри папки `SCRIPTS_FOLDER`: xDC_{NAME}
структура внутри папки xDC_{NAME}:
|-- {NAME}.sql # извлечение из MSSQL
|-- CREATE_TABLE_POSTGRES_{NAME}.sql # DDL для postgres ( если не существует)
|-- CLEAN_TABLE_POSTGRES_{NAME}.sql # очистка для иденпотентности (если выгрузка за {ds} то удаление значений для {ds})
|-- [генерируется автоматически] {NAME}.csv 
"""
import os
from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator

from airflow.providers.microsoft.mssql.hooks.mssql import MsSqlHook
from airflow.hooks.postgres_hook import PostgresHook
from airflow.operators.dummy import DummyOperator

import csv

import logging
# Путь к папке с .sql файлами 
# SCRIPTS_FOLDER = 'data/scripts_sql'
SCRIPTS_FOLDER = [
    'data/scripts_sql/xDC_SERVICE_CATEGORIES',
    'data/scripts_sql/xDC_TARIFS']

for folder_name in SCRIPTS_FOLDER:
    folder_base = os.path.basename(folder_name)
    print(folder_base)
    dag_id = f"auto_dag_{folder_base}"
    NAME = folder_base.replace('xDC_', '')
    

    # Получаю список SQL файлов
    sql_files = [f for f in os.listdir(folder_name) if f.endswith('.sql')]

    def simp_pyth(folder_name=folder_name, sql_files = sql_files, dag_id = dag_id):
        print(f"Привет из папки: {folder_name} в ней {len(sql_files)} шт. файлов)")
        print(f"SQL: файлы: {sql_files}")
        logging.info(f"DAG {dag_id} успешно запущен")

    # Функция для обращения к MSSQL и запись данных в CSV
    

    def extract_sql(folder_path=folder_name, name=NAME,**context):
        date = context['ds']  # Дата запуска в формате YYYY-MM-DD
        try:
            logging.info(f'Дата запуска {date}')
            hook = MsSqlHook(mssql_conn_id='mssql_default')
            conn = hook.get_conn()
            cursor = conn.cursor() 
            
        # читаю скрипт  к MSSQL с помощью менеджера контекста
            with open(f'{folder_path}/{name}.sql', 'r') as file:  
                sql_script = file.read()
                cursor.execute(sql_script)
    
            result = cursor.fetchall()

            if result:
                logging.info(f'Получено {len(result)} записей')
                logging.info(f'Дата запуска {date}')

        #Запись данных в CSV файл
                with open(f'{folder_path}/{name}.csv', mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerows(result)
            
                logging.info(f"Данные витрины {name} записаны в csv файл ✅")
                logging.info(f'Пример данных первой строки: {result[0]} ')
        
            else:
                logging.info("Данные не найдены для указанной даты")

            cursor.close()
            conn.close()
    
        except Exception as e:
            logging.error(f"Ошибка при выполнении запроса: {e}")
            raise


# Функция для создания таблицы в Postgres
    def create_table_postgres(folder_path = folder_name,name=NAME):
    #Инициализирую хук
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    # читаю и запускаю SQL скрипт для создания таблицы
    
        with open(f'{folder_path}/CREATE_TABLE_POSTGRES_{name}.sql', 'r') as file:  
            sql_create_table = file.read()

        try:
        # Выполняем очистку данных
            postgres_hook.run(sql_create_table)
            logging.info("Таблица успешно создана или уже существует✅")
        
        except Exception as e:
            logging.error(f"Ошибка при создании таблицы {e}")
            raise         
    
# Функция для очистки данных из Postgres перед вставкой
    def clean_old_data(folder_path = folder_name, name=NAME,**context):
    #Инициализирую хук
        postgres_hook = PostgresHook(postgres_conn_id='postgres_default')
    
    # Получаем дату запуска из контекста Airflow
        date = context['ds']  # Дата запуска в формате YYYY-MM-DD

    # читаю и запускаю SQL скрипт для очистки таблицы
        with open(f'{folder_path}/CLEAN_TABLE_POSTGRES_{name}.sql', 'r') as file:  
            sql_clean_table = file.read()   

        try:
        # Выполняем очистку данных
            postgres_hook.run(sql_clean_table)
            logging.info(f"Удалены данные для даты {date}")
        
        except Exception as e:
            logging.error(f"Ошибка при удалении данных: {e}")
            raise

# Функция для вставки значений из CSV в Postgres
    def load_csv_to_postgres(folder_path = folder_name, name=NAME):
        try:
            
        #Инициализирую хук
            postgres_hook = PostgresHook(postgres_conn_id='postgres_default')

        #Читааю данные из CSV
            with open(f'{folder_path}/{name}.csv', 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                # Преобразую пустые строки в None для корректной вставки NULL в Postgres
                data = [tuple(None if field == '' else field for field in row) for row in reader]

        # Выполняем массовую вставку
            postgres_hook.insert_rows(
                table=f'xdc.{name}',
                rows=data      
            )
        
            logging.info(f"Успешно загружено {len(data)} записей")

        except Exception as e:
            logging.error(f"Ошибка при загрузке данных: {e}")  
            raise Exception(f"Не удалось выполнить операцию: {e}") from e
    
    with DAG(
        dag_id = dag_id,
        description = f"Авто-DAG для для папки {folder_base}",
        max_active_runs=1,
        schedule_interval = None,  # запускать буду вручную
        start_date = datetime(2026, 1, 31),
        catchup= False,
        tags= ['auto-generated'],
    ) as dag:
        
        start = DummyOperator(task_id = 'start')

        simp_task = PythonOperator(
            task_id = 'simple_print',
            python_callable = simp_pyth
        )
    # Задача для запуска скрипта 
        extract_sql = PythonOperator(
            task_id = 'extract_sql',
            python_callable = extract_sql
            )

    # Задача для создания таблицы если она не существует в Postgres
        create_table_postgres = PythonOperator(
            task_id = 'create_table_postgres',
            python_callable = create_table_postgres
        )

    # Задача для очитски данных (идемпотентность)
        clean_old_data = PythonOperator(
            task_id = 'clean_data',
            python_callable = clean_old_data
        )

    # Задача для загрузки данных в postgres
        load_to_postgres = PythonOperator(
            task_id = 'load_to_postgres',
            python_callable = load_csv_to_postgres,
        )
    
        end = DummyOperator(task_id = 'end')

        start >> extract_sql >> create_table_postgres >> clean_old_data >> load_to_postgres>> end
