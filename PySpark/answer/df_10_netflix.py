from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *
from pyspark.sql import Window
spark = SparkSession.builder \
        .appName("netflix_project") \
        .getOrCreate()

schema = StructType((
            StructField("title", StringType(), True),
            StructField("type", StringType(), True),
            StructField("genres", StringType(), True),
            StructField("releaseYear", IntegerType(), True),
            StructField("imdbId", StringType(), True),
            StructField("imdbAverageRating", DoubleType(), True),
            StructField("imdbNumVotes", IntegerType(), True),
            StructField("availableCountries", StringType(), True)
))
# Считываем со схемой
df = spark.read.option("header", True).csv("netflix_data.csv", schema= schema)

# Преобразуем типы со структурой array
df = df.withColumn("genres", F.split(F.col("genres"), ", "))
df = df.withColumn("availableCountries", F.split(F.col("availableCountries"), ", "))

df.show()
df.printSchema()

# Удаляем дубликаты
print(f"Количество строк до удаления дубликатов: {df.count()}")
df = df.dropDuplicates(["title", "releaseYear", "imdbId"])
print(f"Количество строк после удаления дубликатов: {df.count()}")

# Удаляем пропуски
df.summary().show()
df = df.dropna(subset=["imdbAverageRating","genres"])
df.summary().show()

# Анализ соотношения фильмов и сериалов по жанрам и годам
(df.groupBy("releaseYear")
    .pivot("type")
    .agg(F.count("*").alias("total_titles"))
    .orderBy(F.col("releaseYear").desc())
    .limit(10)
    .show()
)
(df.select(F.explode_outer(F.col("genres")).alias("genre"), "type")
    .groupBy("genre")
    .pivot("type")
    .agg(F.count("*").alias("count"))
    .orderBy((F.col("movie")+F.col("tv")).desc())
    .limit(15)
    .show()
)
# Популярность жанров на IMDb
(df.select(F.explode_outer(F.col("genres")).alias("genre"), "imdbAverageRating", "imdbNumVotes")
    .groupBy("genre")
    .agg(F.round(F.avg("imdbAverageRating"),2).alias("average_rating"), F.sum("imdbNumVotes").alias("total_votes"))
    .orderBy(F.col("average_rating").desc())
    .limit(10)
    .show()
)

# Динамика выпуска контента по годам и рейтинг
(df.groupBy("releaseYear")
    .agg(F.count("*").alias("total_titles"), F.round(F.avg("imdbAverageRating"),2).alias("average_rating"))
    .orderBy(F.col("releaseYear").desc())
    .limit(10)
    .show()
    )
# Анализ динамики прироста фильмов по годам
df_window = (df.groupBy("releaseYear")
.agg(F.count("*").alias("current_year_title_count"))
.withColumn("previous_year_title_count", F.lag("current_year_title_count").over(Window.orderBy("releaseYear")))
.orderBy(F.col("releaseYear").desc()))
df_window = df_window.withColumn("title_count_growth", F.col("current_year_title_count") - F.col("previous_year_title_count"))
df_window.orderBy(F.col("title_count_growth").desc()).limit(10).show()

# Поиск "Скрытых Жемчужин" (High Rating, Low Votes)
(df.filter((F.col("imdbNumVotes") > 300) & (F.col("imdbNumVotes") < 10000))
.orderBy(F.col("imdbAverageRating").desc()).show(10,truncate=False))

# Остановка SparkSession
spark.stop()

