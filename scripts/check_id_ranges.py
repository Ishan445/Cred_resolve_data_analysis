import os
import pandas as pd

data_dir = r"data/raw"
df_bor = pd.read_csv(os.path.join(data_dir, "borrowers.csv"), low_memory=False).drop_duplicates()
df_acc = pd.read_csv(os.path.join(data_dir, "accounts.csv"), low_memory=False).drop_duplicates()

bor_bids = set(df_bor['borrower_id'].unique())
acc_bids = set(df_acc['borrower_id'].dropna().unique())

print(f"Max borrower_id in borrowers: {max(bor_bids)}, Min: {min(bor_bids)}")
print(f"Max borrower_id in accounts: {max(acc_bids)}, Min: {min(acc_bids)}")

# Convert to integers
bor_nums = [int(x.replace('BRW', '')) for x in bor_bids]
acc_nums = [int(x.replace('BRW', '')) for x in acc_bids]

print(f"Borrowers ID integer range: min={min(bor_nums)}, max={max(bor_nums)}, count={len(bor_nums)}")
print(f"Accounts ID integer range: min={min(acc_nums)}, max={max(acc_nums)}, count={len(acc_nums)}")
print(f"Theoretical domain size (max-min+1): {max(max(bor_nums), max(acc_nums))}")
