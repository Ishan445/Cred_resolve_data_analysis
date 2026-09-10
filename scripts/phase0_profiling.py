import os
import glob
import pandas as pd
import numpy as np

data_dir = r"data/raw"

dict_df = pd.read_csv(os.path.join(data_dir, "data_dictionary.csv"))
tables = sorted(list(dict_df['dataset'].unique()))

results = []

for tbl in tables:
    csv_path = os.path.join(data_dir, f"{tbl}.csv")
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        continue
    
    df = pd.read_csv(csv_path, low_memory=False)
    total_rows = len(df)
    total_cols = len(df.columns)
    exact_dups = df.duplicated().sum()
    
    # Null info
    null_counts = df.isnull().sum().to_dict()
    cols_with_nulls = {k: v for k, v in null_counts.items() if v > 0}
    
    # Check date columns from data_dictionary
    date_cols = dict_df[(dict_df['dataset'] == tbl) & (dict_df['dtype'].str.contains('datetime', na=False))]['column'].tolist()
    date_ranges = {}
    for dcol in date_cols:
        if dcol in df.columns:
            valid_dates = pd.to_datetime(df[dcol], errors='coerce').dropna()
            if len(valid_dates) > 0:
                date_ranges[dcol] = {
                    'min': str(valid_dates.min()),
                    'max': str(valid_dates.max())
                }
            else:
                date_ranges[dcol] = {'min': None, 'max': None}
                
    # Specific primary keys / ID uniqueness
    id_cols = [c for c in df.columns if c.endswith('_id') or c == 'employee_code']
    id_unique = {c: df[c].nunique() for c in id_cols}
    
    results.append({
        'table': tbl,
        'total_rows': total_rows,
        'total_cols': total_cols,
        'exact_dups': exact_dups,
        'cols_with_nulls': cols_with_nulls,
        'date_ranges': date_ranges,
        'id_unique': id_unique
    })

print("=== PROFILING RESULTS SUMMARY ===")
print(f"{'Table':<25} | {'Rows':<8} | {'Exact Dups':<10} | {'Cols':<5} | {'Date Columns (Min -> Max)'}")
print("-" * 105)
for r in results:
    date_str = "; ".join([f"{k}: {v['min'][:10]} to {v['max'][:10]}" for k, v in r['date_ranges'].items() if v['min']])
    if not date_str:
        date_str = "No datetime cols"
    print(f"{r['table']:<25} | {r['total_rows']:<8} | {r['exact_dups']:<10} | {r['total_cols']:<5} | {date_str}")

print("\n=== NULLS BREAKDOWN ===")
for r in results:
    if r['cols_with_nulls']:
        print(f"{r['table']}: {r['cols_with_nulls']}")

print("\n=== ID UNIQUENESS BREAKDOWN ===")
for r in results:
    print(f"{r['table']}: {r['id_unique']}")
