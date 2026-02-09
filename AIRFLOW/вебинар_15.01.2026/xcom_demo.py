"""
XCOM ДЕМО - ПЕРЕДАЧА ДАННЫХ МЕЖДУ ЗАДАЧАМИ
XCom = Cross-communication (перекрестная коммуникация)
Хранит данные в БД Airflow, работает по принципу ключ-значение
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime


# =============== ФУНКЦИЯ 1: СОХРАНЕНИЕ ДАННЫХ В XCOM ===============
def save_data_to_xcom(**context):
    """
    Функция показывает, как сохранять данные в XCom.
    Контекст (context) - это словарь с информацией о задаче и DAG.
    """

    # Получаем task instance - объект задачи, через который работаем с XCom
    task_instance = context['ti']

    # СПОСОБ 1: Явное сохранение с указанием ключа
    task_instance.xcom_push(key='user_info', value='Иван Иванов')

    # СПОСОБ 2: Сохранение числа
    task_instance.xcom_push(key='user_age', value=30)

    # СПОСОБ 3: Автоматическое сохранение возвращаемого значения
    return {'status': 'success', 'message': 'Данные сохранены'}


# =============== ФУНКЦИЯ 2: ЧТЕНИЕ ДАННЫХ ИЗ XCOM ===============
def read_data_from_xcom(**context):
    """
    Функция показывает, как читать данные из XCom.
    """

    task_instance = context['ti']

    # Читаем данные по ключам
    name = task_instance.xcom_pull(task_ids='save_task', key='user_info')
    age = task_instance.xcom_pull(task_ids='save_task', key='user_age')

    # Читаем возвращаемое значение (ключ 'return_value' по умолчанию)
    status = task_instance.xcom_pull(task_ids='save_task')

    print(f"Имя пользователя: {name}")
    print(f"Возраст: {age}")
    print(f"Статус: {status}")


# =============== СОЗДАНИЕ DAG И ЗАДАЧ ===============
# DAG - контейнер для задач, определяет порядок их выполнения
with DAG(
        'xcom_demo',  # Уникальное имя DAG
        start_date=datetime(2023, 1, 1),  # Дата начала работы
        schedule_interval=None,  # Запуск только вручную
        catchup=False  # Не запускать пропущенные задачи
) as dag:
    # Задача 1: Сохраняет данные
    save_task = PythonOperator(
        task_id='save_task',  # Уникальный ID задачи
        python_callable=save_data_to_xcom
    )

    # Задача 2: Читает данные
    read_task = PythonOperator(
        task_id='read_task',
        python_callable=read_data_from_xcom
    )

    # Определяем порядок выполнения (задача 1, затем задача 2)
    save_task >> read_task