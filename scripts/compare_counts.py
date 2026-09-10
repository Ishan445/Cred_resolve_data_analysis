import os
import pandas as pd

data_dir = r"data/raw"
df_bor = pd.read_csv(os.path.join(data_dir, "borrowers.csv"), low_memory=False).drop_duplicates()
df_acc = pd.read_csv(os.path.join(data_dir, "accounts.csv"), low_memory=False).drop_duplicates()

bor_counts = df_bor['borrower_id'].value_counts()
acc_counts = df_acc['borrower_id'].value_counts()

df_comp = pd.DataFrame({'bor_count': bor_counts, 'acc_count': acc_counts}).dropna()
df_comp['match'] = df_comp['bor_count'] == df_comp['acc_count']
print(f"Total overlapping borrower_ids: {len(df_comp)}")
print(f"Exact count match: {df_comp['match'].sum()} / {len(df_comp)}")
print("Sample:")
print(df_comp.head(10))
