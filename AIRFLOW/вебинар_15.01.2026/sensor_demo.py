from airflow import DAG
from airflow.sensors.python import PythonSensor
from airflow.operators.python import PythonOperator
from datetime import datetime
import random

# Функция проверки условия - должна возвращать True (условие выполнено) или False (продолжаем ждать)
def check_random_condition():
    # Генерируем случайное число от 1 до 10
    random_number = random.randint(1, 10)

    # Условие выполнится с вероятностью 30% (если выпадет 8, 9 или 10)
    if random_number >= 8:
        print(f"🎉 УСПЕХ! Выпало число: {random_number}. Условие выполнено!")
        return True  # Сенсор завершится успешно
    else:
        print(f"⏳ ЖДЕМ... Выпало число: {random_number}. Условие еще не выполнено.")
        return False  # Продолжаем ждать

# Функция, которая выполнится только после успешного завершения сенсора
def process_after_wait():
    print("=" * 50)
    print("✅ СЕНСОР УСПЕШНО ЗАВЕРШИЛСЯ!")
    print("НАЧИНАЮ ОСНОВНУЮ ОБРАБОТКУ...")
    print("=" * 50)

    return "Обработка успешно завершена"

# Создаем DAG
with DAG(
    'sensor_demo',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,  # Запуск только вручную
    catchup=False
) as dag:

    # Создаем сенсор с настройками
    sensor = PythonSensor(
        task_id='wait_for_condition',
        python_callable=check_random_condition,

        # mode='poke' - воркер занят проверками (использует слот)
        # mode='reschedule' - освобождает воркер между проверками
        mode='poke',

        # Проверять условие каждые 5 секунд
        poke_interval=5,

        # Максимальное время ожидания (30 секунд)
        timeout=30,

        # soft_fail=False - при таймауте задача упадет с ошибкой
        # soft_fail=True - при таймауте задача будет пропущена (skipped)
        soft_fail=False,
    )

    # Задача, которая выполнится после успешного завершения сенсора
    process_task = PythonOperator(
        task_id='process_data',
        python_callable=process_after_wait
    )

    # Определяем порядок выполнения: сенсор -> обработка
    sensor >> process_task