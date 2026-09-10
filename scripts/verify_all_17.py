import os
import glob
import pandas as pd

data_dir = r"data/raw"
files = sorted(glob.glob(os.path.join(data_dir, "*.csv")))

print(f"Total CSV files found in directory: {len(files)}")
total_rows = 0
total_dups = 0

rows_list = []

for f in files:
    name = os.path.basename(f)
    if name == "data_dictionary.csv":
        continue
    df = pd.read_csv(f, low_memory=False)
    r = len(df)
    d = df.duplicated().sum()
    c = len(df.columns)
    null_cols = {col: df[col].isnull().sum() for col in df.columns if df[col].isnull().sum() > 0}
    
    total_rows += r
    total_dups += d
    
    rows_list.append({
        'name': name,
        'rows': r,
        'dups': d,
        'clean': r - d,
        'cols': c,
        'nulls': null_cols
    })

print(f"{'File Name':<28} | {'Raw Rows':>8} | {'Exact Dups':>10} | {'Clean Rows':>10} | {'Cols':>4} | {'Null Columns & Counts'}")
print("-" * 105)
for item in rows_list:
    null_str = str(item['nulls']) if item['nulls'] else "0 nulls"
    print(f"{item['name']:<28} | {item['rows']:>8} | {item['dups']:>10} | {item['clean']:>10} | {item['cols']:>4} | {null_str}")

print("-" * 105)
print(f"{'TOTAL (17 tables)':<28} | {total_rows:>8} | {total_dups:>10} | {total_rows - total_dups:>10} |")
