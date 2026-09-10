import os

# Base paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW_DATA_DIR = os.path.join(BASE_DIR, "data/raw")
GOLDEN_DATA_DIR = os.path.join(BASE_DIR, "data", "golden")
QUARANTINE_DIR = os.path.join(BASE_DIR, "data", "quarantine")

# Target Timezone
CANONICAL_TIMEZONE = "Asia/Kolkata"

# 17 Master Tables
TABLE_FILES = [
    "account_status_history.csv",
    "accounts.csv",
    "agent_sessions.csv",
    "agents.csv",
    "borrowers.csv",
    "call_attempts.csv",
    "call_dispositions.csv",
    "calls.csv",
    "campaigns.csv",
    "complaints.csv",
    "daily_targeting.csv",
    "field_visits.csv",
    "payments.csv",
    "promises_to_pay.csv",
    "sms_events.csv",
    "vendor_telephony.csv",
    "whatsapp_events.csv"
]
