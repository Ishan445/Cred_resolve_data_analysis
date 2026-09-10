import os
import duckdb
import pandas as pd

data_dir = r"data/raw".replace('\\', '/')
con = duckdb.connect()

# Set up tables
exec(open(r"scripts\setup_golden_duckdb.py").read())

print("\n=======================================================")
print("=== 1. FORENSIC A: DUPLICATE PAYMENTS & RETRY ANALYSIS ===")
print("=======================================================")
# Check distribution of payment statuses across months
res_pay_status = con.execute("""
    SELECT 
        STRFTIME(event_at::TIMESTAMP, '%Y-%m') AS month,
        COUNT(*) AS total_txns,
        ROUND(SUM(amount)/1e7, 2) AS gross_cr,
        ROUND(SUM(CASE WHEN payment_status = 'SUCCESS' THEN amount ELSE 0 END)/1e7, 2) AS success_cr,
        ROUND(SUM(CASE WHEN payment_status = 'FAILED' THEN amount ELSE 0 END)/1e7, 2) AS failed_cr,
        ROUND(SUM(CASE WHEN payment_status = 'REVERSED' THEN amount ELSE 0 END)/1e7, 2) AS reversed_cr,
        ROUND(SUM(CASE WHEN payment_status = 'PENDING' THEN amount ELSE 0 END)/1e7, 2) AS pending_cr,
        ROUND(COUNT(CASE WHEN payment_status = 'SUCCESS' THEN 1 END) * 100.0 / COUNT(*), 2) AS success_rate_pct
    FROM golden_payments
    GROUP BY month
    ORDER BY month;
""").df()
print(res_pay_status.to_markdown(index=False))

print("\n=======================================================")
print("=== 2. FORENSIC C: TIMEZONE NORMALIZATION & SHIFTS ===")
print("=======================================================")
# Normalize calling hours: Convert UTC and Asia/Dubai to Asia/Kolkata
con.execute("""
    CREATE OR REPLACE TABLE golden_calls_ist AS
    SELECT 
        *,
        event_at::TIMESTAMP AS raw_timestamp,
        CASE 
            WHEN timezone = 'UTC' THEN event_at::TIMESTAMP + INTERVAL '5 hours 30 minutes'
            WHEN timezone = 'Asia/Dubai' THEN event_at::TIMESTAMP + INTERVAL '1 hour 30 minutes'
            WHEN timezone = 'Asia/Kolkata' THEN event_at::TIMESTAMP
            ELSE event_at::TIMESTAMP
        END AS ist_timestamp
    FROM golden_calls;
""")

res_tz_shift = con.execute("""
    SELECT 
        EXTRACT(HOUR FROM raw_timestamp) AS raw_hour,
        COUNT(*) AS raw_hour_calls,
        EXTRACT(HOUR FROM ist_timestamp) AS ist_hour,
        COUNT(*) AS ist_hour_calls
    FROM golden_calls_ist
    GROUP BY raw_hour, ist_hour
    ORDER BY raw_hour, ist_hour
    LIMIT 10;
""").df()

res_hourly = con.execute("""
    SELECT 
        h AS hour_of_day,
        COUNT(CASE WHEN EXTRACT(HOUR FROM raw_timestamp) = h THEN 1 END) AS raw_calls,
        COUNT(CASE WHEN EXTRACT(HOUR FROM ist_timestamp) = h THEN 1 END) AS ist_calls,
        ROUND(COUNT(CASE WHEN EXTRACT(HOUR FROM ist_timestamp) = h AND call_status = 'ANSWERED' THEN 1 END) * 100.0 / 
              NULLIF(COUNT(CASE WHEN EXTRACT(HOUR FROM ist_timestamp) = h THEN 1 END), 0), 2) AS ist_answer_rate_pct
    FROM (SELECT UNNEST(GENERATE_SERIES(0, 23)) AS h) hours
    CROSS JOIN golden_calls_ist
    GROUP BY h
    ORDER BY h;
""").df()
print("Hourly Calling Profile (Raw vs IST Normalized):")
print(res_hourly.to_markdown(index=False))

print("\n=======================================================")
print("=== 3. FORENSIC D: TELEPHONY VENDOR DISPOSITION SHIFTS ===")
print("=======================================================")
# Join calls, call_dispositions, and vendor_telephony
res_vendor_disp = con.execute("""
    SELECT 
        v.vendor_name,
        d.disposition_version,
        d.disposition_code,
        COUNT(*) AS cnt,
        ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(PARTITION BY v.vendor_name, d.disposition_version), 2) AS pct_within_version
    FROM golden_call_dispositions d
    JOIN golden_calls c ON d.call_id = c.call_id
    JOIN golden_vendor_telephony v ON c.vendor_id = v.vendor_id
    GROUP BY v.vendor_name, d.disposition_version, d.disposition_code
    ORDER BY v.vendor_name, d.disposition_version, cnt DESC;
""").df()
print("Sample of Vendor Disposition Drift across Disposition Versions:")
print(res_vendor_disp.head(25).to_markdown(index=False))

# Check monthly disposition version usage
res_disp_version_month = con.execute("""
    SELECT 
        STRFTIME(event_at::TIMESTAMP, '%Y-%m') AS month,
        disposition_version,
        COUNT(*) AS cnt
    FROM golden_call_dispositions
    GROUP BY month, disposition_version
    ORDER BY month, disposition_version;
""").df()
print("\nMonthly Distribution of Disposition Version:")
print(res_disp_version_month.to_markdown(index=False))

print("\n=======================================================")
print("=== 4. FORENSIC H: CAMPAIGN DEFINITION INCONSISTENCY & LEAKAGE ===")
print("=======================================================")
# Audit all 120 campaigns
res_camp = con.execute("""
    SELECT 
        campaign_name,
        target_definition,
        strategy_version,
        COUNT(*) AS count_campaigns,
        MIN(start_at) AS min_start,
        MAX(end_at) AS max_end
    FROM golden_campaigns
    GROUP BY campaign_name, target_definition, strategy_version
    ORDER BY campaign_name, target_definition, strategy_version;
""").df()
print("Campaign Target Definitions vs Strategy Versions (Semantic Consistency):")
print(res_camp.to_markdown(index=False))

# Check targeting rule adherence (Leakage check):
# Verify if accounts targeted under DPD>=30 actually had DPD>=30
res_leakage = con.execute("""
    SELECT 
        c.target_definition,
        COUNT(*) AS total_targeted,
        COUNT(CASE 
            WHEN c.target_definition = 'DPD>=30' AND a.dpd >= 30 THEN 1
            WHEN c.target_definition = 'DPD>=60' AND a.dpd >= 60 THEN 1
            WHEN c.target_definition = 'HIGH_RISK' AND a.risk_segment IN ('HIGH', 'NPA') THEN 1
            WHEN c.target_definition = 'NPA' AND a.risk_segment = 'NPA' THEN 1
            WHEN c.target_definition = 'PROMISE_BROKEN' THEN 1 -- checked separately
            ELSE NULL 
        END) AS strictly_compliant_accounts,
        ROUND(COUNT(CASE 
            WHEN c.target_definition = 'DPD>=30' AND a.dpd < 30 THEN 1
            WHEN c.target_definition = 'DPD>=60' AND a.dpd < 60 THEN 1
            ELSE NULL 
        END) * 100.0 / COUNT(*), 2) AS dpd_leakage_pct
    FROM golden_daily_targeting t
    JOIN golden_campaigns c ON t.campaign_id = c.campaign_id
    JOIN golden_accounts a ON t.account_id = a.account_id
    GROUP BY c.target_definition;
""").df()
print("\nTargeting Rule Adherence & DPD Leakage Check:")
print(res_leakage.to_markdown(index=False))

print("\n=======================================================")
print("=== 5. FORENSIC G: DENOMINATOR MANIPULATION & SURVIVORSHIP ===")
print("=======================================================")
res_active_pool = con.execute("""
    SELECT 
        STRFTIME(target_date::TIMESTAMP, '%Y-%m') AS month,
        COUNT(DISTINCT account_id) AS unique_targeted_accounts,
        COUNT(*) AS total_targeting_assignments
    FROM golden_daily_targeting
    GROUP BY month
    ORDER BY month;
""").df()
print("Monthly Unique Accounts in Active Targeting Pool:")
print(res_active_pool.to_markdown(index=False))

# Check status transitions in account_status_history
res_status_trans = con.execute("""
    SELECT 
        STRFTIME(event_at::TIMESTAMP, '%Y-%m') AS month,
        status,
        COUNT(*) AS status_changes
    FROM golden_status_history
    GROUP BY month, status
    ORDER BY month, status;
""").df()
print("\nMonthly Account Status Transitions (Write-Off / Closed / Delinquent):")
print(res_status_trans.head(30).to_markdown(index=False))

print("\n=======================================================")
print("=== 6. CONDUCT & COMPLAINTS ATTRIBUTION (Time-Proximity) ===")
print("=======================================================")
# Complaints breakdown by type & severity
res_comp_type = con.execute("""
    SELECT 
        complaint_type,
        severity,
        COUNT(*) AS count_complaints,
        ROUND(COUNT(*) * 100.0 / 8000, 2) AS pct_total
    FROM golden_complaints
    GROUP BY complaint_type, severity
    ORDER BY count_complaints DESC;
""").df()
print("Complaints Breakdown by Type & Severity:")
print(res_comp_type.head(15).to_markdown(index=False))

# Attribute complaint to nearest preceding interaction within 14 days
# Interleaving calls, field visits, whatsapp, sms
con.execute("""
    CREATE OR REPLACE TABLE all_interactions AS
    SELECT account_id, event_at::TIMESTAMP AS interaction_at, 'CALL' AS channel, agent_id, vendor_id, campaign_id FROM golden_calls
    UNION ALL
    SELECT account_id, event_at::TIMESTAMP, 'FIELD', agent_id, NULL, NULL FROM golden_field_visits
    UNION ALL
    SELECT account_id, event_at::TIMESTAMP, 'WHATSAPP', NULL, provider_id, NULL FROM golden_whatsapp_events
    UNION ALL
    SELECT account_id, event_at::TIMESTAMP, 'SMS', NULL, provider_id, NULL FROM golden_sms_events;
""")

res_complaint_attribution = con.execute("""
    WITH ranked_interactions AS (
        SELECT 
            c.complaint_id,
            c.account_id,
            c.complaint_type,
            c.severity,
            c.event_at AS complaint_at,
            i.channel,
            i.interaction_at,
            date_diff('hour', i.interaction_at, c.event_at::TIMESTAMP) AS hours_lag,
            ROW_NUMBER() OVER(
                PARTITION BY c.complaint_id 
                ORDER BY i.interaction_at DESC
            ) AS rn
        FROM golden_complaints c
        JOIN all_interactions i 
          ON c.account_id = i.account_id 
         AND i.interaction_at <= c.event_at::TIMESTAMP
         AND i.interaction_at >= c.event_at::TIMESTAMP - INTERVAL '14 days'
    )
    SELECT 
        channel,
        COUNT(*) AS attributed_complaints,
        ROUND(COUNT(*) * 100.0 / 8000, 2) AS pct_attributed,
        ROUND(AVG(hours_lag), 1) AS avg_hours_to_complaint
    FROM ranked_interactions
    WHERE rn = 1
    GROUP BY channel
    ORDER BY attributed_complaints DESC;
""").df()
print("\nComplaints Attributed to Preceding Operational Touchpoint (14-Day Proximity):")
print(res_complaint_attribution.to_markdown(index=False))
