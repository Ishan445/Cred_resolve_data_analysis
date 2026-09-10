import duckdb
import pandas as pd

# Setup Golden Tables
exec(open(r"scripts/setup_golden_duckdb.py").read())

print("=== COMPUTING MUTUALLY EXCLUSIVE LAST-TOUCH ATTRIBUTION (7D LOOKBACK) ===")

query_last_touch = """
WITH success_payments AS (
    SELECT payment_id, account_id, amount, event_at::TIMESTAMP as paid_at
    FROM golden_payments
    WHERE payment_status = 'SUCCESS'
),
all_touches AS (
    SELECT account_id, event_at::TIMESTAMP as touch_at, 'Human Voice (Calls)' as channel, 1 as priority
    FROM golden_calls
    UNION ALL
    SELECT account_id, event_at::TIMESTAMP as touch_at, 'WhatsApp Interaction' as channel, 2 as priority
    FROM golden_whatsapp_events
    UNION ALL
    SELECT account_id, event_at::TIMESTAMP as touch_at, 'SMS Reminder' as channel, 3 as priority
    FROM golden_sms_events
    UNION ALL
    SELECT account_id, event_at::TIMESTAMP as touch_at, 'Field Visit' as channel, 4 as priority
    FROM golden_field_visits
),
attributed_touches AS (
    SELECT 
        p.payment_id,
        p.amount,
        t.channel,
        t.touch_at,
        ROW_NUMBER() OVER(
            PARTITION BY p.payment_id 
            ORDER BY t.touch_at DESC, t.priority ASC
        ) as rn
    FROM success_payments p
    JOIN all_touches t 
      ON p.account_id = t.account_id
     AND t.touch_at <= p.paid_at
     AND t.touch_at >= p.paid_at - INTERVAL '7 days'
),
final_attribution AS (
    SELECT 
        p.payment_id,
        p.amount,
        COALESCE(a.channel, 'Pure Organic (No touch in 7d)') as final_channel
    FROM success_payments p
    LEFT JOIN (SELECT * FROM attributed_touches WHERE rn = 1) a
      ON p.payment_id = a.payment_id
)
SELECT 
    final_channel as channel,
    COUNT(*) as payment_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM success_payments), 2) as pct_of_payments,
    ROUND(SUM(amount) / 1e7, 2) as cash_cr,
    ROUND(SUM(amount) * 100.0 / (SELECT SUM(amount) FROM success_payments), 2) as pct_of_cash
FROM final_attribution
GROUP BY final_channel
ORDER BY cash_cr DESC;
"""

df_last_touch = con.execute(query_last_touch).df()
print("\n--- Mutually Exclusive Last-Touch Attribution (7-Day Lookback) ---")
print(df_last_touch.to_markdown(index=False))

total_cash = df_last_touch['cash_cr'].sum()
total_pct = df_last_touch['pct_of_cash'].sum()
total_cnt = df_last_touch['payment_count'].sum()
print(f"\nTotal Cash: ₹{total_cash:.2f} Cr, Total Pct: {total_pct:.2f}%, Total Payments: {total_cnt}")
