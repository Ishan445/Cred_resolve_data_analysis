import os
import duckdb
import pandas as pd

data_dir = r"data/raw".replace('\\', '/')
con = duckdb.connect()

res = con.execute(f"""
    WITH dedup_pay AS (
        SELECT * EXCLUDE (rn) FROM (
            SELECT *, ROW_NUMBER() OVER(
                PARTITION BY payment_id 
                ORDER BY CASE WHEN payment_reference IS NOT NULL THEN 1 ELSE 2 END, event_at DESC
            ) as rn
            FROM (SELECT DISTINCT * FROM read_csv_auto('{data_dir}/payments.csv'))
        ) WHERE rn = 1
    ),
    ordered_pay AS (
        SELECT 
            payment_id,
            account_id,
            borrower_id,
            event_at,
            amount,
            payment_status,
            payment_reference,
            LAG(payment_id) OVER(PARTITION BY account_id ORDER BY event_at) as prev_payment_id,
            LAG(event_at) OVER(PARTITION BY account_id ORDER BY event_at) as prev_event,
            LAG(amount) OVER(PARTITION BY account_id ORDER BY event_at) as prev_amount,
            LAG(payment_status) OVER(PARTITION BY account_id ORDER BY event_at) as prev_status,
            LAG(payment_reference) OVER(PARTITION BY account_id ORDER BY event_at) as prev_ref
        FROM dedup_pay
    )
    SELECT 
        payment_id,
        account_id,
        event_at,
        prev_event,
        date_diff('second', prev_event::TIMESTAMP, event_at::TIMESTAMP) as diff_seconds,
        amount,
        prev_amount,
        payment_status,
        prev_status,
        payment_reference,
        prev_ref
    FROM ordered_pay
    WHERE prev_event IS NOT NULL AND date_diff('second', prev_event::TIMESTAMP, event_at::TIMESTAMP) <= 86400
    ORDER BY diff_seconds;
""").df()

print(f"Total payment pairs within 24 hours on same account: {len(res)}")
print(res.to_string())
