-- ==============================================================================
-- 04_golden_marts.sql: Dimensional Fact & Dimension Marts
-- Wide analytical models for executive analysis and business intelligence.
-- ==============================================================================

-- 1. Fact Payments (Audited Realized vs Gross)
CREATE OR REPLACE TABLE fct_payments AS
SELECT 
    payment_id,
    account_id,
    amount,
    payment_status,
    payment_channel,
    payment_reference,
    event_at_ist,
    STRFTIME(event_at_ist, '%Y-%m') AS payment_month,
    CASE WHEN payment_status = 'SUCCESS' THEN amount ELSE 0 END AS success_cash,
    CASE WHEN payment_status = 'REVERSED' THEN amount ELSE 0 END AS reversed_cash,
    CASE 
        WHEN payment_status = 'SUCCESS' THEN amount 
        WHEN payment_status = 'REVERSED' THEN -amount 
        ELSE 0 
    END AS net_realized_cash
FROM golden_payments;

-- 2. Fact Touchpoints Lineage
CREATE OR REPLACE TABLE fct_touchpoints AS
SELECT 
    call_id AS touchpoint_id,
    account_id,
    agent_id,
    'CALL' AS channel,
    call_status AS interaction_status,
    duration_sec,
    event_at_ist AS event_at
FROM golden_calls
UNION ALL
SELECT 
    whatsapp_event_id AS touchpoint_id,
    account_id,
    NULL AS agent_id,
    'WHATSAPP' AS channel,
    event_type AS interaction_status,
    NULL AS duration_sec,
    event_at::TIMESTAMP AS event_at
FROM read_csv_auto('data/raw/whatsapp_events.csv')
UNION ALL
SELECT 
    sms_event_id AS touchpoint_id,
    account_id,
    NULL AS agent_id,
    'SMS' AS channel,
    status AS interaction_status,
    NULL AS duration_sec,
    event_at::TIMESTAMP AS event_at
FROM read_csv_auto('data/raw/sms_events.csv')
UNION ALL
SELECT 
    visit_id AS touchpoint_id,
    account_id,
    agent_id,
    'FIELD' AS channel,
    outcome AS interaction_status,
    NULL AS duration_sec,
    scheduled_at::TIMESTAMP AS event_at
FROM read_csv_auto('data/raw/field_visits.csv');
