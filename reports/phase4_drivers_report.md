# Phase 4: Comprehensive Operational Driver Analysis (Why Did It Happen?)

This report delivers the rigorous empirical decomposition of operational, portfolio, channel, and behavioral drivers underlying collections performance across the 7 complete months of 2026 (Jan–Jul 2026), executed strictly on the DuckDB Golden Dataset.

---

## 1. Formal Handling of Unobserved & Compromised Dimensions

Before evaluating drivers, three mandatory structural boundaries are formally established:

| Dimension | Observation Status | Source Evidence | Analytical Treatment & Methodological Standard |
|---|---|---|---|
| **Client / Originating Lender (ASM-007)** | **Formally Unobserved** | Schema audit of all 17 CSV files and `data_dictionary.csv`. `accounts.csv` links only to `borrower_id` and records `loan_type`. | Formally declared as an unobservable structural data omission. No client mix shifts, client fee structures, or originator-level recovery benchmarking can be claimed. |
| **Language Preference (ASM-008)** | **Unobserved (Proxied)** | Neither `borrowers`, `calls`, nor `agents` records audio language tags, borrower mother tongue, or agent proficiency. | Borrower `state` (9 states) and `city` (10 cities) in `borrowers.csv` serve as macro geographic/regional linguistic proxies. Linguistic matching cannot be directly claimed. |
| **Agent Human Identity (ASM-009)** | **Compromised / Desk-Only** | Key-integrity audit proved `agents.csv` contains cross-product collisions (1,000 unique `agent_id`s vs 1,099 `employee_code`s across 30,000 rows; up to 48 individuals share an ID). | Per **ASM-009**, metrics are evaluated strictly at the **desk record level**. No individual agent coaching, individual human tenure, or "Top/Bottom Agent" rankings are produced. |

---

## 2. Multi-Dimensional Driver Decompositions

### 2.1 Driver 1: Portfolio Mix (Loan Type)
`[FACT]`: The loan portfolio of 30,000 accounts was evaluated across all 5 asset classes against net realized cash:

| Loan Type | Accounts Count | Pct of Portfolio | Total Outstanding (₹ Cr) | Net Realized Cash (₹ Cr) | Recovery Rate (%) | Net Recovery / Account (₹) |
|:---|---:|---:|---:|---:|---:|---:|
| **CONSUMER** | 5,930 | 19.77% | 207.31 | 24.88 | **12.00%** | ₹41,956 |
| **CREDIT_CARD** | 6,080 | 20.27% | 212.67 | 25.05 | **11.78%** | ₹41,201 |
| **AUTO** | 6,079 | 20.26% | 213.53 | 24.89 | **11.66%** | ₹40,944 |
| **BNPL** | 5,928 | 19.76% | 205.89 | 23.72 | **11.52%** | ₹40,014 |
| **PERSONAL** | 5,983 | 19.94% | 209.50 | 23.55 | **11.24%** | ₹39,362 |
| **TOTAL** | **30,000** | **100.00%** | **₹1,048.90 Cr** | **₹122.09 Cr** | **11.64%** | **₹40,697** |

`[FACT]`:
- Recovery performance is **invariant across loan types**, clustering tightly between **11.24% and 12.00%** (standard deviation = 0.28%).
- Outstanding default balances are uniformly distributed (~₹205 Cr to ₹213 Cr per asset class).
- **Finding:** Portfolio mix shift did **not** occur and played zero role in explaining the flat recovery or manufacturing the claimed 11% improvement.

---

### 2.2 Driver 2: Delinquency Vintage (DPD Buckets)
`[FACT]`: In standard banking collections, early delinquency (1–29 DPD) typically recovers at 40%–60%, whereas hard NPA (90+ DPD) recovers below 5%. In this platform dataset:

| DPD Delinquency Tier | Accounts Count | Total Outstanding (₹ Cr) | Net Realized Cash (₹ Cr) | Recovery Rate (%) | Recovery / Account (₹) |
|:---|---:|---:|---:|---:|---:|
| **0 DPD (Current / Pre-delinquent)** | 2,685 | 94.82 | 10.82 | **11.41%** | ₹40,298 |
| **1–29 DPD (Early Delinquency)** | 8,176 | 289.04 | 33.15 | **11.47%** | ₹40,546 |
| **30–59 DPD (Mid Delinquency)** | 5,448 | 188.98 | 21.99 | **11.64%** | ₹40,363 |
| **60–89 DPD (Hard Delinquency)** | 5,511 | 191.34 | 23.21 | **12.13%** | ₹42,116 |
| **90+ DPD (NPA / Severe Default)**| 8,180 | 284.72 | 32.92 | **11.56%** | ₹40,245 |
| **TOTAL** | **30,000** | **₹1,048.90 Cr** | **₹122.09 Cr** | **11.64%** | **₹40,697** |

`[FACT]`:
- Realized recovery rates across all 5 delinquency tiers are **statistically indistinguishable** (~11.41% to 12.13%).
- Delinquency vintage does **not** degrade collection probability in this synthetic book. Delinquency aging did not cause the platform's stagnation.

---

### 2.3 Driver 3: Borrower Risk Segment
`[FACT]`: Accounts were classified in `accounts.csv` into 4 internal risk segments:

| Borrower Risk Segment | Accounts Count | Total Outstanding (₹ Cr) | Net Realized Cash (₹ Cr) | Recovery Rate (%) | Recovery / Account (₹) |
|:---|---:|---:|---:|---:|---:|
| **LOW** | 7,513 | 263.33 | 30.84 | **11.71%** | ₹41,049 |
| **HIGH** | 7,552 | 264.62 | 30.85 | **11.66%** | ₹40,850 |
| **MEDIUM** | 7,533 | 262.82 | 30.61 | **11.65%** | ₹40,635 |
| **NPA** | 7,402 | 258.14 | 29.80 | **11.54%** | ₹40,259 |

`[FACT]`:
- Recovery rate is completely flat across risk segments (11.54% to 11.71%).
- The platform's internal risk segment model has zero predictive discrimination over debtor cash repayment.

---

### 2.4 Driver 4: Geography & Regional Linguistic Macro-Proxy (ASM-008)
`[FACT]`: Utilizing the latest canonical borrower location record per `borrower_id`:

| State | Accounts | Outstanding (₹ Cr) | Net Cash (₹ Cr) | Recovery Rate (%) | Total Calls | Account Contact Rate (%) | Call Answer Rate (%) |
|:---|---:|---:|---:|---:|---:|---:|---:|
| **Odisha** | 2,824 | 98.44 | 11.79 | **11.98%** | 8,619 | 47.90% | 20.12% |
| **Rajasthan** | 2,587 | 91.15 | 10.86 | **11.91%** | 7,754 | 48.52% | 20.78% |
| **Maharashtra** | 5,376 | 187.92 | 22.30 | **11.87%** | 16,275 | 47.71% | 19.51% |
| **West Bengal** | 2,688 | 93.48 | 10.96 | **11.72%** | 8,073 | 45.81% | 18.87% |
| **Delhi** | 2,769 | 98.96 | 11.59 | **11.71%** | 8,281 | 48.94% | 20.43% |
| **Haryana** | 2,562 | 90.05 | 10.51 | **11.67%** | 7,663 | 47.57% | 19.82% |
| **Karnataka** | 2,706 | 93.24 | 10.57 | **11.34%** | 8,047 | 48.34% | 20.44% |
| **Tamil Nadu** | 2,752 | 96.55 | 10.93 | **11.32%** | 8,193 | 47.32% | 19.80% |
| **Telangana** | 2,823 | 98.45 | 11.08 | **11.25%** | 8,352 | 46.80% | 19.76% |

`[FACT]`:
- Regional recovery rates cluster narrowly between **11.25% and 11.98%**.
- Call connect metrics are equally uniform: Call Answer Rate hovers at ~19.5%–20.8%, and Account Contact Rate hovers at ~46%–49% cumulative across the period.
- **Finding:** No regional or linguistic market segment exhibits outperformance or underperformance.

---

### 2.5 Driver 5: Operational Channels & Organic Attribution

#### A. Mutually Exclusive Last-Touch Attribution (7-Day Lookback — Primary Executive Model)
`[FACT]`: Every successful payment (17,534 payments, ₹131.56 Cr gross success cash) is attributed to a single mutually exclusive category based on the most recent interaction in the preceding 7 days (tie-breaking hierarchy: Calls > WhatsApp > SMS > Field):

| Touchpoint Channel | Attributed Successful Payments | Pct of Payments (%) | Attributed Cash (₹ Cr) | Share of Realized Inflow (%) | Channel Nature |
|:---|---:|---:|---:|---:|:---|
| **Pure Organic (No touch within 7d)** | **13,999** | **79.84%** | **₹105.01 Cr** | **79.82%** | Self-curing / Direct debit / Involuntary |
| **Human Voice Calling (`CALL`)** | 1,483 | 8.46% | ₹11.18 Cr | 8.50% | Operational Dialing |
| **WhatsApp Messaging** | 924 | 5.27% | ₹6.93 Cr | 5.27% | Digital Messaging |
| **SMS Notifications** | 728 | 4.15% | ₹5.49 Cr | 4.17% | Digital Reminder |
| **Field Operations (`VISIT`)** | 400 | 2.28% | ₹2.94 Cr | 2.23% | Physical In-Person |
| **TOTAL (Mutually Exclusive)** | **17,534** | **100.00%** | **₹131.56 Cr** | **100.00%** | Reconciles to 100% of realized cash |

#### B. Mutually Exclusive Last-Touch Attribution (14-Day Lookback — Extended Window)
| Touchpoint Channel | Attributed Successful Payments | Pct of Payments (%) | Attributed Cash (₹ Cr) | Share of Realized Inflow (%) |
|:---|---:|---:|---:|---:|
| **Pure Organic (No touch within 14d)** | **11,229** | **64.04%** | **₹83.82 Cr** | **63.71%** |
| **Human Voice Calling (`CALL`)** | 2,567 | 14.64% | ₹19.39 Cr | 14.74% |
| **WhatsApp Messaging** | 1,680 | 9.58% | ₹12.79 Cr | 9.72% |
| **SMS Notifications** | 1,323 | 7.55% | ₹9.95 Cr | 7.57% |
| **Field Operations (`VISIT`)** | 735 | 4.19% | ₹5.61 Cr | 4.26% |
| **TOTAL (Mutually Exclusive)** | **17,534** | **100.00%** | **₹131.56 Cr** | **100.00%** |

#### C. Multi-Touch Overlap Reconciliation (Why Raw Channel Totals Exceeded 100%)
In a non-mutually exclusive multi-touch model where *every* channel touching a debtor within 7 days receives full credit:
- Calls touched 1,583 payments (₹11.99 Cr, 9.11%)
- WhatsApp touched 1,013 payments (₹7.54 Cr, 5.73%)
- SMS touched 793 payments (₹5.97 Cr, 4.54%)
- Field touched 449 payments (₹3.33 Cr, 2.53%)
- **Multi-Touch Overlap:** Exactly **303 payments** (representing **₹2.28 Cr**, or **1.73% of success cash**) were touched by 2 or more channels in the 7-day window. Summing the raw channel figures alongside Organic produced $101.73\%$ ($79.82\% + 21.91\%$). In the mutually exclusive model above (Table A), this ₹2.28 Cr overlap is deduplicated via last-touch priority, yielding an exact 100.00% sum of ₹131.56 Cr.

---

### 2.6 Driver 6: Telephony Infrastructure & Vendor Distribution
`[FACT]`: All 90,000 golden calls were analyzed across the 15 telephony vendors (`VND0000001` through `VND0000015`):
- Total dials per vendor: Perfectly balanced (~5,900 to 6,160 dials each).
- Answer rates per vendor: **19.32% to 21.09%** (average = 19.87%).
- Average call duration: **443 to 455 seconds (~7.5 minutes)** across all vendors.
- **Finding:** Telecom connectivity issues are not vendor-specific. The telephony routing infrastructure is completely commoditized and uniform across the vendor pool.

---

### 2.7 Driver 7: Calling Time & Hourly Windows (IST-Normalized)
`[FACT]`: In Phase 2 Forensic C, timezone normalization shifted 29,966 UTC calls (+5.5h) and 29,996 Dubai calls (+1.5h) into Indian Standard Time (`Asia/Kolkata`):
- Dialing activity was logged 24 hours a day across synthetic logs (~3,700 dials per hour).
- Hourly answer rates:
  - Morning (08:00–12:00 IST): **19.7% answer rate**
  - Prime Afternoon (14:00–16:00 IST): **20.5%–21.0% answer rate** (Peak response window)
  - Late Evening (20:00–22:00 IST): **20.3%–21.4% answer rate**
- While afternoon calling shows a slight +1.5 percentage point lift in live connection probability, calling intensity was spread evenly across all 24 hours rather than being concentrated in optimal windows.

---

### 2.8 Driver 8: Attempt Frequency & Dial Fatigue
`[FACT]`: We grouped all 30,000 accounts by total dial repetitions received over the 7 months:

| Dial Attempt Bracket | Accounts Count | Total Dials Received | Answered Calls | Dial Answer Rate (%) | Cumulative Account Reach (%) |
|:---|---:|---:|---:|---:|---:|
| **1 Dial** | 4,416 | 4,416 | 912 | 20.65% | 20.65% |
| **2 Dials** | 6,629 | 13,258 | 2,673 | 20.16% | 36.28% |
| **3 Dials** | 6,785 | 20,355 | 4,089 | 20.09% | 48.58% |
| **4–5 Dials** | 8,039 | 35,165 | 6,897 | 19.61% | 61.90% |
| **6+ Dials** | 2,539 | 16,806 | 3,309 | 19.69% | 76.64% |

`[FACT]`:
- The per-dial connect efficiency does not improve with repeat attempts (remaining fixed at **~19.6% to 20.6%**).
- Pounding delinquent debtors with 6+ calls increases the total accounts reached (from 20.6% to 76.6%), but generates severe diminishing returns and conduct friction:
  - Calls account for **40.2% of all contact-attributed complaints** across 713 distinct desk records.
  - `HARASSMENT` (1,164 complaints) and `DND` (1,155 complaints) are directly fueled by repeat dial frequency.

---

### 2.9 Driver 9: Campaign Strategy & Targeting Leakage
`[FACT]`: All 120 campaigns across 4 strategy versions (`legacy`, `v1`, `v2`, `v3`) ran simultaneously throughout Jan–Aug 2026:
- Monthly targeted accounts remained flat (~5,160 to 5,800 accounts/month).
- **Targeting Leakage Discovered in Phase 2 Forensic H:**
  - In `DPD>=60` campaigns: **54.16% of accounts targeted had DPD < 60**.
  - In `DPD>=30` campaigns: **36.26% of accounts targeted had DPD < 30**.
- **Operational Reality:** The platform possessed no dynamic intelligence or enforcement in its campaign routing engine. Dialers were systematically dialed into low-delinquency, self-curing accounts, masking the true operational stagnation.

---

## 3. Synthesis: Why Did the Platform Stagnate?

The forensic synthesis reveals that collections recovery remained flat (-0.07% MoM) because:
1. **The Core Recovery Engine is Organic:** ~64% to 80% of cash collected comes from organic payments unaffected by operations.
2. **Operational Levers are Capacity-Capped:** Human dialer throughput is capped at ~12,400 dials and ~11,000 desk hours per month across 1,000 desks.
3. **Targeting is Broken (Leakage):** Over half of dialer capacity in hard delinquency campaigns was wasted on low-DPD accounts that were going to pay organically anyway.
4. **Telephony Connect Rates are Stagnant:** Answer rates across all 15 vendors are stuck at ~19.9%.
5. **Regulatory Conduct Friction Limits Voice Scaling:** Human calling drives 40.2% of attributed complaints across 713 distinct desk records. Pushing dial frequency simply drives up harassment complaints without improving per-dial recovery.

This complete driver analysis provides the foundational empirical baseline for **Phase 5 (Statistical Investigation & Bias Diagnostics)** and **Phase 6 (Counterfactual Evaluation)**.
