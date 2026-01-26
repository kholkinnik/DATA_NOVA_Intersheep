from pyspark.sql import SparkSession
from pyspark.sql import functions as F

# 1. Инициализируем SparkSession
# Убедитесь, что у вас установлен пакет spark-avro
spark = SparkSession.builder \
    .appName("avro_project") \
    .config("spark.jars.packages", "org.apache.spark:spark-avro_2.12:3.5.0") \
    .getOrCreate()

# Загрузка данных из файла Avro
df = spark.read.format("avro").load("activity_log.avro")

# Выведите схему и первые 10 строк
df.printSchema()
df.show(10, truncate=False)

# Преобразование колонки timestamp в TimestampType
df = df.withColumn("event_time", F.to_timestamp("timestamp", "dd-MMM-yyyy HH:mm"))
df.show(5)

# Посчитайте количество уникальных событий для каждого дня
(df.groupBy(F.col("event_time").cast("date").alias("date"))
        .agg(F.count("event_id").alias("total_events"))
        .orderBy("date").show()
)

#  Найдите количество уникальных пользователей
print("Количество уникальных пользователей")
df.select("user_id").distinct().orderBy("user_id").show()

# Найдите общее количество уникальных сессий
print("Количество уникальных сессий")
print(df.select("session_id").distinct().count())

# Количество уникальных сессий на пользователя
(df.groupBy("user_id").agg(
    F.countDistinct("session_id").alias("unique_sessions_count")
    ).orderBy("user_id").show())

# Количество событий в каждой сессии
(df.groupBy("user_id", "session_id")
    .agg(F.count("*").alias("count_sessions"))
    .orderBy("count_sessions")
    .show()
)

# Посчитайте общее количество покупок
(df.filter(F.col("event_type") == "purchase")
    .agg(F.count(F.col("amount")).alias("count_purchase_amount"))
    .show()
)
# Найдите общую сумму всех покупок
(df.filter(F.col("event_type") == "purchase")
    .agg(F.sum(F.col("amount")).alias("sum_purchase_amount"))
    .show()
)
# Посчитайте среднюю сумму покупки
(df.filter(F.col("event_type") == "purchase")
    .agg(F.round(F.avg(F.col("amount")), 2).alias("average_purchase_amount"))
    .show()
)

# Расчет продолжительности каждой сессии
df_session_durations = df.groupBy("user_id", "session_id").agg(
    F.min("event_time").alias("min_time"),
    F.max("event_time").alias("max_time")
).withColumn(
    "session_duration_seconds",
    (F.unix_timestamp(F.col("max_time")) - F.unix_timestamp(F.col("min_time")))
)
df_session_durations.orderBy("user_id", "session_id").show(truncate=False)

# Средняя продолжительность сессии
(df_session_durations
    .agg(F.round(F.avg(F.col("session_duration_seconds")),2).alias("average_session_duration_seconds"))
    .show()
)

# Останавливаем SparkSession
spark.stop()