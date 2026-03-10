-- ====== raw_customers =========
CREATE TABLE IF NOT EXISTS raw_customers
(
    customer_id  String,
    first_name String,
    last_name String,
    email String,
    phone String,
    birth_date Date32,
    gender LowCardinality(String),
    registration_date DateTime,
    is_loyalty_member UInt8,
    loyalty_card_number String

)
ENGINE = TinyLog;