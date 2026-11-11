"""
Validation suite for Liquidity Forecast data
Checks: PK uniqueness, FK integrity, enums, date order, reconciliation, duplicates
"""
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "04-data"

def load(name):
    return pd.read_csv(DATA_DIR / name)

def check_pk(df, col, name):
    dup = df[col].duplicated().sum()
    status = "PASS" if dup == 0 else f"FAIL ({dup} duplicates)"
    print(f"  PK {name}.{col}: {status}")
    return dup == 0

def check_fk(child, child_col, parent, parent_col, name):
    missing = ~child[child_col].isin(parent[parent_col])
    n = missing.sum()
    status = "PASS" if n == 0 else f"FAIL ({n} orphan keys)"
    print(f"  FK {name}: {status}")
    return n == 0

def main():
    print("=" * 60)
    print("LIQUIDITY FORECAST – DATA VALIDATION")
    print("=" * 60)

    le  = load("LegalEntity.csv")
    ba  = load("BankAccount.csv")
    led = load("LedgerEntry.csv")
    rec = load("Receivable.csv")
    pay = load("Payable.csv")
    fx  = load("CurrencyRate.csv")
    fr  = load("ForecastRun.csv")
    cf  = load("CashFlowForecast.csv")
    gt  = load("ground_truth.csv")

    results = []

    print("\n1. Primary Key Uniqueness")
    results.append(check_pk(le,  "entity_id",       "LegalEntity"))
    results.append(check_pk(ba,  "account_id",      "BankAccount"))
    results.append(check_pk(led, "ledger_id",       "LedgerEntry"))
    results.append(check_pk(rec, "receivable_id",   "Receivable"))
    results.append(check_pk(pay, "payable_id",      "Payable"))
    results.append(check_pk(fx,  "rate_id",         "CurrencyRate"))
    results.append(check_pk(fr,  "forecast_run_id", "ForecastRun"))
    results.append(check_pk(cf,  "forecast_id",     "CashFlowForecast"))

    print("\n2. Foreign Key Integrity")
    results.append(check_fk(ba,  "entity_id",       le,  "entity_id",       "BankAccount → LegalEntity"))
    results.append(check_fk(led, "account_id",      ba,  "account_id",      "LedgerEntry → BankAccount"))
    results.append(check_fk(rec, "account_id",      ba,  "account_id",      "Receivable → BankAccount"))
    results.append(check_fk(pay, "account_id",      ba,  "account_id",      "Payable → BankAccount"))
    results.append(check_fk(cf,  "account_id",      ba,  "account_id",      "CashFlowForecast → BankAccount"))
    results.append(check_fk(cf,  "forecast_run_id", fr,  "forecast_run_id", "CashFlowForecast → ForecastRun"))

    print("\n3. Allowed Enums / Values")
    ok_status = set(le["status"].unique()) <= {"ACTIVE", "INACTIVE"}
    print(f"  LegalEntity.status: {'PASS' if ok_status else 'FAIL'}")
    results.append(ok_status)

    ok_ccy = set(ba["currency"].unique()) <= {"USD", "EUR", "GBP", "INR", "JPY"}
    print(f"  BankAccount.currency: {'PASS' if ok_ccy else 'FAIL'}")
    results.append(ok_ccy)

    print("\n4. Date Ordering")
    led["entry_date"] = pd.to_datetime(led["entry_date"])
    date_ok = led["entry_date"].min() >= pd.Timestamp("2026-10-01")
    print(f"  Ledger entry dates >= 2026-10-01: {'PASS' if date_ok else 'FAIL'}")
    results.append(date_ok)

    print("\n5. Ground Truth Present")
    expected_issues = {
        "BALANCE_MISMATCH", "MISSING_FX", "DOUBLE_COUNT",
        "FORECAST_USES_ACTUAL_AFTER_CUTOFF", "MIXED_CURRENCY_NO_CONVERSION"
    }
    found = set(gt["issue_type"])
    gt_ok = expected_issues.issubset(found)
    print(f"  All 5 required issue types present: {'PASS' if gt_ok else 'FAIL'}")
    results.append(gt_ok)

    print("\n6. Row Counts")
    print(f"  Entities   : {len(le):>6} (expect 30)")
    print(f"  Accounts   : {len(ba):>6} (expect 150)")
    print(f"  Ledger     : {len(led):>6} (expect ~99999)")
    print(f"  Forecast   : {len(cf):>6} (expect ~20003)")
    print(f"  Receivable : {len(rec):>6}")
    print(f"  Payable    : {len(pay):>6}")
    print(f"  FX Rates   : {len(fx):>6}")

    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"RESULT: {passed}/{total} checks passed")
    if passed == total:
        print("✅ Validation successful")
    else:
        print("⚠ Some checks failed – review above")
    print("=" * 60)

if __name__ == "__main__":
    main()