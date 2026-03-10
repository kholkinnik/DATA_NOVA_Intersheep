--создание чистой таблицы с дедупликацией ( ORDER BY purchase определяет ключ дубликатов, pur_date (дабавил pur_date, т.к. по заказу может быть возврат)
CREATE TABLE IF NOT EXISTS mart.clean_purchases (
	customer_id String,
	purchase_id String,
	purchase_datetime DateTime,
	product_id String,
	group String,
	price Decimal(10,2),
	total_amount Decimal(10,2),
	is_organic UInt8,
	is_delivery UInt8,
	is_loyalty_member UInt8,
	birth_date Date,
	registration_date DateTime

) ENGINE = ReplacingMergeTree()
ORDER BY (purchase_id, purchase_datetime);