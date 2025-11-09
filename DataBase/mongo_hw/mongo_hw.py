# импортирую необходимые библиотеки
from pymongo import MongoClient
from pprint import pprint   # Библиотека для удобного чтения файлов со сложной структурой
import json
import os # для работы с текуще операционной системой
from datetime import datetime, timedelta # Работа с датой и временем

# устанавливаю конекшн с БД
client = MongoClient("mongodb://localhost:27017/")
db = client["my_database"]
collection = db["user_events"]

# Вычисляю разницу текущей даты и 30 дней, для фильтрации по дате регистрации
dif_date_reg = datetime.now() - timedelta(days = 30)

# Вычисляю разницу текущей даты и и 14 дней, для фильтрации бездействия пользовтаеля в течении 14 дней
dif_date_event = datetime.now() - timedelta(days = 14) 

# формирую запрос на основании задания
query = {
    "$and": [
        {'user_info.registration_date': {'$lt': dif_date_reg}},
        {'event_time': {'$lt': dif_date_event}}
    ]   
}

#выполняю запрос на в mongo
archived_users = collection.find(query, {"user_id": 1, "_id": 0})

# Создаём список user_id для использовании в отчете
archived_user_ids = [doc['user_id'] for doc in archived_users]

#Формат отчета 
report = {
    "date" : datetime.now().date().strftime("%Y-%m-%d"),
    "archived_users_count": len(archived_user_ids),
    "archived_user_ids" : archived_user_ids
}

# Путь для сохранения отчёта
output_dir = os.getcwd()
file_path = os.path.join(output_dir, f'''report_from_{datetime.now().date().strftime("%Y-%m-%d")}.json''')


# Запись отчёта в файл .json
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"Отчёт сохранён в {file_path}")
