import os
import pandas as pd

data_dir = r"data/raw"
df_calls = pd.read_csv(os.path.join(data_dir, "calls.csv"), low_memory=False).drop_duplicates()
calls_coll = df_calls[df_calls.duplicated(subset=['call_id'], keep=False)].sort_values(['call_id', 'event_at'])

# Check what differs
diff_summary = []
for cid, grp in calls_coll.groupby('call_id'):
    d = {}
    d['call_id'] = cid
    d['count'] = len(grp)
    for col in grp.columns:
        if grp[col].nunique() > 1:
            d[col] = list(grp[col].values)
    diff_summary.append(d)

print(f"Total colliding groups in calls: {len(diff_summary)}")
# Check which columns differ across all 79 groups
diff_keys = set()
for d in diff_summary:
    for k in d.keys():
        if k not in ['call_id', 'count']:
            diff_keys.add(k)
print(f"Columns differing in calls collisions: {diff_keys}")

# Print 10 detailed examples
for d in diff_summary[:10]:
    print(d)

# Let's check payments collisions
df_pay = pd.read_csv(os.path.join(data_dir, "payments.csv"), low_memory=False).drop_duplicates()
pay_coll = df_pay[df_pay.duplicated(subset=['payment_id'], keep=False)].sort_values(['payment_id'])
pay_diff = []
for pid, grp in pay_coll.groupby('payment_id'):
    d = {}
    d['payment_id'] = pid
    d['count'] = len(grp)
    for col in grp.columns:
        if grp[col].nunique() > 1:
            d[col] = list(grp[col].values)
        elif grp[col].isnull().any():
            d[col] = 'Contains NULL'
    pay_diff.append(d)

print(f"\nTotal colliding groups in payments: {len(pay_diff)}")
for d in pay_diff:
    print(d)
