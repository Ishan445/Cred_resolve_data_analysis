import os
import duckdb
import pandas as pd
import numpy as np

data_dir = r"data/raw".replace('\\', '/')
output_dir = r"data\golden".replace('\\', '/')
rejected_dir = r"data\rejected".replace('\\', '/')

os.makedirs(output_dir, exist_ok=True)
os.makedirs(rejected_dir, exist_ok=True)

con = duckdb.connect()

print("=== STARTING PHASE 1 GOLDEN DATASET BUILD ===")

# -------------------------------------------------------------
# 1. CLEAN & RESOLVE AGENTS (Lookup desk layer: 1,000 canonical rows)
# -------------------------------------------------------------
print("\n--- 1. Building dim_agents ---")
con.execute(f"""
    CREATE OR REPLACE TABLE raw_agents AS 
    SELECT * FROM read_csv_auto('{data_dir}/agents.csv');
    
    -- Exact duplicate count in raw_agents
    CREATE OR REPLACE TABLE clean_agents_dedup AS 
    SELECT DISTINCT * FROM raw_agents;
    
    -- Collapse to 1 row per agent_id using latest updated_at
    CREATE OR REPLACE TABLE golden_agents AS
    SELECT * EXCLUDE (rn) FROM (
        SELECT *,
            ROW_NUMBER() OVER(PARTITION BY agent_id ORDER BY updated_at DESC, joined_at DESC) AS rn
        FROM clean_agents_dedup
    ) WHERE rn = 1;
""")
agents_raw = con.execute("SELECT COUNT(*) FROM raw_agents").fetchone()[0]
agents_clean = con.execute("SELECT COUNT(*) FROM clean_agents_dedup").fetchone()[0]
agents_golden = con.execute("SELECT COUNT(*) FROM golden_agents").fetchone()[0]
print(f"agents: Raw={agents_raw}, Clean={agents_clean}, Golden (Resolved 1:1)={agents_golden}")

# -------------------------------------------------------------
# 2. CLEAN & DEDUPLICATE CALLS (90,000 canonical calls)
# -------------------------------------------------------------
print("\n--- 2. Building fct_calls ---")
con.execute(f"""
    CREATE OR REPLACE TABLE raw_calls AS 
    SELECT * FROM read_csv_auto('{data_dir}/calls.csv');
    
    -- Step A: Exact deduplication (removes 1,271 exact duplicates)
    CREATE OR REPLACE TABLE clean_calls_exact AS 
    SELECT DISTINCT * FROM raw_calls;
    
    -- Step B: Key deduplication on call_id (prefer agent_id IS NOT NULL, then latest event_at)
    -- Capture rejected rows
    CREATE OR REPLACE TABLE rejected_calls AS
    SELECT * EXCLUDE (rn) FROM (
        SELECT *,
            ROW_NUMBER() OVER(
                PARTITION BY call_id 
                ORDER BY CASE WHEN agent_id IS NOT NULL THEN 1 ELSE 2 END ASC, event_at DESC
            ) AS rn
        FROM clean_calls_exact
    ) WHERE rn > 1;
    
    -- Golden calls
    CREATE OR REPLACE TABLE golden_calls AS
    SELECT * EXCLUDE (rn) FROM (
        SELECT *,
            ROW_NUMBER() OVER(
                PARTITION BY call_id 
                ORDER BY CASE WHEN agent_id IS NOT NULL THEN 1 ELSE 2 END ASC, event_at DESC
            ) AS rn
        FROM clean_calls_exact
    ) WHERE rn = 1;
""")
calls_raw = con.execute("SELECT COUNT(*) FROM raw_calls").fetchone()[0]
calls_exact_clean = con.execute("SELECT COUNT(*) FROM clean_calls_exact").fetchone()[0]
calls_rejected = con.execute("SELECT COUNT(*) FROM rejected_calls").fetchone()[0]
calls_golden = con.execute("SELECT COUNT(*) FROM golden_calls").fetchone()[0]
print(f"calls: Raw={calls_raw}, Exact Clean={calls_exact_clean}, Rejected Collisions={calls_rejected}, Golden={calls_golden}")

# -------------------------------------------------------------
# 3. CLEAN & DEDUPLICATE PAYMENTS (25,000 canonical payments)
# -------------------------------------------------------------
print("\n--- 3. Building fct_payments ---")
con.execute(f"""
    CREATE OR REPLACE TABLE raw_payments AS 
    SELECT * FROM read_csv_auto('{data_dir}/payments.csv');
    
    -- Step A: Exact deduplication (removes 486 exact duplicates)
    CREATE OR REPLACE TABLE clean_payments_exact AS 
    SELECT DISTINCT * FROM raw_payments;
    
    -- Step B: Key deduplication on payment_id (keep populated payment_reference)
    CREATE OR REPLACE TABLE rejected_payments_id_coll AS
    SELECT * EXCLUDE (rn) FROM (
        SELECT *,
            ROW_NUMBER() OVER(
                PARTITION BY payment_id 
                ORDER BY CASE WHEN payment_reference IS NOT NULL THEN 1 ELSE 2 END ASC, event_at DESC
            ) AS rn
        FROM clean_payments_exact
    ) WHERE rn > 1;
    
    CREATE OR REPLACE TABLE payments_unique_id AS
    SELECT * EXCLUDE (rn) FROM (
        SELECT *,
            ROW_NUMBER() OVER(
                PARTITION BY payment_id 
                ORDER BY CASE WHEN payment_reference IS NOT NULL THEN 1 ELSE 2 END ASC, event_at DESC
            ) AS rn
        FROM clean_payments_exact
    ) WHERE rn = 1;
""")

pay_raw = con.execute("SELECT COUNT(*) FROM raw_payments").fetchone()[0]
pay_exact_clean = con.execute("SELECT COUNT(*) FROM clean_payments_exact").fetchone()[0]
pay_id_coll = con.execute("SELECT COUNT(*) FROM rejected_payments_id_coll").fetchone()[0]
pay_uniq_id = con.execute("SELECT COUNT(*) FROM payments_unique_id").fetchone()[0]
print(f"payments: Raw={pay_raw}, Exact Clean={pay_exact_clean}, ID Collisions Rejected={pay_id_coll}, Unique ID Rows={pay_uniq_id}")

# -------------------------------------------------------------
# 4. PAYMENT RETRY DEDUPLICATION & MULTI-WINDOW SENSITIVITY
# -------------------------------------------------------------
print("\n--- 4. Payment Deduplication Sensitivity Analysis ---")

# Let's inspect duplicate payment_reference and retry intervals
df_pay = con.execute("SELECT * FROM payments_unique_id").df()
df_pay['event_at'] = pd.to_datetime(df_pay['event_at'])
df_pay = df_pay.sort_values(['account_id', 'amount', 'event_at'])

# Compute time diff to previous payment for same account & same amount
df_pay['prev_event_at'] = df_pay.groupby(['account_id', 'amount'])['event_at'].shift(1)
df_pay['diff_seconds'] = (df_pay['event_at'] - df_pay['prev_event_at']).dt.total_seconds()

# Check counts under different windows
print("Payment retry intervals across identical (account_id, amount):")
for window_name, secs in [('10 Minutes', 600), ('1 Hour', 3600), ('24 Hours', 86400)]:
    retries = df_pay[df_pay['diff_seconds'] <= secs]
    retry_amt = retries['amount'].sum()
    retry_success = retries[retries['payment_status'] == 'SUCCESS']
    print(f"  Threshold <= {window_name:<10}: {len(retries):>4} rows (INR {retry_amt/1e7:>6.2f} Cr gross), of which SUCCESS: {len(retry_success):>4} rows (INR {retry_success['amount'].sum()/1e7:>6.2f} Cr)")

# Let's check duplicate payment_reference
ref_counts = df_pay['payment_reference'].dropna().value_counts()
dup_refs = ref_counts[ref_counts > 1]
print(f"\nUnique payment_reference values: {df_pay['payment_reference'].nunique()}")
print(f"payment_reference appearing > 1 time: {len(dup_refs)} refs, total rows = {dup_refs.sum()}")

# -------------------------------------------------------------
# 5. CLEAN BORROWERS (Surrogate Key borrower_sk)
# -------------------------------------------------------------
print("\n--- 5. Building dim_borrowers ---")
con.execute(f"""
    CREATE OR REPLACE TABLE raw_borrowers AS 
    SELECT * FROM read_csv_auto('{data_dir}/borrowers.csv');
    
    CREATE OR REPLACE TABLE clean_borrowers_exact AS 
    SELECT DISTINCT * FROM raw_borrowers;
    
    CREATE OR REPLACE TABLE golden_borrowers AS 
    SELECT 
        ROW_NUMBER() OVER() AS borrower_sk,
        *
    FROM clean_borrowers_exact;
""")
bor_raw = con.execute("SELECT COUNT(*) FROM raw_borrowers").fetchone()[0]
bor_clean = con.execute("SELECT COUNT(*) FROM clean_borrowers_exact").fetchone()[0]
print(f"borrowers: Raw={bor_raw}, Clean={bor_clean}, Assigned borrower_sk.")

# -------------------------------------------------------------
# 6. TIMEZONE NORMALIZATION & EVENT FEEDS STANDARDIZATION
# -------------------------------------------------------------
print("\n--- 6. Timezone Standardization (IST & UTC) ---")
# Check timezones in calls
tz_counts = con.execute("SELECT timezone, COUNT(*) FROM golden_calls GROUP BY timezone").fetchall()
print("Calls timezone breakdown:", tz_counts)

# Let's write out the verification summary
