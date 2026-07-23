---
name: add-feature
description: Checklist for adding or changing a feature in PillCheck's backend (FastAPI) or mobile (Expo/React Native) app. Use when asked to add an entity, endpoint, screen, or field; wire a new piece of data end-to-end; or make any code change that touches the backend/mobile layering. Enforces the layered, SOLID-oriented architecture from DECISIONS.md ADR-002/003/004/005 so new code doesn't drift from it.
---

# Adding a feature to PillCheck

PillCheck is two projects, [`backend/`](../../../backend) (FastAPI) and [`mobile/`](../../../mobile) (Expo/React Native), talking over the REST API defined in `backend/app/api/v1/routers/`. Each has its own `CLAUDE.md` with the full convention reference — this skill is the ordered checklist that ties them together. Read both before touching either:

- [`backend/CLAUDE.md`](../../../backend/CLAUDE.md)
- [`mobile/CLAUDE.md`](../../../mobile/CLAUDE.md)

## 0. Scope the change first

- **New backend entity?** New table → full backend checklist below, then the mobile checklist if it needs a UI.
- **New field on an existing entity?** Touch every layer that entity already has (model → migration → schema → service if it needs validation → router if the field is settable) — don't skip a layer because it's "just a field."
- **Mobile-only (new screen over existing data)?** Skip straight to the mobile checklist.
- **Speculative/"might need later"?** Don't build it. Every entity in this codebase maps to a specific PRD requirement (check [`docs/PRD.md`](../../../docs/PRD.md)) — cite the FR/UF number in a comment the way the existing code does, and if you can't find one, ask whether the feature is actually in scope yet.

## 1. Backend (if a new entity or field)

Full detail: `backend/CLAUDE.md` → "Adding a feature." In order:

1. Model (`app/models/`) → register in `app/models/__init__.py`.
2. `uv run alembic revision --autogenerate -m "..."` — **read the generated migration**, don't trust it blindly (enum renames and data backfills need hand-editing).
3. Schema (`app/schemas/`) — separate `Create`/`Update`/`Read`, never reuse the ORM model as a response model.
4. Repository (`app/repositories/`) extending `SQLAlchemyRepository[Model]`.
5. Service (`app/services/`) — only add validation logic the PRD actually calls for (see `MedicationService`/`DoseEventService` for the pattern of a real, narrow business rule vs. speculative validation).
6. DI provider in `app/api/deps.py`.
7. Router in `app/api/v1/routers/`, registered in `app/api/v1/router.py`. Router bodies stay to "call one service method, return it" — if you're writing an `if` statement in a router, that logic belongs in the service.
8. Unit test in `tests/unit/` against a fake repository for any new business rule.
9. Verify: `uv run ruff check app alembic/env.py && uv run mypy app && uv run pytest` — all three must stay clean.

## 2. Mobile (if the feature needs a UI)

Full detail: `mobile/CLAUDE.md` → "Adding a feature." In order:

1. `src/types/api.ts` — add/update the type to match the backend `Read` schema exactly.
2. `src/features/<domain>/api.ts` — TanStack Query hook(s) using the shared `apiClient`. Reuse an existing domain folder if the entity is a sub-resource of one (e.g. schedules live under `regimen`, matching the backend's nested route).
3. Route file under `app/` — thin, composes the hook + `src/constants/styles`. Register in the nearest `_layout.tsx` if it's a new route.
4. Verify: `npm run typecheck && npx eslint . && npx expo-doctor` — all three must stay clean. `npx expo export --platform ios` is the strongest available check (actually bundles the app) — run it if the change touches routing or a new dependency.

## 3. Cross-cutting

- **New architectural decision** (new dependency, new pattern, deviating from an existing ADR)? Add an ADR to [`DECISIONS.md`](../../../DECISIONS.md) using the `architecture` skill's format — don't silently deviate from ADR-002/003/004/005.
- **Field names must match exactly** between `backend/app/schemas/*.py` and `mobile/src/types/api.ts` — there's no code generation wiring them together yet; a rename on one side without the other is a silent runtime bug, not a type error.
- Keep both projects' checks green before calling a change done — a backend change that breaks `mypy` or a mobile change that breaks `tsc` is not finished, even if the specific feature "works."
