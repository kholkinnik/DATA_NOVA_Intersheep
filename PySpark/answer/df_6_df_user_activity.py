from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *
from datetime import date

# Инициализация SparkSession
spark = SparkSession.builder \
        .appName("user_activity_project") \
        .getOrCreate()

schema = StructType((
    StructField("user_id", IntegerType(), True),
    StructField("activity_date", DateType(), True),
    StructField("sessions_by_device", MapType(StringType(), IntegerType()), True),
    StructField("visited_pages", ArrayType(StringType()), True),
    StructField("usability_rating", DoubleType(), True)
))
data = [
    (101, date(2025, 1, 1), {"mobile": 3, "desktop": 1}, ["/home", "/products", "/cart"], 4.5),
    (102, date(2025, 1, 1), {"desktop": 2}, ["/home", "/about"], 3.0),
    (101, date(2025, 1, 2), {"mobile": 2}, ["/products", "/checkout"], None),
    (103, date(2025, 1, 2), {"tablet": 1, "mobile": 1}, ["/blog", "/contact"], 5.0), 
    (104, date(2025, 1, 3), {"desktop": 4}, ["/dashboard"], 3.5),
    (101, date(2025, 1, 3), {"mobile": 1, "desktop": 1}, ["/home", "/products"], 4.0),
    (105, date(2025, 1, 4), {"mobile": 5}, ["/faq"], None),
    (102, date(2025, 1, 4), {"desktop": 1, "mobile": 1}, ["/settings"], 3.8),
    (103, date(2025, 1, 5), {"tablet": 2}, ["/products"], 4.2), 
    (106, date(2025, 1, 5), {"desktop": 3, "mobile": 2}, ["/login", "/profile", "/home"], 4.7),
    (101, date(2025, 1, 6), {"mobile": 1}, ["/cart", "/checkout"], 4.0),
    (104, date(2025, 1, 6), {"desktop": 2, "tablet": 1}, ["/contact"], None),
    (105, date(2025, 1, 7), {"mobile": 3, "desktop": 1}, ["/pricing"], 4.1),
    (106, date(2025, 1, 7), {"desktop": 1}, ["/home", "/about"], 3.9),
    (107, date(2025, 1, 8), {"mobile": 4, "tablet": 2}, ["/products", "/blog"], 4.9) 
]
df_user_activity = spark.createDataFrame(data, schema=schema)

# 1.2. Выведите схему созданного DataFrame
df_user_activity.printSchema()

# 2.1. Рассчитайте total_sessions_count для каждой записи 
df_user_activity = df_user_activity.withColumn("total_sessions_count",
    (F.coalesce(F.col("sessions_by_device").mobile, F.lit(0)) +
     F.coalesce(F.col("sessions_by_device").desktop, F.lit(0)) +
     F.coalesce(F.col("sessions_by_device").tablet, F.lit(0))))
df_user_activity.show()

# 2.2. Извлеките количество "мобильных" сессий
df = df_user_activity.withColumn("mobile_sessions", 
                                 F.when(df_user_activity.sessions_by_device.mobile > 0, df_user_activity.sessions_by_device.mobile).otherwise(0))
df.show()

# 3.1. Для каждого пользователя рассчитайте total_sessions_all_time
df_user_activity.groupBy("user_id").agg(F.sum("total_sessions_count").alias("total_sessions_all_time")).orderBy(F.col("total_sessions_all_time").desc()).show()


# 3.2. Для каждого пользователя получите unique_visited_pages_all_time
df_unique_pages_all_time = df_user_activity.select("user_id", F.explode_outer("visited_pages").alias("page")) \
    .groupBy("user_id").agg(
        F.collect_set("page").alias("unique_visited_pages_all_time")
    )
df_unique_pages_all_time.orderBy("user_id").show(truncate=False)

# 4.1. Отфильтруйте DataFrame df_user_activity по usability_rating
df_filtered_rating = df_user_activity.filter(F.col("usability_rating") > 3.5) \
    .orderBy(F.col("usability_rating").desc())
df_filtered_rating.show()

# Остановка SparkSession
spark.stop()
