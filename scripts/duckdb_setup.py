import os
import duckdb

data_dir = r"data/raw".replace('\\', '/')

def setup_duckdb(con):
    con.execute(f"""
        CREATE OR REPLACE TABLE golden_accounts AS SELECT * FROM read_csv_auto('{data_dir}/accounts.csv');
        CREATE OR REPLACE TABLE golden_agent_sessions AS SELECT * FROM read_csv_auto('{data_dir}/agent_sessions.csv');
        CREATE OR REPLACE TABLE golden_call_dispositions AS SELECT * FROM read_csv_auto('{data_dir}/call_dispositions.csv');
        CREATE OR REPLACE TABLE golden_campaigns AS SELECT * FROM read_csv_auto('{data_dir}/campaigns.csv');
        CREATE OR REPLACE TABLE golden_daily_targeting AS SELECT * FROM read_csv_auto('{data_dir}/daily_targeting.csv');
        CREATE OR REPLACE TABLE golden_complaints AS SELECT * FROM read_csv_auto('{data_dir}/complaints.csv');
        CREATE OR REPLACE TABLE golden_field_visits AS SELECT * FROM read_csv_auto('{data_dir}/field_visits.csv');
        CREATE OR REPLACE TABLE golden_sms_events AS SELECT * FROM read_csv_auto('{data_dir}/sms_events.csv');
        CREATE OR REPLACE TABLE golden_whatsapp_events AS SELECT DISTINCT * FROM read_csv_auto('{data_dir}/whatsapp_events.csv');
        CREATE OR REPLACE TABLE golden_ptp AS SELECT * FROM read_csv_auto('{data_dir}/promises_to_pay.csv');
        CREATE OR REPLACE TABLE golden_status_history AS SELECT * FROM read_csv_auto('{data_dir}/account_status_history.csv');
        CREATE OR REPLACE TABLE golden_vendor_telephony AS SELECT * FROM read_csv_auto('{data_dir}/vendor_telephony.csv');
        
        CREATE OR REPLACE TABLE golden_payments AS
        SELECT * EXCLUDE (rn) FROM (
            SELECT *, ROW_NUMBER() OVER(PARTITION BY payment_id ORDER BY CASE WHEN payment_reference IS NOT NULL THEN 1 ELSE 2 END, event_at DESC) as rn
            FROM (SELECT DISTINCT * FROM read_csv_auto('{data_dir}/payments.csv'))
        ) WHERE rn = 1;

        CREATE OR REPLACE TABLE golden_calls AS
        SELECT * EXCLUDE (rn) FROM (
            SELECT *, ROW_NUMBER() OVER(PARTITION BY call_id ORDER BY CASE WHEN agent_id IS NOT NULL THEN 1 ELSE 2 END, event_at DESC) as rn
            FROM (SELECT DISTINCT * FROM read_csv_auto('{data_dir}/calls.csv'))
        ) WHERE rn = 1;
    """)
