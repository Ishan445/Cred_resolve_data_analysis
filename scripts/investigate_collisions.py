import os
import pandas as pd
import json

data_dir = r"data/raw"

# 1. Investigate calls.csv (79 collisions)
df_calls = pd.read_csv(os.path.join(data_dir, "calls.csv"), low_memory=False).drop_duplicates()
calls_coll = df_calls[df_calls.duplicated(subset=['call_id'], keep=False)].sort_values('call_id')
print(f"=== CALLS.CSV COLLISIONS: {calls_coll['call_id'].nunique()} unique call_ids, total {len(calls_coll)} rows ===")
print("Sample of 10 colliding call_id pairs:")
print(calls_coll.head(20).to_string())

# Analyze differences in calls
call_diff_cols = set()
for cid, group in calls_coll.groupby('call_id'):
    for col in group.columns:
        if group[col].nunique() > 1:
            call_diff_cols.add(col)
print(f"\nColumns that differ across colliding call_id groups: {call_diff_cols}")

# 2. Investigate payments.csv (14 collisions)
df_pay = pd.read_csv(os.path.join(data_dir, "payments.csv"), low_memory=False).drop_duplicates()
pay_coll = df_pay[df_pay.duplicated(subset=['payment_id'], keep=False)].sort_values('payment_id')
print(f"\n=== PAYMENTS.CSV COLLISIONS: {pay_coll['payment_id'].nunique()} unique payment_ids, total {len(pay_coll)} rows ===")
print(pay_coll.to_string())

pay_diff_cols = set()
for pid, group in pay_coll.groupby('payment_id'):
    for col in group.columns:
        if group[col].nunique() > 1:
            pay_diff_cols.add(col)
print(f"\nColumns that differ across colliding payment_id groups: {pay_diff_cols}")

# 3. Investigate borrowers.csv
df_bor = pd.read_csv(os.path.join(data_dir, "borrowers.csv"), low_memory=False).drop_duplicates()
bor_counts = df_bor['borrower_id'].value_counts()
print(f"\n=== BORROWERS.CSV: Total clean {len(df_bor)}, unique borrower_id {df_bor['borrower_id'].nunique()} ===")
print(f"Distribution of rows per borrower_id:")
print(bor_counts.value_counts().sort_index())

# Check diff cols in borrowers
bor_coll = df_bor[df_bor.duplicated(subset=['borrower_id'], keep=False)]
bor_diff_cols = set()
for bid, group in bor_coll.groupby('borrower_id'):
    for col in group.columns:
        if group[col].nunique() > 1:
            bor_diff_cols.add(col)
print(f"\nColumns that differ across colliding borrower_id groups: {bor_diff_cols}")

# 4. Cross-check against accounts.csv
df_acc = pd.read_csv(os.path.join(data_dir, "accounts.csv"), low_memory=False).drop_duplicates()
acc_bids = set(df_acc['borrower_id'].dropna().unique())
bor_bids = set(df_bor['borrower_id'].unique())
print(f"\n=== CROSS CHECK ACCOUNTS <-> BORROWERS ===")
print(f"Distinct borrower_id in accounts.csv: {len(acc_bids)}")
print(f"Distinct borrower_id in borrowers.csv: {len(bor_bids)}")
print(f"Accounts borrower_ids present in borrowers.csv: {len(acc_bids.intersection(bor_bids))}")
print(f"Accounts borrower_ids NOT present in borrowers.csv: {len(acc_bids - bor_bids)}")
print(f"Borrowers borrower_ids NOT present in accounts.csv: {len(bor_bids - acc_bids)}")

