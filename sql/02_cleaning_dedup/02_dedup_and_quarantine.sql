-- ==============================================================================
-- 02_dedup_and_quarantine.sql: Idempotent Deduplication & Quarantine Rules
-- Enforces Phase 1 resolution rules across payments, calls, agents, and borrowers.
-- ==============================================================================

-- 1. Golden Payments (Deduplicate on payment_id, keeping populated payment_reference)
CREATE OR REPLACE TABLE golden_payments AS
SELECT * EXCLUDE (rn) FROM (
    SELECT 
        *, 
        ROW_NUMBER() OVER(
            PARTITION BY payment_id 
            ORDER BY CASE WHEN payment_reference IS NOT NULL THEN 1 ELSE 2 END, event_at_ist DESC
        ) as rn
    FROM (SELECT DISTINCT * FROM stg_payments)
) WHERE rn = 1;

-- 2. Golden Calls (Deduplicate on call_id, prioritizing populated agent_id)
CREATE OR REPLACE TABLE golden_calls AS
SELECT * EXCLUDE (rn) FROM (
    SELECT 
        *, 
        ROW_NUMBER() OVER(
            PARTITION BY call_id 
            ORDER BY CASE WHEN agent_id IS NOT NULL THEN 1 ELSE 2 END, event_at_ist DESC
        ) as rn
    FROM (SELECT DISTINCT * FROM stg_calls)
) WHERE rn = 1;

-- 3. Canonical Desks (Per ASM-009, collapse agents to 1,000 canonical desk lookups)
CREATE OR REPLACE TABLE dim_desks AS
SELECT * EXCLUDE (rn) FROM (
    SELECT 
        agent_id,
        vendor_id,
        team,
        status,
        updated_at,
        ROW_NUMBER() OVER(PARTITION BY agent_id ORDER BY updated_at DESC) as rn
    FROM (SELECT DISTINCT * FROM read_csv_auto('data/raw/agents.csv'))
) WHERE rn = 1;

-- 4. Borrowers Profile (Surrogate Key generation to isolate borrower_id collision)
CREATE OR REPLACE TABLE dim_borrowers AS
SELECT 
    ROW_NUMBER() OVER(ORDER BY borrower_id, created_at) AS borrower_sk,
    *
FROM (SELECT DISTINCT * FROM read_csv_auto('data/raw/borrowers.csv'));
