import pandas as pd
import os

# ====================== PATHS ======================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "04-data"))
FRONTEND_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "01-frontend"))

# ====================== LOAD DATA ======================
df_position = pd.read_csv(os.path.join(DATA_DIR, "CashPosition.csv"))
df_scenarios = pd.read_csv(os.path.join(DATA_DIR, "ScenarioResults.csv"))
df_gt = pd.read_csv(os.path.join(DATA_DIR, "ground_truth.csv"))

# ====================== CALCULATE VALUES ======================
total_ledger = df_position["ledger_balance"].sum()
total_inflow = df_position["expected_inflow"].sum()
total_outflow = df_position["expected_outflow"].sum()
total_projected = df_position["projected_cash"].sum()
num_accounts = len(df_position)
num_exceptions = len(df_gt)

scenario_totals = df_scenarios.groupby("scenario")["adjusted_cash"].sum().round(2)
base_total = scenario_totals.get("BASE", 0)
delayed_total = scenario_totals.get("DELAYED_RECEIPT", 0)
stress_total = scenario_totals.get("STRESS", 0)

top5 = df_position.nlargest(5, "projected_cash")

# ====================== CREATE HTML ======================
html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Liquidity Forecast Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; background: #f4f6f9; margin: 0; padding: 20px; }}
        h1 {{ color: #1a73e8; text-align: center; }}
        .container {{ max-width: 1150px; margin: 0 auto; }}
        .card {{ background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .card h2 {{ margin-top: 0; color: #333; border-bottom: 2px solid #1a73e8; padding-bottom: 8px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }}
        .metric {{ background: #e8f0fe; padding: 15px; border-radius: 8px; text-align: center; }}
        .metric .value {{ font-size: 20px; font-weight: bold; color: #1a73e8; }}
        .metric .label {{ font-size: 13px; color: #555; margin-top: 4px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; font-size: 14px; }}
        th {{ background-color: #1a73e8; color: white; }}
        .high {{ color: #d93025; font-weight: bold; }}
        .medium {{ color: #f9ab00; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Liquidity Forecast Dashboard</h1>

        <!-- Key Metrics -->
        <div class="card">
            <h2>Key Metrics</h2>
            <div class="grid">
                <div class="metric">
                    <div class="value">{total_ledger:,.0f}</div>
                    <div class="label">Current Ledger Balance</div>
                </div>
                <div class="metric">
                    <div class="value">{total_inflow:,.0f}</div>
                    <div class="label">Expected Inflows</div>
                </div>
                <div class="metric">
                    <div class="value">{total_outflow:,.0f}</div>
                    <div class="label">Expected Outflows</div>
                </div>
                <div class="metric">
                    <div class="value">{total_projected:,.0f}</div>
                    <div class="label">Projected Cash (Base)</div>
                </div>
            </div>
        </div>

        <!-- Scenario Comparison -->
        <div class="card">
            <h2>Scenario Comparison</h2>
            <table>
                <tr>
                    <th>Scenario</th>
                    <th>Total Adjusted Cash</th>
                    <th>What it means</th>
                </tr>
                <tr>
                    <td><strong>BASE</strong></td>
                    <td>{base_total:,.2f}</td>
                    <td>Normal conditions – everything on time</td>
                </tr>
                <tr>
                    <td><strong>DELAYED RECEIPT</strong></td>
                    <td>{delayed_total:,.2f}</td>
                    <td>Customers pay late (inflows reduced 30%)</td>
                </tr>
                <tr>
                    <td><strong>STRESS</strong></td>
                    <td>{stress_total:,.2f}</td>
                    <td>Crisis: inflows −40% + outflows +15%</td>
                </tr>
            </table>
        </div>

        <!-- Top 5 Accounts -->
        <div class="card">
            <h2>Top 5 Accounts by Projected Cash</h2>
            <table>
                <tr>
                    <th>Account ID</th>
                    <th>Entity</th>
                    <th>Currency</th>
                    <th>Projected Cash</th>
                </tr>
"""

for _, row in top5.iterrows():
    html += f"""
                <tr>
                    <td>{row['account_id']}</td>
                    <td>{row['entity_name']}</td>
                    <td>{row['currency']}</td>
                    <td>{row['projected_cash']:,.2f}</td>
                </tr>
    """

html += """
            </table>
        </div>

        <!-- Exceptions -->
        <div class="card">
            <h2>Known Exceptions (Ground Truth)</h2>
            <table>
                <tr>
                    <th>Issue ID</th>
                    <th>Issue Type</th>
                    <th>Severity</th>
                    <th>Related Account</th>
                </tr>
"""

for _, row in df_gt.iterrows():
    severity_class = "high" if row["severity"] == "HIGH" else "medium"
    html += f"""
                <tr>
                    <td>{row['issue_id']}</td>
                    <td>{row['issue_type']}</td>
                    <td class="{severity_class}">{row['severity']}</td>
                    <td>{row['related_account']}</td>
                </tr>
    """

html += """
            </table>
        </div>

        <div class="card">
            <h2>How the System Works</h2>
            <ol>
                <li>Generate entities, bank accounts, ledger, receivables, payables and FX rates</li>
                <li>Calculate current ledger balance + expected inflows − expected outflows</li>
                <li>Run three scenarios: Base, Delayed Receipt, Stress</li>
                <li>Flag known data problems using ground truth</li>
                <li>Show everything in this dashboard</li>
            </ol>
        </div>
    </div>
</body>
</html>
"""

# ====================== SAVE ======================
output_file = os.path.join(FRONTEND_DIR, "index.html")
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html)

print("✅ Dashboard updated with new data!")
print(f"Open: {output_file}")