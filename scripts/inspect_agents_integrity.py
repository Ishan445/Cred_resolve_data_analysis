import os
import pandas as pd

data_dir = r"data/raw"
df_agents = pd.read_csv(os.path.join(data_dir, "agents.csv"), low_memory=False).drop_duplicates()

print(f"Total clean rows in agents.csv: {len(df_agents)}")
print(f"Unique agent_id: {df_agents['agent_id'].nunique()}")
print(f"Unique employee_code: {df_agents['employee_code'].nunique()}")

# Group by agent_id
aid_counts = df_agents['agent_id'].value_counts()
print(f"Max group size for agent_id: {aid_counts.max()}")
max_aid = aid_counts.index[0]

# Group by employee_code
emp_counts = df_agents['employee_code'].value_counts()
print(f"Max group size for employee_code: {emp_counts.max()}")
print(f"Number of colliding employee_codes: {(emp_counts > 1).sum()}")

print(f"\n=== LARGEST AGENT_ID GROUP: agent_id = {max_aid} (Size: {aid_counts[max_aid]}) ===")
grp_aid = df_agents[df_agents['agent_id'] == max_aid]
print(f"Distinct employee_code within {max_aid}: {grp_aid['employee_code'].nunique()}")
print(f"Distinct agent_name within {max_aid}: {grp_aid['agent_name'].nunique()} ({grp_aid['agent_name'].unique()})")
print(f"Distinct vendor_id within {max_aid}: {grp_aid['vendor_id'].nunique()}")
print(f"Distinct team within {max_aid}: {grp_aid['team'].nunique()}")
print(f"Distinct status within {max_aid}: {grp_aid['status'].nunique()}")
print(grp_aid.head(15).to_markdown(index=False))

# Check many-to-many relationship
emp_per_aid = df_agents.groupby('agent_id')['employee_code'].nunique()
aid_per_emp = df_agents.groupby('employee_code')['agent_id'].nunique()
print(f"\nAverage employee_code per agent_id: {emp_per_aid.mean():.2f} (Min: {emp_per_aid.min()}, Max: {emp_per_aid.max()})")
print(f"Average agent_id per employee_code: {aid_per_emp.mean():.2f} (Min: {aid_per_emp.min()}, Max: {aid_per_emp.max()})")

# Check agent_sessions.csv
df_sess = pd.read_csv(os.path.join(data_dir, "agent_sessions.csv"), low_memory=False).drop_duplicates()
print(f"\n=== AGENT_SESSIONS.CSV CHECK ===")
print(f"Columns in agent_sessions: {list(df_sess.columns)}")
print(f"Unique agent_id in agent_sessions: {df_sess['agent_id'].nunique()}")
print(f"Does employee_code exist in agent_sessions? {'employee_code' in df_sess.columns}")

# Check calls.csv
df_calls = pd.read_csv(os.path.join(data_dir, "calls.csv"), low_memory=False).drop_duplicates()
print(f"\n=== CALLS.CSV CHECK ===")
print(f"Does employee_code exist in calls? {'employee_code' in df_calls.columns}")
print(f"Unique agent_id in calls: {df_calls['agent_id'].nunique()}")
