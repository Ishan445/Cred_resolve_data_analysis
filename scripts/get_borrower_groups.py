import os
import pandas as pd

data_dir = r"data/raw"

df_bor = pd.read_csv(os.path.join(data_dir, "borrowers.csv"), low_memory=False).drop_duplicates()
bor_counts = df_bor['borrower_id'].value_counts()

top3_ids = bor_counts.head(3).index.tolist()
bottom3_ids = bor_counts[bor_counts == 2].head(3).index.tolist()

print("=== TOP 3 COLLIDING BORROWER GROUPS ===")
for bid in top3_ids:
    print(f"\n--- Borrower ID: {bid} (Size: {bor_counts[bid]}) ---")
    grp = df_bor[df_bor['borrower_id'] == bid]
    print(grp.to_markdown(index=False))

print("\n=== BOTTOM 3 (SIZE 2) COLLIDING BORROWER GROUPS ===")
for bid in bottom3_ids:
    print(f"\n--- Borrower ID: {bid} (Size: {bor_counts[bid]}) ---")
    grp = df_bor[df_bor['borrower_id'] == bid]
    print(grp.to_markdown(index=False))
