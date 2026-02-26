-- ====== raw_products_kbju =========
CREATE TABLE IF NOT EXISTS raw_products_kbju
(
    product_id   String,
    calories Decimal(10,2),
    carbohydrates Decimal(10,2),
    fat Decimal(10,2),
    protein Decimal(10,2)
)
ENGINE = TinyLog;
