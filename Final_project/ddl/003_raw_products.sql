-- ====== raw_products =========
CREATE TABLE IF NOT EXISTS raw_products
(
    product_id   String,
    name String,
    group String,
    description String,
    price Decimal(10,2),
    unit String,
    origin_country String,
    expiry_days UInt32,
    is_organic UInt8,
    barcode String

)
ENGINE = TinyLog;