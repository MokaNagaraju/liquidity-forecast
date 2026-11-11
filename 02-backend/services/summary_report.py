"""
Final summary report
"""
import pandas as pd
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "04-data"))

print("Generating Final Summary Report...\n")

df_position  = pd.read_csv(os.path.join(DATA_DIR, "CashPosition.csv"))
df_scenarios = pd.read_csv(os.path.join(DATA_DIR, "ScenarioResults.csv"))
df_gt        = pd.read_csv(os.path.join(DATA_DIR, "ground_truth.csv"))

# 1. Total cash
total_cash = df_position["ledger_balance"].sum()
print("===== 1. TOTAL CURRENT CASH (Ledger) =====")
print(f"Total Cash across all accounts: {total_cash:,.2f}\n")

# 2. Cash by currency
print("===== 2. CASH BY CURRENCY =====")
print(df_position.groupby("currency")["ledger_balance"].sum().round(2))
print()

# 3. Scenario comparison
print("===== 3. SCENARIO COMPARISON (Adjusted Cash) =====")
print(df_scenarios.groupby("scenario")["adjusted_cash"].sum().round(2))
print()

# 4. Top 5 accounts
print("===== 4. TOP 5 ACCOUNTS BY LEDGER BALANCE =====")
top5 = df_position.nlargest(5, "ledger_balance")[
    ["account_id", "entity_name", "currency", "ledger_balance"]
]
print(top5.to_string(index=False))
print()

# 5. Exceptions
print("===== 5. KNOWN EXCEPTIONS =====")
print(df_gt[["issue_id", "issue_type", "severity", "related_account"]].to_string(index=False))
print()

print("✅ Summary report completed successfully!")