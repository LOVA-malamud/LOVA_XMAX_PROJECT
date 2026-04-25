# XMAX 400 Tech Max Manager

A Streamlit dashboard for managing a **2020 Yamaha XMAX 400 Tech Max** — service logging, fuel tracking, AI-powered mechanical consulting, parts search, and predictive maintenance alerts.

---

## Features

| Tab | Description |
|-----|-------------|
| Dashboard | Health bars for all maintenance items, predictive alerts, usage stats |
| Log Service | Record service events with date, km, cost, and notes |
| Repairs | To-do list for pending repairs with priority tracking |
| Fuel | Log fuel fills, auto-calculate L/100km efficiency, cost metrics |
| Tech Specs | Full engine, fluid, tire, electrical, and torque specs |
| Schematics | Upload and browse vehicle diagram PDFs |
| Parts | Full-text search of 30+ OEM XMAX 400 parts with part numbers |
| AI Mechanic | Gemini-powered chat with context from your service history and parts DB |
| History | Browse and export all service records as CSV |

---

## Tech Stack

- **Python 3.9+** — runtime
- **Streamlit 1.50** — web UI
- **SQLite** — local database (versioned migrations via `PRAGMA user_version`)
- **Google Gemini (`gemini-2.0-flash`)** — AI mechanic assistant
- **pandas / plotly** — data processing and charts
- **pytest** — test suite (37 tests)

---

## Prerequisites

- Python 3.9 or newer
- A Google Gemini API key — get one free at [aistudio.google.com](https://aistudio.google.com/app/apikey)

---

## Quick Start

```bash
# 1. Clone and enter the project
git clone <repo-url> && cd LOVA_XMAX_PROJECT

# 2. Create and activate a virtual environment
python -m venv .venv && source .venv/bin/activate   # macOS / Linux
# python -m venv .venv && .venv\Scripts\activate    # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure your API key
cp .env.example .env
# Edit .env and set: GEMINI_API_KEY=<your_key>

# 5. Seed the parts database (one-time only)
python seed_parts.py

# 6. Run the app
streamlit run xmax_app.py
# Opens at http://localhost:8501
```

**macOS shortcut:** double-click `run_my_app.command` (or `bash run_my_app.command`)

---

## Environment Variables

`.env` (not committed — copy from `.env.example`):

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## Running Tests

```bash
# Run all 37 tests
pytest tests/

# With coverage report
pytest tests/ --cov=. --cov-report=term-missing
```

---

## Project Structure

```
LOVA_XMAX_PROJECT/
├── xmax_app.py            — DashboardApp class; 9-tab Streamlit UI + sidebar
├── database_manager.py    — ScooterDB class; all SQLite reads/writes
├── ai_mechanic.py         — RAG pipeline: parts + history → Gemini API
├── config.py              — Single source of truth for all constants
├── ui_styles.py           — Custom CSS (dark/gold Orbitron theme)
├── seed_parts.py          — One-time CLI script to populate the parts table
├── run_my_app.command     — macOS double-click launcher
├── .env.example           — Environment variable template
├── requirements.txt       — Python dependencies
│
├── services/
│   ├── maintenance.py     — Pure functions: health %, due dates, predictive list
│   └── fuel.py            — Cost categorization (Parts vs Service)
│
├── utils/
│   ├── logging_cfg.py     — Logging setup (logs/xmax_app.log + console)
│   └── validation.py      — Input sanitization + ValidationError
│
├── tests/
│   ├── test_database.py   — ScooterDB unit tests (temp SQLite fixture)
│   ├── test_services.py   — Service layer pure-function tests
│   └── test_validation.py — Validator edge-case tests
│
├── xmax_docs.docs/
│   ├── xmax_parts_database.db       — SQLite database (gitignored)
│   └── xmax_400_2020_tech_summary.txt
│
└── schematics/            — Uploaded PDF diagrams (gitignored)
```

---

## Database

SQLite file at `xmax_docs.docs/xmax_parts_database.db` (not committed to git).

**Tables:** `parts`, `vehicle_stats`, `maintenance_history`, `tech_specs`, `fuel_logs`, `todo_list`, `custom_mechanic_rules`, `chat_history`

Schema version is tracked via `PRAGMA user_version`. Migrations in `database_manager._MIGRATIONS` run automatically on every startup — safe to run repeatedly.

On first run the app auto-creates all tables and seeds `tech_specs` and `custom_mechanic_rules`. Run `python seed_parts.py` once to populate the `parts` table with 30 real OEM parts.

---

## AI Mechanic

The AI tab uses a RAG (Retrieval Augmented Generation) pattern:

1. Extracts keywords from user question (filters `config.AI_STOP_WORDS`)
2. Searches the `parts` table for relevant components
3. Pulls `custom_mechanic_rules` (user-defined tips)
4. Appends recent maintenance history + current mileage
5. Sends the assembled context + question to `gemini-2.0-flash`

Includes exponential backoff retry (up to 3 attempts) for API rate limits.

---

## Security Notes

- `.env` is gitignored — never commit your API key
- An old API key was exposed in early commit history (`3471bf2`). If you forked or cloned before the fix, **revoke it** at [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
- All database writes use parameterized queries (no SQL injection risk)
- User-supplied content is not rendered as raw HTML (no XSS risk)
