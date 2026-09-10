import os
import pandas as pd

data_dir = r"data/raw"
df_calls = pd.read_csv(os.path.join(data_dir, "calls.csv"), low_memory=False).drop_duplicates()
df_acc = pd.read_csv(os.path.join(data_dir, "accounts.csv"), low_memory=False).drop_duplicates()

sample = df_calls[['call_id', 'account_id', 'borrower_id']].merge(df_acc[['account_id', 'borrower_id']], on='account_id', suffixes=('_call', '_acc')).head(10)
print(sample)
