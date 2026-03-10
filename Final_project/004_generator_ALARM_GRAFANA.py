import clickhouse_connect
import os
from dotenv import load_dotenv
from datetime import datetime 

# библиотеки для переменных окружения
load_dotenv()
USERNAME = os.getenv("CLICKHOUSE_USER")
PASSWORD = os.getenv("CLICKHOUSE_PASSWORD")
secret_key = os.getenv("SECRET_KEY")
 
# == подключение к ClickHouse ==
client = clickhouse_connect.get_client(host='localhost', 
                                       port=8123, 
                                       username=USERNAME, 
                                       password=PASSWORD)

def check_connection():
    try:
        if client.ping():
            print("✅ Подключение успешно")
            version_result = client.query('SELECT version()')
            print(f"✅ Версия ClickHouse: {version_result.result_rows[0][0]}")
            return True
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def run_ddl_scripts():
    """Добавляет 5 дублирующих записей покупок"""
    today = datetime.now()  # ← datetime.now() вместо date.today()
    
    # 50 ИДЕНТИЧНЫХ записей (дубликаты)
    duplicate_data = []
    for _ in range(5):
        row = [
            'ord-00201',           # purchase_id
            'cus-1038',            # customer_id
            'store-045',           # store_id  
            'prd-1032',            # product_id
            1250.50,               # total_amount
            'card',                # payment_method
            1,                     # is_delivery
            today                  # дата СЕГОДНЯ
        ]
        duplicate_data.append(row)
    
    try:
        client.insert(
            table='raw_purchases',  
            data=duplicate_data,
            column_names=[
                'purchase_id', 'customer_id', 'store_id', 'product_id',
                'total_amount', 'payment_method', 'is_delivery', 'purchase_datetime'
            ]
        )
        print(f"✅ Добавлено {len(duplicate_data)} дублирующих записей!")
        
       
        result = client.query("SELECT COUNT(*) FROM raw_purchases WHERE purchase_id = 'ord-00201'")
        count = result.result_rows[0][0]
        print(f"📊 Найдено дубликатов: {count}")
        
    except Exception as e:
        print(f"❌ Ошибка вставки: {e}")

# == Основной запуск ==
if __name__ == "__main__":
    if check_connection():
        run_ddl_scripts()
    client.close()
    print("\n🎉 Добавлены дублирующие данные")
    print("✅ Connection ClickHouse закрыто")
