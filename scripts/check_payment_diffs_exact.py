import os
import duckdb
import pandas as pd

data_dir = r"data/raw".replace('\\', '/')
con = duckdb.connect()

res = con.execute(f"""
    WITH ordered_pay AS (
        SELECT 
            account_id,
            event_at,
            amount,
            LAG(event_at) OVER(PARTITION BY account_id ORDER BY event_at) as prev_event,
            LAG(amount) OVER(PARTITION BY account_id ORDER BY event_at) as prev_amount
        FROM (SELECT DISTINCT * FROM read_csv_auto('{data_dir}/payments.csv'))
    )
    SELECT 
        COUNT(*) as total_pairs,
        COUNT(CASE WHEN date_diff('second', prev_event::TIMESTAMP, event_at::TIMESTAMP) <= 600 THEN 1 END) as within_10m,
        COUNT(CASE WHEN date_diff('second', prev_event::TIMESTAMP, event_at::TIMESTAMP) <= 3600 THEN 1 END) as within_1h,
        COUNT(CASE WHEN date_diff('second', prev_event::TIMESTAMP, event_at::TIMESTAMP) <= 86400 THEN 1 END) as within_24h,
        COUNT(CASE WHEN date_diff('day', prev_event::TIMESTAMP, event_at::TIMESTAMP) <= 7 THEN 1 END) as within_7d,
        COUNT(CASE WHEN date_diff('day', prev_event::TIMESTAMP, event_at::TIMESTAMP) <= 30 THEN 1 END) as within_30d,
        MIN(date_diff('day', prev_event::TIMESTAMP, event_at::TIMESTAMP)) as min_days
    FROM ordered_pay
    WHERE prev_event IS NOT NULL;
""").df()
print(res)
