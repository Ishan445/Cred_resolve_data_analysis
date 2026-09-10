import os
import pandas as pd

data_dir = r"data/raw"
df_bor = pd.read_csv(os.path.join(data_dir, "borrowers.csv"), low_memory=False).drop_duplicates()
df_acc = pd.read_csv(os.path.join(data_dir, "accounts.csv"), low_memory=False).drop_duplicates()
df_calls = pd.read_csv(os.path.join(data_dir, "calls.csv"), low_memory=False).drop_duplicates()
df_pay = pd.read_csv(os.path.join(data_dir, "payments.csv"), low_memory=False).drop_duplicates()

print(f"Accounts rows: {len(df_acc)}, unique accounts: {df_acc['account_id'].nunique()}")
print(f"Borrowers rows: {len(df_bor)}, unique borrower_id: {df_bor['borrower_id'].nunique()}")

# Look at accounts.borrower_id vs borrowers.borrower_id
acc_bor = df_acc[['account_id', 'borrower_id', 'opened_at']].merge(df_bor, on='borrower_id', how='inner')
print(f"Inner join accounts with borrowers on borrower_id: {len(acc_bor)}")

# What if accounts had an index or row id?
# Let's check if borrower rows correspond 1:1 by row order with accounts!
df_acc_with_idx = df_acc.copy()
df_acc_with_idx['row_idx'] = range(len(df_acc_with_idx))
df_bor_with_idx = df_bor.copy()
df_bor_with_idx['row_idx'] = range(len(df_bor_with_idx))

merged_by_idx = df_acc_with_idx.merge(df_bor_with_idx, on='row_idx', suffixes=('_acc', '_bor'))
print(f"Merged by row index: {len(merged_by_idx)}")
print(f"Do borrower_id match by row index? {(merged_by_idx['borrower_id_acc'] == merged_by_idx['borrower_id_bor']).sum()} / {len(merged_by_idx)}")
print(merged_by_idx[['account_id', 'borrower_id_acc', 'borrower_id_bor', 'name', 'phone', 'opened_at', 'created_at']].head(10))
