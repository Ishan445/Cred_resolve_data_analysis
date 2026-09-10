import duckdb
import pandas as pd
import numpy as np

# Setup Golden Tables
exec(open(r"scripts/setup_golden_duckdb.py").read())

print("================================================================================")
print("PHASE 4: DRIVER ANALYSIS (WHY DID IT HAPPEN?) — COMPREHENSIVE EXECUTION")
print("================================================================================")

# ------------------------------------------------------------------------------
# 1. DRIVER: LOAN TYPE (PORTFOLIO MIX)
# ------------------------------------------------------------------------------
print("\n--- 1. Portfolio Mix: Loan Type Performance ---")
df_loan = con.execute("""
    WITH loan_base AS (
        SELECT 
            loan_type,
            COUNT(DISTINCT account_id) as accounts,
            ROUND(SUM(outstanding_amount) / 1e7, 2) as outstanding_cr,
            ROUND(AVG(outstanding_amount), 2) as avg_outstanding
        FROM golden_accounts
        GROUP BY loan_type
    ),
    loan_cash AS (
        SELECT 
            a.loan_type,
            COUNT(DISTINCT p.payment_id) as total_txns,
            COUNT(DISTINCT CASE WHEN p.payment_status = 'SUCCESS' THEN p.payment_id END) as success_txns,
            ROUND((SUM(CASE WHEN p.payment_status = 'SUCCESS' THEN p.amount ELSE 0 END) - 
                   SUM(CASE WHEN p.payment_status = 'REVERSED' THEN p.amount ELSE 0 END)) / 1e7, 2) as net_cash_cr
        FROM golden_payments p
        JOIN golden_accounts a ON p.account_id = a.account_id
        GROUP BY a.loan_type
    )
    SELECT 
        b.loan_type,
        b.accounts,
        b.outstanding_cr,
        c.net_cash_cr,
        ROUND(c.net_cash_cr * 100.0 / b.outstanding_cr, 2) as recovery_rate_pct,
        ROUND(c.net_cash_cr * 1e7 / b.accounts, 2) as recovery_per_account
    FROM loan_base b
    JOIN loan_cash c ON b.loan_type = c.loan_type
    ORDER BY recovery_rate_pct DESC;
""").df()
print(df_loan.to_markdown(index=False))

# ------------------------------------------------------------------------------
# 2. DRIVER: DPD DELINQUENCY VINTAGE
# ------------------------------------------------------------------------------
print("\n--- 2. Delinquency Vintage: DPD Buckets ---")
df_dpd = con.execute("""
    WITH dpd_base AS (
        SELECT 
            CASE 
                WHEN dpd = 0 THEN '0 DPD (Current)'
                WHEN dpd BETWEEN 1 AND 29 THEN '1-29 DPD (Early)'
                WHEN dpd BETWEEN 30 AND 59 THEN '30-59 DPD (Mid)'
                WHEN dpd BETWEEN 60 AND 89 THEN '60-89 DPD (Hard)'
                WHEN dpd >= 90 THEN '90+ DPD (NPA)'
            END as dpd_tier,
            COUNT(DISTINCT account_id) as accounts,
            ROUND(SUM(outstanding_amount) / 1e7, 2) as outstanding_cr
        FROM golden_accounts
        GROUP BY dpd_tier
    ),
    dpd_cash AS (
        SELECT 
            CASE 
                WHEN a.dpd = 0 THEN '0 DPD (Current)'
                WHEN a.dpd BETWEEN 1 AND 29 THEN '1-29 DPD (Early)'
                WHEN a.dpd BETWEEN 30 AND 59 THEN '30-59 DPD (Mid)'
                WHEN a.dpd BETWEEN 60 AND 89 THEN '60-89 DPD (Hard)'
                WHEN a.dpd >= 90 THEN '90+ DPD (NPA)'
            END as dpd_tier,
            ROUND((SUM(CASE WHEN p.payment_status = 'SUCCESS' THEN p.amount ELSE 0 END) - 
                   SUM(CASE WHEN p.payment_status = 'REVERSED' THEN p.amount ELSE 0 END)) / 1e7, 2) as net_cash_cr
        FROM golden_payments p
        JOIN golden_accounts a ON p.account_id = a.account_id
        GROUP BY dpd_tier
    )
    SELECT 
        b.dpd_tier,
        b.accounts,
        b.outstanding_cr,
        c.net_cash_cr,
        ROUND(c.net_cash_cr * 100.0 / b.outstanding_cr, 2) as recovery_rate_pct,
        ROUND(c.net_cash_cr * 1e7 / b.accounts, 2) as recovery_per_account
    FROM dpd_base b
    JOIN dpd_cash c ON b.dpd_tier = c.dpd_tier
    ORDER BY b.outstanding_cr DESC;
""").df()
print(df_dpd.to_markdown(index=False))

# ------------------------------------------------------------------------------
# 3. DRIVER: BORROWER RISK SEGMENT
# ------------------------------------------------------------------------------
print("\n--- 3. Borrower Risk Segment ---")
df_risk = con.execute("""
    WITH risk_base AS (
        SELECT 
            risk_segment,
            COUNT(DISTINCT account_id) as accounts,
            ROUND(SUM(outstanding_amount) / 1e7, 2) as outstanding_cr
        FROM golden_accounts
        GROUP BY risk_segment
    ),
    risk_cash AS (
        SELECT 
            a.risk_segment,
            ROUND((SUM(CASE WHEN p.payment_status = 'SUCCESS' THEN p.amount ELSE 0 END) - 
                   SUM(CASE WHEN p.payment_status = 'REVERSED' THEN p.amount ELSE 0 END)) / 1e7, 2) as net_cash_cr
        FROM golden_payments p
        JOIN golden_accounts a ON p.account_id = a.account_id
        GROUP BY a.risk_segment
    )
    SELECT 
        b.risk_segment,
        b.accounts,
        b.outstanding_cr,
        c.net_cash_cr,
        ROUND(c.net_cash_cr * 100.0 / b.outstanding_cr, 2) as recovery_rate_pct,
        ROUND(c.net_cash_cr * 1e7 / b.accounts, 2) as recovery_per_account
    FROM risk_base b
    JOIN risk_cash c ON b.risk_segment = c.risk_segment
    ORDER BY recovery_rate_pct DESC;
""").df()
print(df_risk.to_markdown(index=False))

# ------------------------------------------------------------------------------
# 4. DRIVER: GEOGRAPHY & REGIONAL LINGUISTIC PROXY (ASM-008)
# ------------------------------------------------------------------------------
print("\n--- 4. Geography & Regional Linguistic Proxy (ASM-008) ---")
con.execute("""
    CREATE OR REPLACE TEMP TABLE dim_borrower_geo AS
    SELECT borrower_id, state, city FROM (
        SELECT borrower_id, state, city, ROW_NUMBER() OVER(PARTITION BY borrower_id ORDER BY updated_at DESC) as rn
        FROM golden_borrowers
    ) WHERE rn = 1;
""")

df_geo = con.execute("""
    WITH geo_base AS (
        SELECT 
            b.state,
            COUNT(DISTINCT a.account_id) as accounts,
            ROUND(SUM(a.outstanding_amount) / 1e7, 2) as outstanding_cr
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
            COUNT(DISTINCT CASE WHEN c.call_status = 'ANSWERED' THEN c.account_id END) as contacted_accs,
            COUNT(DISTINCT c.account_id) as attempted_accs,
            ROUND(COUNT(CASE WHEN c.call_status = 'ANSWERED' THEN 1 END) * 100.0 / COUNT(*), 2) as call_answer_rate_pct
        FROM golden_calls c
        JOIN golden_accounts a ON c.account_id = a.account_id
        JOIN dim_borrower_geo b ON a.borrower_id = b.borrower_id
        GROUP BY b.state
    )
    SELECT 
        g.state,
        g.accounts,
        g.outstanding_cr,
        c.net_cash_cr,
        ROUND(c.net_cash_cr * 100.0 / g.outstanding_cr, 2) as recovery_rate_pct,
        cl.total_calls,
        ROUND(cl.contacted_accs * 100.0 / cl.attempted_accs, 2) as account_contact_rate_pct,
        cl.call_answer_rate_pct
    FROM geo_base g
    JOIN geo_cash c ON g.state = c.state
    JOIN geo_calls cl ON g.state = cl.state
    ORDER BY recovery_rate_pct DESC;
""").df()
print(df_geo.to_markdown(index=False))

# ------------------------------------------------------------------------------
# 5. DRIVER: MULTI-TOUCH CHANNEL ATTRIBUTION (7D LOOKBACK)
# ------------------------------------------------------------------------------
print("\n--- 5. Channel Driver: Multi-Touch & Organic Recovery ---")
df_channel = con.execute("""
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
        'Pure Organic (No touch in 7d)' as touchpoint_channel,
        SUM(CASE WHEN touch_call=0 AND touch_wa=0 AND touch_sms=0 AND touch_field=0 THEN 1 ELSE 0 END) as txns,
        ROUND(SUM(CASE WHEN touch_call=0 AND touch_wa=0 AND touch_sms=0 AND touch_field=0 THEN amount ELSE 0 END) / 1e7, 2) as cash_cr,
        ROUND(SUM(CASE WHEN touch_call=0 AND touch_wa=0 AND touch_sms=0 AND touch_field=0 THEN amount ELSE 0 END) * 100.0 / (SELECT SUM(amount) FROM success_payments), 2) as pct_of_success_cash
    FROM channel_touches
    UNION ALL
    SELECT 
        'Human Voice (Calls within 7d)',
        SUM(touch_call),
        ROUND(SUM(CASE WHEN touch_call = 1 THEN amount ELSE 0 END) / 1e7, 2),
        ROUND(SUM(CASE WHEN touch_call = 1 THEN amount ELSE 0 END) * 100.0 / (SELECT SUM(amount) FROM success_payments), 2)
    FROM channel_touches
    UNION ALL
    SELECT 
        'WhatsApp Interaction (within 7d)',
        SUM(touch_wa),
        ROUND(SUM(CASE WHEN touch_wa = 1 THEN amount ELSE 0 END) / 1e7, 2),
        ROUND(SUM(CASE WHEN touch_wa = 1 THEN amount ELSE 0 END) * 100.0 / (SELECT SUM(amount) FROM success_payments), 2)
    FROM channel_touches
    UNION ALL
    SELECT 
        'SMS Reminder (within 7d)',
        SUM(touch_sms),
        ROUND(SUM(CASE WHEN touch_sms = 1 THEN amount ELSE 0 END) / 1e7, 2),
        ROUND(SUM(CASE WHEN touch_sms = 1 THEN amount ELSE 0 END) * 100.0 / (SELECT SUM(amount) FROM success_payments), 2)
    FROM channel_touches
    UNION ALL
    SELECT 
        'Field Visit (within 7d)',
        SUM(touch_field),
        ROUND(SUM(CASE WHEN touch_field = 1 THEN amount ELSE 0 END) / 1e7, 2),
        ROUND(SUM(CASE WHEN touch_field = 1 THEN amount ELSE 0 END) * 100.0 / (SELECT SUM(amount) FROM success_payments), 2)
    FROM channel_touches;
""").df()
print(df_channel.to_markdown(index=False))

# ------------------------------------------------------------------------------
# 6. DRIVER: CALLING TIME & HOURLY WINDOWS (IST-NORMALIZED)
# ------------------------------------------------------------------------------
print("\n--- 6. Calling Time: Hourly Windows (IST Normalized) ---")
df_hourly = con.execute("""
    WITH ist_calls AS (
        SELECT 
            CASE 
                WHEN timezone = 'UTC' THEN event_at::TIMESTAMP + INTERVAL '5 hours 30 minutes'
                WHEN timezone = 'Asia/Dubai' THEN event_at::TIMESTAMP + INTERVAL '1 hour 30 minutes'
                ELSE event_at::TIMESTAMP
            END as ist_time,
            call_status,
            account_id
        FROM golden_calls
    )
    SELECT 
        STRFTIME(ist_time, '%H:00') as call_hour_ist,
        COUNT(*) as total_dials,
        COUNT(DISTINCT account_id) as accounts_attempted,
        COUNT(CASE WHEN call_status = 'ANSWERED' THEN 1 END) as answered_calls,
        ROUND(COUNT(CASE WHEN call_status = 'ANSWERED' THEN 1 END) * 100.0 / COUNT(*), 2) as call_answer_rate_pct
    FROM ist_calls
    GROUP BY call_hour_ist
    ORDER BY call_hour_ist;
""").df()
print(df_hourly.to_markdown(index=False))

# ------------------------------------------------------------------------------
# 7. DRIVER: ATTEMPT FREQUENCY & DIMINISHING RETURNS
# ------------------------------------------------------------------------------
print("\n--- 7. Attempt Frequency: Dial Repetitions per Account ---")
df_freq = con.execute("""
    WITH account_dials AS (
        SELECT 
            account_id,
            COUNT(*) as total_dials,
            COUNT(CASE WHEN call_status = 'ANSWERED' THEN 1 END) as answered_calls
        FROM golden_calls
        GROUP BY account_id
    )
    SELECT 
        CASE 
            WHEN total_dials = 1 THEN '1 Dial'
            WHEN total_dials = 2 THEN '2 Dials'
            WHEN total_dials = 3 THEN '3 Dials'
            WHEN total_dials BETWEEN 4 AND 5 THEN '4-5 Dials'
            ELSE '6+ Dials'
        END as dial_bracket,
        COUNT(*) as total_accounts,
        SUM(total_dials) as total_dials_in_bracket,
        SUM(answered_calls) as total_answers,
        ROUND(SUM(answered_calls) * 100.0 / SUM(total_dials), 2) as answer_rate_pct,
        ROUND(COUNT(CASE WHEN answered_calls > 0 THEN 1 END) * 100.0 / COUNT(*), 2) as account_reach_pct
    FROM account_dials
    GROUP BY dial_bracket
    ORDER BY MIN(total_dials);
""").df()
print(df_freq.to_markdown(index=False))

# ------------------------------------------------------------------------------
# 8. DRIVER: CAMPAIGN STRATEGY VERSIONS & TEMPORAL SPREAD
# ------------------------------------------------------------------------------
print("\n--- 8. Campaign Strategy Versions & Targeting Inflection ---")
df_camp = con.execute("""
    SELECT 
        strategy_version,
        COUNT(*) as campaign_count,
        MIN(start_at::DATE) as min_start,
        MAX(start_at::DATE) as max_start,
        MIN(end_at::DATE) as min_end,
        MAX(end_at::DATE) as max_end
    FROM golden_campaigns
    GROUP BY strategy_version
    ORDER BY min_start;
""").df()
print(df_camp.to_markdown(index=False))
