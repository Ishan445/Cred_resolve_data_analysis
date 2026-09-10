import os
import duckdb
import pandas as pd
from duckdb_setup import setup_duckdb

con = duckdb.connect()
setup_duckdb(con)

# 1. PTP-Kept Reconciliation
res_ptp_recon = con.execute("""
    WITH ptp_base AS (
        SELECT 
            ptp_id,
            account_id,
            event_at::TIMESTAMP as ptp_created_at,
            promised_date::TIMESTAMP as promised_at,
            promised_amount,
            status as raw_ptp_status
        FROM golden_ptp
    ),
    matched_cash AS (
        SELECT 
            p.ptp_id,
            pay.payment_id,
            ROW_NUMBER() OVER(
                PARTITION BY p.ptp_id 
                ORDER BY ABS(date_diff('hour', pay.event_at::TIMESTAMP, p.promised_at)) ASC
            ) as rn
        FROM ptp_base p
        JOIN golden_payments pay 
          ON p.account_id = pay.account_id
         AND pay.payment_status = 'SUCCESS'
         AND pay.event_at::TIMESTAMP >= p.promised_at - INTERVAL '3 days'
         AND pay.event_at::TIMESTAMP <= p.promised_at + INTERVAL '3 days'
         AND pay.amount >= p.promised_amount * 0.90
         AND pay.amount <= p.promised_amount * 1.10
    )
    SELECT 
        p.raw_ptp_status,
        CASE WHEN m.payment_id IS NOT NULL THEN 'KEPT_INDEPENDENT' ELSE 'BROKEN_INDEPENDENT' END as independent_status,
        COUNT(*) as count
    FROM ptp_base p
    LEFT JOIN (SELECT * FROM matched_cash WHERE rn = 1) m
      ON p.ptp_id = m.ptp_id
    GROUP BY p.raw_ptp_status, independent_status;
""").df()

print("PTP-Kept Confusion Matrix Summary:")
print(res_ptp_recon)

# 2. Independent Monthly Operational Metrics
res_metrics = con.execute("""
    WITH monthly_attempts AS (
        SELECT 
            STRFTIME(event_at::TIMESTAMP, '%Y-%m') as month,
            COUNT(DISTINCT account_id) as attempted_accounts,
            COUNT(*) as total_call_dials,
            COUNT(DISTINCT CASE WHEN call_status = 'ANSWERED' THEN account_id END) as contacted_accounts_call,
            COUNT(CASE WHEN call_status = 'ANSWERED' THEN 1 END) as answered_calls
        FROM golden_calls
        GROUP BY month
    ),
    monthly_dispositions AS (
        SELECT 
            STRFTIME(event_at::TIMESTAMP, '%Y-%m') as month,
            COUNT(DISTINCT CASE WHEN disposition_code IN ('PTP', 'PROMISE_TO_PAY', 'PAID', 'DISPUTE', 'REFUSED', 'CALLBACK') THEN account_id END) as rpc_accounts_call
        FROM golden_call_dispositions
        GROUP BY month
    ),
    monthly_ptp AS (
        SELECT 
            STRFTIME(event_at::TIMESTAMP, '%Y-%m') as month,
            COUNT(*) as total_ptps
        FROM golden_ptp
        GROUP BY month
    ),
    monthly_cash AS (
        SELECT 
            STRFTIME(event_at::TIMESTAMP, '%Y-%m') as month,
            COUNT(CASE WHEN payment_status = 'SUCCESS' THEN 1 END) as success_txns,
            ROUND(SUM(CASE WHEN payment_status = 'SUCCESS' THEN amount ELSE 0 END) / 1e7, 2) as success_cash_cr,
            ROUND(SUM(CASE WHEN payment_status = 'REVERSED' THEN amount ELSE 0 END) / 1e7, 2) as reversed_cash_cr,
            ROUND((SUM(CASE WHEN payment_status = 'SUCCESS' THEN amount ELSE 0 END) - 
                   SUM(CASE WHEN payment_status = 'REVERSED' THEN amount ELSE 0 END)) / 1e7, 2) as net_cash_cr
        FROM golden_payments
        GROUP BY month
    ),
    monthly_sessions AS (
        SELECT 
            STRFTIME(login_at::TIMESTAMP, '%Y-%m') as month,
            ROUND(SUM(date_diff('minute', login_at::TIMESTAMP, logout_at::TIMESTAMP)) / 60.0, 1) as total_desk_hours
        FROM golden_agent_sessions
        GROUP BY month
    )
    SELECT 
        a.month,
        a.attempted_accounts,
        a.total_call_dials,
        a.answered_calls,
        ROUND(a.contacted_accounts_call * 100.0 / a.attempted_accounts, 2) as contact_rate_pct,
        d.rpc_accounts_call,
        ROUND(d.rpc_accounts_call * 100.0 / a.contacted_accounts_call, 2) as rpc_conversion_pct,
        p.total_ptps,
        s.total_desk_hours,
        c.net_cash_cr,
        ROUND(c.net_cash_cr * 1e7 / s.total_desk_hours, 2) as recovery_per_desk_hour,
        ROUND(c.net_cash_cr * 1e7 / a.attempted_accounts, 2) as recovery_per_attempted_acc
    FROM monthly_attempts a
    LEFT JOIN monthly_dispositions d ON a.month = d.month
    LEFT JOIN monthly_ptp p ON a.month = p.month
    LEFT JOIN monthly_cash c ON a.month = c.month
    LEFT JOIN monthly_sessions s ON a.month = s.month
    ORDER BY a.month;
""").df()

print("\nIndependent Monthly Operational Metrics:")
print(res_metrics.to_markdown(index=False))

# 3. MoM Growth Rates
res_mom = con.execute("""
    WITH monthly_cash AS (
        SELECT 
            STRFTIME(event_at::TIMESTAMP, '%Y-%m') as month,
            SUM(amount) as golden_gross_cash,
            SUM(CASE WHEN payment_status = 'SUCCESS' THEN amount ELSE 0 END) as success_cash,
            SUM(CASE WHEN payment_status = 'REVERSED' THEN amount ELSE 0 END) as reversed_cash,
            SUM(CASE WHEN payment_status = 'SUCCESS' THEN amount ELSE 0 END) - 
            SUM(CASE WHEN payment_status = 'REVERSED' THEN amount ELSE 0 END) as net_realized_cash
        FROM golden_payments
        GROUP BY month
    )
    SELECT 
        month,
        ROUND(golden_gross_cash / 1e7, 2) as gross_cash_cr,
        ROUND(net_realized_cash / 1e7, 2) as net_realized_cr,
        ROUND((net_realized_cash - LAG(net_realized_cash) OVER(ORDER BY month))*100.0 / 
              NULLIF(LAG(net_realized_cash) OVER(ORDER BY month), 0), 2) as net_cash_mom_pct,
        ROUND((golden_gross_cash - LAG(golden_gross_cash) OVER(ORDER BY month))*100.0 / 
              NULLIF(LAG(golden_gross_cash) OVER(ORDER BY month), 0), 2) as gross_cash_mom_pct
    FROM monthly_cash
    ORDER BY month;
""").df()

print("\nMonthly Recovery Comparison (Gross vs Net Realized MoM):")
print(res_mom.to_markdown(index=False))
