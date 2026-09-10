import os
import pandas as pd

data_dir = r"data/raw"
df_bor = pd.read_csv(os.path.join(data_dir, "borrowers.csv"), low_memory=False).drop_duplicates()
df_acc = pd.read_csv(os.path.join(data_dir, "accounts.csv"), low_memory=False).drop_duplicates()

bor_counts = df_bor['borrower_id'].value_counts()
print(f"Total unique borrower_id in borrowers: {len(bor_counts)}")

# Let's check 25 sampled colliding borrower_id groups
import random
random.seed(42)

# Pick sizes: 11 (1), 10 (4), 8-9 (5), 5-6 (5), 3-4 (5), 2 (5) = 25 groups
sample_bids = []
sample_bids.extend(bor_counts[bor_counts == 11].index.tolist())
sample_bids.extend(bor_counts[bor_counts == 10].sample(4, random_state=42).index.tolist())
sample_bids.extend(bor_counts[bor_counts.isin([8, 9])].sample(5, random_state=42).index.tolist())
sample_bids.extend(bor_counts[bor_counts.isin([5, 6])].sample(5, random_state=42).index.tolist())
sample_bids.extend(bor_counts[bor_counts.isin([3, 4])].sample(5, random_state=42).index.tolist())
sample_bids.extend(bor_counts[bor_counts == 2].sample(5, random_state=42).index.tolist())

print(f"Selected {len(sample_bids)} sample borrower_id groups:")
for bid in sample_bids:
    grp = df_bor[df_bor['borrower_id'] == bid]
    names = grp['name'].tolist()
    cities = grp['city'].tolist()
    states = grp['state'].tolist()
    phones = [f"{p:.0f}" if pd.notnull(p) else "NULL" for p in grp['phone']]
    print(f"[{bid}] (size={len(grp)}): names={names}, cities={cities}, states={states}, phones={phones}")
