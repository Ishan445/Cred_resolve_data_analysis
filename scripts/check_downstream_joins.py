import os
import pandas as pd

data_dir = r"data/raw"
df_bor = pd.read_csv(os.path.join(data_dir, "borrowers.csv"), low_memory=False).drop_duplicates()
df_acc = pd.read_csv(os.path.join(data_dir, "accounts.csv"), low_memory=False).drop_duplicates()

print(f"Total clean rows in borrowers: {len(df_bor)}")
print(f"Unique borrower_id: {df_bor['borrower_id'].nunique()}")
print(f"Unique phone: {df_bor['phone'].nunique()}")
print(f"Unique email: {df_bor['email'].nunique()}")

# Let's inspect join between accounts and borrowers
merged = df_acc.merge(df_bor, on='borrower_id', how='inner')
print(f"\nAccounts inner join Borrowers on borrower_id produces: {len(merged)} rows (from {len(df_acc)} accounts!)")

# Check calls join
df_calls = pd.read_csv(os.path.join(data_dir, "calls.csv"), low_memory=False).drop_duplicates()
print(f"Calls unique borrower_id: {df_calls['borrower_id'].nunique()}")
print(f"Calls unique account_id: {df_calls['account_id'].nunique()}")

# Are borrower_ids in calls matching accounts?
calls_acc = df_calls[['call_id', 'account_id', 'borrower_id']].merge(df_acc[['account_id', 'borrower_id']], on='account_id', suffixes=('_call', '_acc'))
print(f"Calls merged with accounts on account_id: {len(calls_acc)}")
print(f"Mismatch between calls.borrower_id and accounts.borrower_id: {(calls_acc['borrower_id_call'] != calls_acc['borrower_id_acc']).sum()}")
