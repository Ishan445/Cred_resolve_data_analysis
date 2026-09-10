import os
import duckdb
import pandas as pd

data_dir = r"data/raw".replace('\\', '/')
con = duckdb.connect()

# Let's inspect duplicate payment_reference
res = con.execute(f"""
    WITH clean_pay AS (
        SELECT DISTINCT * FROM read_csv_auto('{data_dir}/payments.csv')
    ),
    dedup_id AS (
        SELECT * EXCLUDE (rn) FROM (
            SELECT *, ROW_NUMBER() OVER(PARTITION BY payment_id ORDER BY CASE WHEN payment_reference IS NOT NULL THEN 1 ELSE 2 END, event_at DESC) as rn
            FROM clean_pay
        ) WHERE rn = 1
    )
    SELECT payment_reference, COUNT(*) as cnt, COUNT(DISTINCT account_id) as uniq_accs, COUNT(DISTINCT amount) as uniq_amts, COUNT(DISTINCT payment_status) as uniq_statuses
    FROM dedup_id
    WHERE payment_reference IS NOT NULL
    GROUP BY payment_reference
    HAVING COUNT(*) > 1
    ORDER BY cnt DESC
    LIMIT 10;
""").df()
print("Top 10 duplicate payment_reference groups:")
print(res)

# Let's see an example of one duplicate payment_reference
sample_ref = res.iloc[0]['payment_reference']
sample_rows = con.execute(f"""
    SELECT * FROM read_csv_auto('{data_dir}/payments.csv') WHERE payment_reference = '{sample_ref}'
""").df()
print(f"\nExample rows for payment_reference = {sample_ref}:")
print(sample_rows)
