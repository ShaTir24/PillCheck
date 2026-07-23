# PillCheck backend

FastAPI + SQLAlchemy(async) + Alembic, Postgres via Supabase in staging/prod (see [`../DECISIONS.md`](../DECISIONS.md) ADR-001/002). Layering and conventions: [`CLAUDE.md`](CLAUDE.md).

## Local dev

```bash
cp .env.example .env
docker-compose up -d postgres   # local Postgres on :5433 (5432 may already be taken)
uv sync --dev
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

No auth configured locally — pass `X-Debug-Profile-Id: <any-uuid>` instead of a bearer token (see `app/core/security.py`); `POST /api/v1/profiles` creates that profile.

## Checks

```bash
uv run ruff check app alembic/env.py
uv run mypy app
uv run pytest
```

## New migration

```bash
uv run alembic revision --autogenerate -m "describe the change"
uv run alembic upgrade head
```
