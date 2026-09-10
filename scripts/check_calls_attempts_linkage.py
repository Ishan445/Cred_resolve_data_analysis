import os
import pandas as pd

data_dir = r"data/raw"
df_bor = pd.read_csv(os.path.join(data_dir, "borrowers.csv"), low_memory=False).drop_duplicates()
df_calls = pd.read_csv(os.path.join(data_dir, "calls.csv"), low_memory=False).drop_duplicates()
df_pay = pd.read_csv(os.path.join(data_dir, "payments.csv"), low_memory=False).drop_duplicates()
df_att = pd.read_csv(os.path.join(data_dir, "call_attempts.csv"), low_memory=False).drop_duplicates()

print("Calls row count:", len(df_calls))
print("Call attempts row count:", len(df_att))

# Join calls and call_attempts on call_id
m = df_calls[['call_id', 'account_id', 'borrower_id']].merge(df_att[['call_id', 'account_id', 'borrower_id']], on='call_id', suffixes=('_call', '_att'))
print("Calls merged with call_attempts on call_id:", len(m))
print("Account_id match:", (m['account_id_call'] == m['account_id_att']).sum())
print("Borrower_id match:", (m['borrower_id_call'] == m['borrower_id_att']).sum())
print(m.head(5))
