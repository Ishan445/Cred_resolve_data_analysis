import os
import duckdb
import pandas as pd
import numpy as np

data_dir = r"data/raw".replace('\\', '/')
con = duckdb.connect()

# Setup Golden Tables
exec(open(r"scripts\setup_golden_duckdb.py").read())

print("=== STARTING PHASE 3: INDEPENDENT METRICS & 11% VERDICT ===")

# ----------------------------------------------------------------------
# 1. PTP-KEPT RECONCILIATION & CONFUSION MATRIX
# ----------------------------------------------------------------------
print("\n--- 1. PTP-Kept Disagreement Reconciliation ---")
# An independent PTP-kept match requires a successful payment on the same account within [-3d, +3d] of promised_date
# matching amount within +/- 10%
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
            p.raw_ptp_status,
            p.promised_amount,
            pay.payment_id,
            pay.amount as paid_amount,
            pay.event_at as paid_at,
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
        p.ptp_id,
        p.raw_ptp_status,
        CASE WHEN m.payment_id IS NOT NULL THEN 'KEPT_INDEPENDENT' ELSE 'BROKEN_INDEPENDENT' END as independent_ptp_status
    FROM ptp_base p
    LEFT JOIN (SELECT * FROM matched_cash WHERE rn = 1) m
      ON p.ptp_id = m.ptp_id;
""").df()

confusion_matrix = pd.crosstab(
    res_ptp_recon['raw_ptp_status'], 
    res_ptp_recon['independent_ptp_status'], 
    margins=True
)
print("PTP-Kept Confusion Matrix (Raw Platform Label vs. Independent Cash Match):")
print(confusion_matrix.to_markdown())

# Disagreement rate
disagreements = (res_ptp_recon['raw_ptp_status'] == 'KEPT') & (res_ptp_recon['independent_ptp_status'] == 'BROKEN_INDEPENDENT')
print(f"\nRaw PTPs marked KEPT that had NO verified matching payment: {disagreements.sum()} / {(res_ptp_recon['raw_ptp_status'] == 'KEPT').sum()} ({(disagreements.sum() * 100.0 / (res_ptp_recon['raw_ptp_status'] == 'KEPT').sum()):.2f}%)")

# ----------------------------------------------------------------------
# 2. INDEPENDENT MONTHLY OPERATIONAL METRICS (Jan - Jul 2026)
# ----------------------------------------------------------------------
print("\n--- 2. Independent Monthly Operational Metrics ---")
# Metric definitions:
# - Unique accounts attempted
# - Unique accounts contacted (call_status = 'ANSWERED' or field outcome in ('PAID', 'CONTACTED', 'PTP') or whatsapp READ/REPLIED)
# - Contact rate
# - PTPs created & PTP rate
# - Net cash recovered & Recovery rate against starting outstanding
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
            COUNT(DISTINCT CASE WHEN disposition_code IN ('PROMISE_TO_PAY', 'PTP') THEN account_id END) as ptp_accounts_call,
            COUNT(DISTINCT CASE WHEN disposition_code IN ('PTP', 'PROMISE_TO_PAY', 'PAID', 'DISPUTE', 'REFUSED', 'CALLBACK') THEN account_id END) as rpc_accounts_call
        FROM golden_call_dispositions
        GROUP BY month
    ),
    monthly_ptp AS (
        SELECT 
            STRFTIME(event_at::TIMESTAMP, '%Y-%m') as month,
            COUNT(*) as total_ptps,
            COUNT(DISTINCT account_id) as total_ptp_accounts
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
            COUNT(DISTINCT agent_id) as active_desks,
            ROUND(SUM(date_diff('minute', login_at::TIMESTAMP, logout_at::TIMESTAMP)) / 60.0, 1) as total_desk_hours
        FROM golden_sessions
        GROUP BY month
    )
    SELECT 
        a.month,
        a.attempted_accounts,
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

print("Independent Operational Performance Trajectory (Jan–Aug 2026):")
print(res_metrics.to_markdown(index=False))

# ----------------------------------------------------------------------
# 3. WATERFALL DECOMPOSITION OF THE 11% CLAIM
# ----------------------------------------------------------------------
print("\n--- 3. Waterfall Gap Decomposition of the 11% Claim ---")
# How did legacy reporting reach "11% improvement"?
# Let's inspect raw un-deduplicated gross cash MoM vs Net Cash MoM
res_waterfall = con.execute("""
    WITH raw_p AS (
        SELECT 
            STRFTIME(event_at::TIMESTAMP, '%Y-%m') as month,
            SUM(amount) as raw_gross_cash,
            SUM(CASE WHEN payment_status = 'SUCCESS' THEN amount ELSE 0 END) as raw_success_cash
        FROM read_csv_auto('{data_dir}/payments.csv')
        GROUP BY month
    ),
    golden_p AS (
        SELECT 
            STRFTIME(event_at::TIMESTAMP, '%Y-%m') as month,
            SUM(amount) as golden_gross_cash,
            SUM(CASE WHEN payment_status = 'SUCCESS' THEN amount ELSE 0 END) as golden_success_cash,
            SUM(CASE WHEN payment_status = 'REVERSED' THEN amount ELSE 0 END) as golden_reversed_cash,
            SUM(CASE WHEN payment_status = 'SUCCESS' THEN amount ELSE 0 END) - 
            SUM(CASE WHEN payment_status = 'REVERSED' THEN amount ELSE 0 END) as golden_net_cash
        FROM golden_payments
        GROUP BY month
    )
    SELECT 
        r.month,
        ROUND(r.raw_gross_cash / 1e7, 2) as raw_gross_cr,
        ROUND(g.golden_gross_cash / 1e7, 2) as golden_gross_cr,
        ROUND(g.golden_success_cash / 1e7, 2) as golden_success_cr,
        ROUND(g.golden_reversed_cash / 1e7, 2) as golden_reversed_cr,
        ROUND(g.golden_net_cash / 1e7, 2) as golden_net_cr,
        ROUND((g.golden_net_cash - LAG(g.golden_net_cash) OVER(ORDER BY r.month))*100.0 / 
              NULLIF(LAG(g.golden_net_cash) OVER(ORDER BY r.month), 0), 2) as true_net_mom_pct,
        ROUND((r.raw_gross_cash - LAG(r.raw_gross_cash) OVER(ORDER BY r.month))*100.0 / 
              NULLIF(LAG(r.raw_gross_cash) OVER(ORDER BY r.month), 0), 2) as raw_gross_mom_pct
    FROM raw_p r
    JOIN golden_p g ON r.month = g.month
    ORDER BY r.month;
""").df()

print("Monthly Waterfall Comparison (Raw Gross vs. True Net Cash):")
print(res_waterfall.to_markdown(index=False))
