"""
BRANCH OPERATOR ДЕМО - ВЕТВЛЕНИЕ ЛОГИКИ ВЫПОЛНЕНИЯ
BranchOperator решает, какая задача будет выполняться следующей
Не выбранные задачи пропускаются (status: skipped)
"""

from airflow import DAG
from airflow.operators.python import BranchPythonOperator
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime


# =============== ФУНКЦИЯ ПРИНЯТИЯ РЕШЕНИЯ ===============
def decide_branch(**context):
    """
    Функция принимает решение о пути выполнения.
    ВОЗВРАЩАЕТ: task_id следующей задачи
    """

    # Читаем параметры из контекста или генерируем данные
    import random
    data_quality = random.choice(['good', 'bad', 'unknown'])

    print(f"Качество данных: {data_quality}")

    # ЛОГИКА ВЕТВЛЕНИЯ:
    if data_quality == 'good':
        return 'process_good_data'  # Выполнить эту задачу
    elif data_quality == 'bad':
        return 'clean_bad_data'  # Или эту
    else:
        return 'analyze_unknown_data'  # Или эту

    # Задачи, которые не возвращены, будут пропущены


# =============== ФУНКЦИИ ДЛЯ РАЗНЫХ ВЕТОК ===============
def process_good():
    print("Обрабатываю качественные данные")


def clean_bad():
    print("Чищу плохие данные")


def analyze_unknown():
    print("Анализирую неизвестные данные")


# =============== СОЗДАНИЕ DAG С ВЕТВЛЕНИЕМ ===============
with DAG(
        'branch_demo',
        start_date=datetime(2023, 1, 1),
        schedule_interval=None,
        catchup=False
) as dag:
    # Начальная задача
    start = DummyOperator(task_id='start')

    # Задача ветвления (принимает решение)
    branch_task = BranchPythonOperator(
        task_id='branch_decision',
        python_callable=decide_branch
    )

    # Задачи для разных веток
    good_task = PythonOperator(
        task_id='process_good_data',
        python_callable=process_good
    )

    bad_task = PythonOperator(
        task_id='clean_bad_data',
        python_callable=clean_bad
    )

    unknown_task = PythonOperator(
        task_id='analyze_unknown_data',
        python_callable=analyze_unknown
    )

    # Финальная задача
    # Важно: используем trigger_rule для обработки пропущенных задач
    end = DummyOperator(
        task_id='end',
        trigger_rule='none_failed_or_skipped'  # Выполнится, даже если какие-то задачи пропущены
    )

    # =============== ПОРЯДОК ВЫПОЛНЕНИЯ ===============
    # 1. Старт
    # 2. Branch решает, куда идти
    # 3. Выполняется ОДНА из веток
    # 4. Финальная задача
    start >> branch_task >> [good_task, bad_task, unknown_task]
    [good_task, bad_task, unknown_task] >> end