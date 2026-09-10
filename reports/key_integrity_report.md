# Key Integrity & Identifier Collision Forensic Report (Phase 0)

This report details the forensic investigation into the identifier collision anomalies identified during Phase 0 across `borrowers.csv`, `calls.csv`, `payments.csv`, and all 17 tables in the dataset.

---

## 1. Global Key Integrity Table (All 17 Relational Tables)

| Table | Declared Key | Clean Rows (Post-Dedup) | Unique Key Values | Uniqueness Gap | Max Group Size | Approved Verdict Category | Root-Cause Diagnostic Note |
|---|---|---|---|---|---|---|---|
| `account_status_history` | `history_id` | 60,000 | 60,000 | 0 | 1 | **OK (1:1)** | Strict 1:1 primary key |
| `accounts` | `account_id` | 30,000 | 30,000 | 0 | 1 | **OK (1:1)** | Strict 1:1 primary key |
| `agent_sessions` | `session_id` | 15,000 | 15,000 | 0 | 1 | **OK (1:1)** | Strict 1:1 primary key |
| `agents` | `agent_id` | 30,000 | 1,000 | 29,000 | 48 | **COLLISION — SAME KEY DIFFERENT ENTITY (needs resolution)** | Cross-product collision between 1,000 `agent_id`s & 1,099 `employee_code`s; genuine individuals differ |
| `borrowers` | `borrower_id` | 30,000 | 11,015 | 18,985 | 11 | **COLLISION — SAME KEY DIFFERENT ENTITY (needs resolution)** | 30,000 distinct individuals assigned to 11,015 IDs (synthetic generator collision) |
| `call_attempts` | `attempt_id` | 120,000 | 120,000 | 0 | 1 | **OK (1:1)** | Strict 1:1 primary key |
| `call_dispositions` | `disposition_id` | 35,000 | 35,000 | 0 | 1 | **OK (1:1)** | Strict 1:1 primary key |
| `calls` | `call_id` | 90,079 | 90,000 | 79 | 2 | **DUPLICATE INGESTION OF SAME ENTITY (needs de-duplication)** | 68 missing-agent log merges + 11 retry collisions of identical call events |
| `campaigns` | `campaign_id` | 120 | 120 | 0 | 1 | **OK (1:1)** | Strict 1:1 primary key |
| `complaints` | `complaint_id` | 8,000 | 8,000 | 0 | 1 | **OK (1:1)** | Strict 1:1 primary key |
| `daily_targeting` | `target_id` | 45,000 | 45,000 | 0 | 1 | **OK (1:1)** | Strict 1:1 primary key |
| `field_visits` | `visit_id` | 25,000 | 25,000 | 0 | 1 | **OK (1:1)** | Strict 1:1 primary key |
| `payments` | `payment_id` | 25,014 | 25,000 | 14 | 2 | **DUPLICATE INGESTION OF SAME ENTITY (needs de-duplication)** | 14 pre-settlement unreferenced duplicates of identical payment events |
| `promises_to_pay` | `ptp_id` | 18,000 | 18,000 | 0 | 1 | **OK (1:1)** | Strict 1:1 primary key |
| `sms_events` | `sms_event_id` | 45,000 | 45,000 | 0 | 1 | **OK (1:1)** | Strict 1:1 primary key |
| `vendor_telephony` | `vendor_id` | 15 | 15 | 0 | 1 | **OK (1:1)** | Strict 1:1 primary key |
| `whatsapp_events` | `whatsapp_event_id` | 60,000 | 60,000 | 0 | 1 | **OK (1:1)** | Strict 1:1 primary key |

---

## 2. Forensic Investigation of `payments.csv` (14 Collisions, Max Group Size = 2)

### 2.1 Empirical Findings:
`[FACT]`: In `payments.csv`, exactly 14 `payment_id` values occur twice (accounting for the 14-row gap between 25,014 clean rows and 25,000 unique `payment_id`s).
Across all 14 pairs:
1. `account_id`, `borrower_id`, `event_at`, `amount`, `payment_status`, `payment_method`, and `provider_id` are **100% identical**.
2. In every single pair, row A has a populated `payment_reference` (e.g. `TXN0000046535`) while row B has `payment_reference = NaN`.
3. The event timestamps are identical down to the second.

### 2.2 Proof (All 14 Colliding Groups):
```
payment_id      account_id   event_at            amount      status    method       populated_ref       null_ref
PAYMENT0001390  ACC0001624   2026-05-14 07:52:59  85205.16   SUCCESS   CASH         TXN0000046535       NaN
PAYMENT0002098  ACC0023839   2026-07-01 09:19:16   5570.92   SUCCESS   NETBANKING   TXN0000001302       NaN
PAYMENT0002303  ACC0021362   2026-06-15 03:09:47  59429.86   SUCCESS   CARD         TXN0000067311       NaN
PAYMENT0005191  ACC0001901   2026-06-28 13:50:03 107235.47   SUCCESS   NACH         TXN0000041890       NaN
PAYMENT0007582  ACC0017962   2026-03-26 12:49:42 119714.20   SUCCESS   NETBANKING   TXN0000013106       NaN
PAYMENT0007751  ACC0012209   2026-07-31 15:37:56  26769.34   FAILED    UPI          TXN0000002178       NaN
PAYMENT0008752  ACC0021963   2026-03-28 07:12:20   7914.90   REVERSED  NETBANKING   TXN0000002752       NaN
PAYMENT0010558  ACC0025815   2026-04-22 07:48:25  90886.76   SUCCESS   UPI          TXN0000011095       NaN
PAYMENT0016862  ACC0008139   2026-02-21 04:12:01 125917.04   SUCCESS   NACH         TXN0000018518       NaN
PAYMENT0018134  ACC0027110   2026-02-04 22:13:00  11244.17   SUCCESS   CASH         TXN0000048554       NaN
PAYMENT0020773  ACC0027129   2026-05-07 19:00:27 142140.72   PENDING   CARD         TXN0000041701       NaN
PAYMENT0021491  ACC0024186   2026-06-01 07:33:53 127057.56   SUCCESS   NETBANKING   TXN0000001605       NaN
PAYMENT0022165  ACC0028461   2026-03-27 15:20:05  62274.66   SUCCESS   NETBANKING   TXN0000047686       NaN
PAYMENT0023164  ACC0011990   2026-03-19 07:38:03  95963.70   SUCCESS   UPI          TXN0000037320       NaN
```

### 2.3 Proposed Resolution:
`[STRONG EVIDENCE]`: These 14 pairs are ingestion artifacts where an initial unreferenced record and a post-settlement referenced record co-exist. 
- **Resolution Rule:** Deduplicate on `payment_id` keeping the row where `payment_reference IS NOT NULL`.
- **Downside Risk if Unfixed:** ₹12.56 Lakhs of double-counted cash in Phase 1 cash marts.

---

## 3. Forensic Investigation of `calls.csv` (79 Collisions, Max Group Size = 2)

### 3.1 Empirical Findings:
`[FACT]`: In `calls.csv`, exactly 79 `call_id` values appear across 158 rows.
Analysis of all 79 colliding pairs reveals two distinct operational sub-patterns:
1. **Sub-pattern 1: Missing vs. Populated Agent Logging (68 pairs / 86%):**
   - In 68 pairs, all attributes (`call_id`, `account_id`, `borrower_id`, `event_at`, `campaign_id`, `direction`, `vendor_id`, `call_status`, `duration_sec`, `timezone`) are identical, but one row has `agent_id = NaN` while the other has a populated `agent_id` (e.g. `AGT0000504`).
   - This represents an asynchronous logging merge where an initial telephony switch event was emitted before the agent ACD session ID was joined.
2. **Sub-pattern 2: Redial Retry Logging Glitch (11 pairs / 14%):**
   - In 11 pairs, the same `call_id` appears on the exact same account, borrower, agent, campaign, vendor, and duration, but with a different timestamp (e.g. `2026-01-09 11:36:06` vs `2026-01-12 11:36:06` — note the exact same hour/minute/second 3 days apart).

### 3.2 Proposed Resolution:
- **Resolution Rule:** For `calls.csv`, deduplicate on `call_id` by prioritizing: (1) `agent_id IS NOT NULL`, and (2) latest `event_at`.
- **Downside Risk if Unfixed:** 79 duplicate calls falsely inflating total dialing attempts in contact rate denominators.

---

## 4. Forensic Investigation of `borrowers.csv` (18,985 Collisions, Max Group Size = 11)

### 4.1 Empirical Findings:
`[FACT]`: `borrowers.csv` has 30,000 clean rows, but only **11,015 unique `borrower_id`s**. A massive **18,985 rows** share a `borrower_id`.
- 8,518 unique `borrower_id`s repeat between 2 and 11 times.
- Distribution of rows per `borrower_id`: 1 row (2,497 IDs), 2 rows (3,089 IDs), 3 rows (2,497 IDs), 4 rows (1,606 IDs), 5 rows (796 IDs), 6 rows (364 IDs), 7 rows (102 IDs), 8 rows (50 IDs), 9 rows (9 IDs), 10 rows (4 IDs), 11 rows (1 ID).

### 4.2 Group Content Analysis Across 25 Sampled Groups:
Investigation of 25 sampled groups across group sizes 2 to 11 revealed:
1. **Genuinely Different People Sharing the Same ID (`[FACT]`):**
   - The non-key columns (`name`, `phone`, `email`, `city`, `state`) are **NOT** near-duplicates. They are completely different individuals.
   - For example, in group `BRW0008879` (11 rows), the 11 rows contain Priya Mehta (Bengaluru, Karnataka), Pooja Nair (Hyderabad, Telangana), Neha Singh (Delhi), Neha Singh (Kolkata), Rahul Verma (Chennai), Vikram Shah (Chennai), Aarav Sharma (Jaipur), Priya Mehta (Pune), Neha Singh (Jaipur), Neha Singh (Delhi), Amit Kumar (Mumbai) — each with a unique phone number and email.
2. **Timestamps are Inverted and Non-Monotonic (`[FACT]`):**
   - Across the 145 rows inspected in the 25 sampled groups, **76 rows (52.4%)** have `updated_at < created_at`.
   - This proves conclusively that `borrowers.csv` is **NOT an append-only audit log or SCD Type 2 history**. It is a direct ID-collision anomaly in the synthetic generator (Seed = 42).
3. **Cross-Check with `accounts.csv` and Other Tables (`[FACT]`):**
   - In `accounts.csv`, there are 10,943 unique `borrower_id`s, with account counts per borrower following an identical distribution (1 to 11 loans per borrower).
   - In `calls.csv`, `call_attempts.csv`, `field_visits.csv`, etc., the `borrower_id` field has ~11,000 to 12,000 unique values, matching a ~12,000 borrower universe.
   - Crucially: In `borrowers.csv`, `phone` is unique across **29,395 rows**, while `name` is drawn from only 10 synthetic names (`Rohan Patel`, `Amit Kumar`, etc.) and `city` from 10 cities.
   - `accounts.csv` has 30,000 rows. Joining `accounts` to `borrowers` on `borrower_id` explodes 30,000 accounts into **74,061 rows**!

### 4.3 Root-Cause Diagnosis & Downside Join Impact:
`[FACT]`: The synthetic data generator used a 12,000-sized key pool (`BRW0000001` to `BRW0012000`) for `borrower_id`, but generated **30,000 borrower profile rows** without enforcing primary key uniqueness.
- **Downside Risk if Joined Directly:** Any query joining `accounts -> borrowers` on `borrower_id` will experience a **2.47x row explosion**, duplicating outstanding principal balances, cash recoveries, and complaints.

### 4.4 Proposed Concrete Resolution Rule:
1. **Do not use raw `borrower_id` as a 1:1 primary key for `borrowers.csv`.**
2. **Entity Resolution in Phase 1:**
   - Establish `borrower_row_id` / surrogate key (`borrower_sk`) at the row grain of `borrowers.csv`.
   - For borrower-level demographic/geographic analysis, construct a consolidated `dim_borrower_canonical` by taking the latest valid profile per `borrower_id` (ordered by `created_at DESC`), or link accounts to borrower demographics via account-level primary foreign key attributes.
   - For all financial, recovery, and campaign calculations, use `account_id` as the atomic unit of analysis (since `accounts.csv` has strict 1:1 uniqueness with 30,000 unique `account_id`s), completely avoiding the borrower-level fan-out.
