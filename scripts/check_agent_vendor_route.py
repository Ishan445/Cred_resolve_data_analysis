import os
import pandas as pd

data_dir = r"data/raw"
df_calls = pd.read_csv(os.path.join(data_dir, "calls.csv"), low_memory=False).drop_duplicates()
df_agents = pd.read_csv(os.path.join(data_dir, "agents.csv"), low_memory=False).drop_duplicates()

# Can calls join to agents on (agent_id, vendor_id)?
print(f"Calls unique (agent_id, vendor_id): {len(df_calls[['agent_id', 'vendor_id']].dropna().drop_duplicates())}")
calls_av = df_calls[['agent_id', 'vendor_id']].dropna().drop_duplicates()
agents_av = df_agents[['agent_id', 'vendor_id', 'employee_code', 'agent_name']].drop_duplicates()

merged_av = calls_av.merge(agents_av, on=['agent_id', 'vendor_id'])
print(f"Merged (agent_id, vendor_id) between calls and agents: {len(merged_av)} rows from {len(calls_av)} pairs!")
print(f"Average agent_name/employee_code per (agent_id, vendor_id) in agents: {len(merged_av) / len(calls_av):.2f}")
