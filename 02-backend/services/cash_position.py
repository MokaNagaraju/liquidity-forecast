"""
Calculate current cash position per bank account
"""
import pandas as pd
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "04-data"))

print("Reading data from:", DATA_DIR)

# ====================== LOAD DATA ======================
df_accounts = pd.read_csv(os.path.join(DATA_DIR, "BankAccount.csv"))
df_ledger   = pd.read_csv(os.path.join(DATA_DIR, "LedgerEntry.csv"))
df_entities = pd.read_csv(os.path.join(DATA_DIR, "LegalEntity.csv"))
df_recv     = pd.read_csv(os.path.join(DATA_DIR, "Receivable.csv"))
df_pay      = pd.read_csv(os.path.join(DATA_DIR, "Payable.csv"))
df_fx       = pd.read_csv(os.path.join(DATA_DIR, "CurrencyRate.csv"))
df_forecast = pd.read_csv(os.path.join(DATA_DIR, "CashFlowForecast.csv"))

print(f"Accounts        : {len(df_accounts)}")
print(f"Ledger entries  : {len(df_ledger)}")
print(f"Receivables     : {len(df_recv)}")
print(f"Payables        : {len(df_pay)}")
print(f"Currency rates  : {len(df_fx)}")
print(f"Forecast items  : {len(df_forecast)}")

# ====================== CALCULATE ======================
def calculate_cash_position():
    # 1. Current balance from ledger
    ledger_bal = df_ledger.groupby("account_id")["amount"].sum().reset_index()
    ledger_bal.columns = ["account_id", "ledger_balance"]

    # 2. Expected incoming money (still open)
    incoming = df_recv[df_recv["status"].isin(["EXPECTED", "DELAYED"])]
    incoming = incoming.groupby("account_id")["amount"].sum().reset_index()
    incoming.columns = ["account_id", "expected_inflow"]

    # 3. Expected outgoing money (still open)
    outgoing = df_pay[df_pay["status"].isin(["SCHEDULED", "OVERDUE"])]
    outgoing = outgoing.groupby("account_id")["amount"].sum().reset_index()
    outgoing.columns = ["account_id", "expected_outflow"]

    # 4. Latest FX rate per currency
    df_fx["rate_date"] = pd.to_datetime(df_fx["rate_date"])
    latest_fx = (
        df_fx.sort_values("rate_date")
        .groupby("currency")
        .tail(1)[["currency", "rate_to_usd"]]
    )

    # 5. Build position
    df = df_accounts.merge(df_entities[["entity_id", "entity_name"]], on="entity_id", how="left")
    df = df.merge(ledger_bal, on="account_id", how="left")
    df = df.merge(incoming, on="account_id", how="left")
    df = df.merge(outgoing, on="account_id", how="left")
    df = df.merge(latest_fx, on="currency", how="left")

    # Fill missing values
    df["ledger_balance"]   = df["ledger_balance"].fillna(0.0)
    df["expected_inflow"]  = df["expected_inflow"].fillna(0.0)
    df["expected_outflow"] = df["expected_outflow"].fillna(0.0)
    df["rate_to_usd"]      = df["rate_to_usd"].fillna(1.0)

    # USD converted values
    df["ledger_balance_usd"]   = df["ledger_balance"]   * df["rate_to_usd"]
    df["expected_inflow_usd"]  = df["expected_inflow"]  * df["rate_to_usd"]
    df["expected_outflow_usd"] = df["expected_outflow"] * df["rate_to_usd"]

    # Projected cash
    df["projected_cash"]     = df["ledger_balance"] + df["expected_inflow"] - df["expected_outflow"]
    df["projected_cash_usd"] = df["ledger_balance_usd"] + df["expected_inflow_usd"] - df["expected_outflow_usd"]

    # Final columns
    cols = [
        "account_id", "entity_id", "entity_name", "currency", "account_type",
        "ledger_balance", "expected_inflow", "expected_outflow",
        "rate_to_usd",
        "ledger_balance_usd", "expected_inflow_usd", "expected_outflow_usd",
        "projected_cash", "projected_cash_usd"
    ]
    return df[cols]

# ====================== MAIN ======================
if __name__ == "__main__":
    df_position = calculate_cash_position()

    out_path = os.path.join(DATA_DIR, "CashPosition.csv")
    df_position.to_csv(out_path, index=False)

    print(f"\nCashPosition written → {out_path}")
    print(f"Accounts processed  : {len(df_position)}")
    print(f"Total projected USD : {df_position['projected_cash_usd'].sum():,.2f}")
    print("\n✅ Cash position calculation completed")