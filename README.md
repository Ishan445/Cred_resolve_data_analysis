# CredResolve: Debt Collections Forensic Audit & ₹10 Cr Capital Allocation

An enterprise-grade forensic data engineering, analytics, and econometrics repository investigating a multi-channel collections platform's operational performance, evaluating the claimed *"11% Month-on-Month recovery improvement"*, and modeling the deployment of a **₹10 Cr capital investment**.

---

## 📌 Executive Summary & Findings

| Strategic Question | Executive Finding | Evidentiary Verdict |
|---|---|---|
| **Is the 11% MoM Improvement Real?** | **Factually FALSE.** True ground-truth net realized cash recovery is **flat (-0.07% average MoM)** across Jan–Jul 2026, oscillating tightly between ₹15.87 Cr and ₹17.56 Cr. | `[FACT]` |
| **How was 11% Manufactured?** | **(1)** Calendar bounce (+10.01% in Mar) post-28-day February (-9.64%), **(2)** gross payment attempts (+53.89% cash inflation over net cash), and **(3)** claiming 100% operational credit for organic self-curers. | `[FACT]` |
| **Is Recovery Campaign-Driven?** | **No.** Mutually exclusive 7-day attribution proves **79.82% of collected cash (₹105.01 Cr) is pure organic** (63.71% at 14d). Multi-touch overlap is 303 payments (1.73% / ₹2.28 Cr). | `[FACT]` |
| **Why Did Collections Stagnate?** | **Three Structural Bottlenecks:** **(1)** Voice capacity ceiling (1,000 desks, ~19.9% flat connect rate), **(2)** Massive campaign leakage (54.16% of accounts in `DPD>=60` had DPD < 60), and **(3)** Conduct friction (calls drive 40.2% of complaints across 713 desk records). | `[FACT]` |
| **Where to Deploy ₹10 Cr Capital?** | **Intelligent Targeting & Dynamic Propensity Routing Engine.** Reallocating leaked dialer capacity away from organic accounts to responsive delinquent debt yields **~80% to 100% Net ROI** (Base case: +₹1.65 Cr/mo) and pays back in **~6 to 8 months**. | `[RECOMMENDED LEVER]` |

---

## 🗂️ Repository Structure

```
Cred-resolve/
├── README.md                              # Master project overview & reproduction guide
├── LICENSE                                # MIT License
├── walkthrough.md                         # Chronological phase-by-phase audit & verification record
├── requirements.txt                       # Python environment dependencies
├── .gitignore                             # Standard Git ignore rules
├── dashboard/                             # Deliverable 5: Streamlit Executive Cockpit
│   ├── app.py                             # Single-screen interactive executive dashboard
│   └── README.md                          # Dashboard quickstart & user manual
├── reports/                               # Deliverables 4 & 6: Formal Reports & Audits
│   ├── executive_memo.md                  # C-Suite 2-Page Executive Decision Brief
│   ├── data_quality_report.md             # End-to-End Data Quality & Forensics Report
│   ├── assumptions_log.md                 # Version-controlled assumptions (ASM-001 to ASM-010)
│   ├── phase2_forensics_report.md         # Forensic Hunts Matrix (Hunts A through H)
│   ├── phase3_metrics_report.md           # PTP confusion matrix & independent operational framework
│   └── phase4_drivers_report.md           # Multi-dimensional driver decomposition
├── architecture/                          # Deliverable 7: System Architecture & Design
│   ├── production_analytics_design.md     # Production lakehouse design, contracts & SLAs
│   └── system_architecture.mmd            # Version-controlled Mermaid.js architecture blueprint
├── sql/                                   # Deliverable 1: Production SQL Repository
│   ├── 01_staging/01_staging_ddl.sql      # Type casting & timezone normalization to IST
│   ├── 02_cleaning_dedup/                 # Idempotent deduplication & entity resolution
│   ├── 03_transformations/                # Multi-touch attribution & touchpoint lineage
│   ├── 04_golden_marts/                   # Analytical dimensional facts & dimensions
│   └── 05_analytics_metrics/              # Reusable executive KPI queries
├── pipeline/                              # Deliverable 3: Automated Pipeline Code
│   ├── config.py                          # Environment paths & schema configurations
│   └── build_golden.py                    # Automated, idempotent Golden Dataset builder
├── scripts/                               # Dedicated analysis, profiling & audit scripts
│   ├── phase0_profiling.py                # Raw table baseline profiling
│   ├── setup_golden_duckdb.py             # DuckDB in-memory golden tables instantiation
│   ├── run_phase4_complete_analysis.py    # Driver analysis execution
│   └── reconcile_attribution_last_touch.py# Mutually exclusive attribution runner
└── data/raw/           # 17 Raw Relational CSV Feeds (639,185 rows)
```

---

## 🚀 Quickstart & Reproduction

### 1. Environment Setup
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
pip install -r requirements.txt
```

### 2. Build the Golden Dataset (Idempotent Pipeline)
Executes deduplication, entity resolution, and timezone normalization to produce clean Parquet files:
```bash
python -m pipeline.build_golden
```

### 3. Launch the Executive Dashboard (Streamlit)
Launches the single-screen C-suite dashboard with interactive waterfall bridge and ₹10 Cr scenario simulator:
```bash
streamlit run dashboard/app.py
```

---

## 🔬 Core Methodological Standards

- **Evidentiary Hierarchy:** Every finding is tagged: `[FACT]` (database ground truth), `[STRONG EVIDENCE]` (statistically verified), `[CORRELATION]`, or `[HYPOTHESIS]`.
- **Standing Boundary Disclosures:**
  - **ASM-007 (Client):** Originator/client dimension is formally unobservable in the raw schema.
  - **ASM-008 (Language):** Direct language is unrecorded; the 9 states and 10 cities serve as regional linguistic macro-proxies.
  - **ASM-009 (Agent Identity):** `agents.csv` contains cross-product key collisions (1,000 IDs vs 1,099 codes across 30,000 rows). Performance is strictly valid at the **desk record level**; no individual employee coaching or rankings are produced.
