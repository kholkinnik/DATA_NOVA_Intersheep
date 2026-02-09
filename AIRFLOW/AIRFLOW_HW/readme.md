# Автоматический генератор DAG для ETL витрин данных (xDC_*)

## Назначение

Скрипт **динамически генерирует Airflow DAG** для каждой папки из `SCRIPTS_FOLDER`.  
Каждый DAG выполняет полный **ETL цикл** для одной витрины данных **xDC_{NAME}**.

**Полный путь данных**: `MSSQL → CSV → PostgreSQL (схема xdc)`

## Пример структуры
dags/
├── auto_etl_generator.py # ← Этот скрипт (генератор DAG)
└── data/
└── scripts_sql/
├── xDC_SERVICE_CATEGORIES/ # ← DAG: auto_dag_xDC_SERVICE_CATEGORIES
│ ├── SERVICE_CATEGORIES.sql # 1️⃣ Извлечение из MSSQL
│ ├── CREATE_TABLE_POSTGRES_SERVICE_CATEGORIES.sql # 2️⃣ DDL таблицы PG
│ ├── CLEAN_TABLE_POSTGRES_SERVICE_CATEGORIES.sql # 3️⃣ Очистка данных по {{ ds }}
│ └── SERVICE_CATEGORIES.csv # 4️⃣ [ГЕНЕРИРУЕТСЯ] промежуточный файл
│
└── xDC_TARIFS/ # ← DAG: auto_dag_xDC_TARIFS
├── TARIFS.sql
├── CREATE_TABLE_POSTGRES_TARIFS.sql
├── CLEAN_TABLE_POSTGRES_TARIFS.sql
└── TARIFS.csv # [ГЕНЕРИРУЕТСЯ]


## Нейминг внутри папок

**Папка**: `xDC_{NAME}`  
**Таблица PG**: `xdc.{NAME}`  
**Файлы**:
- `{NAME}.sql` — извлечение из MSSQL
- `CREATE_TABLE_POSTGRES_{NAME}.sql` — DDL для postgres (если не существует)
- `CLEAN_TABLE_POSTGRES_{NAME}.sql` — очистка для идемпотентности (DELETE WHERE date_column = '{{ ds }}')
- `{NAME}.csv` — [генерируется автоматически]

## Быстрое добаление новой витрины
##### 1. Создать папку
mkdir -p data/scripts_sql/xDC_NEW_VITRINA

###### 2. Добавить 3 обязательных SQL файла:
    - NEW_VITRINA.sql
    - CREATE_TABLE_POSTGRES_NEW_VITRINA.sql  
    - CLEAN_TABLE_POSTGRES_NEW_VITRINA.sql

###### 3. ✅ DAG auto_dag_xDC_NEW_VITRINA готов!
###### 4. Проверить: airflow dags list | grep NEW_VITRINA ( или через UI AIRFLOW)

## Особенности реализации

| 🔄 Идемпотентность   - CREATE TABLE IF NOT EXISTS + ежедневная очистка по {{ ds }} 
| 💾 CSV-посредник     - Надежная передача данных между разными БД                   
| 🏷️ Теги              - auto-generated для фильтрации в UI                          
| 📅 Ручной запуск     - schedule_interval=None + max_active_runs=1                  
| 🛡️ Обработка ошибок   - Логирование + raise для retry в Airflow                     



