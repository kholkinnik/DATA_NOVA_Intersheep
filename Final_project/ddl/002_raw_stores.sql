-- ====== raw_stores =========
CREATE TABLE IF NOT EXISTS raw_stores
(
    store_id  String,
    store_name String,
    store_network String,
    store_type_description String,
    type LowCardinality(String)  

)
ENGINE = TinyLog;