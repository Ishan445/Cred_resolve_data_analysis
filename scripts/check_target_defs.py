import duckdb
con = duckdb.connect()
print(con.execute("""
    SELECT target_definition, COUNT(*) as cnt
    FROM read_csv_auto('data/raw/campaigns.csv')
    GROUP BY target_definition
""").df().to_markdown(index=False))
