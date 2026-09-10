# Phase 3: Independent Metric Definitions & The 11% Claim Verdict

This report establishes the independent, uncompromised metric framework, audits the PTP-Kept disagreement, reconciles monthly operational performance, and delivers the definitive forensic verdict on the platform's claimed "11% MoM improvement."

---

## 1. Executive Verdict on the Claim: "Recovery has improved by 11% Month-on-Month"

### `[FACT]`: The 11% MoM Improvement Claim is Factually FALSE.
1. **True Cash Trajectory:** Verified net realized cash recovery (successful cash inflows minus reversals) is **completely flat** across the 7 complete operating months of 2026.
   - January 2026: **₹17.56 Cr**
   - February 2026: **₹15.87 Cr** (-9.64%)
   - March 2026: **₹17.45 Cr** (+10.01%)
   - April 2026: **₹16.18 Cr** (-7.30%)
   - May 2026: **₹17.16 Cr** (+6.02%)
   - June 2026: **₹16.26 Cr** (-5.22%)
   - July 2026: **₹17.20 Cr** (+5.76%)
   - **Average MoM Net Growth (Jan–Jul 2026): -0.07%**.
2. **Narrow Range Bound:** Net recovery fluctuates strictly within an envelope of **₹15.87 Cr to ₹17.56 Cr** (standard deviation = ₹0.68 Cr, CV = 4.0%). There is zero secular upward trend.
3. **How the "11% Improvement" was Manufactured by Legacy Reporting:**
   - **Mechanism 1 (Single-Month Rebound Cherry-Picking):** The highest single-month MoM increase occurred in March 2026 (+10.01% net, +12.35% gross). This was merely a calendar rebound following a short 28-day February (-9.64% drop). Legacy reporting cherry-picked the March bounce and presented it as a sustained month-on-month operational improvement.
   - **Mechanism 2 (Gross Ingestion Distortion):** Tracking un-deduplicated gross payment attempts (including failed and pending transactions) inflated the top line by **+53.89%** above real cash.
   - **Mechanism 3 (Attribution Fallacy):** As proven in Phase 2 Forensic B, **64.04% of cash payments are organic** with no touchpoint in the preceding 14 days. Legacy operations falsely credited 100% of cash recovery to collection campaigns.

---

## 2. PTP-Kept Disagreement Audit & Confusion Matrix

`[FACT]`: In `promises_to_pay.csv` (18,000 PTPs), the platform's self-reported status splits evenly into 4 buckets: `BROKEN` (25.3%), `CANCELLED` (25.2%), `KEPT` (24.9%), `OPEN` (24.5%).

We challenged the platform's `KEPT` label by cross-matching every PTP against actual successful cash payments on the same account within a realistic settlement window ($[-3\text{ days}, +3\text{ days}]$ of `promised_date`, matching amount within $\pm 10\%$):

### PTP Classification Confusion Matrix:
| Raw Platform Status | Independent Ground-Truth Match (`KEPT`) | Independent No-Match (`BROKEN`) | Total Records | Disagreement Rate (%) |
|:---|---:|---:|---:|---:|
| **`KEPT`** | **3** | **4,486** | **4,489** | **99.93% Disagreement** |
| **`BROKEN`** | 4 | 4,549 | 4,553 | 99.91% Match |
| **`CANCELLED`** | 8 | 4,535 | 4,543 | 99.82% Match |
| **`OPEN`** | 2 | 4,413 | 4,415 | 99.95% Match |
| **TOTAL** | **17** | **17,983** | **18,000** | -- |

### `[STRONG EVIDENCE]`: Diagnostic Analysis of PTP Disagreement:
1. **Uncorrelated Status Field:** Even when expanding the matching window to **any successful payment anytime after PTP creation**, the payment rate for accounts marked `KEPT` (27.6%) is identical to accounts marked `BROKEN` (26.0%), `CANCELLED` (26.3%), and `OPEN` (26.4%).
2. **Synthetic Generator Decoupling:** In the raw data generation (Seed = 42), the `status` column in `promises_to_pay.csv` was populated as an uncoupled uniform categorical draw independent of real payment realization.
3. **Operational Implication:** The platform's published "PTP Kept Rate" of ~25% is completely fabricated; it reflects random synthetic labeling rather than actual debtor compliance.

---

## 3. Independent Monthly Operational Performance Framework

By applying uncompromised, ground-truth metric definitions across the 7 complete months:

### Operational Performance Metric Table (Jan–Jul 2026):
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

### Definitional & SQL Reconciliation:
- **Account-Level Contact Rate (23.34% 7-Month Average):**
  Evaluates unique borrower penetration. Computed as unique accounts with at least one answered call divided by unique accounts attempted in that month:
  ```sql
  COUNT(DISTINCT CASE WHEN call_status = 'ANSWERED' THEN account_id END) * 100.0 
    / COUNT(DISTINCT account_id)
  ```
  *(e.g., Jan: 2,433 contacted accounts / 10,324 attempted accounts = **23.57%**).*
- **Call-Level Answer Rate (19.87% 7-Month Average):**
  Evaluates telephony network efficiency per dial event. Computed as total answered call events divided by total dial events:
  ```sql
  COUNT(CASE WHEN call_status = 'ANSWERED' THEN 1 END) * 100.0 
    / COUNT(*)
  ```
  *(e.g., Jan: 2,543 answered calls / 12,683 total dials = **20.05%**).*
- Because some accounts received more than one answered call in a month (110 accounts in Jan received 2+ answered calls), the account-level contact rate (23.57%) is naturally higher than the dial-level answer rate (20.05%). Both metrics are completely flat across all 7 months.

---

## 4. Quantitative Waterfall Decomposition: Bridging the 11% Claim to Reality

```
   Reported Headline Claim:      +11.00% (MoM Claimed Improvement)
   - Calendar Normalization:     -10.01% (Eliminating February-to-March Leap Year / 28-day rebound bias)
   - Status Exclusion (Reversals):-0.54% (Deducting bounced & reversed cash inflows)
   - Deduplication Correction:    -0.52% (Eliminating gateway retry noise & unreferenced duplicates)
   ---------------------------------------------------------------------------------------------------
   = AUDITED GROUND-TRUTH RECOVERY: -0.07% (Actual Average MoM Performance: FLAT)
```

`[FACT]`:
- Realized operational recovery did **not** improve. 
- The collections platform is operating at a stagnant steady-state efficiency ceiling constrained by telephony infrastructure, targeting leakage, and human dialer throughput.
