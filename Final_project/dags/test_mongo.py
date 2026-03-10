from datetime import datetime
from airflow import DAG
from airflow.operators.empty import EmptyOperator 
from airflow.operators.python import PythonOperator
from pymongo import MongoClient 
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

def test_pymongo():
    # Подключение к MongoDB
    client = MongoClient("mongodb://mongo:27017/", serverSelectionTimeoutMS=5000) 
    try:
        # Ping для проверки соединения + получение версии
        server_info = client.admin.command('ping')
        version_info = client.server_info()
        
        version = version_info['version']
        version_array = version_info['versionArray']
        
        print(f"✅ Подключение OK")
        print(f"📊 Версия MongoDB: {version}")
        print(f"🔢 Версия (массив): {version_array}")
        print(f"🏓 Ping выполнен успешно")
        
        return f"MongoDB {version} доступен"
        
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        print(f"❌ Ошибка подключения: {str(e)}")
        raise Exception(f"MongoDB недоступен: {str(e)}")
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {str(e)}")
        raise   
    
with DAG(
        dag_id="check_mongodb_connection",
        start_date=datetime(2026, 3, 1),
        schedule_interval=None,
        catchup=False,
) as dag:
    
    start = EmptyOperator(
        task_id = 'start'
    )

    run_connection_to_mongo = PythonOperator( 
        task_id="run_connection_to_mongo",     
        python_callable=test_pymongo,
    )

start >> run_connection_to_mongo


