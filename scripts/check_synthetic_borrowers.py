import os
import pandas as pd

data_dir = r"data/raw"
df_bor = pd.read_csv(os.path.join(data_dir, "borrowers.csv"), low_memory=False).drop_duplicates()

# Check name distinctness
print(f"Borrowers count: {len(df_bor)}")
print("Value counts of name in borrowers:")
print(df_bor['name'].value_counts())
print("\nValue counts of city in borrowers:")
print(df_bor['city'].value_counts())
print("\nValue counts of state in borrowers:")
print(df_bor['state'].value_counts())
