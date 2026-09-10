import os
import duckdb
import pandas as pd

data_dir = r"data/raw".replace('\\', '/')
con = duckdb.connect()

# Set up tables
exec(open(r"scripts\setup_golden_duckdb.py").read())

print("=== DEEP DIVE INTO FORENSIC D (VENDOR DISPOSITION DRIFT) ===")
# Check if disposition codes changed over months or across versions
res = con.execute("""
    SELECT 
        d.disposition_version,
        d.disposition_code,
        COUNT(*) as cnt,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY d.disposition_version), 2) as pct
    FROM golden_call_dispositions d
    GROUP BY d.disposition_version, d.disposition_code
    ORDER BY d.disposition_version, cnt DESC;
""").df()
print(res.to_markdown(index=False))

print("\n=== DEEP DIVE INTO FORENSIC B (ATTRIBUTION LOOKBACK WINDOWS) ===")
# Attribute payments to channels across 1d, 3d, 7d, 14d lookback
con.execute("""
    CREATE OR REPLACE TABLE all_touchpoints AS
    SELECT account_id, event_at::TIMESTAMP as touch_at, 'CALL' as channel, call_status as status FROM golden_calls
    UNION ALL
    SELECT account_id, event_at::TIMESTAMP, 'FIELD', outcome FROM golden_field_visits
    UNION ALL
    SELECT account_id, event_at::TIMESTAMP, 'WHATSAPP', event_type FROM golden_whatsapp_events
    UNION ALL
    SELECT account_id, event_at::TIMESTAMP, 'SMS', event_type FROM golden_sms_events;
""")

res_attr = con.execute("""
    WITH success_payments AS (
        SELECT payment_id, account_id, event_at::TIMESTAMP as payment_at, amount
        FROM golden_payments
        WHERE payment_status = 'SUCCESS'
    ),
    matched_touchpoints AS (
        SELECT 
            p.payment_id,
            p.amount,
            t.channel,
            date_diff('hour', t.touch_at, p.payment_at) as hours_diff,
            ROW_NUMBER() OVER(PARTITION BY p.payment_id ORDER BY t.touch_at DESC) as rn
        FROM success_payments p
        JOIN all_touchpoints t 
          ON p.account_id = t.account_id 
         AND t.touch_at <= p.payment_at
         AND t.touch_at >= p.payment_at - INTERVAL '14 days'
    )
    SELECT 
        channel,
        COUNT(*) as total_attributed_payments_14d,
        COUNT(CASE WHEN hours_diff <= 24 THEN 1 END) as payments_1d,
        COUNT(CASE WHEN hours_diff <= 72 THEN 1 END) as payments_3d,
        COUNT(CASE WHEN hours_diff <= 168 THEN 1 END) as payments_7d,
        COUNT(CASE WHEN hours_diff <= 336 THEN 1 END) as payments_14d,
        ROUND(SUM(CASE WHEN hours_diff <= 168 THEN amount ELSE 0 END)/1e7, 2) as cash_7d_cr
    FROM matched_touchpoints
    WHERE rn = 1
    GROUP BY channel
    ORDER BY total_attributed_payments_14d DESC;
""").df()
print(res_attr.to_markdown(index=False))

total_success_p = con.execute("SELECT COUNT(*), ROUND(SUM(amount)/1e7, 2) FROM golden_payments WHERE payment_status = 'SUCCESS'").fetchone()
print(f"Total Successful Payments: {total_success_p[0]} (INR {total_success_p[1]} Cr)")
