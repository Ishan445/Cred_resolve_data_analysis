-- ==============================================================================
-- 01_staging_ddl.sql: Staging & Type Casting Layer
-- Standardizes all raw event tables into typed columnar models with IST timestamps.
-- ==============================================================================

-- 1. Staging Calls with Row-Level Timezone Normalization to IST
CREATE OR REPLACE TABLE stg_calls AS
SELECT 
    call_id,
    account_id,
    borrower_id,
    agent_id,
    vendor_id,
    campaign_id,
    call_status,
    duration_sec,
    timezone as raw_timezone,
    event_at as raw_event_at,
    CASE 
        WHEN timezone = 'UTC' THEN event_at::TIMESTAMP + INTERVAL '5 hours 30 minutes'
        WHEN timezone = 'Asia/Dubai' THEN event_at::TIMESTAMP + INTERVAL '1 hour 30 minutes'
        ELSE event_at::TIMESTAMP
    END AS event_at_ist
FROM read_csv_auto('data/raw/calls.csv');

-- 2. Staging Payments
CREATE OR REPLACE TABLE stg_payments AS
SELECT 
    payment_id,
    account_id,
    amount,
    payment_status,
    payment_channel,
    payment_reference,
    event_at::TIMESTAMP AS event_at_ist
FROM read_csv_auto('data/raw/payments.csv');

-- 3. Staging Accounts Master
CREATE OR REPLACE TABLE stg_accounts AS
SELECT 
    account_id,
    borrower_id,
    loan_type,
    principal_amount,
    outstanding_amount,
    dpd,
    risk_segment,
    status,
    opened_at::TIMESTAMP AS opened_at
FROM read_csv_auto('data/raw/accounts.csv');
