-- =============================================
-- Liquidity Forecast - Complete Schema
-- =============================================

-- 1. Legal Entity
CREATE TABLE LegalEntity (
    entity_id       VARCHAR(20) PRIMARY KEY,
    entity_name     VARCHAR(100) NOT NULL,
    country         VARCHAR(10),
    status          VARCHAR(20) DEFAULT 'ACTIVE'
);

-- 2. Bank Account
CREATE TABLE BankAccount (
    account_id      VARCHAR(40) PRIMARY KEY,
    entity_id       VARCHAR(20) NOT NULL,
    currency        VARCHAR(10) NOT NULL,
    account_type    VARCHAR(20),
    status          VARCHAR(20) DEFAULT 'ACTIVE',
    FOREIGN KEY (entity_id) REFERENCES LegalEntity(entity_id)
);

-- 3. Ledger Entry
CREATE TABLE LedgerEntry (
    ledger_id       VARCHAR(30) PRIMARY KEY,
    account_id      VARCHAR(40) NOT NULL,
    entry_date      DATE NOT NULL,
    amount          DECIMAL(18,2) NOT NULL,
    entry_type      VARCHAR(20),
    description     VARCHAR(200),
    FOREIGN KEY (account_id) REFERENCES BankAccount(account_id)
);

-- 4. Receivable
CREATE TABLE Receivable (
    receivable_id   VARCHAR(30) PRIMARY KEY,
    account_id      VARCHAR(40) NOT NULL,
    entity_id       VARCHAR(20) NOT NULL,
    amount          DECIMAL(18,2) NOT NULL,
    currency        VARCHAR(10),
    expected_date   DATE,
    status          VARCHAR(20),
    FOREIGN KEY (account_id) REFERENCES BankAccount(account_id),
    FOREIGN KEY (entity_id) REFERENCES LegalEntity(entity_id)
);

-- 5. Payable
CREATE TABLE Payable (
    payable_id      VARCHAR(30) PRIMARY KEY,
    account_id      VARCHAR(40) NOT NULL,
    entity_id       VARCHAR(20) NOT NULL,
    amount          DECIMAL(18,2) NOT NULL,
    currency        VARCHAR(10),
    due_date        DATE,
    status          VARCHAR(20),
    FOREIGN KEY (account_id) REFERENCES BankAccount(account_id),
    FOREIGN KEY (entity_id) REFERENCES LegalEntity(entity_id)
);

-- 6. Currency Rate (FX)
CREATE TABLE CurrencyRate (
    rate_id         VARCHAR(40) PRIMARY KEY,
    rate_date       DATE NOT NULL,
    currency        VARCHAR(10) NOT NULL,
    rate_to_usd     DECIMAL(12,4) NOT NULL
);

-- 7. Forecast Run
CREATE TABLE ForecastRun (
    forecast_run_id VARCHAR(40) PRIMARY KEY,
    run_date        DATE,
    scenario        VARCHAR(30),
    status          VARCHAR(20),
    created_by      VARCHAR(50)
);

-- 8. Ground Truth (known issues)
CREATE TABLE GroundTruth (
    issue_id        VARCHAR(20) PRIMARY KEY,
    issue_type      VARCHAR(50) NOT NULL,
    description     VARCHAR(255),
    related_account VARCHAR(40),
    severity        VARCHAR(20)
);