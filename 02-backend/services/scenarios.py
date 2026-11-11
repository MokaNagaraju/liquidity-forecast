import pandas as pd
import os

# ====================== PATH SETUP ======================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "04-data"))

# ====================== LOAD DATA ======================
df_position = pd.read_csv(os.path.join(DATA_DIR, "CashPosition.csv"))
print(f"Loaded cash position for {len(df_position)} accounts")

# ====================== SCENARIO FUNCTIONS ======================

def base_scenario(df):
    """Normal situation - no change"""
    result = df.copy()
    result["scenario"] = "BASE"
    result["adjusted_cash"] = result["projected_cash"]
    return result

def delayed_receipt_scenario(df):
    """
    Delayed Receipt:
    Assume 30% of expected inflows will be delayed
    (so we reduce the inflow impact)
    """
    result = df.copy()
    result["scenario"] = "DELAYED_RECEIPT"
    
    # Reduce the benefit of expected inflows by 30%
    adjusted_inflow = result["expected_inflow"] * 0.70
    result["adjusted_cash"] = (
        result["ledger_balance"] + adjusted_inflow - result["expected_outflow"]
    )
    return result

def stress_scenario(df):
    """
    Stress scenario:
    - 40% of inflows are delayed/lost
    - Outflows increase by 15% (extra costs)
    """
    result = df.copy()
    result["scenario"] = "STRESS"
    
    adjusted_inflow = result["expected_inflow"] * 0.60
    adjusted_outflow = result["expected_outflow"] * 1.15
    
    result["adjusted_cash"] = (
        result["ledger_balance"] + adjusted_inflow - adjusted_outflow
    )
    return result

# ====================== RUN ALL SCENARIOS ======================
def run_all_scenarios():
    base = base_scenario(df_position)
    delayed = delayed_receipt_scenario(df_position)
    stress = stress_scenario(df_position)

    all_scenarios = pd.concat([base, delayed, stress], ignore_index=True)

    all_scenarios = all_scenarios[[
        "scenario", "account_id", "entity_id", "entity_name", "currency",
        "ledger_balance", "expected_inflow", "expected_outflow",
        "projected_cash", "adjusted_cash"
    ]]

    return all_scenarios

# ====================== MAIN ======================
if __name__ == "__main__":
    result = run_all_scenarios()

    print("\n===== SCENARIO TOTALS =====")
    summary = result.groupby("scenario")["adjusted_cash"].agg(["count", "sum", "mean"]).round(2)
    print(summary)

    output_file = os.path.join(DATA_DIR, "ScenarioResults.csv")
    result.to_csv(output_file, index=False)
    print(f"\n✅ Scenario results saved to: {output_file}")