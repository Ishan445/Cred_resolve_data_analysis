import os
import duckdb
import pandas as pd

data_dir = r"data/raw".replace('\\', '/')
con = duckdb.connect()

res = con.execute(f"""
    SELECT 
        COUNT(*) as total_payments,
        COUNT(DISTINCT account_id) as paying_accounts,
        MAX(cnt) as max_payments_per_acc,
        AVG(cnt) as avg_payments_per_acc
    FROM (
        SELECT account_id, COUNT(*) as cnt
        FROM read_csv_auto('{data_dir}/payments.csv')
        GROUP BY account_id
    )
""").df()
print("Account payment distribution:")
print(res)

res2 = con.execute(f"""
    SELECT cnt, COUNT(*) as num_accounts
    FROM (
        SELECT account_id, COUNT(*) as cnt
        FROM read_csv_auto('{data_dir}/payments.csv')
        GROUP BY account_id
    )
    GROUP BY cnt
    ORDER BY cnt;
""").df()
print("\nPayments per account frequency:")
print(res2)

# Check payments on same account: time between them
res3 = con.execute(f"""
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
        MIN(date_diff('day', prev_event::TIMESTAMP, event_at::TIMESTAMP)) as min_days_between_payments,
        AVG(date_diff('day', prev_event::TIMESTAMP, event_at::TIMESTAMP)) as avg_days_between_payments
    FROM ordered_pay
    WHERE prev_event IS NOT NULL;
""").df()
print("\nTime interval between successive payments on the same account:")
print(res3)
