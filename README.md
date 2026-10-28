# XMAX 400 · Maintenance Dashboard

A Streamlit prototype for scooter maintenance records, parts/specifications, fuel logs and an AI-assisted mechanic conversation.

**Status:** prototype with incomplete dependency setup. Review the credential and data notes below before running it.

## Code map

| File | Responsibility |
| --- | --- |
| [xmax_app.py](xmax_app.py) | Dashboard and user interactions |
| [database_manager.py](database_manager.py) | SQLite persistence and data access |
| [config.py](config.py) | File locations and application configuration |
| [ai_mechanic.py](ai_mechanic.py) | Gemini integration and database context |
| [ui_styles.py](ui_styles.py) | Streamlit presentation |
| [requirements.txt](requirements.txt) | Current dependency list |

## Setup status

The intended entry point is `python -m streamlit run xmax_app.py` from the repository root, inside a project-local virtual environment. **The current dependency list is incomplete:** `ai_mechanic.py` imports `google.generativeai`, whose package is not listed in `requirements.txt`. A clean installation and launch have not been verified. Resolve that compatibility issue before treating this as a reproducible setup.

`config.py` points to the existing SQLite database under `xmax_docs.docs/`. Preserve the database and backup files. `test.py` initializes/inserts database content; it is not a harmless automated test command. Do not run database initializers against important records as part of setup experimentation.

## Credentials and data

The previously exposed Gemini API key was revoked in Google AI Studio, as confirmed by the repository owner on 29 October 2026. `.env` is no longer tracked; its local contents were preserved in the cleanup checkout. Historical commits still contain the revoked value because Git history has not been rewritten.

Before pulling this change into another checkout that still tracks `.env`, save a private copy outside that checkout: Git may remove the tracked file when applying the deletion. Restore your saved configuration afterward as an ignored local file.

For a new checkout, copy `.env.example` to `.env` only if `.env` does not already exist, then replace the placeholder locally with your own Gemini API key. For an existing checkout, preserve the existing `.env` and update only `GEMINI_API_KEY` locally when a replacement key is available. The revoked key will no longer authenticate AI requests. Never paste a replacement key into commits, PRs, logs or screenshots.

`.gitignore` excludes `.env` and `.env.*`, while allowing placeholder-only example files. An ignore rule cannot remove content already committed; do not force-add local environment files.

Tracked databases and the legacy backup require a separate privacy/data review. The AI integration can send conversation and selected database context to an external provider; review that flow before using private information. No live provider calls or database migrations were made during documentation review.

## Learning and limitations

The project explores a Streamlit UI, SQLite schema design, data visualization and an external AI integration. There is no verified automated test suite or production deployment. Maintenance values and generated advice are application content, not independently validated servicing instructions.
