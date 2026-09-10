import os
import pandas as pd

data_dir = r"data/raw"
df_calls = pd.read_csv(os.path.join(data_dir, "calls.csv"), low_memory=False).drop_duplicates()
calls_coll = df_calls[df_calls.duplicated(subset=['call_id'], keep=False)].sort_values(['call_id', 'event_at'])

# Export all 79 groups as markdown table with group indicators
markdown_lines = []
markdown_lines.append("| Group # | call_id | account_id | borrower_id | event_at | agent_id | campaign_id | direction | vendor_id | call_status | duration_sec | timezone | Difference |")
markdown_lines.append("|---:|:---|:---|:---|:---|:---|:---|:---|:---|:---|---:|:---|:---|")

grp_num = 1
for cid, grp in calls_coll.groupby('call_id'):
    r1 = grp.iloc[0]
    r2 = grp.iloc[1]
    
    diff_desc = "event_at differed" if r1['event_at'] != r2['event_at'] else "agent_id (NaN vs Populated)"
    
    markdown_lines.append(f"| {grp_num}a | {r1['call_id']} | {r1['account_id']} | {r1['borrower_id']} | {r1['event_at']} | {str(r1['agent_id'])} | {r1['campaign_id']} | {r1['direction']} | {r1['vendor_id']} | {r1['call_status']} | {r1['duration_sec']} | {r1['timezone']} | {diff_desc} |")
    markdown_lines.append(f"| {grp_num}b | {r2['call_id']} | {r2['account_id']} | {r2['borrower_id']} | {r2['event_at']} | {str(r2['agent_id'])} | {r2['campaign_id']} | {r2['direction']} | {r2['vendor_id']} | {r2['call_status']} | {r2['duration_sec']} | {r2['timezone']} | {diff_desc} |")
    grp_num += 1

with open(r"reports\all_79_calls_table.md", "w") as f:
    f.write("\n".join(markdown_lines))

print(f"Successfully generated all 79 calls table ({len(markdown_lines)} lines).")
