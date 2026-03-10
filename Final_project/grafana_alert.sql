SELECT
(1- divide(toInt64(uniqExact(purchase_id, purchase_datetime)),toInt64(count())))*100 as perc
FROM raw_purchases
WHERE purchase_datetime >= today()


--==== Дашборд ====
select 
count(purchase_id) as cnt_purchases
from raw_purchases

select 
count(distinct(store_id)) as cnt_Big_Pikcha
from raw_stores
WHERE store_network = 'Большая Пикча'

select 
count(distinct(store_id)) as cnt_Big_Pikcha
from raw_stores
WHERE store_network = 'Маленькая Пикча'
