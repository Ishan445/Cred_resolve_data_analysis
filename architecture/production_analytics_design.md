# Production Analytics Platform Design & System Architecture

**Document Version:** 1.0.0  
**Target Deployment:** Enterprise Debt Collections Lakehouse  
**Author:** Forensic Data Engineering & Analytics Architecture Taskforce  

---

## 1. Executive Blueprint & Pipeline Flow

The end-to-end production architecture replaces fragile, unvalidated batch CSV feeds with a robust, event-driven Lakehouse design built around **Data Contracts**, **Automated Idempotent Transformations**, **Golden Analytical Marts**, and an **Intelligent Targeting Engine**.

The visual blueprint is maintained in declarative Mermaid format at [`architecture/system_architecture.mmd`](architecture/system_architecture.mmd).

---

## 2. Core Architectural Pillars

### 2.1 Pillar 1: Ingestion & Data Contracts Layer
To prevent the recurrence of generator bugs, key collisions, and unannounced schema drifts, all incoming operational feeds must satisfy explicit data contracts:
- **Contract Engine:** Enforced via Pydantic / Great Expectations schemas at the ingestion gateway.
- **Contract Rules:**
  1. **Strict Key Uniqueness:** Primary keys must be strictly unique within entity tables (`account_id` in accounts, `payment_id` in payments). Any collision routes immediately to the Quarantine DLQ.
  2. **Timestamp Normalization Contract:** Every event payload must include an ISO-8601 timestamp and an explicit IANA timezone tag (`Asia/Kolkata`). Any non-standard timezone triggers automatic conversion.
  3. **Payment Realization Contract:** Banking gateway feeds must provide terminal status flags (`SUCCESS`, `FAILED`, `REVERSED`, `PENDING`) and bank transaction IDs (`payment_reference`).

### 2.2 Pillar 2: Staging & Quarantine Isolation Layer (Bronze Tier)
- **Dead-Letter Queue (DLQ):** Records failing contract checks (e.g. orphan borrower IDs or non-canonical roster rows) are quarantined into `quarantine_events` with detailed `error_code` and `payload_json`.
- **Audit Ledger:** Maintains an auditable record of quarantined records without blocking downstream clean pipeline execution.

### 2.3 Pillar 3: Canonical Transformation Layer (Silver / DuckDB & dbt)
- **Idempotent De-duplication:** Uses windowed ranking (`ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)`) prioritizing populated reference columns and latest updates.
- **Timezone Standardization:** Standardizes all event feeds to Indian Standard Time (IST, UTC+05:30).
- **Entity Resolution Engine:**
  - Implements surrogate keys (`borrower_sk`) for borrower profiles.
  - Collapses agent operational rosters to canonical desk lookup (`dim_desks`) per **ASM-009**.
- **Attribution Engine:** Applies deterministic, mutually exclusive last-touch attribution (7-day and 14-day lookback windows) with priority ordering (`CALL` > `WHATSAPP` > `SMS` > `FIELD`).

### 2.4 Pillar 4: Golden Analytical Marts (Gold Tier)
Optimized columnar dimensional models for executive reporting:
1. `dim_accounts`: Account master, delinquency DPD, outstanding balance, risk segment.
2. `dim_desks`: Canonical desk capacity, active logins, logged session hours.
3. `fct_payments`: Net realized cash transactions, excluding non-realized attempts.
4. `fct_touchpoints`: Unified operational contact lineage across human calls, WhatsApp, SMS, and field visits.
5. `fct_complaints`: Time-proximity joined regulatory tickets linked to desk codes.

### 2.5 Pillar 5: Intelligent Targeting & Dynamic Propensity Engine (Winning Lever)
Implements the core intervention funded by the **₹10 Cr capital investment**:
- **Propensity Scoring Model:** Predicts debtor self-cure probability. Accounts with high self-cure probability are excluded from outbound dialers and routed to low-cost digital reminders.
- **Campaign Leakage Guardrails:** Hard algorithmic constraints preventing accounts with DPD < 60 from being targeted in hard collections campaigns, eliminating the audited 54.16% leakage.
- **Channel Arbitration:** Directs debtor accounts to the optimal channel (WhatsApp bot vs human voice vs SMS).

### 2.6 Pillar 6: C-Suite Consumption & Alerting
- **Streamlit Cockpit:** Real-time executive dashboard displaying audited net cash, contact rates, and interactive scenario modeling.
- **Automated Alerts:** Triggers Slack/PagerDuty notifications if:
  1. MoM net cash deviates by more than $\pm 5\%$.
  2. Campaign targeting leakage exceeds $1.0\%$.
  3. Single-desk complaint velocity exceeds 3 tickets in 24 hours.

---

## 3. SLA & Performance Standards

| Data Product | Ingestion Cadence | Transformation SLA | Query Latency Target | Data Retention |
|---|---|---|---|---|
| Gateway Payments | Real-time (Webhook / CDC) | $\le 5$ Minutes | $< 100$ ms (OLAP) | 7 Years (Financial Audit) |
| Call & Dialer Logs | Hourly Batch | $\le 15$ Minutes | $< 250$ ms | 3 Years |
| Digital Messages (WA/SMS)| Hourly Batch | $\le 15$ Minutes | $< 250$ ms | 1 Year |
| Core LMS Master | Daily Snapshot (00:00 IST) | $\le 30$ Minutes | $< 100$ ms | Permanent History |
| Executive Marts | Daily at 06:00 IST | $\le 15$ Minutes | $< 500$ ms | Permanent |
