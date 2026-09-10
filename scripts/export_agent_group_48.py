import os
import pandas as pd

data_dir = r"data/raw"
df_agents = pd.read_csv(os.path.join(data_dir, "agents.csv"), low_memory=False).drop_duplicates()

aid_counts = df_agents['agent_id'].value_counts()
max_aid = aid_counts.index[0]
grp_aid = df_agents[df_agents['agent_id'] == max_aid].sort_values('joined_at')

print(f"Full 48 rows for largest agent_id group: {max_aid}")
with open(r"reports\largest_agent_group_48.md", "w") as f:
    f.write(grp_aid.to_markdown(index=False))
print("Written to reports/largest_agent_group_48.md")
