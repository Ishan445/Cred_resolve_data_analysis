import os
import pandas as pd

data_dir = r"data/raw"
df_bor = pd.read_csv(os.path.join(data_dir, "borrowers.csv"), low_memory=False).drop_duplicates()
bor_counts = df_bor['borrower_id'].value_counts()

print("Checking 25 sampled borrower_id groups for created_at vs updated_at monotonicity...")
sample_25 = [
    bor_counts[bor_counts == 11].index[0],
    *bor_counts[bor_counts == 10].sample(4, random_state=42).index,
    *bor_counts[bor_counts.isin([8, 9])].sample(5, random_state=42).index,
    *bor_counts[bor_counts.isin([5, 6])].sample(5, random_state=42).index,
    *bor_counts[bor_counts.isin([3, 4])].sample(5, random_state=42).index,
    *bor_counts[bor_counts == 2].sample(5, random_state=42).index
]

inversion_count = 0
for bid in sample_25:
    grp = df_bor[df_bor['borrower_id'] == bid]
    for idx, row in grp.iterrows():
        if pd.notnull(row['created_at']) and pd.notnull(row['updated_at']):
            if row['updated_at'] < row['created_at']:
                inversion_count += 1

print(f"Total rows inspected in 25 groups: {sum(len(df_bor[df_bor['borrower_id'] == bid]) for bid in sample_25)}")
print(f"Total rows where updated_at < created_at: {inversion_count}")
