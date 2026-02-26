-- ====== raw_purchases =========
CREATE TABLE IF NOT EXISTS raw_purchases
(
        purchase_id String,
        customer_id String,
        store_id String,
        product_id String,
        total_amount Decimal(10,2),     
        payment_method LowCardinality(String),
        is_delivery UInt8,
        purchase_datetime DateTime

)
ENGINE = MergeTree
PARTITION BY toYYYYMM(purchase_datetime)
ORDER BY (purchase_datetime, customer_id);