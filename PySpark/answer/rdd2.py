from pyspark import SparkContext
sc = SparkContext("local", "RDD_project_2")

rdd_password = sc.textFile("password.txt")
rdd_password = rdd_password.map(lambda x: x.strip())
rdd_password = rdd_password.filter(lambda x: len(x) != 0)

# Средняя дина пароля 
len_password = rdd_password.map(lambda x: len(x))
sum_len_password = len_password.sum()
cnt_password = rdd_password.count()
print(f"Средняя длина пароля: {round(sum_len_password/cnt_password)}")

# Минимальная и максимальна длина 
print(f"Минимальная длина пароля: {len_password.min()}")
print(f"Максимальная длина пароля: {len_password.max()}")

# Топ-5 самых распространенных длин паролей
tuple_len = len_password.map(lambda x: (x,1))
cnt_len_password = tuple_len.reduceByKey(lambda a, b: a + b)
for num, cnt in cnt_len_password.top(5, key=lambda x: x[1]):
    print(f"{num}: {cnt}")

# Количество паролей, содержащих только цифры
only_digit = rdd_password.filter(lambda x: x.isdigit())
print("Количество паролей, содержащих только цифры")
print(only_digit.count())

# Количество паролей, содержащих только буквы
only_alpha = rdd_password.filter(lambda x: x.isalpha())
print("Количество паролей, содержащих только буквы")
print(only_alpha.count())

# Топ-5 самых распространенных префикса
list_perfix = rdd_password.map(lambda x: (x[0:3],1))
cnt_perfix = list_perfix.reduceByKey(lambda a, b: a +b)
top_perfix = cnt_perfix.top(5, key = lambda x: x[1])
print("Топ-5 самых распространенных префикса")
for perfix in top_perfix:
    print(perfix)

# Топ-5 самых распространенных суффикса
list_suffix = rdd_password.map(lambda x: (x[-3:],1))
cnt_suffix = list_suffix.reduceByKey(lambda a, b: a +b)
top_suffix = cnt_suffix.top(5, key = lambda x: x[1])
print("Топ-5 самых распространенных суффикса")
for suffix in top_suffix:
    print(suffix)

# Остановка SparkContext 
sc.stop()