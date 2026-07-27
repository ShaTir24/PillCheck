# PillCheck backend — conventions

FastAPI + SQLAlchemy 2.0 (async) + Alembic + Supabase Postgres. Rationale: [`../DECISIONS.md`](../DECISIONS.md) ADR-001..003.

## Layering — one-way dependency, no shortcuts

```
api/routers  →  services  →  repositories  →  models
 (HTTP only)   (business rules)  (data access)   (ORM)
```

- **Routers** (`app/api/v1/routers/`): parse request, call one service method, shape the response. No business logic, no direct SQLAlchemy/repository calls. If a router needs to fetch something to 404-check it, that's a service method (see `ScheduleService.get`, `CaregiverLinkService.get`) — never `service.repo.get(...)` reaching through the service.
- **Services** (`app/services/`): business rules and validation live here (e.g. `MedicationService._validate_appearance`, `DoseEventService._validate_consistency`). Depend on repositories via their public interface, not on `AsyncSession` directly.
- **Repositories** (`app/repositories/`): one per entity, extends `SQLAlchemyRepository[Model]` from `base.py`. Add entity-specific queries here (e.g. `list_for_profile`) — never build ad-hoc queries in a service or router.
- **Models** (`app/models/`): SQLAlchemy ORM only. **Never** reused as API schemas.
- **Schemas** (`app/schemas/`): Pydantic request/response DTOs, kept separate from ORM models on purpose (ADR-002) — an internal-only model field should never leak into a schema by accident because they're different classes.

## Adding a feature (new entity)

Follow `.claude/skills/add-feature/SKILL.md` at the project root — it's the authoritative checklist and covers both this backend and the mobile client. Short version for a backend-only change:

1. `app/models/<entity>.py` — SQLAlchemy model, add to `app/models/__init__.py`.
2. `uv run alembic revision --autogenerate -m "..."` — inspect the generated migration before applying; hand-edit if autogenerate misses something (enum changes, data backfills).
3. `app/schemas/<entity>.py` — `EntityCreate` / `EntityUpdate` (optional fields) / `EntityRead` (`from_attributes=True`).
4. `app/repositories/<entity>.py` — extend `SQLAlchemyRepository[Entity]`, add query methods the service actually needs (don't pre-build ones it doesn't).
5. `app/services/<entity>.py` — business rules. If there are none yet beyond CRUD, that's fine — don't invent validation the PRD doesn't ask for.
6. `app/api/deps.py` — a `get_<entity>_service` provider wiring repo → service.
7. `app/api/v1/routers/<entity>.py` — thin endpoints, register in `app/api/v1/router.py`.
8. Tests: a unit test in `tests/unit/` against a fake repository for any real business rule (see `tests/unit/test_medication_service.py`, `test_dose_event_service.py` for the pattern) — don't write a DB-backed test for logic a fake repo can exercise.

## Non-negotiables

- **Never store the metric-learning embedding vector in Postgres.** It lives in the on-device FAISS index (build pipeline artifact). `ReferenceAppearance` is metadata only — see the comment on that model.
- **`get_db_session` (app/core/database.py) must commit.** Closing an `AsyncSession` context manager does not commit — it silently rolls back. If you ever touch this dependency, keep the `yield` → `commit()` → `except: rollback()` shape; this exact bug shipped once during scaffolding and every write endpoint 500'd or silently no-op'd because of it.
- **Supabase transaction-pooler mode** (`DB_USE_TRANSACTION_POOLER=true`) requires `NullPool` + disabled asyncpg statement caching — don't remove that branch in `app/core/database.py` even though local dev doesn't need it (ADR-002).
- Auth is in-house (ADR-006): `users` table (email/password_hash), JWT access+refresh tokens signed with `AUTH_JWT_SECRET`, revocation via a `token_version` counter bumped on password reset — no Supabase Auth, no sessions table. `app/core/security.py` is pure crypto/JWT (no DB access); `app/api/deps.py`'s `get_current_user`/`get_current_profile_id` do the DB lookups.
- Run `uv run ruff check app alembic/env.py && uv run mypy app && uv run pytest` before considering a change done. All three are clean on the current codebase — keep them that way.
