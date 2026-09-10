import os
import pandas as pd

data_dir = r"data/raw"
df_bor = pd.read_csv(os.path.join(data_dir, "borrowers.csv"), low_memory=False).drop_duplicates()

bor_counts = df_bor['borrower_id'].value_counts()
print(f"Top 5 borrower_id with max collisions:\n{bor_counts.head(5)}")

# Let's inspect the group with max size 11
max_bid = bor_counts.index[0]
print(f"\n=== MAX COLLISION GROUP FOR BORROWERS (borrower_id = {max_bid}, count = {bor_counts[max_bid]}) ===")
print(df_bor[df_bor['borrower_id'] == max_bid].to_string())

# Sample of size 10
bid_10 = bor_counts[bor_counts == 10].index[0]
print(f"\n=== COLLISION GROUP SIZE 10 (borrower_id = {bid_10}) ===")
print(df_bor[df_bor['borrower_id'] == bid_10].to_string())

# Sample of size 6
bid_6 = bor_counts[bor_counts == 6].index[0]
print(f"\n=== COLLISION GROUP SIZE 6 (borrower_id = {bid_6}) ===")
print(df_bor[df_bor['borrower_id'] == bid_6].to_string())

# Sample of size 3
bid_3 = bor_counts[bor_counts == 3].index[0]
print(f"\n=== COLLISION GROUP SIZE 3 (borrower_id = {bid_3}) ===")
print(df_bor[df_bor['borrower_id'] == bid_3].to_string())

# Sample of size 2
bid_2 = bor_counts[bor_counts == 2].index[0]
print(f"\n=== COLLISION GROUP SIZE 2 (borrower_id = {bid_2}) ===")
print(df_bor[df_bor['borrower_id'] == bid_2].to_string())
