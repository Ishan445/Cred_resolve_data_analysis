-- ==============================================================================
-- 05_executive_kpis.sql: Standardized Executive KPI Queries
-- Reusable, auditable metrics powering executive reporting and dashboards.
-- ==============================================================================

-- 1. Audited Monthly Financial Inflow & True MoM Growth
SELECT 
    payment_month,
    COUNT(*) AS total_payment_attempts,
    ROUND(SUM(amount) / 1e7, 2) AS gross_cash_cr,
    COUNT(CASE WHEN payment_status = 'SUCCESS' THEN 1 END) AS success_txns,
    ROUND(SUM(success_cash) / 1e7, 2) AS success_cash_cr,
    ROUND(SUM(reversed_cash) / 1e7, 2) AS reversed_cash_cr,
    ROUND(SUM(net_realized_cash) / 1e7, 2) AS net_realized_cash_cr,
    ROUND(
        (SUM(net_realized_cash) - LAG(SUM(net_realized_cash)) OVER(ORDER BY payment_month)) * 100.0 
        / NULLIF(LAG(SUM(net_realized_cash)) OVER(ORDER BY payment_month), 0), 
        2
    ) AS mom_net_growth_pct
FROM fct_payments
WHERE payment_month <= '2026-07'
GROUP BY payment_month
ORDER BY payment_month;

-- 2. Disentangled Contact Rate vs Dial Answer Rate
SELECT 
    STRFTIME(event_at, '%Y-%m') AS month,
    COUNT(DISTINCT account_id) AS attempted_accounts,
    COUNT(DISTINCT CASE WHEN interaction_status = 'ANSWERED' THEN account_id END) AS contacted_accounts,
    ROUND(
        COUNT(DISTINCT CASE WHEN interaction_status = 'ANSWERED' THEN account_id END) * 100.0 
        / COUNT(DISTINCT account_id), 
        2
    ) AS account_contact_rate_pct,
    COUNT(*) AS total_dials,
    COUNT(CASE WHEN interaction_status = 'ANSWERED' THEN 1 END) AS answered_calls,
    ROUND(
        COUNT(CASE WHEN interaction_status = 'ANSWERED' THEN 1 END) * 100.0 
        / COUNT(*), 
        2
    ) AS call_level_answer_rate_pct
FROM fct_touchpoints
WHERE channel = 'CALL' AND STRFTIME(event_at, '%Y-%m') <= '2026-07'
GROUP BY month
ORDER BY month;
