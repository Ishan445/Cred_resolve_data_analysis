import os
import glob
import pandas as pd
import numpy as np

data_dir = r"data/raw"

# Declared primary keys from schema/domain
declared_keys = {
    'account_status_history.csv': 'history_id',
    'accounts.csv': 'account_id',
    'agent_sessions.csv': 'session_id',
    'agents.csv': 'agent_id',
    'borrowers.csv': 'borrower_id',
    'call_attempts.csv': 'attempt_id',
    'call_dispositions.csv': 'disposition_id',
    'calls.csv': 'call_id',
    'campaigns.csv': 'campaign_id',
    'complaints.csv': 'complaint_id',
    'daily_targeting.csv': 'target_id',
    'field_visits.csv': 'visit_id',
    'payments.csv': 'payment_id',
    'promises_to_pay.csv': 'ptp_id',
    'sms_events.csv': 'sms_event_id',
    'vendor_telephony.csv': 'vendor_id',
    'whatsapp_events.csv': 'whatsapp_event_id'
}

print("=== RUNNING KEY INTEGRITY AUDIT ACROSS ALL 17 TABLES ===")
summary_rows = []

for filename, key in declared_keys.items():
    filepath = os.path.join(data_dir, filename)
    df = pd.read_csv(filepath, low_memory=False)
    
    # Drop exact duplicates first to get clean rows
    df_clean = df.drop_duplicates()
    clean_rows = len(df_clean)
    unique_keys = df_clean[key].nunique()
    
    key_counts = df_clean[key].value_counts()
    max_group_size = key_counts.max() if len(key_counts) > 0 else 0
    colliding_keys_count = (key_counts > 1).sum()
    colliding_rows_count = key_counts[key_counts > 1].sum()
    
    summary_rows.append({
        'table': filename,
        'key': key,
        'clean_rows': clean_rows,
        'unique_keys': unique_keys,
        'gap': clean_rows - unique_keys,
        'colliding_keys': colliding_keys_count,
        'max_group_size': max_group_size
    })

sum_df = pd.DataFrame(summary_rows)
print(sum_df.to_string(index=False))
