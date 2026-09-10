import os
import pandas as pd

data_dir = r"data/raw"
df_acc = pd.read_csv(os.path.join(data_dir, "accounts.csv"), low_memory=False).drop_duplicates()
acc_bids = df_acc['borrower_id'].value_counts()
print(f"Distribution of accounts per borrower_id in accounts.csv:")
print(acc_bids.value_counts().sort_index())
