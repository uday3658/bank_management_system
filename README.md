# 🏦 Bank Transaction Analytics System

A full-stack bank management application with a Streamlit frontend and MySQL backend, featuring PIN-authenticated account operations and a config-driven, real-time analytics dashboard built on Pandas, NumPy, and Seaborn.

## Features

- **Account Management** — create, delete, and manage accounts with PIN authentication
- **Transactions** — deposit, withdraw, and view full transaction history
- **Analytics Dashboard**
  - Business KPIs: total transactions, inflow, outflow, net cash flow, average transaction value
  - Daily transaction volume trend
  - Account-level balance summary
  - Top active accounts
  - Age-group spending analysis
  - High-value transaction flagging (mean + N·σ threshold, configurable)
  - Rule-based risk scoring (amount percentile + transaction hour, configurable)
  - Cash flow distribution (boxplot by transaction type)
  - Key business insights (highest/lowest transaction, total deposits)

## Tech Stack

Python · Streamlit · MySQL · Pandas · NumPy · Seaborn · Matplotlib · PyYAML · python-dotenv

## Architecture

The project follows a `src/`-layout package structure with clean separation of concerns:

- **Config-driven**: all tunables (risk thresholds, quantiles, age bins, top-N accounts) live in `config/config.yaml`, not hardcoded in logic
- **Secrets isolated**: DB password loaded from `.env`, never committed
- **Typed config objects**: `ConfigurationManager` reads YAML + env vars and dispenses immutable `DatabaseConfig` / `AppConfig` dataclasses — no raw dicts passed around
- **Custom exceptions + centralized logging**: every DB/IO operation wraps errors in `BankAnalyticsException` with file/line context, logged to `logs/`
- **Thin UI layer**: `app/streamlit_app.py` only wires config → `Bank` → `analytics`; no business logic lives in the UI file
- **Tested**: `tests/` covers the core analytics functions with pytest

## Project Structure

```
bank-transaction-analytics/
├── app/
│   └── streamlit_app.py          # Streamlit UI — wires config, Bank, analytics together
├── config/
│   └── config.yaml                # non-secret, tunable configuration
├── sql/
│   └── schema.sql                  # MySQL table definitions (users, transactions)
├── src/
│   └── bank_analytics/
│       ├── __init__.py
│       ├── constants/
│       │   └── __init__.py         # CONFIG_FILE_PATH
│       ├── entity/
│       │   └── config_entity.py    # DatabaseConfig, AppConfig dataclasses
│       ├── config/
│       │   └── configuration.py    # ConfigurationManager
│       ├── database/
│       │   └── bank.py             # Bank class — account/transaction logic
│       ├── analytics/
│       │   └── analytics.py        # cleaning, KPIs, risk scoring, charts
│       ├── utils/
│       │   ├── common.py           # read_yaml
│       │   └── logger.py           # centralized logging setup
│       └── exception.py            # BankAnalyticsException
├── tests/
│   └── test_analytics.py
├── logs/                            # gitignored — created at runtime
├── .env.example                     # template for secrets
├── .gitignore
├── requirements.txt
├── setup.py                         # makes `bank_analytics` pip-installable (src layout)
└── README.md
```

## Setup

1. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate      # venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
   This also installs the local `bank_analytics` package in editable mode (`-e .`), so imports like `from bank_analytics.database.bank import Bank` work anywhere.

2. **Set up MySQL**
   ```bash
   mysql -u root -p < sql/schema.sql
   ```
   Creates the `bank_db` database with `users` and `transactions` tables.

3. **Configure secrets**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set your real `DB_PASSWORD`. Non-secret DB settings (host, user, database, port) live in `config/config.yaml`.

4. **Run the app**
   ```bash
   streamlit run app/streamlit_app.py
   ```

5. **Run tests**
   ```bash
   pytest tests/
   ```

## Notes

- Risk scoring is rule-based (quantile thresholds + transaction hour), not a trained ML model.
- PINs are stored as plain integers for simplicity — in production these would be hashed (e.g. bcrypt) rather than stored/compared in plaintext.
