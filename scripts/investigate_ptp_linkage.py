import os
import duckdb
import pandas as pd
from duckdb_setup import setup_duckdb

con = duckdb.connect()
setup_duckdb(con)

# Check PTP payment matching with varying windows (14 days, 30 days) and without amount restrictions
res = con.execute("""
    WITH ptp_base AS (
        SELECT 
            ptp_id,
            account_id,
            event_at::TIMESTAMP as ptp_at,
            promised_date::TIMESTAMP as promised_at,
            promised_amount,
            status as raw_ptp_status
        FROM golden_ptp
    )
    SELECT 
        raw_ptp_status,
        COUNT(*) as total_ptps,
        COUNT(CASE WHEN pay.payment_id IS NOT NULL THEN 1 END) as any_payment_after_ptp,
        COUNT(CASE WHEN pay.payment_id IS NOT NULL AND pay.payment_status = 'SUCCESS' THEN 1 END) as success_payment_after_ptp,
        COUNT(CASE WHEN pay.payment_id IS NOT NULL AND pay.payment_status = 'SUCCESS' 
                   AND pay.event_at::TIMESTAMP BETWEEN p.ptp_at AND p.promised_at + INTERVAL '7 days' THEN 1 END) as success_within_7d_window
    FROM ptp_base p
    LEFT JOIN golden_payments pay 
      ON p.account_id = pay.account_id 
     AND pay.event_at::TIMESTAMP >= p.ptp_at
    GROUP BY raw_ptp_status;
""").df()

print("PTP vs Payment matching across broader windows:")
print(res.to_markdown(index=False))

# Check distribution of promised_amount in PTP vs amount in payments
print("\nDistribution of promised_amount vs payment amount:")
print(con.execute("SELECT MIN(promised_amount), AVG(promised_amount), MAX(promised_amount) FROM golden_ptp").df())
print(con.execute("SELECT MIN(amount), AVG(amount), MAX(amount) FROM golden_payments").df())
