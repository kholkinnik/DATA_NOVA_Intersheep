# Автоматический генератор DAG для ETL витрин данных (xDC_*)

## Назначение

Скрипт **динамически генерирует Airflow DAG** для каждой папки из `SCRIPTS_FOLDER`.  
Каждый DAG выполняет полный **ETL цикл** для одной витрины данных **xDC_{NAME}**.

**Полный путь данных**: `MSSQL → CSV → PostgreSQL (схема xdc)`

## Нейминг внутри папок `SCRIPTS_FOLDER`:

**Папка**: `xDC_{NAME}` {NAME}- наименование витрины

**Файлы**:
- `{NAME}.sql` — извлечение из MSSQL
- `CREATE_TABLE_POSTGRES_{NAME}.sql` — DDL для postgres (если не существует)
- `CLEAN_TABLE_POSTGRES_{NAME}.sql` — очистка для идемпотентности (DELETE WHERE date_column = '{{ ds }}')
- `{NAME}.csv` — [генерируется автоматически]

## Быстрое добаление новой витрины
##### 1. Создать папку
mkdir -p data/scripts_sql/xDC_{NEW_NAME}

###### 2. Добавить 3 обязательных SQL файла:
    - {NEW_NAME}.sql   запрос на выгрузку из MSSQL
    - CREATE_TABLE_POSTGRES_{NEW_NAME}.sql  создание таблицы в Postgres(если не существует)
    - CLEAN_TABLE_POSTGRES_{NEW_NAME}.sql   проверка на идемпотентность ( если выгрузка по дате используй в скрипте {{ds}})

###### 3. ✅ DAG auto_dag_xDC_{NEW_NAME} готов!
###### 4. Проверить: airflow dags list | grep NEW_VITRINA ( или через UI AIRFLOW)

## Особенности реализации

| 🔄 Идемпотентность   - CREATE TABLE IF NOT EXISTS + ежедневная очистка по {{ ds }} 
| 💾 CSV-посредник     - Надежная передача данных между разными БД                   
| 🏷️ Теги              - auto-generated для фильтрации в UI                          
| 📅 Ручной запуск     - schedule_interval=None + max_active_runs=1                  
| 🛡️ Обработка ошибок   - Логирование + raise для retry в Airflow 