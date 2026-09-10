# Executive Collections Forensics & Investment Dashboard

## Overview
A dedicated single-screen Streamlit application designed for C-suite and Investment Committee leadership. Provides a complete 60-second walkthrough of the forensic audit, audited net cash reconciliations, channel attribution, and interactive sensitivity levers for deploying the ₹10 Cr capital investment.

## Quickstart (Launch in 5 Seconds)
To launch the dashboard locally:
```bash
streamlit run dashboard/app.py
```

## Key Executive Views
1. **Executive Verdict & Topline KPI Cards:**
   - Realized Net Cash: **₹122.09 Cr** (vs ₹187.89 Cr gross attempts, +53.89% legacy overstatement).
   - Audited MoM Growth: **-0.07%** (vs +11.00% claimed).
   - Account Contact Rate: **23.34%** (vs Call Answer Rate: 19.87%).
   - Organic Cash Share: **79.82%** (7d lookback) / **63.71%** (14d lookback).
   - Implicated Desk Codes: **713 Desks** (40.2% of attributed complaints).
2. **Quantitative Waterfall:** Interactive chart bridging the +11% claim down to -0.07% ground truth.
3. **Monthly Cash Trajectory:** Visual comparison of net cash vs gross attempts across Jan–Jul 2026.
4. **Mutually Exclusive Channel Attribution:** Dynamic toggle between 7-day and 14-day lookbacks, reconciling to 100% of cash.
5. **Interactive ₹10 Cr Capital Investment Simulator:** Sliders to adjust leakage reduction and digital adoption with live dynamic ROI and payback metrics.
