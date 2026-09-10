import duckdb

con = duckdb.connect()
exec(open('scripts/setup_golden_duckdb.py').read())

print("=== 1. FULL DATASET COMPLAINTS BREAKDOWN (8,000 ROWS) ===")
print(con.execute("""
    SELECT 
        complaint_type,
        COUNT(*) as total_complaints,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM golden_complaints), 2) as pct_of_total
    FROM golden_complaints
    GROUP BY complaint_type
    ORDER BY total_complaints DESC;
""").df().to_markdown(index=False))

print("\n=== 2. CHANNEL ATTRIBUTED COMPLAINTS (14-DAY LOOKBACK) ===")
# Attributing each complaint to nearest preceding touchpoint within 14 days
query_attr = """
WITH all_touches AS (
    SELECT account_id, event_at::TIMESTAMP as touch_at, 'CALL' as channel, agent_id
    FROM golden_calls
    UNION ALL
    SELECT account_id, event_at::TIMESTAMP as touch_at, 'WHATSAPP' as channel, NULL as agent_id
    FROM golden_whatsapp_events
    UNION ALL
    SELECT account_id, event_at::TIMESTAMP as touch_at, 'SMS' as channel, NULL as agent_id
    FROM golden_sms_events
    UNION ALL
    SELECT account_id, scheduled_at::TIMESTAMP as touch_at, 'FIELD' as channel, agent_id
    FROM golden_field_visits
),
complaint_matches AS (
    SELECT 
        c.complaint_id,
        c.complaint_type,
        c.event_at as complaint_at,
        t.channel,
        t.agent_id,
        t.touch_at,
        ROW_NUMBER() OVER(
            PARTITION BY c.complaint_id 
            ORDER BY t.touch_at DESC
        ) as rn
    FROM golden_complaints c
    JOIN all_touches t 
      ON c.account_id = t.account_id
     AND t.touch_at <= c.event_at::TIMESTAMP
     AND t.touch_at >= c.event_at::TIMESTAMP - INTERVAL '14 days'
)
SELECT 
    COALESCE(m.channel, 'UNATTRIBUTED / NO TOUCH') as attributed_channel,
    COUNT(DISTINCT c.complaint_id) as complaint_count,
    ROUND(COUNT(DISTINCT c.complaint_id) * 100.0 / (SELECT COUNT(*) FROM golden_complaints), 2) as pct_of_all_complaints
FROM golden_complaints c
LEFT JOIN (SELECT * FROM complaint_matches WHERE rn = 1) m
  ON c.complaint_id = m.complaint_id
GROUP BY attributed_channel
ORDER BY complaint_count DESC;
"""
print(con.execute(query_attr).df().to_markdown(index=False))

print("\n=== 3. CALL-ATTRIBUTED COMPLAINTS SPECIFIC BREAKDOWN (1,176 ROWS) ===")
query_call_attr = """
WITH all_touches AS (
    SELECT account_id, event_at::TIMESTAMP as touch_at, 'CALL' as channel, agent_id
    FROM golden_calls
    UNION ALL
    SELECT account_id, event_at::TIMESTAMP as touch_at, 'WHATSAPP' as channel, NULL as agent_id
    FROM golden_whatsapp_events
    UNION ALL
    SELECT account_id, event_at::TIMESTAMP as touch_at, 'SMS' as channel, NULL as agent_id
    FROM golden_sms_events
    UNION ALL
    SELECT account_id, scheduled_at::TIMESTAMP as touch_at, 'FIELD' as channel, agent_id
    FROM golden_field_visits
),
complaint_matches AS (
    SELECT 
        c.complaint_id,
        c.complaint_type,
        c.event_at as complaint_at,
        t.channel,
        t.agent_id,
        ROW_NUMBER() OVER(
            PARTITION BY c.complaint_id 
            ORDER BY t.touch_at DESC
        ) as rn
    FROM golden_complaints c
    JOIN all_touches t 
      ON c.account_id = t.account_id
     AND t.touch_at <= c.event_at::TIMESTAMP
     AND t.touch_at >= c.event_at::TIMESTAMP - INTERVAL '14 days'
)
SELECT 
    c.complaint_type,
    COUNT(*) as call_attributed_count,
    ROUND(COUNT(*) * 100.0 / 1176, 2) as pct_of_call_complaints,
    COUNT(DISTINCT m.agent_id) as desk_records_involved
FROM complaint_matches m
JOIN golden_complaints c ON m.complaint_id = c.complaint_id
WHERE m.rn = 1 AND m.channel = 'CALL'
GROUP BY c.complaint_type
ORDER BY call_attributed_count DESC;
"""
print(con.execute(query_call_attr).df().to_markdown(index=False))
