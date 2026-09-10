import duckdb
con = duckdb.connect()

print("Daily targeting by strategy version and month:")
print(con.execute("""
    SELECT 
        STRFTIME(t.target_date::TIMESTAMP, '%Y-%m') as month,
        c.strategy_version,
        COUNT(*) as targets_count,
        COUNT(DISTINCT t.account_id) as unique_accounts
    FROM read_csv_auto('data/raw/daily_targeting.csv') t
    JOIN read_csv_auto('data/raw/campaigns.csv') c ON t.campaign_id = c.campaign_id
    GROUP BY month, c.strategy_version
    ORDER BY month, c.strategy_version
""").df().to_markdown(index=False))

print("\nDaily targeting by channel:")
print(con.execute("""
    SELECT 
        c.channel,
        COUNT(*) as targets_count,
        COUNT(DISTINCT t.account_id) as unique_accounts
    FROM read_csv_auto('data/raw/daily_targeting.csv') t
    JOIN read_csv_auto('data/raw/campaigns.csv') c ON t.campaign_id = c.campaign_id
    GROUP BY c.channel
    ORDER BY targets_count DESC
""").df().to_markdown(index=False))
