# Tarakki

Tarakki is a student career‑guidance web app that combines an aptitude/personality test, ML‑based career prediction, and AI‑generated roadmaps/chat. The main app is a Django project with HTML templates; a separate `AptitudeTest` folder contains a lightweight Flask prototype for serving the test.

## What It Does
- Aptitude + personality test with per‑dimension scoring.
- Career prediction using a pre‑trained MLP model.
- Roadmap generation and chat powered by Gemini.
- Visual dashboards (Plotly charts).

## Tech Stack
- Django 5, Python 3
- PostgreSQL (default in settings) or SQLite (commented in settings)
- scikit‑learn + joblib (pre‑trained models)
- Plotly for charts
- Google Gemini API

## Project Structure
- `backend/tarakki/`: Django project root
- `backend/tarakki/core/`: core app (auth, dashboard, test)
- `backend/tarakki/rag/`: Gemini chat app
- `backend/tarakki/*.pkl`: saved ML model + scaler + label encoder
- `AptitudeTest/`: Flask prototype for aptitude testing
- `Data_final.csv`, `Data2.csv`, notebooks: training/experimentation artifacts

## Quick Start (Django)
1. Create and activate a virtual environment.
2. Install dependencies.
3. Configure environment variables.
4. Run migrations and start the server.

```bash
cd /Users/vedant/Downloads/Tarakki-main-2/Tarakki-main/backend
python -m venv .venv
source .venv/bin/activate

# requirements.txt is UTF‑16 encoded; convert if pip fails
iconv -f utf-16 -t utf-8 requirements.txt > /tmp/requirements.utf8.txt
pip install -r /tmp/requirements.utf8.txt
```

Create a `.env` file in `backend/tarakki/` (same folder as `manage.py`):
```
GEMINI_API_KEY=your_key_here

# PostgreSQL (default settings)
PGDATABASE=tarakki
PGUSER=your_user
PGPASSWORD=your_password
PGHOST=localhost
PGPORT=5432
```

Run the app:
```bash
cd /Users/vedant/Downloads/Tarakki-main-2/Tarakki-main/backend/tarakki
python manage.py migrate
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

### SQLite Option (Local/Quick)
If you don’t want Postgres, switch `DATABASES` in
`/Users/vedant/Downloads/Tarakki-main-2/Tarakki-main/backend/tarakki/tarakki/settings.py`
to the commented SQLite config and rerun migrations. A sample `db.sqlite3` is already present for development use.

## Quick Start (Flask Prototype)
```bash
cd /Users/vedant/Downloads/Tarakki-main-2/Tarakki-main/AptitudeTest
python app2.py
```
Open `http://127.0.0.1:5000/`.

## Key Routes (Django)
- `/` home/landing
- `/signin`, `/signup`
- `/dash` dashboard
- `/test/`, `/start_test/`, `/submit_test/`
- `/roadmap/` (Gemini roadmap)
- `/chat/` (Gemini chat)

## Notes
- The ML artifacts live in `backend/tarakki/` and are loaded at runtime.
- The test question bank lives in `backend/tarakki/core/your_data_2.csv` (and a copy under `AptitudeTest/`).
- Gemini requires `GEMINI_API_KEY` to be set in the environment.


