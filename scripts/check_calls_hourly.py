import duckdb
con = duckdb.connect()

print("Timezone distribution in calls.csv:")
print(con.execute("""
    SELECT timezone, COUNT(*) as cnt
    FROM read_csv_auto('data/raw/calls.csv')
    GROUP BY timezone
""").df().to_markdown(index=False))

print("\nRaw hours distribution by timezone:")
print(con.execute("""
    SELECT 
        timezone,
        STRFTIME(event_at::TIMESTAMP, '%H') as raw_hour,
        COUNT(*) as cnt
    FROM read_csv_auto('data/raw/calls.csv')
    GROUP BY timezone, raw_hour
    ORDER BY timezone, raw_hour
""").df().head(30).to_markdown(index=False))
