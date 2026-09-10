import os
import pandas as pd

data_dir = r"data/raw"
df_pay = pd.read_csv(os.path.join(data_dir, "payments.csv"), low_memory=False).drop_duplicates()
pay_coll = df_pay[df_pay.duplicated(subset=['payment_id'], keep=False)].sort_values(['payment_id'])

print("All 14 colliding payment_id groups (28 rows):")
print(pay_coll[['payment_id', 'account_id', 'borrower_id', 'event_at', 'payment_reference', 'amount', 'payment_status', 'payment_method', 'provider_id']].to_markdown(index=True))
