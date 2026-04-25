# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Yamaha XMAX 400 (2020 Tech Max Edition) maintenance dashboard — a Streamlit web app with AI-powered mechanical consulting via Google Gemini, SQLite-backed service logging, fuel tracking, parts search, and predictive maintenance alerts.

## Running the App

```bash
# Setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # then set GEMINI_API_KEY

# Seed parts database (first time only)
python seed_parts.py

# Run
streamlit run xmax_app.py
# Opens at http://localhost:8501
```

macOS shortcut: double-click `run_my_app.command` (uses `$(dirname "$0")` so it works from any location)

## Tests

```bash
pytest tests/
pytest tests/ --cov=. --cov-report=term-missing
```

## Environment

`.env` requires:
```
GEMINI_API_KEY=<your_google_gemini_api_key>
```

## Architecture

```
xmax_app.py            — DashboardApp class; 9-tab Streamlit UI + sidebar (UI only)
database_manager.py    — ScooterDB class; all SQLite reads/writes (8 tables)
ai_mechanic.py         — RAG integration: queries parts DB + history, calls Gemini
config.py              — All constants: intervals, model name, stop words, file paths
ui_styles.py           — Custom CSS (dark/gold Orbitron theme, health bars)
seed_parts.py          — One-time CLI script to populate the parts table
services/
  maintenance.py       — Pure functions: health %, due dates, predictive task list
  fuel.py              — Cost categorization logic
utils/
  logging_cfg.py       — Logging setup (writes to logs/xmax_app.log + console)
  validation.py        — Input validation + ValidationError
tests/
  test_database.py     — ScooterDB unit tests against a temp SQLite file
  test_services.py     — Service layer pure-function tests
  test_validation.py   — Validator unit tests
```

## Database

SQLite at `xmax_docs.docs/xmax_parts_database.db`. Tables: `parts`, `vehicle_stats`, `maintenance_history`, `tech_specs`, `fuel_logs`, `todo_list`, `custom_mechanic_rules`, `chat_history`.

Schema versioning via `PRAGMA user_version`. `ScooterDB._run_migrations()` runs idempotent migrations on every startup — safe to run repeatedly.

On first run, `ScooterDB` auto-creates all tables and seeds `tech_specs` and `custom_mechanic_rules`. If `scooter_db.json` exists, data migrates automatically (file renamed to `.bak`). Run `python seed_parts.py` once to populate the `parts` table.

## AI Mechanic (RAG Pattern)

`ai_mechanic.py` builds context by: searching `parts` table → fetching `custom_mechanic_rules` → pulling recent maintenance history + current mileage → sending the assembled prompt to `config.GEMINI_MODEL`. Includes exponential backoff retry for rate limits. All via `google.generativeai` (imported as `genai`).

## Key Config Values (`config.py`)

- `DB_PATH` — path to the SQLite database
- `GEMINI_MODEL` — Gemini model name (e.g. `"gemini-2.0-flash"`)
- `GEMINI_MAX_RETRIES` — number of retry attempts for Gemini API calls
- `MAINTENANCE_INTERVALS` — dict of service types → km intervals + keywords + predictive flag
- `TECH_SPECS_SEED` — list of tuples used to seed the `tech_specs` table on first run
- `AI_STOP_WORDS` — words filtered from user queries before parts DB search
- `COST_CATEGORY_KEYWORDS` — keywords used to classify expenses as "Parts" vs "Service"
