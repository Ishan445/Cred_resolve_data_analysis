import os
import duckdb
import pandas as pd

data_dir = r"data/raw".replace('\\', '/')
con = duckdb.connect()

# 1. Accounts portfolio mix by loan_type
res_mix = con.execute(f"""
    SELECT 
        loan_type,
        COUNT(*) as accounts_count,
        ROUND(COUNT(*) * 100.0 / 30000, 2) as pct_accounts,
        ROUND(SUM(principal_amount) / 1e7, 2) as total_principal_cr,
        ROUND(AVG(principal_amount), 2) as avg_principal,
        ROUND(SUM(outstanding_amount) / 1e7, 2) as total_outstanding_cr,
        ROUND(AVG(outstanding_amount), 2) as avg_outstanding
    FROM read_csv_auto('{data_dir}/accounts.csv')
    GROUP BY loan_type
    ORDER BY total_outstanding_cr DESC;
""").df()
print("=== PORTFOLIO MIX BY LOAN TYPE ===")
print(res_mix.to_markdown(index=False))

# 2. DPD Distribution
res_dpd = con.execute(f"""
    SELECT 
        dpd,
        COUNT(*) as accounts_count,
        ROUND(COUNT(*) * 100.0 / 30000, 2) as pct_accounts,
        ROUND(SUM(outstanding_amount) / 1e7, 2) as total_outstanding_cr,
        ROUND(AVG(outstanding_amount), 2) as avg_outstanding
    FROM read_csv_auto('{data_dir}/accounts.csv')
    GROUP BY dpd
    ORDER BY dpd;
""").df()
print("\n=== DPD DISTRIBUTION IN ACCOUNTS ===")
print(res_dpd.to_markdown(index=False))

# 3. Risk Segment Distribution
res_risk = con.execute(f"""
    SELECT 
        risk_segment,
        COUNT(*) as accounts_count,
        ROUND(COUNT(*) * 100.0 / 30000, 2) as pct_accounts,
        ROUND(SUM(outstanding_amount) / 1e7, 2) as total_outstanding_cr
    FROM read_csv_auto('{data_dir}/accounts.csv')
    GROUP BY risk_segment
    ORDER BY accounts_count DESC;
""").df()
print("\n=== RISK SEGMENT DISTRIBUTION ===")
print(res_risk.to_markdown(index=False))

# 4. Monthly Recovery Trend (Gross vs Verified Success)
res_monthly_cash = con.execute(f"""
    WITH dedup_pay AS (
        SELECT * EXCLUDE (rn) FROM (
            SELECT *, ROW_NUMBER() OVER(
                PARTITION BY payment_id 
                ORDER BY CASE WHEN payment_reference IS NOT NULL THEN 1 ELSE 2 END, event_at DESC
            ) as rn
            FROM (SELECT DISTINCT * FROM read_csv_auto('{data_dir}/payments.csv'))
        ) WHERE rn = 1
    )
    SELECT 
        STRFTIME(event_at::TIMESTAMP, '%Y-%m') as month,
        COUNT(*) as total_payments,
        ROUND(SUM(amount) / 1e7, 2) as raw_gross_cash_cr,
        COUNT(CASE WHEN payment_status = 'SUCCESS' THEN 1 END) as success_payments_count,
        ROUND(SUM(CASE WHEN payment_status = 'SUCCESS' THEN amount ELSE 0 END) / 1e7, 2) as success_cash_cr,
        ROUND(SUM(CASE WHEN payment_status = 'FAILED' THEN amount ELSE 0 END) / 1e7, 2) as failed_cash_cr,
        ROUND(SUM(CASE WHEN payment_status = 'REVERSED' THEN amount ELSE 0 END) / 1e7, 2) as reversed_cash_cr,
        ROUND(SUM(CASE WHEN payment_status = 'PENDING' THEN amount ELSE 0 END) / 1e7, 2) as pending_cash_cr
    FROM dedup_pay
    GROUP BY month
    ORDER BY month;
""").df()
print("\n=== MONTHLY RECOVERY TREND (GROSS VS SUCCESSFUL CASH) ===")
print(res_monthly_cash.to_markdown(index=False))
