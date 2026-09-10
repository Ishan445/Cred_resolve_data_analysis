import os
import duckdb
import pandas as pd

data_dir = r"data/raw".replace('\\', '/')
con = duckdb.connect()
exec(open(r"scripts\setup_golden_duckdb.py").read())

con.execute("""
    CREATE OR REPLACE TABLE all_touchpoints AS
    SELECT account_id, event_at::TIMESTAMP as touch_at, 'CALL' as channel FROM golden_calls
    UNION ALL
    SELECT account_id, event_at::TIMESTAMP, 'FIELD' FROM golden_field_visits
    UNION ALL
    SELECT account_id, event_at::TIMESTAMP, 'WHATSAPP' FROM golden_whatsapp_events
    UNION ALL
    SELECT account_id, event_at::TIMESTAMP, 'SMS' FROM golden_sms_events;
""")

res = con.execute("""
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
        COUNT(p.payment_id) as total_success_payments,
        COUNT(m.payment_id) as touchpoint_attributed_payments,
        COUNT(p.payment_id) - COUNT(m.payment_id) as organic_direct_payments,
        ROUND((COUNT(p.payment_id) - COUNT(m.payment_id))*100.0 / COUNT(p.payment_id), 2) as organic_pct
    FROM success_payments p
    LEFT JOIN (SELECT DISTINCT payment_id FROM matched_touchpoints WHERE rn = 1) m
      ON p.payment_id = m.payment_id;
""").df()
print("Touchpoint vs Organic Payments (14-day lookback):")
print(res)
