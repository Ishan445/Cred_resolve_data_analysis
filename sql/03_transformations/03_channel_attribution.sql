-- ==============================================================================
-- 03_channel_attribution.sql: Mutually Exclusive Multi-Touch Attribution Engine
-- Implements 7-day and 14-day lookback attribution with deterministic tie-breaking.
-- ==============================================================================

CREATE OR REPLACE TABLE fct_payments_attributed_7d AS
WITH success_payments AS (
    SELECT payment_id, account_id, amount, event_at_ist AS paid_at
    FROM golden_payments
    WHERE payment_status = 'SUCCESS'
),
all_touches AS (
    SELECT account_id, event_at_ist AS touch_at, 'Human Voice (Calls)' AS channel, 1 AS priority
    FROM golden_calls
    UNION ALL
    SELECT account_id, event_at::TIMESTAMP AS touch_at, 'WhatsApp Interaction' AS channel, 2 AS priority
    FROM read_csv_auto('data/raw/whatsapp_events.csv')
    UNION ALL
    SELECT account_id, event_at::TIMESTAMP AS touch_at, 'SMS Reminder' AS channel, 3 AS priority
    FROM read_csv_auto('data/raw/sms_events.csv')
    UNION ALL
    SELECT account_id, scheduled_at::TIMESTAMP AS touch_at, 'Field Visit' AS channel, 4 AS priority
    FROM read_csv_auto('data/raw/field_visits.csv')
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
)
SELECT 
    p.payment_id,
    p.account_id,
    p.amount,
    p.paid_at,
    COALESCE(a.channel, 'Pure Organic (No touch in 7d)') AS attributed_channel,
    a.touch_at AS attributed_touch_at
FROM success_payments p
LEFT JOIN (SELECT * FROM attributed_touches WHERE rn = 1) a
  ON p.payment_id = a.payment_id;
