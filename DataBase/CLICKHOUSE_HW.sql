--создание таблицы user_events--
drop table if exists  learn_db.user_events;
CREATE TABLE learn_db.user_events(
	user_id UInt32,
	event_type String,
	points_spent UInt32,
	event_time DateTime
) ENGINE = MergeTree()
ORDER BY (event_type, event_time)
TTL event_time + INTERVAL 30 DAY DELETE;

-- создание агрегированой таблицы --
drop table if exists  learn_db.events_agg;
CREATE TABLE learn_db.events_agg (
    event_date DateTime,
    event_type String,
    unique_users AggregateFunction(uniq, UInt32),
    total AggregateFunction(sum, UInt32),
    total_action AggregateFunction(count, UInt8)
) ENGINE = AggregatingMergeTree()
ORDER BY (event_type, event_date)
TTL event_date + INTERVAL 180 DAY DELETE;

-- MV для вставки сырых данных в агрегированную таблицу events_agg--
drop Table if exists learn_db.events_mv;
CREATE MATERIALIZED VIEW learn_db.events_mv
TO learn_db.events_agg
AS
SELECT 
	toDate(event_time) as event_date,
	event_type,
 	uniqState(user_id) as unique_users,
	sumState(points_spent) AS total,
	countState(event_type) as  total_action
FROM learn_db.user_events
GROUP BY toDate(event_time), event_type;

-- вставка данных --
INSERT INTO learn_db.user_events VALUES
-- События 10 дней назад
(1, 'login', 0, now() - INTERVAL 10 DAY),
(2, 'signup', 0, now() - INTERVAL 10 DAY),
(3, 'login', 0, now() - INTERVAL 10 DAY),
(1, 'login', 0, now() - INTERVAL 7 DAY),
(2, 'login', 0, now() - INTERVAL 7 DAY),
(3, 'purchase', 30, now() - INTERVAL 7 DAY),
(1, 'purchase', 50, now() - INTERVAL 5 DAY),
(2, 'logout', 0, now() - INTERVAL 5 DAY),
(4, 'login', 0, now() - INTERVAL 5 DAY),
(1, 'login', 0, now() - INTERVAL 3 DAY),
(3, 'purchase', 70, now() - INTERVAL 3 DAY),
(5, 'signup', 0, now() - INTERVAL 3 DAY),
(2, 'purchase', 20, now() - INTERVAL 1 DAY),
(4, 'logout', 0, now() - INTERVAL 1 DAY),
(5, 'login', 0, now() - INTERVAL 1 DAY),
(1, 'purchase', 25, now()),
(2, 'login', 0, now()),
(3, 'logout', 0, now()),
(6, 'signup', 0, now()),
(6, 'purchase', 100, now());

-- запрос к агрегированной таблице--
SELECT 
    event_date,
    event_type,
    uniqMerge(unique_users) as unique_users,
    sumMerge(total) as total_points,
    countMerge(total_action) as total_actions
FROM learn_db.events_agg
GROUP BY event_date, event_type
ORDER BY event_date, event_type;

--ad-hoc запрос, для проверки к таблице с сырыми данными-
SELECT 
    toDate(event_time) as event_date,
    event_type,
    uniq(user_id) as unique_users,
    SUM(points_spent) as total_points,
    COUNT(*) as total_actions
FROM learn_db.user_events
GROUP BY event_date, event_type
ORDER BY event_date, event_type;


---Подсчет retention из сырых данных user_events--
WITH 
--таблица отражающая пользователя и его дату первого действия на сайте --
first_actions AS (
    SELECT 
        user_id,
        min(toDate(event_time)) as first_date
    FROM learn_db.user_events
    GROUP BY user_id
),
-- строю кагорту по пользователем min.дата входа - пользователь и дальнейшие его действия в течении 7 дней
cohort_actions AS (
    SELECT 
        fa.first_date as cohort_date,
        fa.user_id,
        toDate(ue.event_time) as action_date,
        datediff('day', fa.first_date, toDate(ue.event_time)) as days_diff
    FROM first_actions fa
    JOIN learn_db.user_events ue ON fa.user_id = ue.user_id
    WHERE toDate(ue.event_time) BETWEEN fa.first_date AND fa.first_date + INTERVAL 7 DAY
),
-- 
cohort_stats AS (
    SELECT 
        cohort_date,
        count(DISTINCT user_id) as total_users_day_0,
        count(DISTINCT if(days_diff BETWEEN 1 AND 7, user_id, NULL)) as returned_in_7_days
    FROM cohort_actions
    GROUP BY cohort_date
)
SELECT 
    cohort_date,
    total_users_day_0,
    returned_in_7_days,
    toString(round(returned_in_7_days * 100.0 / total_users_day_0, 2))||'%' as retention_7d_percent
FROM cohort_stats
ORDER BY cohort_date;


-- подсчет из MV (использовал GPT) --
DROP TABLE IF EXISTS learn_db.cohort_table;
CREATE TABLE learn_db.cohort_table (
    cohort_date Date,
    user_id UInt32, 
    has_returned UInt8,
    _version UInt64 DEFAULT 1
) ENGINE = ReplacingMergeTree(_version)
ORDER BY (cohort_date, user_id);

-- Соответствующий MV
DROP TABLE IF EXISTS learn_db.retention_mv_to_cohort;
CREATE MATERIALIZED VIEW learn_db.retention_mv_to_cohort
TO learn_db.cohort_table
AS
WITH user_first_dates AS (
    SELECT 
        user_id,
        min(toDate(event_time)) as first_date
    FROM learn_db.user_events
    GROUP BY user_id
)
SELECT 
    ufd.first_date as cohort_date,
    ufd.user_id,
    if(
        maxIf(toDate(ue.event_time), 
              toDate(ue.event_time) BETWEEN ufd.first_date + INTERVAL 1 DAY AND ufd.first_date + INTERVAL 7 DAY
        ) > ufd.first_date, 1, 0
    ) as has_returned,
    1 as _version
FROM user_first_dates ufd
LEFT JOIN learn_db.user_events ue ON ufd.user_id = ue.user_id
GROUP BY ufd.first_date, ufd.user_id;

-- вызов retention из агрегированной таблицы --
SELECT 
    cohort_date,
    count(*) as total_users_day_0,
    sum(has_returned) as returned_in_7_days,
    toString(round(sum(has_returned) * 100.0 / count(*), 2))|| '%' as retention_7d_percent
FROM learn_db.cohort_table
GROUP BY cohort_date
ORDER BY cohort_date;



