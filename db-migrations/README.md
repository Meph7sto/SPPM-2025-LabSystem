# Database Migrations

This project uses Alembic for schema migrations.

Quick usage:
- Windows: `backend/scripts/db.ps1 init`
- Linux/macOS: `backend/scripts/db.sh init`

Common commands:
- `init` or `upgrade` applies migrations to latest
- `downgrade` rolls back one revision
- `revision "message"` creates a new auto-generated revision
