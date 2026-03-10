from pyspark.sql import SparkSession

from datetime import datetime
import pyspark.sql.functions as F

from datetime import datetime, date
import logging

def run_spark_s3():
    spark = SparkSession.builder \
        .appName("SUCCESS") \
        .master("local[*]") \
        .config("spark.jars",
                "/opt/spark/jars/clickhouse-jdbc-0.4.6.jar,"
                "/opt/spark/jars/hadoop-aws-3.3.4.jar,"
                "/opt/spark/jars/aws-java-sdk-bundle-1.12.262.jar,"
                "/opt/spark/jars/commons-compress-1.20.jar") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "admin") \
        .config("spark.hadoop.fs.s3a.secret.key", "StrongPassword123!") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
        .getOrCreate()
    

    
   

    spark.sparkContext.setLogLevel("WARN")
    logging.info(f"✅ SparkSession готова {datetime.now()}")



    df_test = spark.read \
        .format("jdbc") \
        .option("url", "jdbc:clickhouse://clickhouse:8123/mart") \
        .option("dbtable", "(SELECT * FROM clean_purchases) AS subq") \
        .option("user", "default") \
        .option("password", "password") \
        .option("driver", "com.clickhouse.jdbc.ClickHouseDriver") \
        .load()
    # перенос DF  в оперативную память 
    df = df_test.cache()


    print("Уникальные значения в столбце к ним буду проводить left join")
    df_cus_uniq = df.select("customer_id").distinct()

    print("🥛 пользоватля покупавшие молоко за последние 30 дней") 
    bought_milk_last_30d = df.filter(
        (F.col("group") == "Молочные продукты") & 
        (F.col("purchase_datetime") >= F.date_sub(F.current_date(), 30))
    ).select("customer_id").distinct()

    print("🍏 Покупалb фрукты и ягоды за последние 14 дней")
    bought_fruits_last_14d = df.filter(
        (F.col("group") == "Фрукты и ягоды") &
        (F.col("purchase_datetime") >= F.date_sub(F.current_date(), 14))
    ).select("customer_id").distinct()

    print("🥦 Не покупал овощи и зелень за последние 14 дней")
    not_bought_veggies_14d = df.filter(
        (F.col("group") != "Овощи и зелень") &
        (F.col("purchase_datetime") >= F.date_sub(F.current_date(), 14))
    ).select("customer_id").distinct()


    print("✅ Делал более 2 покупок за последние 30 дней")
    recurrent_buyer = (df
        .filter(F.col("purchase_datetime") >= F.date_sub(F.current_date(), 30)) \
        .groupBy("customer_id") \
        .agg(F.count("purchase_id").alias("cnt_pur")) \
        .filter(F.col("cnt_pur") >= 2).select("customer_id")
        )

    print("✅ Не покупал 14–30 дней (ушедший клиент?)")
    inactive_14_30 = (df
        .groupBy("customer_id")
        .agg(F.max("purchase_datetime").alias("last_pur"))
        .filter(
            (F.col("last_pur") <= F.date_sub(F.current_date(), 14)) &
            (F.col("last_pur") > F.date_sub(F.current_date(), 30)))
        .orderBy(F.col("last_pur"))\
        .select("customer_id")
        )
    

    print("✅ Покупатель зарегистрировался менее 30 дней назад")
    new_customer = df.filter(
        F.col("registration_date") >= F.date_sub(F.current_date(), 30))\
    .select("customer_id").distinct()


    print("✅ Пользовался доставкой хотя бы раз")
    delivery_user = df.filter(
        F.col("is_delivery") == 1)\
    .select("customer_id").distinct()

    print("✅ Купил хотя бы 1 органический продукт")
    organic_preference = df.filter(
        F.col("is_organic") == 1)\
    .select("customer_id").distinct()

    print("✅ Средняя корзина > 1000₽")
    bulk_buyer = (df
        .groupBy("customer_id") \
        .agg(F.avg("total_amount").alias("avg_amount")) \
        .filter(F.col("avg_amount") > 1000)\
    .select("customer_id")
        )

    print("✅ Средняя корзина < 200₽")
    low_cost_buyer = (df
        .groupBy("customer_id") \
        .agg(F.avg("total_amount").alias("avg_amount")) \
        .filter(F.col("avg_amount") < 1000)\
    .select("customer_id")
        )

    print("✅ Покупал хлеб/выпечку хотя бы раз")
    buys_bakery = df.filter(
        F.col("group") == "Зерновые и хлебобулочные изделия")\
    .select("customer_id").distinct()

    print("✅ Финальный результат для отчета")
    result = df_cus_uniq.alias("all_cust")\
    .join(
        bought_milk_last_30d.alias("milk"), 
        F.col("all_cust.customer_id") == F.col("milk.customer_id"), 
        "left")\
    .join(
        bought_fruits_last_14d.alias("fruits"),
        F.col("all_cust.customer_id") == F.col("fruits.customer_id"), 
        "left") \
    .join(
        not_bought_veggies_14d.alias("not_vegg"),
        F.col("all_cust.customer_id") == F.col("not_vegg.customer_id"), 
        "left") \
    .join(
        recurrent_buyer.alias("rec_buyer"),
        F.col("all_cust.customer_id") == F.col("rec_buyer.customer_id"), 
        "left") \
    .join(
        inactive_14_30.alias("inact"),
        F.col("all_cust.customer_id") == F.col("inact.customer_id"), 
        "left") \
    .join(
        new_customer.alias("new_cus"),
        F.col("all_cust.customer_id") == F.col("new_cus.customer_id"), 
        "left") \
    .join(
        delivery_user.alias("deliv_user"),
        F.col("all_cust.customer_id") == F.col("deliv_user.customer_id"), 
        "left") \
    .join(
        organic_preference.alias("organic"),
        F.col("all_cust.customer_id") == F.col("organic.customer_id"), 
        "left") \
    .join(
        bulk_buyer.alias("b_b"),
        F.col("all_cust.customer_id") == F.col("b_b.customer_id"), 
        "left") \
    .join(
        low_cost_buyer.alias("low_cost"),
        F.col("all_cust.customer_id") == F.col("low_cost.customer_id"), 
        "left") \
    .join(
        buys_bakery.alias("bakery"),
        F.col("all_cust.customer_id") == F.col("bakery.customer_id"), 
        "left") \
    .select(                                              
            F.col("all_cust.customer_id"),
            F.when(F.col("milk.customer_id").isNotNull(), 1).otherwise(0).alias("bought_milk_last_30d"),
            F.when(F.col("fruits.customer_id").isNotNull(), 1).otherwise(0).alias("bought_fruits_last_14d"),
            F.when(F.col("not_vegg.customer_id").isNotNull(),1).otherwise(0).alias("not_bought_veggies_14d"),
            F.when(F.col("rec_buyer.customer_id").isNotNull(),1).otherwise(0).alias("recurrent_buyer"),
            F.when(F.col("inact.customer_id").isNotNull(),1).otherwise(0).alias("inactive_14_30"),
            F.when(F.col("new_cus.customer_id").isNotNull(),1).otherwise(0).alias("new_customer"),
            F.when(F.col("deliv_user.customer_id").isNotNull(),1).otherwise(0).alias("delivery_user"),
            F.when(F.col("organic.customer_id").isNotNull(),1).otherwise(0).alias("organic_preference"),
            F.when(F.col("b_b.customer_id").isNotNull(),1).otherwise(0).alias("bulk_buyer"),
            F.when(F.col("low_cost.customer_id").isNotNull(),1).otherwise(0).alias("low_cost_buyer"),
            F.when(F.col("bakery.customer_id").isNotNull(),1).otherwise(0).alias("buys_bakery")
        ) \
    .orderBy("all_cust.customer_id")

    print("✅ Пример отчета по 1- му пользователю")
    result.show(1, vertical= True)

    today = date.today().strftime('%Y_%m_%d')  # '2026_03_09'
    path = f"s3a://report-clickhouse/analityc_result_{today}.csv"
    result.write.mode("overwrite").csv(path)
    logging.info(f"✅ запись отчета analityc_result_{today}.csv Успешна!")

    spark.stop()
    logging.info(f"✓ SparkSession остановлена {datetime.now()}")


