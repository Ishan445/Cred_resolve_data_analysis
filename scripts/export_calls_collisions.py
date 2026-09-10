import os
import pandas as pd

data_dir = r"data/raw"
df_calls = pd.read_csv(os.path.join(data_dir, "calls.csv"), low_memory=False).drop_duplicates()
calls_coll = df_calls[df_calls.duplicated(subset=['call_id'], keep=False)].sort_values(['call_id', 'event_at'])

print(f"Total rows in calls collisions: {len(calls_coll)}")
# Save all 79 groups to a CSV or markdown table
calls_coll.to_csv(r"reports\calls_collisions_79.csv", index=True)
print("Saved all 79 colliding call groups to reports/calls_collisions_79.csv")
print("\nFirst 10 colliding call groups in full:")
print(calls_coll.head(20).to_markdown(index=True))
