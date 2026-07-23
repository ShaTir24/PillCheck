# Decision Log

ADRs for PillCheck. Format per `architecture` skill. Append-only; supersede, don't edit history.

---

# ADR-001: Database & Hosting — Supabase (Postgres)

**Status:** Accepted
**Date:** 2026-07-23
**Deciders:** Tirth Shah

## Context
PillCheck needs a backend datastore for non-image account/regimen data: profiles, medications, schedules, dose events, caregiver links (PRD §10.3, §11.2). Core pill-verification inference stays on-device (PRD NFR "Availability" — no server dependency in the *verification loop*), but P1 features (caregiver sync FR-11, multi-profile FR-12) need a durable, syncable store behind the device.

## Decision
Use Supabase-hosted Postgres as the primary datastore, accessed from a FastAPI backend via SQLAlchemy — not through the Supabase client SDK/PostgREST directly. This keeps a real service layer between mobile clients and the DB (schema evolution, business rules, decision-engine-adjacent validation stay server-side, not scattered across mobile RLS policies).

## Options Considered

### Option A: Supabase Postgres + FastAPI/SQLAlchemy (chosen)
| Dimension | Assessment |
|-----------|------------|
| Complexity | Low — managed Postgres, standard driver |
| Cost | Free tier covers dev/portfolio scale |
| Scalability | Postgres scales conventionally; Supavisor pooler handles connection fan-out |
| Team familiarity | High — plain SQL/ORM, no new query language |

**Pros:** Real migrations via Alembic, full SQL/ORM control, easy local parity (any Postgres works), auth available if needed later (Supabase Auth) without being required now.
**Cons:** Two moving pieces (Supabase infra + our own API layer) vs. using PostgREST directly.

### Option B: Supabase client SDK / PostgREST directly from mobile
**Pros:** Less backend code, faster to a demo.
**Cons:** Business logic (decision-engine adjacent validation, caregiver-alert thresholds) leaks into RLS policies and client code; harder to unit test; conflicts with "server owns business rules" and with FR-4's safety-critical framing.

### Option C: Self-hosted Postgres (RDS/Docker on a VPS)
**Pros:** No vendor lock-in.
**Cons:** More ops overhead for a solo portfolio project; Supabase gives the same Postgres with less setup.

## Trade-off Analysis
Option A keeps Supabase as "just Postgres + optional Auth" and puts all business logic behind FastAPI, which is what SOLID-oriented layering (services/repositories) needs. Option B is faster but undermines the service layer entirely. Chose A.

## Consequences
- Connection must go through Supabase's Supavisor transaction pooler (port 6543) in production; `NullPool` + disabled asyncpg statement caching required (see ADR-002).
- Supabase Auth is available to adopt later for caregiver accounts (FR-11) without a schema rework — not built now (YAGNI).
- Local dev uses a plain Postgres container (docker-compose) for parity + fast Alembic autogenerate, pointed at Supabase only for staging/prod.

## Action Items
1. [x] `backend/.env.example` documents both connection strings (local docker + Supabase pooler).
2. [ ] Adopt Supabase Auth when FR-11 (caregiver link) is built.

---

# ADR-002: ORM & Migrations — SQLAlchemy 2.0 (async) + Alembic

**Status:** Accepted
**Date:** 2026-07-23
**Deciders:** Tirth Shah

## Context
Need an ORM + migration tool for the Postgres schema in ADR-001, compatible with FastAPI's async request handling and Supabase's pooler behavior.

## Decision
SQLAlchemy 2.0 with the `asyncpg` driver for the ORM layer, Alembic (async-aware `env.py`) for migrations. ORM models and Pydantic API schemas are kept as **separate classes** (not SQLModel's merged model).

## Options Considered

### Option A: SQLAlchemy 2.0 async + Alembic + separate Pydantic schemas (chosen)
| Dimension | Assessment |
|-----------|------------|
| Complexity | Medium — two model definitions (ORM + schema) per entity |
| Cost | N/A |
| Scalability | Async session frees the event loop under load; well-trodden production path |
| Team familiarity | High — standard FastAPI stack |

**Pros:** Clean separation of persistence model from API contract (SRP) — an ORM change (e.g., new internal column) doesn't leak into the API response shape, and vice versa. Full Alembic control.
**Cons:** More boilerplate than SQLModel per entity.

### Option B: SQLModel (SQLAlchemy + Pydantic merged)
**Pros:** One class per entity, less boilerplate.
**Cons:** Couples persistence schema to API schema — violates the separation clean-architecture layering wants; harder to have an internal-only field (e.g., `embedding_ref_id`) that's never exposed over the API without extra work.

### Option C: Sync SQLAlchemy (psycopg2)
**Pros:** Simpler, no async gotchas.
**Cons:** Blocks FastAPI's event loop per request — throws away FastAPI's main concurrency advantage for no real gain here.

## Trade-off Analysis
Option A costs a bit more boilerplate per entity but keeps the repository/service/schema boundary real, which matters given the user explicitly asked for SOLID-oriented layering. Option B is the "lazy" pick in isolation but actively fights that goal, so it's the wrong lazy.

## Consequences
- Every entity gets: ORM model (`app/models/`), Pydantic schema(s) (`app/schemas/`), repository (`app/repositories/`).
- `alembic/env.py` must run migrations via `async_engine_from_config` + `run_sync`.
- Supabase pooler mode requires `asyncpg` connect args: `statement_cache_size=0`, `prepared_statement_cache_size=0` (transaction-mode pooling disallows server-side prepared statement reuse across pooled connections).

## Action Items
1. [x] Hand-author the initial Alembic revision from the models (no live Supabase DB to autogenerate against yet); regenerate via `--autogenerate` once a dev DB is reachable.

---

# ADR-003: Backend Architecture — Layered (Router → Service → Repository)

**Status:** Accepted
**Date:** 2026-07-23
**Deciders:** Tirth Shah

## Context
User asked explicitly for SOLID principles and low-level design discipline in the backend scaffold, not just "an API that works."

## Decision
Four layers, one-way dependency (outer depends on inner, never reverse):
`api/routers` (HTTP/HTTP-only) → `services` (business rules) → `repositories` (data access, defined as ABCs + SQLAlchemy impl) → `models` (ORM).
Routers depend on service *interfaces* via FastAPI `Depends()`; services depend on repository *interfaces*, not concrete SQLAlchemy classes — satisfies DIP and makes services unit-testable with fake repositories.

## Options Considered

### Option A: Layered w/ repository interfaces (chosen)
**Pros:** Each layer has one reason to change (SRP); repositories are swappable/mockable (DIP, testable services without a DB); routers stay thin (no business logic to review for correctness bugs).
**Cons:** More files per feature than a "router calls DB directly" script.

### Option B: Routers call SQLAlchemy directly ("fat router")
**Pros:** Fewest files, fastest to write.
**Cons:** Business rules end up duplicated across routers; untestable without spinning up a DB; directly contradicts the SOLID ask.

### Option C: Full DDD (entities, value objects, domain events, CQRS)
**Pros:** Maximum rigor.
**Cons:** Massive over-build for a solo portfolio backend with ~6 entities — this is the YAGNI failure mode, not the SOLID one.

## Trade-off Analysis
B fails the explicit requirement. C is real over-engineering for this project's actual size (PRD §11.2 has 3 core entities plus profile/schedule/caregiver — not a domain complex enough to earn DDD). A is the point on the ladder that satisfies the requirement without inventing unneeded abstraction.

## Consequences
- New feature = new router + service + repository (+ migration if new table) — codified in `.claude/skills/add-feature/SKILL.md` so this stays consistent as the project grows.
- Repository ABCs live next to their SQLAlchemy implementation (`app/repositories/<entity>.py`), not a separate `interfaces/` package — one file, two classes, avoids a needless package split.

## Action Items
1. [x] Scaffold `app/{models,schemas,repositories,services,api}` per this layering.

---

# ADR-004: Mobile Framework — React Native via Expo (managed workflow, Expo Router)

**Status:** Accepted
**Date:** 2026-07-23
**Deciders:** Tirth Shah

## Context
PRD §12 originally scoped an Android-only reference app (Q1, open) built alongside a Gradio demo. The user has since directed the primary mobile client to be React Native. This ADR supersedes PRD Q1's "Android-first only" framing — React Native gives iOS for near-free later, which changes that open question's answer.

## Decision
React Native with Expo (managed workflow) + TypeScript + Expo Router (file-based navigation).

## Options Considered

### Option A: Expo (managed) + Expo Router (chosen)
| Dimension | Assessment |
|-----------|------------|
| Complexity | Low — no native build tooling to hand-maintain |
| Cost | Free; EAS Build free tier covers early dev |
| Scalability | Ejectable to bare workflow later if a native module Expo doesn't support is needed |
| Team familiarity | Standard for new RN projects in 2026 |

**Pros:** `expo-camera` covers FR-1's guided capture without native camera code; OTA updates; fast iteration; Expo Router gives typed, file-based screens matching the PRD's UF-1..UF-5 flows directly.
**Cons:** Managed workflow adds an abstraction over bare native; a few native libraries need a config plugin or a dev-client build.

### Option B: Bare React Native CLI
**Pros:** No Expo abstraction, full native control from day one.
**Cons:** More native build maintenance (Xcode/Gradle config) for no benefit at this stage — premature; Expo covers camera/ML-model-bundling needs already.

### Option C: Native Android only (original PRD framing)
**Pros:** Matches PRD's original single-platform scope.
**Cons:** Explicitly overridden by this session's direction toward React Native; forecloses iOS.

## Trade-off Analysis
The on-device CV pipeline (detector/encoder/OCR, PRD §12) will still need a native inference path (TFLite/ONNX Runtime) — Expo's config plugins / a custom dev client handle that without giving up managed-workflow convenience. Full bare RN only pays off if Expo can't ship the ONNX/TFLite integration, which isn't yet known to be true.

## Consequences
- `mobile/app/` holds Expo Router screens; native inference module is added later as a config plugin or dev-client, not by ejecting outright.
- If Expo's TFLite/ONNX Runtime support proves insufficient in Phase 2, revisit via a new ADR — don't pre-eject speculatively now.

## Action Items
1. [x] Scaffold `mobile/` as an Expo + TS + Expo Router app.

---

# ADR-005: Mobile State & Data Layer — Zustand + TanStack Query

**Status:** Accepted
**Date:** 2026-07-23
**Deciders:** Tirth Shah

## Context
The mobile app needs local UI/session state (active profile, capture flow state) and server state (regimen, dose history, caregiver data from the FastAPI backend).

## Decision
Zustand for local/client state, TanStack Query for server state (fetching/caching/invalidating API data).

## Options Considered

### Option A: Zustand + TanStack Query (chosen)
**Pros:** Minimal boilerplate (no actions/reducers/providers ceremony); TanStack Query gives caching, retries, and offline-friendly stale-while-revalidate for free, which matters given FR-7's offline requirement for the *verification* flow and general flaky-network tolerance for the *sync* flows.
**Cons:** Two libraries instead of one.

### Option B: Redux Toolkit for everything
**Pros:** One library, very standard.
**Cons:** RTK Query duplicates most of TanStack Query's value with more ceremony; plain Redux slices for server state means hand-rolling cache invalidation — unnecessary weight for this app's state complexity.

### Option C: React Context + useReducer only
**Pros:** Zero dependencies.
**Cons:** No caching/retry/invalidation for server state — would mean hand-building what TanStack Query already solved; premature to reinvent.

## Trade-off Analysis
A gives the least code for the actual needs (local state is small — active profile, in-flight capture; server state is the bulk of the app). B and C both mean writing more code to reach the same place.

## Consequences
- `mobile/src/store/` holds Zustand stores (small, per-concern).
- `mobile/src/lib/api/` holds the API client + TanStack Query hooks per entity.

## Action Items
1. [x] Scaffold store/query-client wiring in `mobile/src/lib`.
