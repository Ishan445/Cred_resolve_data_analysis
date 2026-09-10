import os
import duckdb
import pandas as pd
import numpy as np

data_dir = r"data/raw".replace('\\', '/')
con = duckdb.connect()

print("=== SETTING UP GOLDEN TABLES IN DUCKDB ===")

# Build Golden Tables in DuckDB memory
con.execute(f"""
    -- 2. Golden Agent Sessions
    CREATE OR REPLACE TABLE golden_agent_sessions AS
    SELECT * FROM read_csv_auto('{data_dir}/agent_sessions.csv');

    -- 2. Golden Payments (25,000 rows post exact & id collision dedup)
    CREATE OR REPLACE TABLE golden_payments AS
    SELECT * EXCLUDE (rn) FROM (
        SELECT *, ROW_NUMBER() OVER(
            PARTITION BY payment_id 
            ORDER BY CASE WHEN payment_reference IS NOT NULL THEN 1 ELSE 2 END, event_at DESC
        ) as rn
        FROM (SELECT DISTINCT * FROM read_csv_auto('{data_dir}/payments.csv'))
    ) WHERE rn = 1;

    -- 3. Golden Calls (90,000 rows post exact & id collision dedup)
    CREATE OR REPLACE TABLE golden_calls AS
    SELECT * EXCLUDE (rn) FROM (
        SELECT *, ROW_NUMBER() OVER(
            PARTITION BY call_id 
            ORDER BY CASE WHEN agent_id IS NOT NULL THEN 1 ELSE 2 END, event_at DESC
        ) as rn
        FROM (SELECT DISTINCT * FROM read_csv_auto('{data_dir}/calls.csv'))
    ) WHERE rn = 1;

    -- 4. Golden Call Dispositions (35,000 rows)
    CREATE OR REPLACE TABLE golden_call_dispositions AS
    SELECT * FROM read_csv_auto('{data_dir}/call_dispositions.csv');

    -- 5. Golden Campaigns (120 rows)
    CREATE OR REPLACE TABLE golden_campaigns AS
    SELECT * FROM read_csv_auto('{data_dir}/campaigns.csv');

    -- 6. Golden Daily Targeting (45,000 rows)
    CREATE OR REPLACE TABLE golden_daily_targeting AS
    SELECT * FROM read_csv_auto('{data_dir}/daily_targeting.csv');

    -- 7. Golden Complaints (8,000 rows)
    CREATE OR REPLACE TABLE golden_complaints AS
    SELECT * FROM read_csv_auto('{data_dir}/complaints.csv');

    -- 8. Golden Field Visits (25,000 rows)
    CREATE OR REPLACE TABLE golden_field_visits AS
    SELECT * FROM read_csv_auto('{data_dir}/field_visits.csv');

    -- 9. Golden SMS Events (45,000 rows)
    CREATE OR REPLACE TABLE golden_sms_events AS
    SELECT * FROM read_csv_auto('{data_dir}/sms_events.csv');

    -- 10. Golden WhatsApp Events (60,000 rows post exact dedup)
    CREATE OR REPLACE TABLE golden_whatsapp_events AS
    SELECT DISTINCT * FROM read_csv_auto('{data_dir}/whatsapp_events.csv');

    -- 11. Golden PTP (18,000 rows)
    CREATE OR REPLACE TABLE golden_ptp AS
    SELECT * FROM read_csv_auto('{data_dir}/promises_to_pay.csv');

    -- 12. Golden Account Status History (60,000 rows)
    CREATE OR REPLACE TABLE golden_status_history AS
    SELECT * FROM read_csv_auto('{data_dir}/account_status_history.csv');

    -- 13. Golden Vendor Telephony (15 rows)
    CREATE OR REPLACE TABLE golden_vendor_telephony AS
    SELECT * FROM read_csv_auto('{data_dir}/vendor_telephony.csv');

    -- 14. Golden Accounts (30,000 rows)
    CREATE OR REPLACE TABLE golden_accounts AS
    SELECT * FROM read_csv_auto('{data_dir}/accounts.csv');

    -- 15. Golden Borrowers (30,000 clean rows with surrogate key borrower_sk)
    CREATE OR REPLACE TABLE golden_borrowers AS
    SELECT 
        ROW_NUMBER() OVER(ORDER BY borrower_id, created_at) as borrower_sk,
        *
    FROM (SELECT DISTINCT * FROM read_csv_auto('{data_dir}/borrowers.csv'));

    -- 16. Golden Agents Canonical (1,000 desk rows per ASM-009)
    CREATE OR REPLACE TABLE golden_agents AS
    SELECT * EXCLUDE(rn) FROM (
        SELECT *, ROW_NUMBER() OVER(PARTITION BY agent_id ORDER BY updated_at DESC) as rn
        FROM (SELECT DISTINCT * FROM read_csv_auto('{data_dir}/agents.csv'))
    ) WHERE rn = 1;

    -- 17. Golden Call Attempts (120,000 rows)
    CREATE OR REPLACE TABLE golden_call_attempts AS
    SELECT * FROM read_csv_auto('{data_dir}/call_attempts.csv');
""")

print("Golden tables successfully instantiated in DuckDB.")
