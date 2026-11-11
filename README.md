# Liquidity Forecast – Short-Term Cash Position System

End-to-end synthetic data solution for consolidating account balances and expected cash flows to forecast short-term liquidity under multiple scenarios.

## Overview

This project generates a complete, reproducible dataset and supporting services for:

- Multi-entity, multi-currency bank accounts
- Ledger entries with opening balances
- Scheduled receivables and payables
- FX rates
- Cash flow forecasts under three scenarios (BASE, DELAYED_RECEIPT, STRESS)
- Injected and labelled edge cases
- Validation and basic analytics services

## Project Structure

liquidity-forecast/
├── 01-frontend/               # Simple dashboard (HTML)
├── 02-backend/
│   └── services/              # Cash position, scenarios, exceptions, reports
├── 03-sql/
│   └── schema.sql             # Database schema
├── 04-data/                   # Generated CSVs + ground_truth + manifest
├── 05-docs/
│   └── data_dictionary.md     # Full field-level data dictionary
├── 07-scripts/
│   ├── generator_data.py      # Main synthetic data generator
│   └── validate_data.py       # Validation suite
└── README.md

## Quick Start

### 1. Generate Data
```bash
python 07-scripts/generator_data.py

2. Validate DataBashpython 07-scripts/validate_data.py
Expected result: 18/18 checks passed3. Run Backend Services (examples)Bashpython 02-backend/services/cash_position.py
python 02-backend/services/scenarios.py
python 02-backend/services/exceptions.py
python 02-backend/services/summary_report.pyKey Design Decisions

AspectDecisionSeedFixed 20261022 for full reproducibilityVolume30 entities, 150 accounts, ~100k ledger entries, ~20k forecast itemsCurrenciesUSD, EUR, GBP, INR, JPYScenariosBASE, DELAYED_RECEIPT, STRESSEdge Cases5 labelled anomalies actually injected into the dataHistoryNo silent overwrites – all records are append-only styleGround TruthKept separate in ground_truth.csvInjected Edge Cases (Ground Truth)

Issue IDTypeDescriptionGT-001BALANCE_MISMATCHOpening + Ledger ≠ ClosingGT-002MISSING_FXFX rate missing for a required date/currencyGT-003DOUBLE_COUNTSame cash flow counted twiceGT-004FORECAST_USES_ACTUAL_AFTER_CUTOFFForecast uses data after cutoffGT-005MIXED_CURRENCY_NO_CONVERSIONMixed currencies without proper conversionData Volumes (after generation)
LegalEntity: 30
BankAccount: 150
LedgerEntry: 99,999
Receivable: 800
Payable: 600
CurrencyRate: 229
CashFlowForecast: 20,003
ForecastRun: 3
ReproducibilityThe generator uses a fixed seed (20261022). Running it multiple times produces identical row counts and content (except timestamp in manifest.json).Requirements
Python 3.9+
pandas
numpy
Bash pip install pandas numpyLicense / ProvenanceAll data is 100% synthetic. No external or personal data was used.Text
---


How to Run the ProjectBash# 1. Generate the data
python 07-scripts/generator_data.py

# 2. Validate the data
python 07-scripts/validate_data.py

# 3. Calculate cash positions
python 02-backend/services/cash_position.py

# 4. Run scenarios
python 02-backend/services/scenarios.py

# 5. Check exceptions
python 02-backend/services/exceptions.py

# 6. Generate summary report
python 02-backend/services/summary_report.py