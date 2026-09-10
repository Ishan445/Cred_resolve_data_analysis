import duckdb
import pandas as pd
import numpy as np

# Setup Golden Tables
exec(open(r"scripts/setup_golden_duckdb.py").read())

print("=== STARTING PHASE 4: DRIVER ANALYSIS (WHY DID IT HAPPEN?) ===")

# ----------------------------------------------------------------------
# 1. DRIVER BY LOAN TYPE
# ----------------------------------------------------------------------
print("\n--- 1. Performance by Loan Type ---")
loan_driver = con.execute("""
    WITH loan_base AS (
        SELECT 
            a.loan_type,
            COUNT(DISTINCT a.account_id) as total_accounts,
            ROUND(SUM(a.outstanding_amount) / 1e7, 2) as total_outstanding_cr,
            ROUND(AVG(a.outstanding_amount), 2) as avg_outstanding
        FROM golden_accounts a
        GROUP BY a.loan_type
    ),
    loan_cash AS (
        SELECT 
            a.loan_type,
            COUNT(DISTINCT p.payment_id) as total_payments,
            COUNT(DISTINCT CASE WHEN p.payment_status = 'SUCCESS' THEN p.payment_id END) as success_payments,
            ROUND(SUM(CASE WHEN p.payment_status = 'SUCCESS' THEN p.amount ELSE 0 END) / 1e7, 2) as success_cash_cr,
            ROUND(SUM(CASE WHEN p.payment_status = 'REVERSED' THEN p.amount ELSE 0 END) / 1e7, 2) as reversed_cash_cr,
            ROUND((SUM(CASE WHEN p.payment_status = 'SUCCESS' THEN p.amount ELSE 0 END) - 
                   SUM(CASE WHEN p.payment_status = 'REVERSED' THEN p.amount ELSE 0 END)) / 1e7, 2) as net_cash_cr
        FROM golden_payments p
        JOIN golden_accounts a ON p.account_id = a.account_id
        GROUP BY a.loan_type
    )
    SELECT 
        b.loan_type,
        b.total_accounts,
        b.total_outstanding_cr,
        c.net_cash_cr,
        ROUND(c.net_cash_cr * 100.0 / b.total_outstanding_cr, 2) as recovery_rate_pct,
        ROUND(c.net_cash_cr * 1e7 / b.total_accounts, 2) as recovery_per_account
    FROM loan_base b
    JOIN loan_cash c ON b.loan_type = c.loan_type
    ORDER BY recovery_rate_pct DESC;
""").df()
print(loan_driver.to_markdown(index=False))

# ----------------------------------------------------------------------
# 2. DRIVER BY DPD BUCKET
# ----------------------------------------------------------------------
print("\n--- 2. Performance by DPD Delinquency Bucket ---")
dpd_driver = con.execute("""
    WITH dpd_base AS (
        SELECT 
            CASE 
                WHEN dpd = 0 THEN '0 DPD (Current)'
                WHEN dpd BETWEEN 1 AND 29 THEN '1-29 DPD (Early)'
                WHEN dpd BETWEEN 30 AND 59 THEN '30-59 DPD (Mid)'
                WHEN dpd BETWEEN 60 AND 89 THEN '60-89 DPD (Hard)'
                WHEN dpd >= 90 THEN '90+ DPD (NPA)'
            END as dpd_segment,
            COUNT(DISTINCT account_id) as total_accounts,
            ROUND(SUM(outstanding_amount) / 1e7, 2) as total_outstanding_cr
        FROM golden_accounts
        GROUP BY dpd_segment
    ),
    dpd_cash AS (
        SELECT 
            CASE 
                WHEN a.dpd = 0 THEN '0 DPD (Current)'
                WHEN a.dpd BETWEEN 1 AND 29 THEN '1-29 DPD (Early)'
                WHEN a.dpd BETWEEN 30 AND 59 THEN '30-59 DPD (Mid)'
                WHEN a.dpd BETWEEN 60 AND 89 THEN '60-89 DPD (Hard)'
                WHEN a.dpd >= 90 THEN '90+ DPD (NPA)'
            END as dpd_segment,
            ROUND((SUM(CASE WHEN p.payment_status = 'SUCCESS' THEN p.amount ELSE 0 END) - 
                   SUM(CASE WHEN p.payment_status = 'REVERSED' THEN p.amount ELSE 0 END)) / 1e7, 2) as net_cash_cr
        FROM golden_payments p
        JOIN golden_accounts a ON p.account_id = a.account_id
        GROUP BY dpd_segment
    )
    SELECT 
        b.dpd_segment,
        b.total_accounts,
        b.total_outstanding_cr,
        c.net_cash_cr,
        ROUND(c.net_cash_cr * 100.0 / b.total_outstanding_cr, 2) as recovery_rate_pct,
        ROUND(c.net_cash_cr * 1e7 / b.total_accounts, 2) as recovery_per_account
    FROM dpd_base b
    JOIN dpd_cash c ON b.dpd_segment = c.dpd_segment
    ORDER BY b.total_outstanding_cr DESC;
""").df()
print(dpd_driver.to_markdown(index=False))

# ----------------------------------------------------------------------
# 3. DRIVER BY GEOGRAPHY & REGIONAL LINGUISTIC PROXY (ASM-008)
# ----------------------------------------------------------------------
print("\n--- 3. Performance by State & Regional Linguistic Proxy (ASM-008) ---")
# To prevent 1:N explosion on borrower_id, collapse borrower geography to 1:1 lookup by latest updated_at
con.execute("""
    CREATE OR REPLACE TEMP TABLE dim_borrower_geo AS
    SELECT borrower_id, state, city FROM (
        SELECT borrower_id, state, city, ROW_NUMBER() OVER(PARTITION BY borrower_id ORDER BY updated_at DESC) as rn
        FROM golden_borrowers
    ) WHERE rn = 1;
""")

geo_driver = con.execute("""
    WITH geo_base AS (
        SELECT 
            b.state,
            COUNT(DISTINCT a.account_id) as total_accounts,
            ROUND(SUM(a.outstanding_amount) / 1e7, 2) as total_outstanding_cr
        FROM golden_accounts a
        JOIN dim_borrower_geo b ON a.borrower_id = b.borrower_id
        GROUP BY b.state
    ),
    geo_cash AS (
        SELECT 
            b.state,
            ROUND((SUM(CASE WHEN p.payment_status = 'SUCCESS' THEN p.amount ELSE 0 END) - 
                   SUM(CASE WHEN p.payment_status = 'REVERSED' THEN p.amount ELSE 0 END)) / 1e7, 2) as net_cash_cr
        FROM golden_payments p
        JOIN golden_accounts a ON p.account_id = a.account_id
        JOIN dim_borrower_geo b ON a.borrower_id = b.borrower_id
        GROUP BY b.state
    ),
    geo_calls AS (
        SELECT 
            b.state,
            COUNT(*) as total_calls,
            ROUND(COUNT(CASE WHEN c.call_status = 'ANSWERED' THEN 1 END) * 100.0 / COUNT(*), 2) as answer_rate_pct
        FROM golden_calls c
        JOIN golden_accounts a ON c.account_id = a.account_id
        JOIN dim_borrower_geo b ON a.borrower_id = b.borrower_id
        GROUP BY b.state
    )
    SELECT 
        g.state,
        g.total_accounts,
        g.total_outstanding_cr,
        c.net_cash_cr,
        ROUND(c.net_cash_cr * 100.0 / g.total_outstanding_cr, 2) as recovery_rate_pct,
        cl.total_calls,
        cl.answer_rate_pct
    FROM geo_base g
    JOIN geo_cash c ON g.state = c.state
    JOIN geo_calls cl ON g.state = cl.state
    ORDER BY recovery_rate_pct DESC;
""").df()
print(geo_driver.to_markdown(index=False))

# ----------------------------------------------------------------------
# 4. DRIVER BY CHANNEL AT 7-DAY ATTRIBUTION
# ----------------------------------------------------------------------
print("\n--- 4. Channel Efficiency & Multi-Touch Realized Recovery ---")
channel_driver = con.execute("""
    WITH success_payments AS (
        SELECT payment_id, account_id, amount, event_at::TIMESTAMP as paid_at
        FROM golden_payments
        WHERE payment_status = 'SUCCESS'
    ),
    channel_touches AS (
        SELECT p.payment_id, p.amount,
               MAX(CASE WHEN c.call_id IS NOT NULL THEN 1 ELSE 0 END) as touch_call,
               MAX(CASE WHEN w.whatsapp_event_id IS NOT NULL THEN 1 ELSE 0 END) as touch_wa,
               MAX(CASE WHEN s.sms_event_id IS NOT NULL THEN 1 ELSE 0 END) as touch_sms,
               MAX(CASE WHEN f.visit_id IS NOT NULL THEN 1 ELSE 0 END) as touch_field
        FROM success_payments p
        LEFT JOIN golden_calls c ON p.account_id = c.account_id 
             AND c.event_at::TIMESTAMP <= p.paid_at 
             AND c.event_at::TIMESTAMP >= p.paid_at - INTERVAL '7 days'
        LEFT JOIN golden_whatsapp_events w ON p.account_id = w.account_id 
             AND w.event_at::TIMESTAMP <= p.paid_at 
             AND w.event_at::TIMESTAMP >= p.paid_at - INTERVAL '7 days'
        LEFT JOIN golden_sms_events s ON p.account_id = s.account_id 
             AND s.event_at::TIMESTAMP <= p.paid_at 
             AND s.event_at::TIMESTAMP >= p.paid_at - INTERVAL '7 days'
        LEFT JOIN golden_field_visits f ON p.account_id = f.account_id 
             AND f.event_at::TIMESTAMP <= p.paid_at 
             AND f.event_at::TIMESTAMP >= p.paid_at - INTERVAL '7 days'
        GROUP BY p.payment_id, p.amount
    )
    SELECT 
        SUM(CASE WHEN touch_call=0 AND touch_wa=0 AND touch_sms=0 AND touch_field=0 THEN 1 ELSE 0 END) as organic_txns,
        ROUND(SUM(CASE WHEN touch_call=0 AND touch_wa=0 AND touch_sms=0 AND touch_field=0 THEN amount ELSE 0 END) / 1e7, 2) as organic_cash_cr,
        SUM(touch_call) as call_txns,
        ROUND(SUM(CASE WHEN touch_call = 1 THEN amount ELSE 0 END) / 1e7, 2) as call_cash_cr,
        SUM(touch_wa) as wa_txns,
        ROUND(SUM(CASE WHEN touch_wa = 1 THEN amount ELSE 0 END) / 1e7, 2) as wa_cash_cr,
        SUM(touch_sms) as sms_txns,
        ROUND(SUM(CASE WHEN touch_sms = 1 THEN amount ELSE 0 END) / 1e7, 2) as sms_cash_cr,
        SUM(touch_field) as field_txns,
        ROUND(SUM(CASE WHEN touch_field = 1 THEN amount ELSE 0 END) / 1e7, 2) as field_cash_cr
    FROM channel_touches;
""").df()
print(channel_driver.to_markdown(index=False))

# ----------------------------------------------------------------------
# 5. TELEPHONY VENDOR CONNECTIVITY & DESK CAPACITY
# ----------------------------------------------------------------------
print("\n--- 5. Telephony Vendor Connect Performance ---")
vendor_driver = con.execute("""
    SELECT 
        COALESCE(c.vendor_id, 'UNKNOWN') as vendor_id,
        COUNT(*) as total_dials,
        COUNT(CASE WHEN c.call_status = 'ANSWERED' THEN 1 END) as answered_calls,
        ROUND(COUNT(CASE WHEN c.call_status = 'ANSWERED' THEN 1 END) * 100.0 / COUNT(*), 2) as answer_rate_pct,
        ROUND(AVG(c.duration_sec), 1) as avg_duration_sec
    FROM golden_calls c
    GROUP BY vendor_id
    ORDER BY total_dials DESC;
""").df()
print(vendor_driver.to_markdown(index=False))
