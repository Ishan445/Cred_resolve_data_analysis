import os
import pandas as pd

data_dir = r"data/raw"
df_calls = pd.read_csv(os.path.join(data_dir, "calls.csv"), low_memory=False).drop_duplicates()
calls_coll = df_calls[df_calls.duplicated(subset=['call_id'], keep=False)].sort_values(['call_id', 'event_at'])

print(f"Total colliding rows in calls: {len(calls_coll)} (across {calls_coll['call_id'].nunique()} call_ids)")

# Let's inspect all 79 colliding groups
groups = []
for cid, grp in calls_coll.groupby('call_id'):
    r1 = grp.iloc[0]
    r2 = grp.iloc[1]
    
    diffs = []
    for col in grp.columns:
        val1 = r1[col]
        val2 = r2[col]
        if pd.isna(val1) and pd.isna(val2):
            continue
        if val1 != val2:
            diffs.append((col, str(val1), str(val2)))
    groups.append((cid, diffs))

print(f"Number of groups with diffs: {len(groups)}")
from collections import Counter
diff_types = Counter([tuple(sorted([d[0] for d in g[1]])) for g in groups])
print("Distribution of differing column sets across all 79 groups:")
for dt, count in diff_types.items():
    print(f"  {dt}: {count} groups")

print("\n--- All 11 groups with differing event_at ---")
for cid, diffs in groups:
    cols = [d[0] for d in diffs]
    if 'event_at' in cols:
        print(f"Call ID: {cid} -> {diffs}")

print("\n--- Sample of 10 groups with differing agent_id (agent_id=NaN vs populated) ---")
c = 0
for cid, diffs in groups:
    cols = [d[0] for d in diffs]
    if 'agent_id' in cols and 'event_at' not in cols:
        print(f"Call ID: {cid} -> {diffs}")
        c += 1
        if c >= 10: break
