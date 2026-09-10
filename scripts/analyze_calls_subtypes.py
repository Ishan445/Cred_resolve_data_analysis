import os
import pandas as pd

data_dir = r"data/raw"
df_calls = pd.read_csv(os.path.join(data_dir, "calls.csv"), low_memory=False).drop_duplicates()
calls_coll = df_calls[df_calls.duplicated(subset=['call_id'], keep=False)].sort_values(['call_id'])

# Check what differs in groups where event_at is identical
null_agent_groups = []
different_event_groups = []

for cid, grp in calls_coll.groupby('call_id'):
    if grp['event_at'].nunique() > 1:
        different_event_groups.append((cid, grp))
    else:
        null_agent_groups.append((cid, grp))

print(f"Colliding call groups with DIFFERENT event_at: {len(different_event_groups)}")
print(f"Colliding call groups with SAME event_at (one has agent_id=NaN): {len(null_agent_groups)}")

print("\nSample of different event_at:")
for cid, grp in different_event_groups[:5]:
    print(grp[['call_id', 'account_id', 'borrower_id', 'event_at', 'agent_id', 'call_status']])

print("\nSample of same event_at:")
for cid, grp in null_agent_groups[:5]:
    print(grp[['call_id', 'account_id', 'borrower_id', 'event_at', 'agent_id', 'call_status']])
