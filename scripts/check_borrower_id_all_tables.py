import os
import pandas as pd

data_dir = r"data/raw"
tables = ['accounts', 'borrowers', 'calls', 'call_attempts', 'call_dispositions', 'field_visits', 'payments', 'promises_to_pay', 'sms_events', 'whatsapp_events', 'complaints', 'account_status_history']

print("Distinct borrower_id count in each table:")
for t in tables:
    df = pd.read_csv(os.path.join(data_dir, f"{t}.csv"), low_memory=False)
    if 'borrower_id' in df.columns:
        print(f"{t:<25}: {df['borrower_id'].nunique()} unique, {df['borrower_id'].isnull().sum()} nulls")
