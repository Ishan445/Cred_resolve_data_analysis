# EXECUTIVE MEMO: DEBT COLLECTIONS FORENSIC AUDIT & ₹10 CR CAPITAL ALLOCATION

**TO:** Investment Committee & Executive Leadership  
**FROM:** Senior Analytics Engineering & Forensics Taskforce  
**DATE:** September 10, 2026  
**SUBJECT:** Forensic Verification of the Claimed "11% MoM Recovery Improvement" & Capital Deployment Recommendation  
**STATUS:** Confidential / Final Audited Assessment  

---

## 1. Executive Summary & Verdict

### The headline claim of an "11% Month-on-Month Recovery Improvement" is demonstrably false.
An audit across all 17 underlying operational tables (reconciling 639,185 raw records to **607,135 golden clean records**) demonstrates that **net realized cash collections remained essentially flat** throughout the seven complete operating months of 2026 (January through July):
- **True Average MoM Net Recovery Growth:** **-0.07%**, reflecting negligible secular change.
- **Monthly Net Cash Trajectory:** Collections oscillated within a narrow corridor between **₹15.87 Cr** (February) and **₹17.56 Cr** (January), averaging **₹16.81 Cr/month** with a standard deviation of ₹0.68 Cr (a 4.0% coefficient of variation).
- **Three Reporting Distortions Created the Illusion of Growth:**
  1. **Calendar Rebound Bias (-10.01%):** Management highlighted March 2026 (+10.01% net, +12.35% gross), which was simply an arithmetic snap-back after February's 28-day dip (-9.64%), misrepresenting a short-month artifact as an operational breakthrough.
  2. **Gross vs. Net Overstatement (+53.89%):** Legacy dashboards booked un-deduplicated gross payment attempts—including failed authorizations and pending transactions—tallying **₹187.89 Cr**. This overstated audited net realized cash (**₹122.09 Cr**) by **+53.89%** (+57.04% when measured against the pre-dedup gross volume of ₹191.73 Cr).
  3. **The Attribution Fallacy (79.82% Organic Cash):** In reality, **79.82% of all collected cash (₹105.01 Cr)** arrived without a single customer touchpoint across any channel in the preceding 7 days (and 63.71% remained untouched over a 14-day window). Operations had been claiming credit for payments borrowers made on their own initiative.

```
Quantitative Waterfall Bridging Headline Claim to Audited Reality:
   Reported Headline Claim:        +11.00% (MoM Claimed Improvement)
   - Calendar Normalization:       -10.01% (Eliminating February-to-March 28-day rebound bias)
   - Status Exclusion (Reversals):  -0.54% (Deducting bounced & reversed cash inflows)
   - Deduplication Correction:      -0.52% (Eliminating gateway retry noise & unreferenced duplicates)
   ---------------------------------------------------------------------------------------------------
   = AUDITED GROUND-TRUTH RECOVERY:   -0.07% (Actual Average MoM Performance: FLAT)
```

---

## 2. Forensic Financial & Operational Reconciliations

### Where the Money Actually Went: The Cash Realization Ledger
Reconciling all 25,000 recorded transactions across the 30,000 delinquent portfolio accounts directly against gateway settlements establishes the true cash position:
- **Gross Recorded Payment Volume:** **₹187.89 Cr** across 25,000 transactions.
- **Successful Inflows (`payment_status = 'SUCCESS'`):** **₹131.56 Cr** across 17,534 transactions.
- **Deducted Reversals (`payment_status = 'REVERSED'`):** **₹9.47 Cr** across 1,254 transactions.
- **Net Realized Cash Recovery (Numerator):** $\mathbf{₹122.09\text{ Cr}}$ ($₹131.56 - ₹9.47\text{ Cr}$).
- **Non-Realized Ingestion Noise:** **₹56.33 Cr** (29.98% of gross), consisting of `FAILED` transactions (**₹27.84 Cr** across 3,677 attempts) and `PENDING` transactions (**₹19.02 Cr** across 2,535 attempts).

### The Promise-to-Pay (PTP) Signal Is Broken
Prior operational reviews highlighted an apparent ~25% "PTP Kept Rate" as evidence of predictive borrower commitments. When we tested all 18,000 recorded promises against bank settlements ($\pm 3$ days of `promised_date`, $\pm 10\%$ amount), that correlation fell apart:
- Across 4,489 accounts marked `KEPT`, **4,486 had no matching payment whatsoever**—a 99.93% classification disagreement.
- Furthermore, accounts marked `KEPT` settled at a 27.6% rate, statistically indistinguishable from those labeled `BROKEN` (26.0%), `CANCELLED` (26.3%), and `OPEN` (26.4%). The platform's disposition labels provide zero forward visibility into borrower settlement behavior.

### Stable Benchmarks: Seven Months of Capped Performance
| Operational Metric | Jan 2026 | Feb 2026 | Mar 2026 | Apr 2026 | May 2026 | Jun 2026 | Jul 2026 | 7-Month Trajectory |
|:---|---:|---:|---:|---:|---:|---:|---:|:---|
| **Unique Accounts Attempted** | 10,324 | 9,531 | 10,417 | 10,036 | 10,370 | 9,971 | 10,278 | **Flat (~10,100/mo)** |
| **Unique Accounts Contacted** | 2,433 | 2,188 | 2,457 | 2,258 | 2,491 | 2,385 | 2,345 | **Flat (~2,365/mo)** |
| **Account Contact Rate (%)** | **23.57%** | **22.96%** | **23.59%** | **22.50%** | **24.02%** | **23.92%** | **22.82%** | **Stable (23.34% Avg)** |
| **Total Call Dials** | 12,683 | 11,569 | 12,844 | 12,241 | 12,746 | 12,128 | 12,578 | **Flat (~12,400/mo)** |
| **Answered Calls** | 2,543 | 2,279 | 2,567 | 2,362 | 2,592 | 2,474 | 2,433 | **Flat (~2,460/mo)** |
| **Call-Level Answer Rate (%)** | **20.05%** | **19.70%** | **19.99%** | **19.30%** | **20.34%** | **20.40%** | **19.34%** | **Stable (19.87% Avg)** |
| **Active Desk Hours** | 11,162 | 10,557 | 11,131 | 10,620 | 10,833 | 10,703 | 11,180 | **Capacity Capped** |
| **Net Realized Cash (₹ Cr)** | **₹17.56** | **₹15.87** | **₹17.45** | **₹16.18** | **₹17.16** | **₹16.26** | **₹17.20** | **Static (₹16.81 Cr Avg)** |
| **Recovery per Desk Hour (₹)** | **₹15,732** | **₹15,033** | **₹15,677** | **₹15,235** | **₹15,840** | **₹15,192** | **₹15,385** | **Completely Flat** |

---

## 3. The Structural Bottlenecks Capping Collections

Portfolio mix was remarkably steady throughout the observation window: loan products (11.24%–12.00%), delinquency tiers (11.41%–12.13%), borrower credit risk segments (11.54%–11.71%), and regional states (11.25%–11.98%) all tracked near-identical recovery rates with negligible variation. The plateau in recoveries is not driven by macro or debtor-mix shifts; rather, it stems directly from three operational bottlenecks:

### 1. Hard Telephony and Workstation Ceilings
- Outbound dialing capacity is physically constrained by 1,000 desk records producing ~12,400 dials across ~11,000 session hours monthly (1.54 dials per desk-hour).
- Telecom connectivity is entirely commoditized: call answer rates across all 15 telephony vendors cluster uniformly between **19.32% and 21.09%** (averaging 19.87%). No vendor provides a routing edge.
- Pounding debtors with repeat dials exhibits steep diminishing returns: moving from 1 dial to 6+ dials raises cumulative reach from 20.6% to 76.6%, but per-dial connect efficiency stays flat at ~19.9% while escalating customer backlash.

### 2. Chronic Campaign Targeting Leakage
- Auditing all 45,000 daily targeting records against campaign strategy rules revealed severe operational leakage:
  - In `DPD>=60` campaigns: **54.16% of targeted accounts had DPD < 60**.
  - In `DPD>=30` campaigns: **36.26% of targeted accounts had DPD < 30**.
- **Impact:** Over half of expensive human dialing capacity was misallocated toward early-stage, low-delinquency accounts that were already poised to settle organically, starving hard delinquent accounts of targeted intervention.

### 3. Escalating Conduct Friction and Regulatory Exposure
- Examining all 8,000 complaints in `complaints.csv` against interaction history (via 14-day backward time-proximity) confirms that human voice outreach is the primary catalyst for escalation: phone calls precede **40.2% of all contact-attributed complaints** (1,176 complaints out of 2,926 touchpoint-attributed tickets; the remaining 5,074 had no touchpoint within 14 days) across **713 distinct `agent_id` desk records**.
- **Portfolio-wide vs. Call-Attributed Complaint Breakdown:** Across the entire 8,000-ticket dataset, `AGENT_BEHAVIOUR` (1,202 tickets, 15.0%) and `HARASSMENT` (1,126 tickets, 14.1%) represent the largest conduct categories. Within the 1,176 complaints specifically following phone calls across the 713 desk records, conduct violations remain prominent: `HARASSMENT` accounts for **167 tickets** (14.2% across 159 desk records), `DND` violations account for **163 tickets** (13.9% across 148 desk records), and `AGENT_BEHAVIOUR` accounts for **156 tickets** (13.3% across 149 desk records), alongside disputes (184 tickets) and payment issues (181 tickets).
- Because desk records represent shared terminal logins rather than unique individuals (up to 48 people cycle through a single ID over time), these figures reflect workstation-level contact volume rather than personal agent scorecards. Attempting to lift recovery by simply ramping up calling volume without fixing targeting will multiply regulatory exposure.

---

## 4. Multi-Touch Channel Attribution: Isolating True Channel Impact

To eliminate channel double-counting, every successful payment was attributed under a strict 7-day last-touch hierarchy (Calls > WhatsApp > SMS > Field):

| Channel | Attributed Payments | Pct of Payments (%) | Attributed Cash (₹ Cr) | Share of Realized Cash (%) | Operational Role |
|:---|---:|---:|---:|---:|:---|
| **Pure Organic** | **13,999** | **79.84%** | **₹105.01 Cr** | **79.82%** | Self-curing / Direct debit (No touch within 7d) |
| **Human Voice Calling** | **1,483** | **8.46%** | **₹11.18 Cr** | **8.50%** | High cash yield, severe conduct risk |
| **WhatsApp Messaging** | **924** | **5.27%** | **₹6.93 Cr** | **5.27%** | High margin, zero harassment complaints |
| **SMS Notifications** | **728** | **4.15%** | **₹5.49 Cr** | **4.17%** | Low-cost reminder channel |
| **Field Operations** | **400** | **2.28%** | **₹2.94 Cr** | **2.23%** | High touch, low scale |
| **TOTAL** | **17,534** | **100.00%** | **₹131.56 Cr** | **100.00%** | **Exact match to Gross Success Cash** |

*(Note: In a non-exclusive model, 303 payments representing ₹2.28 Cr / 1.73% received touches from multiple channels, causing raw channel additions to sum to 101.73%. At a 14-day lookback, Organic recovery accounts for 63.71% / ₹83.82 Cr).*

---

## 5. ₹10 Cr Capital Investment Recommendation

### Strategic Evaluation of Candidate Levers
1. **More Collection Agents:** **REJECT.** Unit economics do not justify expansion. Agent calling drives 40.2% of complaints across 713 desk records; adding headcount without fixing routing will merely amplify regulatory harassment risk and dilute recovery per desk hour.
2. **Telephony Infrastructure:** **REJECT.** Connect rates across 15 vendors are commoditized (~19.9%). Upgrading telecom switches provides no incremental debtor willingness to pay.
3. **Field Operations:** **REJECT.** Represents only 2.23% of cash (₹2.94 Cr). High travel OpEx makes unit scaling unviable.
4. **AI Voice Automation:** **HOLD / PHASE 2.** Promising long-term, but automated bots fired into leaked targeting lists will trigger severe DND and harassment fines.
5. **WhatsApp / Digital Engagement:** **HIGH MERIT / CO-INVEST.** Delivered ₹6.93 Cr with near-zero conduct friction; essential digital bridge.
6. **Better Borrower Targeting & Dynamic Propensity Routing:** **RECOMMENDED PRIMARY LEVER (WINNER).**

### The Investment Mandate: Deploy ₹10 Cr into "Intelligent Targeting & Orchestration Engine"
- **Capital Allocation (₹10.00 Cr):**
  - **₹5.50 Cr (CapEx):** Real-time event-driven targeting engine, machine-learning propensity scoring models, and integration of automated guardrails to eliminate the 54.16% campaign leakage.
  - **₹2.50 Cr (CapEx/OpEx):** WhatsApp interactive resolution bot & two-way digital settlement journeys.
  - **₹2.00 Cr (OpEx):** Telecom caller ID reputation management and compliance call monitoring.
- **Financial Return & Unit Economics (Modeled Projection):**
  - **Derivation & Modeling Mechanism:** Dialers currently expend ~3,600 dials/month (representing ~₹1.18 Cr/month of nominal collections) on low-DPD accounts that cure organically without intervention. Implementing ML propensity models and hard guardrails redirects this misallocated capacity toward actionable delinquent accounts (excluding both organic self-curers and hard uncollectible write-offs).
  - **Sensitivity Scenario Analysis:**
    - **Conservative Scenario** *(25% leakage redirected, +5% relative lift)*: **+₹0.75 Cr/month** incremental cash $\rightarrow$ ₹9.0 Cr annual collections $\rightarrow$ **-10% to 0% Net ROI** (break-even: 13–15 months).
    - **Base Case Scenario** *(50% leakage redirected + digital WhatsApp journey adoption, +10% lift)*: **+₹1.65 Cr/month** incremental cash (+9.8% lift over current ₹16.81 Cr baseline) $\rightarrow$ **₹19.8 Cr** 12-month gross collections $\rightarrow$ **~80% to 100% Net ROI** (break-even: ~6 to 8 months).
    - **Optimistic Scenario** *(75% leakage eliminated + full digital automation)*: **+₹2.40 Cr/month** incremental cash $\rightarrow$ ₹28.8 Cr annual collections $\rightarrow$ **~160% to 190% Net ROI** (break-even: ~4 to 5 months).
  - **Downside Risk Mitigation (Modeled Scenario):** Eliminating ~3,600 aggressive outbound dials per month to non-delinquent borrowers is modeled to reduce customer complaint friction by an estimated **25% to 40%** (base: ~35%), directly safeguarding against regulatory intervention.

---

## 6. Standing Limitations & Boundary Declarations

To ensure analytical integrity, three structural data boundaries are formally documented:
1. **Lender/Originator Identity (ASM-007):** No institutional originator ID exists in the raw schema. Institutional client benchmarking or client fee structures cannot be investigated.
2. **Borrower Language (ASM-008):** Direct borrower linguistic preference is unrecorded. Borrower state (9 states) and city (10 cities) serve as macro regional/linguistic proxies.
3. **Workstation-Level Agent Data (ASM-009):** `agents.csv` contains cross-product key collisions (1,000 IDs vs 1,099 employee codes across 30,000 rows; up to 48 people per ID). Metrics are strictly valid at the **desk record level**. No individual coaching, agent tenure, or individual employee ranking can be made against this dataset.
