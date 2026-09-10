import duckdb
con = duckdb.connect()
print(con.execute("SELECT * FROM read_csv_auto('data/raw/campaigns.csv') LIMIT 5").df().to_markdown(index=False))
