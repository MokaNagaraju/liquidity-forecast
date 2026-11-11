"""
Show known exceptions from ground_truth
"""
import pandas as pd
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "04-data"))

df_gt       = pd.read_csv(os.path.join(DATA_DIR, "ground_truth.csv"))
df_position = pd.read_csv(os.path.join(DATA_DIR, "CashPosition.csv"))

print("\n===== KNOWN EXCEPTIONS =====")
print(df_gt.to_string(index=False))

print("\n===== ACCOUNTS WITH ISSUES =====")
for _, row in df_gt.iterrows():
    account  = row["related_account"]
    issue    = row["issue_type"]
    severity = row["severity"]

    balance_row = df_position[df_position["account_id"] == account]

    if len(balance_row) > 0:
        balance = balance_row.iloc[0]["ledger_balance"]
        print(f"{account} | {issue} | Severity: {severity} | Ledger Balance: {balance:,.2f}")
    else:
        print(f"{account} | {issue} | Account not found in CashPosition")

print("\n✅ Exception check completed")