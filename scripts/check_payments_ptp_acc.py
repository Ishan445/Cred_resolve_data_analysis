import os
import pandas as pd

data_dir = r"data/raw"
df_pay = pd.read_csv(os.path.join(data_dir, "payments.csv"), low_memory=False).drop_duplicates()
df_acc = pd.read_csv(os.path.join(data_dir, "accounts.csv"), low_memory=False).drop_duplicates()
df_ptp = pd.read_csv(os.path.join(data_dir, "promises_to_pay.csv"), low_memory=False).drop_duplicates()

print(f"Payments total: {len(df_pay)}, unique account_id: {df_pay['account_id'].nunique()}")
print(f"PTP total: {len(df_ptp)}, unique account_id: {df_ptp['account_id'].nunique()}")

# Check payments on account_id
m_pay = df_pay[['payment_id', 'account_id', 'amount', 'event_at']].merge(df_acc[['account_id', 'outstanding_amount', 'dpd']], on='account_id')
print(f"Payments merged with accounts on account_id: {len(m_pay)} / {len(df_pay)}")
print(m_pay.head(5))

# Check PTP on account_id
m_ptp = df_ptp[['ptp_id', 'account_id', 'promised_amount', 'event_at']].merge(df_acc[['account_id', 'outstanding_amount', 'dpd']], on='account_id')
print(f"\nPTP merged with accounts on account_id: {len(m_ptp)} / {len(df_ptp)}")
print(m_ptp.head(5))
