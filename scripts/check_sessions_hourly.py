import duckdb
con = duckdb.connect()

print("Agent Sessions login hour distribution:")
print(con.execute("""
    SELECT 
        STRFTIME(login_at::TIMESTAMP, '%H') as login_hour,
        COUNT(*) as cnt,
        ROUND(AVG(date_diff('minute', login_at::TIMESTAMP, logout_at::TIMESTAMP))/60.0, 2) as avg_hours
    FROM read_csv_auto('data/raw/agent_sessions.csv')
    GROUP BY login_hour
    ORDER BY login_hour
""").df().to_markdown(index=False))
