"""
Liquidity Forecast - Synthetic Data Generator
Seed: 20261022 | Reproducible | Edge cases injected
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import hashlib

# ====================== CONFIG ======================
SEED = 20261022
np.random.seed(SEED)

NUM_ENTITIES = 30
NUM_ACCOUNTS = 150
NUM_LEDGER_ENTRIES = 100000
NUM_FORECAST_ITEMS = 20000
CURRENCIES = ["USD", "EUR", "GBP", "INR", "JPY"]
START_DATE = datetime(2026, 10, 1)
END_DATE = datetime(2026, 11, 15)
CUTOFF_DATE = datetime(2026, 10, 20)          # for forecast-after-cutoff anomaly

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "04-data"))
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"Seed: {SEED}")
print(f"Output: {OUTPUT_DIR}")

# ====================== 1. LEGAL ENTITY ======================
entities = []
for i in range(1, NUM_ENTITIES + 1):
    entities.append({
        "entity_id": f"ENT-{i:06d}",
        "entity_name": f"Entity {i}",
        "country": np.random.choice(["US", "UK", "IN", "DE", "JP"]),
        "status": "ACTIVE"
    })
df_entities = pd.DataFrame(entities)
df_entities.to_csv(f"{OUTPUT_DIR}/LegalEntity.csv", index=False)
print(f"LegalEntity: {len(df_entities)}")

# ====================== 2. BANK ACCOUNT ======================
accounts = []
for ent in df_entities["entity_id"]:
    for j in range(1, 6):
        accounts.append({
            "account_id": f"BANKACC-{ent}-{j:03d}",
            "entity_id": ent,
            "currency": np.random.choice(CURRENCIES),
            "account_type": np.random.choice(["OPERATING", "COLLECTION", "PAYABLE"]),
            "status": "ACTIVE"
        })
df_accounts = pd.DataFrame(accounts)
df_accounts.to_csv(f"{OUTPUT_DIR}/BankAccount.csv", index=False)
print(f"BankAccount: {len(df_accounts)}")

# ====================== 3. LEDGER ENTRIES ======================
ledger = []
ledger_id = 1

# Opening balances
for _, acc in df_accounts.iterrows():
    opening = round(np.random.uniform(10000, 500000), 2)
    ledger.append({
        "ledger_id": f"LED-2026-{ledger_id:08d}",
        "account_id": acc["account_id"],
        "entry_date": START_DATE.strftime("%Y-%m-%d"),
        "amount": opening,
        "entry_type": "OPENING",
        "description": "Opening Balance"
    })
    ledger_id += 1

# Remaining transactions
remaining = NUM_LEDGER_ENTRIES - len(ledger)
for _ in range(remaining):
    acc = df_accounts.iloc[np.random.randint(0, len(df_accounts))]
    days = np.random.randint(1, (END_DATE - START_DATE).days + 1)
    entry_date = START_DATE + timedelta(days=days)
    amount = round(np.random.uniform(-40000, 70000), 2)
    ledger.append({
        "ledger_id": f"LED-2026-{ledger_id:08d}",
        "account_id": acc["account_id"],
        "entry_date": entry_date.strftime("%Y-%m-%d"),
        "amount": amount,
        "entry_type": "TRANSACTION",
        "description": "Daily movement"
    })
    ledger_id += 1

df_ledger = pd.DataFrame(ledger)

# ----- INJECT EDGE CASE 1: BALANCE_MISMATCH -----
# Remove one random transaction for account BANKACC-ENT-000001-001 so opening + ledger ≠ expected closing
target_acc = "BANKACC-ENT-000001-001"
mask = (df_ledger["account_id"] == target_acc) & (df_ledger["entry_type"] == "TRANSACTION")
if mask.any():
    idx_to_drop = df_ledger[mask].sample(1, random_state=SEED).index
    df_ledger = df_ledger.drop(idx_to_drop)

df_ledger.to_csv(f"{OUTPUT_DIR}/LedgerEntry.csv", index=False)
print(f"LedgerEntry: {len(df_ledger)} (BALANCE_MISMATCH injected on {target_acc})")

# ====================== 4. RECEIVABLES ======================
receivables = []
for i in range(1, 801):
    acc = df_accounts.sample(1, random_state=SEED + i).iloc[0]
    days = np.random.randint(5, 45)
    status = np.random.choice(["EXPECTED", "DELAYED", "RECEIVED"], p=[0.6, 0.25, 0.15])
    receivables.append({
        "receivable_id": f"REC-2026-{i:06d}",
        "account_id": acc["account_id"],
        "entity_id": acc["entity_id"],
        "amount": round(np.random.uniform(5000, 80000), 2),
        "currency": acc["currency"],
        "expected_date": (START_DATE + timedelta(days=days)).strftime("%Y-%m-%d"),
        "status": status
    })
df_recv = pd.DataFrame(receivables)
df_recv.to_csv(f"{OUTPUT_DIR}/Receivable.csv", index=False)
print(f"Receivable: {len(df_recv)}")

# ====================== 5. PAYABLES ======================
payables = []
for i in range(1, 601):
    acc = df_accounts.sample(1, random_state=SEED + 1000 + i).iloc[0]
    days = np.random.randint(3, 40)
    payables.append({
        "payable_id": f"PAY-2026-{i:06d}",
        "account_id": acc["account_id"],
        "entity_id": acc["entity_id"],
        "amount": round(np.random.uniform(3000, 60000), 2),
        "currency": acc["currency"],
        "due_date": (START_DATE + timedelta(days=days)).strftime("%Y-%m-%d"),
        "status": np.random.choice(["SCHEDULED", "OVERDUE", "PAID"], p=[0.65, 0.2, 0.15])
    })
df_pay = pd.DataFrame(payables)
df_pay.to_csv(f"{OUTPUT_DIR}/Payable.csv", index=False)
print(f"Payable: {len(df_pay)}")

# ====================== 6. CURRENCY RATES ======================
fx_rates = []
base_rates = {"USD": 1.0, "EUR": 0.92, "GBP": 0.79, "INR": 83.5, "JPY": 149.0}

for day in range(0, 46):
    date = (START_DATE + timedelta(days=day)).strftime("%Y-%m-%d")
    for ccy, rate in base_rates.items():
        movement = np.random.uniform(-0.015, 0.015)
        fx_rates.append({
            "rate_id": f"RATE-{date}-{ccy}",
            "rate_date": date,
            "currency": ccy,
            "rate_to_usd": round(rate * (1 + movement), 4)
        })

df_fx = pd.DataFrame(fx_rates)

# ----- INJECT EDGE CASE 2: MISSING_FX -----
# Delete all rates for one currency on one day that will be needed
missing_mask = (df_fx["currency"] == "JPY") & (df_fx["rate_date"] == "2026-10-15")
df_fx = df_fx[~missing_mask]

df_fx.to_csv(f"{OUTPUT_DIR}/CurrencyRate.csv", index=False)
print(f"CurrencyRate: {len(df_fx)} (MISSING_FX injected for JPY on 2026-10-15)")

# ====================== 7. FORECAST RUN ======================
forecast_runs = [
    {"forecast_run_id": "FCAST-2026-10-01-001", "run_date": "2026-10-01", "scenario": "BASE", "status": "COMPLETED", "created_by": "system"},
    {"forecast_run_id": "FCAST-2026-10-01-002", "run_date": "2026-10-01", "scenario": "DELAYED_RECEIPT", "status": "COMPLETED", "created_by": "system"},
    {"forecast_run_id": "FCAST-2026-10-01-003", "run_date": "2026-10-01", "scenario": "STRESS", "status": "COMPLETED", "created_by": "system"},
]
df_runs = pd.DataFrame(forecast_runs)
df_runs.to_csv(f"{OUTPUT_DIR}/ForecastRun.csv", index=False)
print(f"ForecastRun: {len(df_runs)}")

# ====================== 8. CASH FLOW FORECAST ======================
forecast_items = []
fid = 1

# Derive a good portion from receivables / payables
for _, r in df_recv.iterrows():
    if r["status"] in ["EXPECTED", "DELAYED"] and fid <= NUM_FORECAST_ITEMS:
        scenario = "DELAYED_RECEIPT" if r["status"] == "DELAYED" else "BASE"
        run_id = "FCAST-2026-10-01-002" if scenario == "DELAYED_RECEIPT" else "FCAST-2026-10-01-001"
        forecast_items.append({
            "forecast_id": f"CF-2026-{fid:06d}",
            "account_id": r["account_id"],
            "forecast_date": r["expected_date"],
            "currency": r["currency"],
            "amount": r["amount"],
            "flow_type": "INFLOW",
            "scenario": scenario,
            "forecast_run_id": run_id
        })
        fid += 1

for _, p in df_pay.iterrows():
    if p["status"] in ["SCHEDULED", "OVERDUE"] and fid <= NUM_FORECAST_ITEMS:
        forecast_items.append({
            "forecast_id": f"CF-2026-{fid:06d}",
            "account_id": p["account_id"],
            "forecast_date": p["due_date"],
            "currency": p["currency"],
            "amount": p["amount"],
            "flow_type": "OUTFLOW",
            "scenario": "BASE",
            "forecast_run_id": "FCAST-2026-10-01-001"
        })
        fid += 1

# Fill remaining with synthetic items
while fid <= NUM_FORECAST_ITEMS:
    acc = df_accounts.iloc[np.random.randint(0, len(df_accounts))]
    fdate = START_DATE + timedelta(days=np.random.randint(1, (END_DATE - START_DATE).days + 1))
    scenario = np.random.choice(["BASE", "DELAYED_RECEIPT", "STRESS"])
    run_map = {"BASE": "FCAST-2026-10-01-001", "DELAYED_RECEIPT": "FCAST-2026-10-01-002", "STRESS": "FCAST-2026-10-01-003"}
    forecast_items.append({
        "forecast_id": f"CF-2026-{fid:06d}",
        "account_id": acc["account_id"],
        "forecast_date": fdate.strftime("%Y-%m-%d"),
        "currency": acc["currency"],
        "amount": round(np.random.uniform(1000, 100000), 2),
        "flow_type": np.random.choice(["INFLOW", "OUTFLOW"]),
        "scenario": scenario,
        "forecast_run_id": run_map[scenario]
    })
    fid += 1

df_forecast = pd.DataFrame(forecast_items)

# ----- INJECT EDGE CASE 3: DOUBLE_COUNT -----
# Duplicate one high-value inflow for account BANKACC-ENT-000001-003
double_acc = "BANKACC-ENT-000001-003"
dup_row = df_forecast[df_forecast["account_id"] == double_acc].iloc[0].copy()
dup_row["forecast_id"] = f"CF-2026-{fid:06d}"
df_forecast = pd.concat([df_forecast, pd.DataFrame([dup_row])], ignore_index=True)
fid += 1

# ----- INJECT EDGE CASE 4: FORECAST_USES_ACTUAL_AFTER_CUTOFF -----
# Add a forecast item whose date is after cutoff but marked as using actual
after_cutoff = CUTOFF_DATE + timedelta(days=5)
df_forecast = pd.concat([df_forecast, pd.DataFrame([{
    "forecast_id": f"CF-2026-{fid:06d}",
    "account_id": "BANKACC-ENT-000001-004",
    "forecast_date": after_cutoff.strftime("%Y-%m-%d"),
    "currency": "USD",
    "amount": 75000.00,
    "flow_type": "INFLOW",
    "scenario": "BASE",
    "forecast_run_id": "FCAST-2026-10-01-001"
}])], ignore_index=True)

# ----- INJECT EDGE CASE 5: MIXED_CURRENCY_NO_CONVERSION -----
# Force a forecast item on an account whose currency does not match the rate used later
df_forecast = pd.concat([df_forecast, pd.DataFrame([{
    "forecast_id": f"CF-2026-{fid+1:06d}",
    "account_id": "BANKACC-ENT-000001-005",
    "forecast_date": "2026-10-25",
    "currency": "EUR",          # account may be in different currency
    "amount": 42000.00,
    "flow_type": "INFLOW",
    "scenario": "BASE",
    "forecast_run_id": "FCAST-2026-10-01-001"
}])], ignore_index=True)

df_forecast.to_csv(f"{OUTPUT_DIR}/CashFlowForecast.csv", index=False)
print(f"CashFlowForecast: {len(df_forecast)} (DOUBLE_COUNT, AFTER_CUTOFF, MIXED_CURRENCY injected)")

# ====================== 9. GROUND TRUTH ======================
ground_truth = [
    {"issue_id": "GT-001", "issue_type": "BALANCE_MISMATCH",
     "description": "Opening + Ledger does not equal Closing", "related_account": "BANKACC-ENT-000001-001", "severity": "HIGH"},
    {"issue_id": "GT-002", "issue_type": "MISSING_FX",
     "description": "FX rate missing for currency conversion", "related_account": "BANKACC-ENT-000001-002", "severity": "MEDIUM"},
    {"issue_id": "GT-003", "issue_type": "DOUBLE_COUNT",
     "description": "Cash flow counted twice", "related_account": "BANKACC-ENT-000001-003", "severity": "HIGH"},
    {"issue_id": "GT-004", "issue_type": "FORECAST_USES_ACTUAL_AFTER_CUTOFF",
     "description": "Forecast used actual data after cutoff date", "related_account": "BANKACC-ENT-000001-004", "severity": "HIGH"},
    {"issue_id": "GT-005", "issue_type": "MIXED_CURRENCY_NO_CONVERSION",
     "description": "Mixed currencies without proper FX conversion", "related_account": "BANKACC-ENT-000001-005", "severity": "MEDIUM"},
]
df_gt = pd.DataFrame(ground_truth)
df_gt.to_csv(f"{OUTPUT_DIR}/ground_truth.csv", index=False)
print("ground_truth.csv written")

# ====================== MANIFEST ======================
manifest = {
    "seed": SEED,
    "generated_at": datetime.now().isoformat(),
    "entities": len(df_entities),
    "accounts": len(df_accounts),
    "ledger_entries": len(df_ledger),
    "receivables": len(df_recv),
    "payables": len(df_pay),
    "currency_rates": len(df_fx),
    "forecast_items": len(df_forecast),
    "forecast_runs": len(df_runs),
    "edge_cases_injected": 5
}
with open(f"{OUTPUT_DIR}/manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)

print("\n✅ Data generation completed with injected edge cases.")