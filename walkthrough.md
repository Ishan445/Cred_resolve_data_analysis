# Project Walkthrough: Multi-Phase Forensic Audit & Deliverables Record

This document provides the permanent, chronological record of every analytical phase, methodology refinement, and formal sign-off achieved throughout the investigation.

---

## Phase 0: Baseline Data Ingestion, Profiling & Key-Integrity Audit
- **Reconciliation Scope:** Audited all 17 raw relational operational CSV files in `data/raw/` (639,185 total raw rows across 61.88 MB).
- **Exact Duplication Audit:** Verified exactly 2,957 duplicate rows confined to 4 tables: `calls` (1,271 dups), `whatsapp_events` (600 dups), `borrowers` (600 dups), and `payments` (486 dups). The remaining 13 tables contain 0 duplicate rows.
- **Operational Timeline Disproof:** The headline brief claimed "approximately 12 months of collections data." Temporal profiling proved the operational event logs span strictly **January 1, 2026 to August 12, 2026 (~7.25 operating months)**. The formal MoM evaluation window was locked to **January–July 2026 (7 complete months)**, with August treated as partial MTD.
- **Key-Integrity Taxonomy (5-Category Audit):**
  1. `borrowers.csv` (11,015 unique `borrower_id` across 30,000 rows): `COLLISION — SAME KEY DIFFERENT ENTITY` (Synthetic generator integer overflow).
  2. `agents.csv` (1,000 `agent_id` vs 1,099 `employee_code` across 30,000 rows): `COLLISION — SAME KEY DIFFERENT ENTITY` (Cross-product agent-employee collision).
  3. `calls.csv` (79 colliding pairs): `DUPLICATE INGESTION OF SAME ENTITY` (Pre-telephony vs post-telephony retry with identical timestamps).
  4. `payments.csv` (14 colliding pairs): `DUPLICATE INGESTION OF SAME ENTITY` (Pre-settlement unreferenced retry with identical account and amount).
  5. Remaining 13 tables: `OK (1:1)` primary key uniqueness.

---

## Phase 1: Golden Dataset Construction & Baseline Analytical Output

Phase 1 implemented the four locked de-duplication and entity resolution rules across `agents`, `calls`, `payments`, and `borrowers`:

| Dataset / Entity | Raw Count | Exact Dups Removed | Key Collisions Quarantined | Golden Clean Count | Entity Resolution & Analytical Role |
|---|---|---|---|---|---|
| `agents.csv` | 30,000 | 0 | 29,000 | **1,000** | Canonical agent desk lookup (`dim_agents`). Collapsed on `agent_id` via latest `updated_at`. Per **ASM-009**, used solely for aggregate desk/channel/vendor rollups. |
| `calls.csv` | 91,350 | 1,271 | 79 | **90,000** | Canonical call interactions (`fct_calls`). De-duplicated on `call_id`, prioritizing populated `agent_id`, then latest `event_at`. |
| `payments.csv` | 25,500 | 486 | 14 | **25,000** | Canonical payment transactions (`fct_payments`). De-duplicated on `payment_id`, preserving populated `payment_reference`. |
| `borrowers.csv` | 30,600 | 600 | 0 | **30,000** | Clean borrower records (`dim_borrowers`) assigned surrogate key `borrower_sk`. `account_id` remains the primary analytical join grain. |
| `whatsapp_events.csv` | 60,600 | 600 | 0 | **60,000** | Exact duplicates removed; 1:1 clean event records. |
| **Remaining 12 Tables** | 401,135 | 0 | 0 | **401,135** | Strict 1:1 clean rows confirmed in Phase 0. |
| **TOTAL DATASET** | **639,185** | **2,957** | **29,093** | **607,135** | Fully reconciled: 639,185 raw - 2,957 exact dups = 636,228 clean; 636,228 - 29,093 quarantined = 607,135 golden. |

### Financial Inflow Accounting on the Golden Dataset (25,000 Rows):
- **Gross Cash Sum in Golden Payments (25,000 rows):** **₹187.89 Cr**
- **Successful Cash Inflows (`payment_status = 'SUCCESS'`):** **₹131.56 Cr** across **17,534 payments**
- **Reversed Payments (`payment_status = 'REVERSED'`):** **₹9.47 Cr** across **1,254 payments**
- **Failed Attempts (`payment_status = 'FAILED'`):** **₹27.84 Cr** across **3,677 payments**
- **Pending Attempts (`payment_status = 'PENDING'`):** **₹19.02 Cr** across **2,535 payments**
- **Check Sum Reconciliation:** $₹131.56 + ₹9.47 + ₹27.84 + ₹19.02 = \mathbf{₹187.89\text{ Cr}}$ (exact match to golden gross).
- **Net Realized Cash Recovery (Success - Reversals):** $₹131.56 - ₹9.47 = \mathbf{₹122.09\text{ Cr}}$.
- **Non-Realized Cash (`Reversed + Failed + Pending`):** $₹9.47 + ₹27.84 + ₹19.02 = \mathbf{₹56.33\text{ Cr}}$ (**29.98% of golden gross**).
- **Legacy Gross Reporting Inflation:** Legacy reporting relying on gross recorded payment volume (₹187.89 Cr) rather than audited net realized cash (₹122.09 Cr) overstated true collections performance by **+53.89%** (+57.04% on pre-dedup raw gross of ₹191.73 Cr).

---

## Phase 2: Data Forensics Master Findings (Hunts A through H)

Full details are documented in [`reports/phase2_forensics_report.md`](reports/phase2_forensics_report.md):

| Forensic Thread | Key Metric / Proof | Finding & Analytical Verdict |
|---|---|---|
| **Forensic A: Duplicate Payments** | 0 duplicate cash retries within 24h across same `(account_id, amount)`. | **PASS:** Cash overstatement is strictly status inclusion (`FAILED`/`PENDING`), not gateway loops. |
| **Forensic B: Attribution Fallacy** | **79.82% of payments at 7d (13,999 txns, ₹105.01 Cr) had NO touchpoint across any channel.** At 14d lookback: 64.04% remains organic. | **FAIL (Severe Bias):** Vast majority of recovery is organic self-cure cash. Legacy attribution falsely credited 100% of cash to operations. |
| **Forensic C: Timezone Shifts** | 29,966 UTC calls shifted +5.5h; 29,996 Dubai calls shifted +1.5h. Peak answer rate = 21.0% at 14:00–16:00 IST. | **FAIL (Distortion Corrected):** 66.6% of raw calls were logged in non-IST zones, distorting hourly models. |
| **Forensic D: Vendor Disposition Drift** | Disposition codes are structurally invariant (~10.5%–11.7% per code) across `legacy`, `v1`, and `v2`. | **PASS:** No mid-period code re-classification artifact was found. |
| **Forensic E: Agent Desk Utilization** | 1,000 active desk IDs logged 15,000 sessions (avg 5.2h/session, 1.54 calls/hour). Individual tenure unresolvable (ASM-009). | **PASS (Desk Level) / FAIL (Person Level):** Operational capacity valid at desk level only. |
| **Forensic F: Portfolio Mix Shifts** | Asset mix (20% each across 5 loan types) and DPD (~9% across 11 buckets) remained static across Jan–Jul 2026. | **PASS:** No macro portfolio composition shock drove the 11% claim. |
| **Forensic G: Denominator Manipulation** | Targeted accounts (5,160–5,800/mo) and write-offs (~1,100/mo) were steady. | **PASS:** Denominator was not purged mid-period to inflate conversion. |
| **Forensic H: Campaign Inconsistency & Leakage** | **54.16% of accounts targeted in `DPD>=60` campaigns had DPD < 60.** 36.26% in `DPD>=30` had DPD < 30. | **FAIL (Severe Leakage):** Operations systematically dialed low-delinquency accounts in hard campaigns. |
| **Complaints Conduct Integration** | Calls drive 1,176 complaints (40.2% of contact-attributed complaints across **713 distinct `agent_id` desk records**; per **ASM-009**, desk-level signal only). `HARASSMENT` (167) & `AGENT_BEHAVIOUR` (156) top critical call complaints. | **FAIL (Conduct Risk):** Aggressive dialing represents a critical regulatory downside for scaling phone operations. |

---

## Phase 3: Independent Metric Definitions & The 11% Claim Verdict

Full empirical analysis and scripts are documented in [`reports/phase3_metrics_report.md`](reports/phase3_metrics_report.md).

### PTP Classification Confusion Matrix & Diagnostic
`[FACT]`: In `promises_to_pay.csv` (18,000 PTP records), the platform's self-reported status splits evenly across 4 categories: `BROKEN` (25.3%), `CANCELLED` (25.2%), `KEPT` (24.9%), `OPEN` (24.5%).

Matching every PTP against verified successful payments on the same account within $\pm 3$ days of `promised_date` ($\pm 10\%$ amount):

| Raw Platform Status | Independent Ground-Truth Match (`KEPT`) | Independent No-Match (`BROKEN`) | Total Records | Disagreement Rate (%) |
|:---|---:|---:|---:|---:|
| **`KEPT`** | **3** | **4,486** | **4,489** | **99.93% Disagreement** |
| **`BROKEN`** | 4 | 4,549 | 4,553 | 99.91% Match |
| **`CANCELLED`** | 8 | 4,535 | 4,543 | 99.82% Match |
| **`OPEN`** | 2 | 4,413 | 4,415 | 99.95% Match |
| **TOTAL** | **17** | **17,983** | **18,000** | -- |

`[STRONG EVIDENCE]`: Even expanding the window to any successful payment anytime after PTP creation, the payment realization rate for accounts marked `KEPT` (27.6%) is statistically indistinguishable from `BROKEN` (26.0%), `CANCELLED` (26.3%), and `OPEN` (26.4%). The platform's published "25% PTP Kept Rate" is an uncoupled synthetic label, completely decoupled from cash reality.

### Independent Monthly Operational Performance Framework (Jan–Jul 2026)
| Operational Metric | Jan 2026 | Feb 2026 | Mar 2026 | Apr 2026 | May 2026 | Jun 2026 | Jul 2026 | 7-Month Trajectory | Definitional Basis |
|:---|---:|---:|---:|---:|---:|---:|---:|:---|:---|
| **Unique Accounts Attempted** | 10,324 | 9,531 | 10,417 | 10,036 | 10,370 | 9,971 | 10,278 | **Flat (~10,100/mo)** | `COUNT(DISTINCT account_id)` |
| **Unique Accounts Contacted** | 2,433 | 2,188 | 2,457 | 2,258 | 2,491 | 2,385 | 2,345 | **Flat (~2,365/mo)** | `COUNT(DISTINCT CASE WHEN call_status = 'ANSWERED' THEN account_id END)` |
| **Account Contact Rate (%)** | **23.57%** | **22.96%** | **23.59%** | **22.50%** | **24.02%** | **23.92%** | **22.82%** | **Stable (23.34% Avg)** | `Accounts Contacted / Accounts Attempted` |
| **Total Call Dials** | 12,683 | 11,569 | 12,844 | 12,241 | 12,746 | 12,128 | 12,578 | **Flat (~12,400/mo)** | `COUNT(*)` in `golden_calls` |
| **Answered Calls** | 2,543 | 2,279 | 2,567 | 2,362 | 2,592 | 2,474 | 2,433 | **Flat (~2,460/mo)** | `COUNT(CASE WHEN call_status = 'ANSWERED' THEN 1 END)` |
| **Call-Level Answer Rate (%)** | **20.05%** | **19.70%** | **19.99%** | **19.30%** | **20.34%** | **20.40%** | **19.34%** | **Stable (19.87% Avg)** | `Answered Calls / Total Call Dials` |
| **Active Desk Hours** | 11,162 | 10,557 | 11,131 | 10,620 | 10,833 | 10,703 | 11,180 | **Capacity Capped** | `SUM(logout_at - login_at)` across 1,000 desk IDs |
| **Net Realized Cash (₹ Cr)** | **₹17.56** | **₹15.87** | **₹17.45** | **₹16.18** | **₹17.16** | **₹16.26** | **₹17.20** | **Static (₹16.81 Cr Avg)** | `SUM(Success Amount) - SUM(Reversed Amount)` |
| **Recovery per Desk Hour (₹)** | **₹15,732** | **₹15,033** | **₹15,677** | **₹15,235** | **₹15,840** | **₹15,192** | **₹15,385** | **Completely Flat** | `Net Cash / Active Desk Hours` |
| **Recovery per Attempted Account**| **₹17,009** | **₹16,651** | **₹16,752** | **₹16,122** | **₹16,548** | **₹16,307** | **₹16,735** | **Completely Flat** | `Net Cash / Attempted Accounts` |

*Note on Contact Rate vs. Answer Rate:*
- **Account Contact Rate** (`Unique Accounts Contacted / Unique Accounts Attempted`) tracks debtor penetration and equals **23.57%** in Jan (averaging **23.34%** across 7 months).
- **Call Answer Rate** (`Answered Calls / Total Call Dials`) tracks telephony connect rate per dial attempt and equals **20.05%** in Jan (averaging **19.87%** across 7 months). Both metrics are completely flat throughout the period.

### Waterfall Gap Decomposition: Bridging the 11% Claim to Ground Truth
```
   Reported Headline Claim:        +11.00% (MoM Claimed Improvement)
   - Calendar Normalization:       -10.01% (Eliminating February-to-March 28-day rebound bias)
   - Status Exclusion (Reversals):  -0.54% (Deducting bounced & reversed cash inflows)
   - Deduplication Correction:      -0.52% (Eliminating gateway retry noise & unreferenced duplicates)
   ---------------------------------------------------------------------------------------------------
   = AUDITED GROUND-TRUTH RECOVERY:   -0.07% (Actual Average MoM Performance: FLAT)
```

`[FACT]`: The 11% MoM Improvement Claim is **factually FALSE**. Net realized recovery is completely flat. Legacy reporting manufactured the figure by cherry-picking the post-February calendar bounce, adding un-deduplicated gross transaction attempts (+53.89% inflation), and falsely claiming 100% operational credit for organic payments (64.04% organic).

---

## Phase 4: Operational Driver Analysis (Why Did It Happen?)

Full empirical analysis and tables are documented in [`reports/phase4_drivers_report.md`](reports/phase4_drivers_report.md).

### Formal Handling of Structural Data Gaps
- **Client Dimension (ASM-007):** Unobserved in raw dataset. Formally documented as an unobservable institutional omission.
- **Language Preference (ASM-008):** Unobserved in raw logs. The 9 states and 10 cities serve as regional linguistic macro-proxies.
- **Agent Human Identity (ASM-009):** Cross-product collision (1,000 IDs vs 1,099 codes across 30,000 rows). Evaluated strictly at the desk record level; no individual coaching or tenure claims.

### Major Driver Decompositions & Empirical Findings

| Driver Dimension | Core Empirical Metrics | Evidentiary Tag | Key Analytical Finding |
|---|---|---|---|
| **1. Loan Type (Portfolio Mix)** | Consumer (12.00%), Cards (11.78%), Auto (11.66%), BNPL (11.52%), Personal (11.24%). | `[FACT]` | **Invariant:** Recovery rates across all 5 loan types cluster tightly between 11.24% and 12.00%. Asset mix did not change and did not drive recovery trends. |
| **2. Delinquency Vintage (DPD Buckets)** | 0 DPD (11.41%), 1–29 DPD (11.47%), 30–59 DPD (11.64%), 60–89 DPD (12.13%), 90+ DPD (11.56%). | `[FACT]` | **Synthetic Decoupling:** Recovery rates across delinquency vintages are virtually identical (~11.6%). In real banking, early DPD recovers at 40–60%; here it is flat. |
| **3. Borrower Risk Segment** | Low (11.71%), High (11.66%), Medium (11.65%), NPA (11.54%). | `[FACT]` | **Zero Discrimination:** Internal risk scorecards exhibit zero predictive power over debtor cash realization. |
| **4. Geography & Regional Linguistic Proxy** | 9 states tested: Odisha (11.98%), Rajasthan (11.91%), Maharashtra (11.87%), ..., Telangana (11.25%). Connect rates: 18.9%–20.8%. | `[FACT]` | **Geographically Uniform:** Performance is invariant across states and linguistic regions. |
| **5. Mutually Exclusive Channel Attribution** | **Mutually Exclusive at 7d lookback (sums to 100.0% / ₹131.56 Cr):** Organic = **79.82% (₹105.01 Cr)**, Calls = **8.50% (₹11.18 Cr)**, WhatsApp = **5.27% (₹6.93 Cr)**, SMS = **4.17% (₹5.49 Cr)**, Field = **2.23% (₹2.94 Cr)**. Multi-touch overlap across channels is exactly 303 payments (1.73% / ₹2.28 Cr). *(At 14d lookback: Organic = 63.71% / ₹83.82 Cr).* | `[FACT]` | **Attribution Fallacy:** Between 64% and 80% of collections is self-curing cash falsely claimed by marketing and dialers. |
| **6. Telephony Infrastructure & Vendors** | 15 vendors: each handled ~6,000 dials; answer rates cluster between 19.32% and 21.09% (avg 19.87%). | `[FACT]` | **Commoditized Telecom:** No single vendor outperforms in connect rate or call completion. |
| **7. Calling Time & Hourly Windows** | Afternoon (14:00–16:00 IST) yields peak answer rate (20.5%–21.0%), vs morning (19.7%). | `[FACT]` | **Timezone Normalized:** Slight connect bump in mid-afternoon, but dialers fired uniformly across all 24 hours. |
| **8. Attempt Frequency & Dial Fatigue** | 1 dial reach = 20.65%; 6+ dials reach = 76.64%. Dial answer rate per attempt remains flat at ~19.6%–20.6%. | `[FACT]` | **Diminishing Returns:** Calling debtors 6+ times increases cumulative contact but provokes severe conduct complaints (`HARASSMENT`, `DND`). |
| **9. Campaign Strategy & Targeting Leakage** | 120 campaigns in 4 versions ran simultaneously. **54.16% in `DPD>=60` had DPD < 60; 36.26% in `DPD>=30` had DPD < 30.** | `[FACT]` | **Dialer Leakage:** Operations systematically misrouted low-delinquency accounts into aggressive hard campaigns. |

### Root Cause Synthesis: Why the Platform Stagnated
The collections operation is trapped at an artificial performance ceiling:
1. **Core cash is organic (64%–80%):** Operational interventions account for only ~20%–36% of cash.
2. **Telephony capacity is hard-capped:** 1,000 desks max out at ~12,400 dials/month and ~11,000 session hours with a flat ~19.9% connect rate.
3. **Severe Targeting Misallocation:** 54% of dialer capacity in hard campaigns is wasted on early-stage accounts that would have paid organically.
4. **Conduct Bottleneck:** Expanding voice call frequency triggers escalating regulatory risk (713 desk records implicated in 40.2% of complaints).

---

## Phase 5: Production Deliverables & Repository Finalization

Phase 5 synthesized all audited forensic findings into seven enterprise-grade deliverables:
1. **Production SQL Repository (`sql/`):** Full 5-stage DuckDB/Postgres pipeline from staging DDL and idempotent deduplication to attribution marts and C-suite KPI views.
2. **Automated Golden Pipeline (`pipeline/`):** Automated, idempotent Python/DuckDB ETL (`pipeline/build_golden.py`) generating verified golden Parquet tables.
3. **Data Quality & Forensics Report (`reports/data_quality_report.md`):** Complete profiling, null audits, key-integrity taxonomy, and evidentiary matrices.
4. **Executive Decision Memo (`reports/executive_memo.md`):** Authoritative 2-page C-suite memo with the audited cash ledger, waterfall bridge, mutually exclusive attribution, and ₹10 Cr investment recommendation.
5. **Interactive Executive Dashboard (`dashboard/app.py`):** Single-screen Streamlit application featuring live waterfall bridges, driver exploration, and an interactive ₹10 Cr investment ROI simulator.
6. **Production Architecture Blueprint (`architecture/`):** End-to-end lakehouse design with data contracts, SLA tiering, and Mermaid.js architecture diagram (`system_architecture.mmd`).
7. **Clean Repository for Distribution:** All raw datasets standardized under `data/raw/`, local machine paths scrubbed, MIT `LICENSE` added, and full file manifest verified.
