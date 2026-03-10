from pymongo import MongoClient
from pprint import pprint
import json
import os
import glob


# Подключение к MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["pikcha_market"]

# Инициализация коллекций
collections = {
    "products": db["products"],
    "customers": db["customers"],
    "purchases": db["purchases"],  
    "stores": db["stores"]
}

print("🎉 Успешное подключение к MongoDB")

# Загрузка данных для КАЖДОЙ коллекции
for coll_name, collection in collections.items():
    print(f"\n{'='*50}")
    print(f"🔄 Обрабатываем коллекцию: {coll_name}")
    
    # Очистка
    collection.drop()
    print(f"🗑️Коллекция  {coll_name} очищена")
    
    # Поиск JSON файлов
    json_files = glob.glob(f"data/{coll_name}/*.json")
    print(f"📁 Найдено файлов: в папке {coll_name} :{len(json_files)}")
    
    if not json_files:
        print(f"⚠️  Файлы не найдены в data/{coll_name}/")
        continue
    
    total_imported = 0
    for file_path in json_files:
        filename = os.path.basename(file_path)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            if isinstance(data, list):
                result = collection.insert_many(data)
                count = len(result.inserted_ids)
            else:
                result = collection.insert_one(data)
                count = 1
                
            total_imported += count
            #print(f"✅ {filename}: {count} док.")
            
        except Exception as e:
            print(f"❌ {filename}: {e}")
    
    print(f"🎉 {coll_name}: {total_imported} документов")
    
    # Проверка на количество загруженых файлов
    count = collection.count_documents({})
    print(f"📦 Подтверждено наличие  Mongo: {count} документов")
    # if count > 0:
    #     print("📋 Пример:")
    #     pprint(list(collection.find().limit(1))[0], indent=2)


print("\n✅ Загрузка завершена в MongoDB завершена!")
client.close()
print("\n✅ Клиент закрыт! ")