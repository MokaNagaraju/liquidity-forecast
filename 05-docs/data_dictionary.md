# Data Dictionary – Liquidity Forecast

## 1. LegalEntity

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| entity_id | VARCHAR(20) | Yes | Primary key. Format: ENT-000001 | Unique, immutable |
| entity_name | VARCHAR(100) | Yes | Display name | Non-empty |
| country | VARCHAR(10) | No | Country code | US, UK, IN, DE, JP |
| status | VARCHAR(20) | Yes | Lifecycle state | ACTIVE / INACTIVE |

**Cardinality**: 1 LegalEntity → N BankAccounts

---

## 2. BankAccount

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| account_id | VARCHAR(40) | Yes | Primary key. Format: BANKACC-ENT-000001-001 | Unique |
| entity_id | VARCHAR(20) | Yes | FK → LegalEntity | Must exist |
| currency | VARCHAR(10) | Yes | Account currency | USD, EUR, GBP, INR, JPY |
| account_type | VARCHAR(20) | No | OPERATING / COLLECTION / PAYABLE | Enum |
| status | VARCHAR(20) | Yes | ACTIVE / INACTIVE | Enum |

**Cardinality**: 1 BankAccount → N LedgerEntries, Receivables, Payables, Forecasts

---

## 3. LedgerEntry

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| ledger_id | VARCHAR(30) | Yes | Primary key. Format: LED-2026-00000001 | Unique |
| account_id | VARCHAR(40) | Yes | FK → BankAccount | Must exist |
| entry_date | DATE | Yes | Posting date | ≥ 2026-10-01 |
| amount | DECIMAL(18,2) | Yes | Signed amount | Opening > 0 |
| entry_type | VARCHAR(20) | Yes | OPENING / TRANSACTION | Enum |
| description | VARCHAR(200) | No | Free text | - |

---

## 4. Receivable

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| receivable_id | VARCHAR(30) | Yes | Primary key. Format: REC-2026-000001 | Unique |
| account_id | VARCHAR(40) | Yes | FK → BankAccount | Must exist |
| entity_id | VARCHAR(20) | Yes | FK → LegalEntity | Must exist |
| amount | DECIMAL(18,2) | Yes | Expected amount | > 0 |
| currency | VARCHAR(10) | Yes | Currency | Matches account preferred |
| expected_date | DATE | Yes | Expected receipt date | - |
| status | VARCHAR(20) | Yes | EXPECTED / DELAYED / RECEIVED | Enum |

---

## 5. Payable

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| payable_id | VARCHAR(30) | Yes | Primary key. Format: PAY-2026-000001 | Unique |
| account_id | VARCHAR(40) | Yes | FK → BankAccount | Must exist |
| entity_id | VARCHAR(20) | Yes | FK → LegalEntity | Must exist |
| amount | DECIMAL(18,2) | Yes | Amount due | > 0 |
| currency | VARCHAR(10) | Yes | Currency | - |
| due_date | DATE | Yes | Payment due date | - |
| status | VARCHAR(20) | Yes | SCHEDULED / OVERDUE / PAID | Enum |

---

## 6. CurrencyRate

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| rate_id | VARCHAR(40) | Yes | Primary key. Format: RATE-YYYY-MM-DD-CCY | Unique |
| rate_date | DATE | Yes | Rate effective date | - |
| currency | VARCHAR(10) | Yes | Currency code | USD, EUR, GBP, INR, JPY |
| rate_to_usd | DECIMAL(12,4) | Yes | Conversion rate to USD | > 0 |

---

## 7. ForecastRun

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| forecast_run_id | VARCHAR(40) | Yes | Primary key. Format: FCAST-2026-10-01-001 | Unique |
| run_date | DATE | Yes | When the run was executed | - |
| scenario | VARCHAR(30) | Yes | BASE / DELAYED_RECEIPT / STRESS | Enum |
| status | VARCHAR(20) | Yes | COMPLETED / FAILED / RUNNING | Enum |
| created_by | VARCHAR(50) | No | User or system | - |

---

## 8. CashFlowForecast

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| forecast_id | VARCHAR(30) | Yes | Primary key. Format: CF-2026-000001 | Unique |
| account_id | VARCHAR(40) | Yes | FK → BankAccount | Must exist |
| forecast_date | DATE | Yes | Expected flow date | - |
| currency | VARCHAR(10) | Yes | Currency | - |
| amount | DECIMAL(18,2) | Yes | Forecasted amount | > 0 |
| flow_type | VARCHAR(10) | Yes | INFLOW / OUTFLOW | Enum |
| scenario | VARCHAR(30) | Yes | BASE / DELAYED_RECEIPT / STRESS | Enum |
| forecast_run_id | VARCHAR(40) | Yes | FK → ForecastRun | Must exist |

---

## 9. GroundTruth (Exception Labels)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| issue_id | VARCHAR(20) | Yes | Primary key (GT-001 …) |
| issue_type | VARCHAR(50) | Yes | Anomaly category |
| description | VARCHAR(255) | Yes | Human-readable explanation |
| related_account | VARCHAR(40) | Yes | Account affected |
| severity | VARCHAR(20) | Yes | HIGH / MEDIUM / LOW |

**Note**: This table is kept separate from operational data and must never be used as an input feature.