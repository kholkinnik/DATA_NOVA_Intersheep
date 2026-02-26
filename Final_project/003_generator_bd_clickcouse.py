import clickhouse_connect

# библиотеки для переменных окружения
import os
import glob
from dotenv import load_dotenv
# загружаю переменные окружения
load_dotenv()
USERNAME = os.getenv("CLICKHOUSE_USER")
PASSWORD = os.getenv("CLICKHOUSE_PASSWORD")
secret_key = os.getenv("SECRET_KEY")

# == подключение к ClickHouse через ClockHouse connect ==
client = clickhouse_connect.get_client(host='localhost', 
                                       port=8123, 
                                       username = USERNAME, 
                                       password=PASSWORD)
# == Проверка подключения ==

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
    ddl_folder = 'ddl'    # папка с sql скриптами
    sql_files = glob.glob(os.path.join(ddl_folder, '*.sql'))
       
      
    for sql_file in sorted(sql_files):  # Сортируем для предсказуемого порядка
        try:
            print(f"\n📄 Выполняю: {os.path.basename(sql_file)}")
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Выполняем DDL (CREATE, DROP, ALTER)
            client.command(sql_content)
            print(f"✅ {os.path.basename(sql_file)} Выполнено успешно")
            
        except Exception as e:
            print(f"❌ Ошибка в {os.path.basename(sql_file)}: {e}")
            continue  # Продолжаем с остальными файлами
    
   


# == Основной запуск ==
if __name__ == "__main__":
    if check_connection():
        run_ddl_scripts()
    client.close()
print("\n🎉 Все DDL скрипты обработаны! База Данных готова")
print("✅ Connection Clickhouse закрыто")
