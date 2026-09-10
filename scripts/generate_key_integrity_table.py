import os
import pandas as pd

data_dir = r"data/raw"

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

verdicts = {
    'account_status_history.csv': 'OK (1:1)',
    'accounts.csv': 'OK (1:1)',
    'agent_sessions.csv': 'OK (1:1)',
    'agents.csv': 'COLLISION — MULTIPLE ROLES/SNAPSHOTS PER AGENT (needs resolution)',
    'borrowers.csv': 'COLLISION — SAME KEY DIFFERENT ENTITY (synthetic ID collision / needs resolution)',
    'call_attempts.csv': 'OK (1:1)',
    'call_dispositions.csv': 'OK (1:1)',
    'calls.csv': 'COLLISION — NEAR-DUPLICATE RETRY/LOGGING INGESTION (needs resolution)',
    'campaigns.csv': 'OK (1:1)',
    'complaints.csv': 'OK (1:1)',
    'daily_targeting.csv': 'OK (1:1)',
    'field_visits.csv': 'OK (1:1)',
    'payments.csv': 'COLLISION — INGESTION RETRY WITH NULL TXN REF (needs resolution)',
    'promises_to_pay.csv': 'OK (1:1)',
    'sms_events.csv': 'OK (1:1)',
    'vendor_telephony.csv': 'OK (1:1)',
    'whatsapp_events.csv': 'OK (1:1)'
}

results = []
for filename, key in declared_keys.items():
    filepath = os.path.join(data_dir, filename)
    df = pd.read_csv(filepath, low_memory=False).drop_duplicates()
    clean_rows = len(df)
    uniq_keys = df[key].nunique()
    max_grp = df[key].value_counts().max() if len(df) > 0 else 0
    results.append({
        'Table': filename.replace('.csv', ''),
        'Declared Key': key,
        'Clean Rows': clean_rows,
        'Unique Key Values': uniq_keys,
        'Max Group Size': max_grp,
        'Verdict': verdicts[filename]
    })

res_df = pd.DataFrame(results)
print(res_df.to_markdown(index=False))
