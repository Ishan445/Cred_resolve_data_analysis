# Data Quality & Forensics Report

**Project:** Debt Collections Platform Analytics & ₹10 Cr Investment Due Diligence  
**Evaluation Window:** 2026-01-01 to 2026-08-12  
**Dataset Grain:** 17 Relational Operational Feeds (604,185 raw records)  

---

## 1. Phase 0: Baseline Data Ingestion, Profiling & Boundary Verification

### 1.1 File Inventory & Grain Reconciliation Table
A comprehensive physical audit of all 17 raw CSV files located in `data/raw/` was conducted using automated scripts (`scripts/phase0_profiling.py`). All row counts, column counts, exact duplicate rows, and primary keys were verified against the data dictionary:

| Table | File Size | Raw Rows | Exact Duplicate Rows | Distinct Rows | Columns | Verified Grain | Primary / Identifier Key(s) |
|---|---|---|---|---|---|---|---|
| `account_status_history` | 6.04 MB | 60,000 | 0 | 60,000 | 8 | Status event | `history_id` (60,000 unique) |
| `accounts` | 2.90 MB | 30,000 | 0 | 30,000 | 11 | Loan Account | `account_id` (30,000 unique) |
| `agent_sessions` | 1.29 MB | 15,000 | 0 | 15,000 | 7 | Session log | `session_id` (15,000 unique) |
| `agents` | 2.87 MB | 30,000 | 0 | 30,000 | 8 | Agent record | `agent_id` (1,000 unique), `employee_code` (1,099 unique) |
| `borrowers` | 3.43 MB | 30,600 | **600** | 30,000 | 8 | Borrower entity | `borrower_id` (11,015 unique) |
| `call_attempts` | 12.10 MB | 120,000 | 0 | 120,000 | 9 | Dial attempt | `attempt_id` (120,000 unique) |
| `call_dispositions` | 3.42 MB | 35,000 | 0 | 35,000 | 8 | Call disposition | `disposition_id` (35,000 unique) |
| `calls` | 10.70 MB | 91,350 | **1,271** | 90,079 | 11 | Call record | `call_id` (90,000 unique) |
| `campaigns` | 0.01 MB | 120 | 0 | 120 | 7 | Campaign strategy | `campaign_id` (120 unique) |
| `complaints` | 0.88 MB | 8,000 | 0 | 8,000 | 9 | Complaint ticket | `complaint_id` (8,000 unique) |
| `daily_targeting` | 2.73 MB | 45,000 | 0 | 45,000 | 7 | Target assignment | `target_id` (45,000 unique) |
| `field_visits` | 3.53 MB | 25,000 | 0 | 25,000 | 10 | Field visit | `visit_id` (25,000 unique) |
| `payments` | 2.67 MB | 25,500 | **486** | 25,014 | 9 | Payment transaction | `payment_id` (25,000 unique, 20,821 unique `payment_reference`) |
| `promises_to_pay` | 1.90 MB | 18,000 | 0 | 18,000 | 9 | PTP agreement | `ptp_id` (18,000 unique) |
| `sms_events` | 4.59 MB | 45,000 | 0 | 45,000 | 8 | SMS event | `sms_event_id` (45,000 unique) |
| `vendor_telephony` | <0.01 MB | 15 | 0 | 15 | 6 | Telephony vendor | `vendor_id` (15 unique) |
| `whatsapp_events` | 6.52 MB | 60,600 | **600** | 60,000 | 8 | WhatsApp message | `whatsapp_event_id` (60,000 unique) |
| **TOTAL** | **61.88 MB** | **639,185** | **2,957** | **636,228** | -- | -- | -- |

**Duplicate Audit Summary:** Exactly 4 tables contain full row duplications: `calls` (1,271 dups), `whatsapp_events` (600 dups), `borrowers` (600 dups), and `payments` (486 dups), accounting for 2,957 duplicate rows. All other 13 tables are free of exact duplicate rows.

---

### 1.2 Timeline Verification & Analytical Window Reconciliation
While the initial project framing referenced approximately 12 months of collections data, our temporal profiling across all 17 operational feeds established the empirical timeline:

| Table Category | Tables | Verified Min Date | Verified Max Date | Operational Span |
|---|---|---|---|---|
| **Operational Event Feeds** | `calls`, `call_attempts`, `call_dispositions`, `payments`, `promises_to_pay`, `sms_events`, `whatsapp_events`, `field_visits`, `complaints`, `daily_targeting`, `agent_sessions`, `account_status_history` | **2026-01-01** (Calls min: 2025-12-29 23:45 UTC) | **2026-08-08** (Calls max: 2026-08-12 18:20 IST) | **~7.25 Operating Months** |
| **Campaign Strategy Windows** | `campaigns` | **2026-01-01** | **2026-08-16** | 7.5 Months |
| **Master Loan Originations** | `accounts` (`opened_at`) | **2024-01-01** | **2025-11-30** | 23 Months (Historical book) |
| **Borrower Master Records** | `borrowers` (`created_at`) | **2025-01-01** | **2026-08-03** | 19 Months |
| **Agent Tenure Records** | `agents` (`joined_at`) | **2024-01-01** | **2025-11-30** | 23 Months |

#### Decision on Analytical Window:
1. **The 12-month claim is factually false regarding operational collections.** The operational event logs span only from **January 1, 2026 through August 12, 2026**.
2. **Standardized Complete Months for MoM Reporting:** To calculate month-on-month operational trends without severe calendar boundary distortion, the formal evaluation period consists of **January 2026 through July 2026 (7 complete months)**.
3. **August 2026 Treatment:** August 2026 contains only 8 to 12 days of data across event tables. Any monthly aggregation for August must be explicitly annotated as **Partial Month (Run-Rate / MTD)** to prevent leadership from misinterpreting a calendar cutoff as an operational collapse.

---

### 1.3 Formal Documentation of Missing Dimensions (Client & Language)
The assignment brief instructs the analyst to investigate major drivers across: *Portfolio mix, DPD, Client, Geography, Language, Agent, Agent tenure, Campaign, Channel, Telephony vendor, Calling time, Attempt frequency, Borrower segment.*

During Phase 0 schema validation against `data_dictionary.csv` and all 17 CSV files, two critical data gaps were uncovered:

#### 1. Dimension: "Client" — Formally Unobserved
- **Finding:** Neither `accounts.csv` nor any other dataset contains a `client_id`, `lender_id`, `originator_id`, or institutional client name. The `accounts.csv` table links only to `borrower_id` and specifies `loan_type` (`CONSUMER`, `BNPL`, `CREDIT_CARD`, `PERSONAL`, `AUTO`).
- **Impact:** Client-level performance, client mix shifts, and client contract attribution **cannot be directly investigated**.
- **Audit Declaration:** This is a structural data omission in the source delivery, not an analytical oversight. It will be reported directly to leadership in the Data Quality Report and Executive Memo.

#### 2. Dimension: "Language" — Unobserved with Geographic Macro-Proxy
- **Finding:** Neither `borrowers.csv`, `calls.csv`, nor `agents.csv` records borrower native language, call language audio tag, or agent language proficiency.
- **Proxy Strategy:** `borrowers.csv` provides `city` (10 unique cities) and `state` (9 unique states: Maharashtra, Karnataka, Delhi, West Bengal, Telangana, Haryana, Odisha, Rajasthan, Tamil Nadu). While individual language preference is unobserved, borrower geography will be utilized as a macro regional/linguistic proxy.
- **Audit Declaration:** Explicitly document that native language preference and language-matching conversion efficiency cannot be directly established.

---

### 1.4 Detailed Null & Missingness Audit
A full column-by-column missingness audit across all 17 tables revealed that null values are strictly confined to 6 specific columns:

| Table | Column Name | Total Rows | Null Count | Null Pct (%) | Analytical Significance & Treatment Plan |
|---|---|---|---|---|---|
| `accounts` | `borrower_id` | 30,000 | 455 | 1.52% | Orphan loans unlinked to borrower profile. In Phase 1, these accounts will be retained for loan-level cash accounting but excluded from borrower-level aggregation. |
| `borrowers` | `phone` | 30,600 | 614 | 2.01% | Missing phone numbers preclude telephony contact; must be checked against digital channels. |
| `borrowers` | `email` | 30,600 | 895 | 2.92% | Digital contact gap; digital reminder delivery failure analysis. |
| `call_attempts` | `vendor_id` | 120,000 | 2,400 | 2.00% | Dial attempts missing telephony vendor attribution. |
| `calls` | `agent_id` | 91,350 | 1,827 | 2.00% | Unattributed calls; must evaluate whether these represent automated dialer / IVR drops or missing logs. |
| `field_visits` | `scheduled_at` | 25,000 | 250 | 1.00% | Unscheduled / ad-hoc field visits. |
| `payments` | `payment_reference` | 25,500 | 382 | 1.50% | Payments without gateway transaction references. |

**Completeness Confirmation:** All other 120 columns across the 17 tables have 0.0% null values.

---

### 1.5 Special Forensic Flag: `complaints.csv` Foreign Key Linkage & Attribution
As noted during plan refinement, `complaints.csv` (8,000 rows) contains:
- `complaint_id`, `account_id`, `borrower_id`, `event_at`, `complaint_type`, `severity`, `status`, `source`, `resolution_at`.
- It **lacks** direct foreign keys for `agent_id`, `vendor_id`, and `campaign_id`.
- Therefore, in Phase 2 Forensics, complaints were attributed to operational drivers using a **14-day backward time-proximity join** linking the complaint timestamp to the most recent interaction (`calls`, `field_visits`, `whatsapp_events`, `sms_events`) on that `account_id`.
- **Empirical Attribution Result:** 1,176 complaints (40.2% of contact-attributed complaints) directly follow a phone call across **713 distinct `agent_id` desk records**; 819 follow WhatsApp; 594 follow SMS; 334 follow Field visits.
- **ASM-009 Boundary Enforcement:** Per **ASM-009**, this is a desk-level signal only — it cannot be used to identify, discipline, or coach individual employees, because up to 48 distinct individuals share a single `agent_id` over time. Any regulatory or conduct escalation based on this finding needs a different, person-level identifier that does not currently exist in the dataset.

---

## 2. Phase 1: Golden Dataset Resolution & Reconciliation

### 2.1 Entity Resolution & De-duplication Ledger
The raw dataset contained 639,185 records across 17 tables. Through four locked resolution rules, 2,957 exact duplicate rows were removed, and 29,093 non-canonical snapshots and key collisions were quarantined:

| Table / Entity | Raw Rows | Exact Dups Removed | Key Collisions / Non-Canonical Quarantined | Golden Clean Rows | Resolution Rule & Analytical Role |
|---|---|---|---|---|---|
| `agents.csv` | 30,000 | 0 | 29,000 | **1,000** | Collapsed to canonical desk lookup on `agent_id` via latest `updated_at`. Per **ASM-009**, used solely for aggregate desk/channel/vendor rollups. |
| `calls.csv` | 91,350 | 1,271 | 79 | **90,000** | De-duplicated on `call_id`, prioritizing populated `agent_id`, then latest `event_at`. |
| `payments.csv` | 25,500 | 486 | 14 | **25,000** | De-duplicated on `payment_id`, preserving populated `payment_reference`. |
| `borrowers.csv` | 30,600 | 600 | 0 | **30,000** | Exact dups removed; assigned surrogate key `borrower_sk`. `account_id` remains the primary analytical join grain. |
| `whatsapp_events.csv` | 60,600 | 600 | 0 | **60,000** | Exact dups removed; clean event records. |
| **Remaining 12 Tables** | 401,135 | 0 | 0 | **401,135** | Strict 1:1 clean rows verified in Phase 0. |
| **TOTAL DATASET** | **639,185** | **2,957** | **29,093** | **607,135** | **639,185 raw - 2,957 dups - 29,093 quarantined = 607,135 golden.** |

### 2.2 Financial Reconciliation (25,000 Golden Payments)
- **Gross Recorded Payment Volume:** **₹187.89 Cr** across 25,000 transactions.
- **Successful Inflows (`payment_status = 'SUCCESS'`):** **₹131.56 Cr** across 17,534 transactions.
- **Deducted Reversals (`payment_status = 'REVERSED'`):** **₹9.47 Cr** across 1,254 transactions.
- **Net Realized Cash Recovery (True Inflow):** **₹122.09 Cr**.
- **Non-Realized Inflow Attempts:** **₹56.33 Cr** (29.98% of gross), consisting of `FAILED` attempts (**₹27.84 Cr**, 3,677 txns) and `PENDING` attempts (**₹19.02 Cr**, 2,535 txns).
- **Check Sum Reconciliation:** $₹131.56 + ₹9.47 + ₹27.84 + ₹19.02 = \mathbf{₹187.89\text{ Cr}}$ (exact match to gross).
- **Legacy Gross Overstatement:** Reporting gross attempts (₹187.89 Cr) over net realized cash (₹122.09 Cr) inflated true recovery by **+53.89%** (+57.04% on raw gross).

---

## 3. Phase 2: Forensics Findings Matrix (Hunts A through H)

| Forensic Thread | Investigation Question | Empirical Finding | Evidentiary Tag | Status / Impact |
|---|---|---|---|---|
| **A. Duplicate Payments** | Did rapid retries inflate collections? | 0 rapid cash retries within 24h on same `(account_id, amount)`. Inflation is driven by status inclusion (`FAILED`/`PENDING`), not gateway loops. | `[FACT]` | **PASS** |
| **B. Attribution Fallacy** | Are payments misattributed to touchpoints? | **79.82% of successful payments at 7d lookback (₹105.01 Cr) had zero touchpoint across any channel.** At 14d lookback, 64.04% remains organic. | `[FACT]` | **FAIL** (Legacy models claimed 100% operational credit). |
| **C. Timezone Shifts** | Were calls misclassified across operating hours? | Standardizing UTC (+5.5h) and Dubai (+1.5h) calls into IST shifts calls realistically into 08:00–20:00 IST. Peak answer rate occurs at 14:00–16:00 IST (21.0%). | `[FACT]` | **FAIL** (66.6% of raw calls logged outside IST). |
| **D. Vendor Disposition Drift** | Did vendors shift disposition codes? | Disposition distributions are structurally invariant (~10.5%–11.7% per code) across `legacy`, `v1`, and `v2`. | `[FACT]` | **PASS** |
| **E. Agent Identity & Capacity** | Did ghost IDs distort agent capacity? | 1,000 active desk IDs logged 15,000 sessions (5.2h avg, 1.54 calls/hour). Capacity is valid at desk level only (ASM-009). | `[STRONG EVIDENCE]` | **PASS (Desk) / FAIL (Individual)** |
| **F. Portfolio Mix Shifts** | Did fresh low-DPD intake inflate recovery? | Asset mix (20% each across 5 loan types) and DPD (~9% across 11 buckets) remained static across Jan–Jul 2026. | `[FACT]` | **PASS** |
| **G. Denominator Manipulation** | Were uncollectible accounts purged? | Monthly targeted accounts (5,160–5,800) and write-offs (~1,100/mo) were steady. Denominator was not manipulated. | `[FACT]` | **PASS** |
| **H. Campaign Targeting Leakage** | Did campaigns dial outside stated criteria? | **54.16% of accounts targeted in `DPD>=60` campaigns had DPD < 60.** 36.26% in `DPD>=30` had DPD < 30. | `[FACT]` | **FAIL** (Severe dialer misallocation). |
| **Conduct: Complaints Attribution** | Which channels drive regulatory risk? | Calls drive 1,176 complaints (40.2% of attributed complaints) across **713 distinct `agent_id` desk records** (per ASM-009, desk-level signal only). | `[FACT]` | **FAIL** (Severe voice dialing conduct hazard). |

---

## 4. Phase 3 & 4: Independent Metrics & Structural Root Causes

### 4.1 PTP Classification Confusion Matrix
Matching 18,000 PTPs against verified payments within $\pm 3$ days of `promised_date` ($\pm 10\%$ amount):
- **Disagreement Rate:** **99.93%**. 4,486 of 4,489 accounts labeled `KEPT` had no matching payment.
- Actual cash realization across all 4 statuses was statistically identical (~26%–28%). PTP status is an uncoupled synthetic label.

### 4.2 Independent Monthly Operational Benchmarks
- **Net Realized Recovery:** Flat across 7 months (averaging **₹16.81 Cr/mo**, -0.07% avg MoM change).
- **Account Contact Rate:** Stable at **23.34%** (`accounts_contacted / accounts_attempted`).
- **Call-Level Answer Rate:** Stable at **19.87%** (`answered_calls / total_dials`).
- **Recovery per Desk Hour:** Stable at **₹15,400/hour**.

### 4.3 Mutually Exclusive Last-Touch Channel Attribution (7-Day Lookback)
- **Pure Organic (No touch in 7d):** **79.82% (₹105.01 Cr)** across 13,999 payments.
- **Human Voice (`CALL`):** **8.50% (₹11.18 Cr)** across 1,483 payments.
- **WhatsApp Messaging:** **5.27% (₹6.93 Cr)** across 924 payments.
- **SMS Notifications:** **4.17% (₹5.49 Cr)** across 728 payments.
- **Field Visits:** **2.23% (₹2.94 Cr)** across 400 payments.
- **Total:** **100.00% (₹131.56 Cr)** across 17,534 payments.
*(Note: Multi-touch overlap across channels is exactly 303 payments / ₹2.28 Cr / 1.73%).*

---

## 5. Formal Data Limitations Summary

1. **ASM-007 (Client Dimension):** Unobservable in dataset. No institutional lender benchmarks possible.
2. **ASM-008 (Language Preference):** Unobserved in raw logs. State and city serve as regional proxies.
3. **ASM-009 (Agent Identity):** Desk-level attribution only. No individual employee coaching, ranking, or tenure claims can be supported.

