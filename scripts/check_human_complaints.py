import os
import duckdb
import pandas as pd

data_dir = r"data/raw".replace('\\', '/')
con = duckdb.connect()
exec(open(r"scripts\setup_golden_duckdb.py").read())

# Check complaints by agent_id and vendor_id via 14-day touchpoint attribution
con.execute("""
    CREATE OR REPLACE TABLE all_touchpoints_ops AS
    SELECT account_id, event_at::TIMESTAMP as touch_at, 'CALL' as channel, agent_id, vendor_id, campaign_id FROM golden_calls
    UNION ALL
    SELECT account_id, event_at::TIMESTAMP, 'FIELD', agent_id, NULL, NULL FROM golden_field_visits;
""")

res_agent_comp = con.execute("""
    WITH ranked_comp AS (
        SELECT 
            c.complaint_id,
            c.complaint_type,
            c.severity,
            t.agent_id,
            t.channel,
            ROW_NUMBER() OVER(PARTITION BY c.complaint_id ORDER BY t.touch_at DESC) as rn
        FROM golden_complaints c
        JOIN all_touchpoints_ops t 
          ON c.account_id = t.account_id 
         AND t.touch_at <= c.event_at::TIMESTAMP
         AND t.touch_at >= c.event_at::TIMESTAMP - INTERVAL '14 days'
    )
    SELECT 
        channel,
        COUNT(*) as total_complaints,
        COUNT(CASE WHEN complaint_type = 'HARASSMENT' THEN 1 END) as harassment_complaints,
        COUNT(CASE WHEN complaint_type = 'DND' THEN 1 END) as dnd_complaints,
        COUNT(CASE WHEN severity = 'CRITICAL' THEN 1 END) as critical_severity,
        COUNT(DISTINCT agent_id) as agents_implicated
    FROM ranked_comp
    WHERE rn = 1
    GROUP BY channel;
""").df()
print("Complaints breakdown by operational human channels:")
print(res_agent_comp)
