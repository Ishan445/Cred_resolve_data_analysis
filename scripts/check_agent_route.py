import os
import pandas as pd

data_dir = r"data/raw"
df_agents = pd.read_csv(os.path.join(data_dir, "agents.csv"), low_memory=False).drop_duplicates()
df_sess = pd.read_csv(os.path.join(data_dir, "agent_sessions.csv"), low_memory=False).drop_duplicates()
df_calls = pd.read_csv(os.path.join(data_dir, "calls.csv"), low_memory=False).drop_duplicates()

print("Checking composite keys in agents.csv:")
combos = [
    ['agent_id', 'employee_code'],
    ['agent_id', 'vendor_id'],
    ['agent_id', 'team'],
    ['agent_id', 'agent_name'],
    ['employee_code', 'agent_name'],
    ['employee_code', 'vendor_id'],
    ['agent_id', 'employee_code', 'vendor_id', 'team']
]

for c in combos:
    uniq = len(df_agents.drop_duplicates(subset=c))
    print(f"Unique {c}: {uniq} / {len(df_agents)}")

# Check agent_sessions
print("\nChecking agent_sessions linkage to agents:")
sess_aids = set(df_sess['agent_id'].unique())
agents_aids = set(df_agents['agent_id'].unique())
print(f"agent_sessions unique agent_id: {len(sess_aids)}, agents.csv unique agent_id: {len(agents_aids)}")
print(f"Difference: {sess_aids - agents_aids}")

# Check if session device_id or channel can disambiguate
print(f"agent_sessions device_id unique: {df_sess['device_id'].nunique()}")
print("Does device_id appear in agents.csv?", 'device_id' in df_agents.columns)
