import os
import duckdb
import pandas as pd

data_dir = r"data/raw".replace('\\', '/')
con = duckdb.connect()

# Check payments on clean 25,000 dataset
res = con.execute(f"""
    WITH clean_pay AS (
        SELECT DISTINCT * FROM read_csv_auto('{data_dir}/payments.csv')
    ),
    dedup_pay AS (
        SELECT * EXCLUDE (rn) FROM (
            SELECT *, ROW_NUMBER() OVER(
                PARTITION BY payment_id 
                ORDER BY CASE WHEN payment_reference IS NOT NULL THEN 1 ELSE 2 END, event_at DESC
            ) as rn
            FROM clean_pay
        ) WHERE rn = 1
    )
    SELECT 
        payment_status,
        COUNT(*) as cnt,
        SUM(amount) as sum_amt,
        ROUND(SUM(amount) / 1e7, 4) as sum_cr,
        ROUND(SUM(amount) / 1e7, 2) as sum_cr_2dp
    FROM dedup_pay
    GROUP BY payment_status
    ORDER BY sum_amt DESC;
""").df()

print("Exact status breakdown on golden 25,000 payments:")
print(res)

total_cash = con.execute(f"""
    WITH clean_pay AS (
        SELECT DISTINCT * FROM read_csv_auto('{data_dir}/payments.csv')
    ),
    dedup_pay AS (
        SELECT * EXCLUDE (rn) FROM (
            SELECT *, ROW_NUMBER() OVER(
                PARTITION BY payment_id 
                ORDER BY CASE WHEN payment_reference IS NOT NULL THEN 1 ELSE 2 END, event_at DESC
            ) as rn
            FROM clean_pay
        ) WHERE rn = 1
    )
    SELECT COUNT(*), SUM(amount), ROUND(SUM(amount) / 1e7, 4) as total_cr FROM dedup_pay;
""").fetchall()

print(f"\nTotal golden payments: {total_cash}")
