import duckdb

exec(open('scripts/setup_golden_duckdb.py').read())

df = con.execute('''
    SELECT 
        STRFTIME(event_at::TIMESTAMP, '%Y-%m') as month,
        COUNT(DISTINCT account_id) as attempted_accounts,
        COUNT(DISTINCT CASE WHEN call_status = 'ANSWERED' THEN account_id END) as contacted_accounts,
        ROUND(COUNT(DISTINCT CASE WHEN call_status = 'ANSWERED' THEN account_id END) * 100.0 / COUNT(DISTINCT account_id), 2) as account_contact_rate_pct,
        COUNT(*) as total_call_dials,
        COUNT(CASE WHEN call_status = 'ANSWERED' THEN 1 END) as answered_calls,
        ROUND(COUNT(CASE WHEN call_status = 'ANSWERED' THEN 1 END) * 100.0 / COUNT(*), 2) as call_answer_rate_pct
    FROM golden_calls
    WHERE STRFTIME(event_at::TIMESTAMP, '%Y-%m') <= '2026-07'
    GROUP BY month
    ORDER BY month
''').df()

print(df.to_markdown(index=False))
