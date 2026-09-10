import duckdb
con = duckdb.connect()

print("Campaign names and targets across strategy versions:")
print(con.execute("""
    SELECT 
        strategy_version,
        channel,
        COUNT(*) as count,
        STRING_AGG(DISTINCT campaign_name, ', ') as sample_names
    FROM read_csv_auto('data/raw/campaigns.csv')
    GROUP BY strategy_version, channel
    ORDER BY strategy_version, channel
""").df().to_markdown(index=False))
