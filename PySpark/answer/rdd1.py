from pyspark import SparkContext
from datetime import datetime
sc = SparkContext("local", "RDD_project_1")

# timestamp|sensor_id|temperature|pressure|status|error_code
raw_data = """2025-01-10 08:00:05|S101|25.3|10.1|OK|NULL
2025-01-10 08:05:10|S102|26.1|NULL|WARNING|E01
2025-01-10 08:10:00|S101|25.5|10.2|OK|NULL
2025-01-10 08:15:30|S103|NULL|9.9|ERROR|E05
2025-01-10 08:20:15|S102|25.8|10.0|OK|NULL
2025-01-10 08:25:00|S101|25.4|10.1|OK|NULL
2025-01-10 08:30:20|S104|27.0|10.3|OK|NULL
2025-01-10 08:35:05|S101|25.6|NULL|OK|NULL
2025-01-10 08:40:00|S103|24.9|9.8|WARNING|NULL
2025-01-10 08:45:10|S102|26.0|10.1|OK|NULL
2025-01-11 09:00:00|S104|27.2|10.4|ERROR|E03
2025-01-11 09:05:30|S101|25.7|10.2|OK|NULL
2025-01-11 09:10:00|S105|24.0|9.5|OK|NULL
2025-01-11 09:15:10|S101|25.8|10.3|OK|NULL
2025-01-11 09:20:20|S102|26.2|NULL|WARNING|E02
2025-01-11 09:25:00|S103|25.0|9.7|OK|NULL
2025-01-12 10:00:15|S104|NULL|10.5|ERROR|E04
2025-01-12 10:05:00|S105|24.1|9.6|OK|NULL
2025-01-12 10:10:05|S101|25.9|10.4|OK|NULL
2025-01-12 10:15:00|S102|26.3|10.2|OK|NULL
2025-01-12 10:20:10|S103|NULL|NULL|ERROR|E05
2025-01-13 11:00:00|S104|27.3|10.6|OK|NULL
2025-01-13 11:05:15|S105|24.2|9.7|WARNING|E01
2025-01-13 11:10:00|S101|26.0|10.5|OK|NULL
2025-01-13 11:15:20|S102|NULL|10.3|OK|NULL
2025-01-13 11:20:00|S103|25.1|9.9|OK|NULL
2025-01-14 08:30:10|S104|27.4|NULL|ERROR|E03
2025-01-14 08:35:00|S105|24.3|9.8|OK|NULL
2025-01-14 08:40:15|S101|26.1|10.6|OK|NULL
2025-01-14 08:45:00|S102|26.4|10.4|OK|NULL
2025-01-14 08:50:10|S103|25.2|10.0|WARNING|NULL
2025-01-15 09:00:00|S104|27.5|10.7|OK|NULL
2025-01-15 09:05:15|S105|NULL|9.9|ERROR|E02
2025-01-15 09:10:00|S101|26.2|10.7|OK|NULL
2025-01-15 09:15:20|S102|26.5|NULL|OK|NULL
2025-01-15 09:20:00|S103|25.3|10.1|OK|NULL
2025-01-16 10:00:10|S104|27.6|10.8|OK|NULL
2025-01-16 10:05:00|S105|24.5|10.0|WARNING|E04
2025-01-16 10:10:15|S101|26.3|10.8|OK|NULL
2025-01-16 10:15:00|S102|26.6|10.5|OK|NULL"""

# Создаем RDD из списка строк
raw_rdd = sc.parallelize([line for line in raw_data.split('\n')])

# Разделяем каждую строку RDD на отдельные поля
parsed_rdd = raw_rdd.map(lambda line: line.split('|'))

print(parsed_rdd.collect())
# Преобразуем числовые поля в соответствующий числовой тип и обрабатываем NULL значения
def parse_and_convert(record):
    timestamp, sensor_id, temperature, pressure, status, error_code = record
     # Преобразование timestamp_str в datetime объект
    timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    # Используем None, если значение 'NULL'
    temperature = float(temperature) if temperature != "NULL" else None
    pressure = float(pressure) if pressure != "NULL" else None
    # Используем None, если значение NULL
    error_code = error_code if error_code != "NULL" else None
    
    # Возвращаем кортеж с преобразованными типами
    return (timestamp, sensor_id, temperature, pressure, status, error_code)

# Применяем функцию преобразования к каждому элементу RDD
transformed_rdd = parsed_rdd.map(parse_and_convert)

# Подсчет общего количества записей по статусам
# Извлекаем статус и создаем пару (status, 1)
# Статус находится по индексу 4 
status_counts_rdd = transformed_rdd.map(lambda status: (status[4], 1))

# Суммируем количество для каждого статуса
total_status_counts = status_counts_rdd.reduceByKey(lambda a, b: a + b)

for status, count in total_status_counts.collect():
    print(f"{status}: {count}")

# Подсчет активных сенсоров с ошибками
error_list = transformed_rdd.filter(lambda status: status[4] == "ERROR")
sensor_error_list = error_list.map(lambda rdd: (rdd[1],1))
sensor_error_list = sensor_error_list.reduceByKey(lambda a,b: a + b).sortByKey()
for sensor,cnt_error in sensor_error_list.collect():
    print(f"{sensor}: {cnt_error}")

# Расчет среднего значения температуры 
avg_temp = transformed_rdd.filter(lambda status: status[2] is not None)
avg_temp = avg_temp.map(lambda rdd: (rdd[2],1))
avg_temp = avg_temp.reduce(lambda a, b: (a[0] + b[0],a[1]+b[1]))
print(round(avg_temp[0]/avg_temp[1],2))

# Общее количество ошибок по коду
error_code_list = transformed_rdd.filter(lambda status: status[5] is not None)
error_code_list = error_code_list.map(lambda rdd: (rdd[5], 1))
error_code_list = error_code_list.reduceByKey(lambda a,b: a + b)
for error_code, cnt_error in error_code_list.sortByKey().collect():
        print(f"{error_code}: {cnt_error}")

# Высокое давление и температура
filter_rdd = transformed_rdd.filter(lambda rdd: rdd[2] is not None and rdd[3] is not None)
filter_rdd = filter_rdd.filter(lambda rdd: rdd[2]> 26 and rdd[3]>10)
for timestamp, sensor, temp, pressure, status, eroor in filter_rdd.collect():
    print(timestamp, sensor, temp, pressure)

# Остановка SparkContext 
sc.stop()