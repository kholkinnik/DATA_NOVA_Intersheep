from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *
from pyspark.sql.window import Window

spark = SparkSession.builder \
         .appName("project_avtovaz") \
         .getOrCreate()


df = spark.read.option("header", True).option("sep", ",").csv("avtovaz.csv")
df.show(truncate=False)
df.printSchema()
new_columns_standardized = []
for col_name in df.columns:
# Очистка имени колонки
    cleaned_name = col_name.strip() \
                            .replace(" ", "_") \
                            .replace("(", "_") \
                            .replace(")", "_") \
                            .replace(".", "") \
                            .lower()
# Убираем возможные двойные подчеркивания
    cleaned_name = "_".join(filter(None, cleaned_name.split("_")))
    new_columns_standardized.append(cleaned_name)

# Применяем новые имена к DataFrame
df = df.toDF(*new_columns_standardized)
print(df.columns)

columns_to_cast_types = {
    "год": IntegerType(),
    "реализация_внутренний_рынок:_тыс": DoubleType(),
    "реализация_внешний_рынок:_тыс": DoubleType(),
    "себестоимость_реализации_млн_руб": DoubleType(),
    "валовая_прибыль_от_реализации": DoubleType(),
    "общая_сумма_дивидендов_млн_руб": DoubleType(),
    "чистая_прибыль_отчётного_года_млн_руб": DoubleType(),
    "всего_текущие_активы": DoubleType(),
    "потоки_денежных_средств_от_инвестиционной_деятельности": DoubleType(),
    "потоки_денежных_средств_от_фин_деятельности": DoubleType(),
    "чистые_денежные_средства_от_операционной_деятельности": DoubleType(),
    "прибыль_до_налогов": DoubleType(),
    "тип": StringType()
}

# Применяем преобразования типов
for col_name, col_type in columns_to_cast_types.items():
    df = df.withColumn(col_name, F.col(col_name).cast(col_type))
df.printSchema()

# Расчет чистой прибыли за предыдущий год
df_task1 = df.withColumn(
    "чистая_прибыль_предыдущего_года",
    F.lag(F.col("чистая_прибыль_отчётного_года_млн_руб"), 1).over(Window.orderBy("год"))
)
# Вычисление изменения чистой прибыли
df_task1 = df_task1.withColumn(
    "изменение_прибыли",
    F.col("чистая_прибыль_отчётного_года_млн_руб") - F.col("чистая_прибыль_предыдущего_года")
)
# Ранжирование годов по абсолютному росту чистой прибыли
window_rank_spec = Window.orderBy(F.desc("изменение_прибыли"))
df_task1 = df_task1.withColumn(
    "ранг_роста_прибыли",
    F.rank().over(window_rank_spec)
)
df_task1.select("год",
            "чистая_прибыль_отчётного_года_млн_руб",
            "чистая_прибыль_предыдущего_года",
            "изменение_прибыли",
            "ранг_роста_прибыли") \
    .orderBy("ранг_роста_прибыли") \
    .show(25,truncate=False)

# Создаем новую колонку категория_прибыли
"""" условие категорий:
Высокоприбыльный год": если чистая прибыль > 5000 млн руб.
"Среднеприбыльный год": если чистая прибыль от 1000 до 5000 млн руб. (включительно)
"Низкоприбыльный год": если чистая прибыль от 0 до 1000 млн руб. (исключая 0)
"Убыточный год": если чистая прибыль < 0
"Нулевая прибыль": если чистая прибыль = 0"""
df_task2 = df.withColumn(
    "категория_прибыли", 
    F.when(F.col("чистая_прибыль_отчётного_года_млн_руб") > 5000, "Высокоприбыльный год")
    .when((F.col("чистая_прибыль_отчётного_года_млн_руб") > 1000) &  (F.col("чистая_прибыль_отчётного_года_млн_руб") <= 5000), "Среднеприбыльный год")
    .when((F.col("чистая_прибыль_отчётного_года_млн_руб") > 0) &  (F.col("чистая_прибыль_отчётного_года_млн_руб") <= 1000), "Низкоприбыльный год")
    .when(F.col("чистая_прибыль_отчётного_года_млн_руб") < 0, "Убыточный год")
    .when(F.col("чистая_прибыль_отчётного_года_млн_руб") == 0, "Нулевая прибыль")
)

df_task2.groupBy(F.col("категория_прибыли")).agg(F.count("год").alias("количество_лет")
                                            ,F.round(F.avg(F.col("реализация_внутренний_рынок:_тыс")
                                                           +F.col("реализация_внешний_рынок:_тыс")),2).alias("средняя_общая_реализация_тыс_шт")
                                            ).orderBy(F.col("количество_лет").desc()).show()

# Остановка SparkSession
spark.stop()

