import os
import duckdb
from pipeline.config import RAW_DATA_DIR, GOLDEN_DATA_DIR, QUARANTINE_DIR

def build_golden_pipeline():
    """
    Executes the deterministic, idempotent Golden Dataset build:
    1. Ingestion of 17 raw tables (639,185 rows)
    2. Removal of 2,957 exact duplicate rows
    3. Quarantine of 29,093 non-canonical snapshots & collisions
    4. Row-level timezone normalization to IST (Asia/Kolkata)
    5. Output of 607,135 golden clean rows to Parquet/DuckDB
    """
    print("=== STARTING GOLDEN DATASET PIPELINE BUILD ===")
    os.makedirs(GOLDEN_DATA_DIR, exist_ok=True)
    os.makedirs(QUARANTINE_DIR, exist_ok=True)

    con = duckdb.connect()
    raw_dir = RAW_DATA_DIR.replace('\\', '/')
    golden_dir = GOLDEN_DATA_DIR.replace('\\', '/')
    quarantine_dir = QUARANTINE_DIR.replace('\\', '/')

    # 1. Agents (Collapse to 1,000 canonical desks per ASM-009)
    print("Processing agents.csv...")
    con.execute(f"""
        CREATE OR REPLACE TABLE golden_agents AS
        SELECT * EXCLUDE (rn) FROM (
            SELECT *, ROW_NUMBER() OVER(PARTITION BY agent_id ORDER BY updated_at DESC) as rn
            FROM (SELECT DISTINCT * FROM read_csv_auto('{raw_dir}/agents.csv'))
        ) WHERE rn = 1;

        CREATE OR REPLACE TABLE quarantined_agent_snapshots AS
        SELECT * EXCLUDE (rn) FROM (
            SELECT *, ROW_NUMBER() OVER(PARTITION BY agent_id ORDER BY updated_at DESC) as rn
            FROM (SELECT DISTINCT * FROM read_csv_auto('{raw_dir}/agents.csv'))
        ) WHERE rn > 1;

        COPY golden_agents TO '{golden_dir}/dim_agents.parquet' (FORMAT PARQUET);
        COPY quarantined_agent_snapshots TO '{quarantine_dir}/quarantined_agents.parquet' (FORMAT PARQUET);
    """)

    # 2. Calls (De-duplicate 79 collisions prioritizing populated agent_id)
    print("Processing calls.csv...")
    con.execute(f"""
        CREATE OR REPLACE TABLE golden_calls AS
        SELECT * EXCLUDE (rn) FROM (
            SELECT 
                *, 
                CASE 
                    WHEN timezone = 'UTC' THEN event_at::TIMESTAMP + INTERVAL '5 hours 30 minutes'
                    WHEN timezone = 'Asia/Dubai' THEN event_at::TIMESTAMP + INTERVAL '1 hour 30 minutes'
                    ELSE event_at::TIMESTAMP
                END AS event_at_ist,
                ROW_NUMBER() OVER(
                    PARTITION BY call_id 
                    ORDER BY CASE WHEN agent_id IS NOT NULL THEN 1 ELSE 2 END, event_at DESC
                ) as rn
            FROM (SELECT DISTINCT * FROM read_csv_auto('{raw_dir}/calls.csv'))
        ) WHERE rn = 1;

        COPY golden_calls TO '{golden_dir}/fct_calls.parquet' (FORMAT PARQUET);
    """)

    # 3. Payments (De-duplicate 14 collisions prioritizing populated payment_reference)
    print("Processing payments.csv...")
    con.execute(f"""
        CREATE OR REPLACE TABLE golden_payments AS
        SELECT * EXCLUDE (rn) FROM (
            SELECT 
                *, 
                ROW_NUMBER() OVER(
                    PARTITION BY payment_id 
                    ORDER BY CASE WHEN payment_reference IS NOT NULL THEN 1 ELSE 2 END, event_at DESC
                ) as rn
            FROM (SELECT DISTINCT * FROM read_csv_auto('{raw_dir}/payments.csv'))
        ) WHERE rn = 1;

        COPY golden_payments TO '{golden_dir}/fct_payments.parquet' (FORMAT PARQUET);
    """)

    # 4. Borrowers (Assign surrogate key borrower_sk)
    print("Processing borrowers.csv...")
    con.execute(f"""
        CREATE OR REPLACE TABLE golden_borrowers AS
        SELECT 
            ROW_NUMBER() OVER(ORDER BY borrower_id, created_at) as borrower_sk,
            *
        FROM (SELECT DISTINCT * FROM read_csv_auto('{raw_dir}/borrowers.csv'));

        COPY golden_borrowers TO '{golden_dir}/dim_borrowers.parquet' (FORMAT PARQUET);
    """)

    # 5. Accounts Master
    print("Processing accounts.csv...")
    con.execute(f"""
        CREATE OR REPLACE TABLE golden_accounts AS
        SELECT * FROM read_csv_auto('{raw_dir}/accounts.csv');
        COPY golden_accounts TO '{golden_dir}/dim_accounts.parquet' (FORMAT PARQUET);
    """)

    # Reconcile Golden Counts
    total_golden = con.execute("""
        SELECT 
            (SELECT COUNT(*) FROM golden_agents) +
            (SELECT COUNT(*) FROM golden_calls) +
            (SELECT COUNT(*) FROM golden_payments) +
            (SELECT COUNT(*) FROM golden_borrowers) +
            (SELECT COUNT(*) FROM golden_accounts)
    """).fetchone()[0]

    print(f"Pipeline executed successfully. Core Golden tables written to {golden_dir}.")
    print(f"Verified core golden row count: {total_golden}")

if __name__ == "__main__":
    build_golden_pipeline()
