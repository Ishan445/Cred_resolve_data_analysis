# Phase 2: Data Forensics Matrix & Empirical Findings

This report delivers the complete empirical results across all planned forensic threads (Forensics A through H, plus Complaints Conduct Integration), executed strictly on the Golden Dataset in DuckDB.

---

## 1. Forensic Master Findings Matrix

| Forensic Thread | Core Investigation Question | Detection Methodology | Key Empirical Metric / Finding | Evidentiary Tag | Pass / Fail Verdict |
|---|---|---|---|---|---|
| **Forensic A: Duplicate Payments & Ingestion Inflation** | Did gateway retries or automated ingestion loops inflate monthly collections? | Screened golden payments for multi-payment retries within 10m / 1h / 24h. | 0 duplicate cash retries found within 24h on same `(account_id, amount)`. Cash inflation is strictly driven by including non-realized `FAILED` (₹27.84 Cr) and `PENDING` (₹19.02 Cr) attempts. | `[FACT]` | **PASS** (Payment dedup holds; inflation is driven by status filtering, not duplicate transactions). |
| **Forensic B: Attribution Lookback Fallacy** | Are payments misattributed to the latest automated touchpoint rather than true drivers? | Re-ran last-touch attribution across 1d, 3d, 7d, and 14d lookbacks across all 4 interaction channels. | 64.04% of successful payments have **no operational touchpoint within 14 days** (pure organic repayments). Calls capture 1,486 payments (₹11.20 Cr) at 7d, WhatsApp 927 (₹6.95 Cr), SMS 730 (₹5.51 Cr), Field 402 (₹2.95 Cr). | `[FACT]` | **FAIL** (Severe last-touch distortion: 64% of collections are organic, but legacy models falsely claim 100% operational attribution). |
| **Forensic C: Timezone Shift & Classification** | Were calls misclassified into wrong business hours due to mixed UTC / Dubai timestamps? | Standardized all calls from `UTC`, `Asia/Dubai`, and `Asia/Kolkata` into Indian Standard Time (IST). | 29,966 UTC calls were shifted +5.5 hours, and 29,996 Dubai calls were shifted +1.5 hours. Calls originally appearing at 00:00–04:00 UTC shifted into prime 09:00–17:00 IST calling hours. Peak answer rate (17.38%) occurs at 14:00–16:00 IST. | `[FACT]` | **FAIL** (Legacy raw reporting misclassified 66.6% of calling hours, corrupting hourly efficiency models). |
| **Forensic D: Telephony Vendor Disposition Drift** | Did telephony vendors alter disposition code mappings across versions? | Analyzed disposition code proportions across `legacy`, `v1`, `v2` versions and vendors. | Disposition codes remain perfectly uniform (~10.5% to 11.7% per code) across all three versions (`legacy`, `v1`, `v2`). No artificial spike in RPC or contact rate was engineered via vendor code reclassification. | `[FACT]` | **PASS** (Vendor disposition distributions are structurally invariant). |
| **Forensic E: Agent Identity & Desk Utilization** | Did ghost IDs or multi-desk logins distort agent productivity? | Evaluated session logged hours across 1,000 active desk `agent_id`s in `agent_sessions.csv`. | 1,000 active `agent_id`s logged 15,000 sessions (averaging 5.2 hours per session). Because individual human identity is unresolvable (ASM-009), productivity is strictly valid at the desk level (averaging 1.54 calls per logged session hour). | `[STRONG EVIDENCE]` | **PASS (Desk Level)** / **FAIL (Person Level)** (Desk metrics hold; individual coaching/tenure unobservable). |
| **Forensic F: Portfolio Mix Shifts** | Did an influx of fresh, low-DPD loans create an illusion of improved recovery? | Analyzed monthly active book intake and outstanding balance by loan type and DPD. | Loan asset mix (20% across Auto, Card, Personal, Consumer, BNPL) and DPD distribution (~9% across 11 buckets) remained virtually static across Jan–Jul 2026. No sudden portfolio shift occurred. | `[FACT]` | **PASS** (Portfolio intake was stable; mix shift did not manufacture the 11% claim). |
| **Forensic G: Denominator Manipulation** | Did uncollectible accounts drop out of active targeting to inflate recovery rates? | Tracked active unique accounts targeted monthly in `daily_targeting.csv` and status changes in `account_status_history.csv`. | Active targeted accounts hovered between 5,160 and 5,800 every month. Account status transitions to `WRITEOFF` (~1,100/mo) and `CLOSED` (~1,200/mo) were perfectly steady. | `[FACT]` | **PASS** (Denominator was not artificially purged mid-period). |
| **Forensic H: Campaign Semantic Inconsistency & Leakage** | Did campaign rules change meaning or target accounts outside stated criteria? | Cross-audited 120 campaign target definitions and cross-checked 45,000 daily targets against account DPD. | **Massive Targeting Leakage Discovered:** In `DPD>=60` campaigns, **54.16% of targeted accounts had DPD < 60**. In `DPD>=30` campaigns, **36.26% had DPD < 30**. 120 campaigns ran with identical names across 4 strategy versions (`legacy`, `v1`, `v2`, `v3`). | `[FACT]` | **FAIL** (Extensive operational leakage: campaigns routinely dial low-delinquency accounts outside their mandate). |
| **Forensic Conduct: Complaints Attribution** | What operational channels and practices drive regulatory and conduct risk? | Linked 8,000 complaints to nearest preceding touchpoint within 14 days. | 1,176 complaints (14.7%) directly follow a phone call across **713 distinct `agent_id` desk records** (per **ASM-009**, this is a desk-level signal only — it cannot be used to identify, discipline, or coach individual employees, and any regulatory/conduct escalation based on this finding needs a different, person-level identifier that does not currently exist in the dataset); 819 follow WhatsApp; 594 follow SMS; 334 follow Field visits. `AGENT_BEHAVIOUR` (1,202) and `HARASSMENT` (1,164) dominate critical complaints. | `[FACT]` | **FAIL** (Calling drives 40.2% of all contact-attributed complaints; critical conduct hazard for scaling phone operations). |

---

## 2. Deep-Dive Findings & Concrete Evidence

### 2.1 Forensic B: Multi-Window Touchpoint Attribution Fallacy
`[FACT]`: Legacy operations credited collection channels with 100% of cash recovery. By cross-matching all 17,534 successful payments against interactions across 1d, 3d, 7d, and 14d lookbacks:
- **64.04% of payments (11,229 payments) had NO touchpoint in the preceding 14 days.** These represent organic direct debits and self-motivated borrower payments.
- Only **6,305 payments (35.96%)** occurred within 14 days of any interaction:
  - **Human Voice (`CALL`):** 2,567 payments (14.64% of total success payments; ₹11.20 Cr attributed at 7d).
  - **WhatsApp:** 1,680 payments (9.58%; ₹6.95 Cr attributed at 7d).
  - **SMS:** 1,323 payments (7.55%; ₹5.51 Cr attributed at 7d).
  - **Field Visits:** 735 payments (4.19%; ₹2.95 Cr attributed at 7d).

### 2.2 Forensic C: Timezone Shift Impact on Operational Hours
`[FACT]`: Standardizing timestamps to Indian Standard Time (`Asia/Kolkata`) drastically altered the calling curve:
- Under raw logging, calling appeared spread across all 24 hours (with 11,250 calls recorded between 00:00 and 06:00 UTC).
- Post-normalization, calls cluster realistically between **08:00 and 20:00 IST**.
- Peak borrower answer rates occur at **14:00–16:00 IST (17.38% answer rate)**, whereas morning calling (08:00–10:00 IST) yields only **11.2% answer rate**.

### 2.3 Forensic H: Operational Targeting Leakage Proof
`[FACT]`: In `daily_targeting.csv` (45,000 targeting events), accounts were matched against their actual state in `accounts.csv`:
- `DPD>=60` Campaigns: 11,534 accounts targeted $\rightarrow$ **6,247 accounts (54.16%) had DPD < 60** at the time of targeting.
- `DPD>=30` Campaigns: 8,256 accounts targeted $\rightarrow$ **2,994 accounts (36.26%) had DPD < 30**.
- This proves that operational dialers were systematically dialing fresh, low-delinquency accounts under the guise of "hard collections" campaigns.

### 2.4 Conduct Risk: Complaints Thread Integration
`[FACT]`: In `complaints.csv`, 8,000 complaints were analyzed:
- Distribution: `DISPUTE` (1,180, 14.8%), `AGENT_BEHAVIOUR` (1,202, 15.0%), `HARASSMENT` (1,164, 14.6%), `DND` (1,155, 14.4%), `PRIVACY` (1,142, 14.3%), `WRONG_CONTACT` (1,105, 13.8%), `PAYMENT` (1,052, 13.2%).
- Time-proximity matching reveals that **Human Voice Calling generates 3.5x more complaints than Field Visits and 1.4x more than WhatsApp**, driving 1,176 complaints (40.2% of all contact-attributed complaints) across **713 distinct `agent_id` desk records**.
- **ASM-009 Boundary Enforcement**: This is a desk-level signal only — it cannot be used to identify, discipline, or coach individual employees (as up to 48 distinct individuals share a single `agent_id` over time). Any regulatory or conduct escalation based on this finding needs a different, person-level identifier that does not currently exist in the dataset.
- This is a critical downside risk for the ₹10 Cr investment: investing blindly in "More Collection Agents" or aggressive predictive dialers directly escalates regulatory harassment liability.
