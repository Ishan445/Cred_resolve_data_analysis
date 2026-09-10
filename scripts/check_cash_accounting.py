import os
import duckdb
import pandas as pd

data_dir = r"data/raw".replace('\\', '/')
con = duckdb.connect()

# Total gross cash
gross_cash = con.execute(f"SELECT SUM(amount) FROM read_csv_auto('{data_dir}/payments.csv')").fetchone()[0]

# Successful cash
success_cash = con.execute(f"SELECT SUM(amount) FROM read_csv_auto('{data_dir}/payments.csv') WHERE payment_status = 'SUCCESS'").fetchone()[0]

# Successful cash minus reversals
reversed_cash = con.execute(f"SELECT SUM(amount) FROM read_csv_auto('{data_dir}/payments.csv') WHERE payment_status = 'REVERSED'").fetchone()[0]

print(f"Gross cash in raw payments: INR {gross_cash/1e7:.2f} Cr")
print(f"Successful cash (gross):    INR {success_cash/1e7:.2f} Cr")
print(f"Reversed cash:              INR {reversed_cash/1e7:.2f} Cr")
print(f"Net Realized Cash (Success - Reversed): INR {(success_cash - reversed_cash)/1e7:.2f} Cr")
print(f"Total phantom / non-realized cash: INR {(gross_cash - (success_cash - reversed_cash))/1e7:.2f} Cr ({(gross_cash - (success_cash - reversed_cash))*100.0/gross_cash:.1f}%)")
