# LESMS

Laboratory Equipment Service Management System for Jiangnan University.

## Structure
- `backend/` FastAPI service
- `frontend/` Vue3 client
- `db-migrations/` Alembic migration scripts
- `docs/` system documentation

## Backend quick start
1. Create and activate a virtual environment.
2. Install deps: `pip install -r backend/requirements.txt`
3. Copy `.env.example` to `.env` and update `DB_URL` (SQLite or PostgreSQL).
4. Run: `uvicorn backend.app.main:app --reload`

API docs: `http://localhost:8000/api/v1/docs`

DB_URL examples:
- `sqlite:///./data/lesms.db`
- `postgresql+psycopg://lesms:lesms@localhost:5432/lesms`

## One-click (Conda)
`.\start.ps1`

## Database migrations
Windows:
`backend/scripts/db.ps1 init`

Linux/macOS:
`backend/scripts/db.sh init`
