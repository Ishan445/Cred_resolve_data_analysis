import duckdb
import os

data_dir = r"data/raw".replace('\\', '/')

con = duckdb.connect()

print("Testing DuckDB query on raw_payments...")
res = con.execute(f"""
    SELECT 
        COUNT(*) AS total_rows,
        COUNT(DISTINCT payment_id) AS uniq_payment_ids,
        COUNT(DISTINCT payment_reference) AS uniq_refs,
        SUM(amount) AS gross_cash,
        SUM(CASE WHEN payment_status = 'SUCCESS' THEN amount ELSE 0 END) AS success_cash
    FROM read_csv_auto('{data_dir}/payments.csv')
""").df()
print(res)

print("\nTesting DuckDB query on date boundaries...")
res_dates = con.execute(f"""
    SELECT 'calls' AS tbl, MIN(event_at) AS min_dt, MAX(event_at) AS max_dt FROM read_csv_auto('{data_dir}/calls.csv')
    UNION ALL
    SELECT 'payments', MIN(event_at), MAX(event_at) FROM read_csv_auto('{data_dir}/payments.csv')
    UNION ALL
    SELECT 'complaints', MIN(event_at), MAX(event_at) FROM read_csv_auto('{data_dir}/complaints.csv')
    UNION ALL
    SELECT 'promises_to_pay', MIN(event_at), MAX(event_at) FROM read_csv_auto('{data_dir}/promises_to_pay.csv')
""").df()
print(res_dates)
