-- создание MATERIALIZED VIEW cleaning_purchases_mv
CREATE MATERIALIZED VIEW IF NOT EXISTS mart.cleaning_purchases_mv
TO mart.clean_purchases
AS
SELECT
    lower(rpur.customer_id) as customer_id,
    lower(rpur.purchase_id) as purchase_id,
    rpur.purchase_datetime,
	lower(rpur.product_id) as product_id,
	lower(rprod.group) as `group`,
	rprod.price,
	rpur.total_amount,
	rprod.is_organic,
	rpur.is_delivery,
	rcus.is_loyalty_member,
	rcus.birth_date,
	rcus.registration_date
FROM raw_purchases rpur
	LEFT JOIN raw_products rprod ON rpur.product_id = rprod.product_id
	LEFT JOIN raw_customers rcus ON rpur.customer_id = rcus.customer_id
-- ФИЛЬТРЫ ВАЛИДНОСТИ (только чистые данные):
WHERE length(coalesce(rpur.customer_id, '')) > 0 -- так же обработает и NUll
  AND length(coalesce(rpur.purchase_id, '')) > 0
  AND rpur.purchase_datetime <= now() AND rpur.purchase_datetime IS NOT NULL
  AND length(coalesce(rpur.product_id, '')) > 0
  AND length(coalesce(rprod.group, '')) > 0  
  AND coalesce(rprod.price, 0) >= 0 
  AND coalesce(rpur.total_amount, 0) >= 0
  AND coalesce(rprod.is_organic, -1) >= 0
  AND coalesce(rpur.is_delivery, -1) >= 0
  AND coalesce(rcus.is_loyalty_member, -1) >= 0
  AND rcus.birth_date <= now() AND rcus.birth_date IS NOT NULL
  AND rcus.registration_date <= now() AND rcus.registration_date IS NOT NULL;