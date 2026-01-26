from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import *
spark = SparkSession.builder \
        .appName("star_wars_project") \
        .getOrCreate()

characters = spark.read.parquet('parquet_files/characters.parquet')
species = spark.read.parquet('parquet_files/species.parquet')
organizations = spark.read.parquet('parquet_files/organizations.parquet')

species.show(40)
characters.show()
organizations.show()

# Удаляем дубликаты 
characters = characters.dropDuplicates(subset=["name", "species", "homeworld", "year_born"])
species = species.dropDuplicates(subset=["name","classification", "designation", "average_height"])

# Распространенность видов и их классификаций
(characters.groupBy("species")
    .agg(F.count("*").alias("character_count"))
    .orderBy(F.col("character_count").desc())
    .limit(10).show())

# Распространенность классификаций
(species.join(characters, species.name == characters.species, "left") 
    .groupBy(species.classification).agg(F.count("*").alias("total_character_count")) 
    .orderBy(F.col("total_character_count").desc())
    .show())

# Средний рост по классификации
(species.groupBy("classification")
    .agg(F.round(F.avg("average_height"),1).alias("average_height_class"))
    .orderBy(F.col("average_height_class").desc())
    .show())

# Члены Ордена Джедаев и Ситхов
# Преобразуем тип колонки
organizations = organizations.withColumn(
    "leader_array", 
    F.split(F.col("leader"), ", ").cast(ArrayType(StringType()))
)
organizations = organizations.withColumn(
    "members_array", 
    F.split(F.col("members"), ", ").cast(ArrayType(StringType()))
)

members = (organizations
           .select("name", F.explode_outer("leader_array").alias("name_member"))
           .filter(F.col("name").isin("Jedi Order", "Sith Order"))
    .union
           (organizations
            .select("name", F.explode_outer("members_array").alias("name_member"))
            .filter(F.col("name").isin("Jedi Order", "Sith Order")))
            )

members.orderBy("name").show()

# Топ-5 старейших и топ-5 самых юных персонажей
(characters.select("name", "year_born")
    .dropna(subset=["year_born"])
    .orderBy(F.col("year_born")).limit(5)
    .show())
(characters.select("name", "year_born")
    .dropna(subset=["year_born"])
    .orderBy(F.col("year_born").desc()).limit(5)
    .show())

# Расчитываем ИМТ
bmi_characters = characters.withColumn("bmi", F.round(F.col("weight")/ (F.col("height"))**2,2))
bmi_characters.orderBy(F.col("bmi").desc()).limit(5).show()
bmi_characters.dropna(subset=["height","weight"]).orderBy(F.col("bmi")).limit(5).show()

# Остановка SparkSession
spark.stop()
