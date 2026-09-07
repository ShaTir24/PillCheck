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

---

# ADR-006: Authentication — In-house (email/password) auth, replacing Supabase Auth

**Status:** Proposed
**Date:** 2026-07-26
**Deciders:** Tirth Shah

## Context
ADR-001's action item 2 assumed Supabase Auth would be adopted once caregiver accounts (FR-11) were built; `app/core/security.py` already decodes a Supabase JWT and treats its `sub` claim as the profile id directly (identity == profile, 1:1). The user has now explicitly ruled out Supabase Auth and wants auth managed entirely by our own `users` table in Postgres, with signup, login, and forgot-password. This supersedes ADR-001 action item 2 — Supabase stays "just Postgres," no Auth product.

This is one decision with four coupled parts: (1) how login identity relates to the existing `Profile` entity, (2) whether "role" is a stored field, (3) how password-reset email gets sent, (4) how sessions/tokens get invalidated. Bundled here because they're one feature, per the bundling style of ADR-002.

## Decision

**1. New `User` table, 1 : many `Profile`.** `users` (id, email unique, password_hash, token_version, password_reset_token_hash nullable, password_reset_expires_at nullable, timestamps) becomes the login identity. `profiles.user_id` FK is added (`NOT NULL`, `ondelete="CASCADE"`). Chosen over merging auth fields into `Profile` (1:1) to avoid a later migration when FR-12 (aide, multi-profile) is built — the column exists now even though it's unused beyond 1 profile/user until FR-12 ships.

  **Scope guard for this ADR:** no router changes ship for multi-profile *selection*. `get_current_profile_id` still resolves to "the caller's one profile" (the profile created at signup) — every existing router (`medications`, `schedules`, `dose_events`, etc.) is untouched. Real profile-switching (which of several profiles is "active") is FR-12's job, not this one.

**2. No stored role field.** Access control keeps deriving from relationships already in the schema: a profile always acts on its own data; cross-profile access requires an active `CaregiverLink` + its `scopes`. Nothing in the codebase yet checks a role, and the PRD personas aren't mutually exclusive per account (the same person can be a subject in one link and a caregiver in another) — a role enum would either duplicate `CaregiverLink.scopes` or be wrong the moment someone has both relationships.

**3. Email sending behind a one-method interface.** `EmailSender` (ABC, mirrors the `Repository` ABC pattern in `app/repositories/base.py`) with `send_password_reset(to_email, reset_link)`. Concrete impl for now: `LoggingEmailSender` (logs the link — no provider is configured yet). Swapping in SES later is a new `SESEmailSender` class + one line of DI wiring in `app/api/deps.py`; `AuthService` and the router never change.

**4. Stateless JWT + `token_version` counter — no sessions table.** Access (short-lived, ~15 min) and refresh (long-lived, ~30 days) tokens are both signed JWTs carrying `user_id` and `token_version`. Each `User` row has a `token_version` int; password reset (and a future explicit "log out everywhere") increments it, and every token is checked against the current value at verification time. Gives real revocation without a sessions table or cleanup job.

`app/core/security.py`'s Supabase JWT decode path and the `X-Debug-Profile-Id` local-dev bypass are removed — logging in for local dev is now just calling `POST /auth/login`, so the bypass is no longer needed.

## Options Considered

### User↔Profile relationship
| Option | Pros | Cons |
|---|---|---|
| **A. 1:many `User`→`Profile` (chosen)** | No future migration for FR-12; `profiles.user_id` ships now | Adds a column unused beyond cardinality 1 until FR-12 |
| B. Merge auth fields into `Profile` (1:1) | Fewest tables now | FR-12 needs a real migration + data move later |

### Role modeling
| Option | Pros | Cons |
|---|---|---|
| **A. No role field, derive from relationships (chosen)** | No duplicate source of truth vs. `CaregiverLink.scopes`; matches "same person, multiple relationships" reality | Any future per-role UI copy/config still has to compute role from relationships |
| B. Explicit `role` enum on `User` | Cheap to read in a JWT claim | Wrong the moment one account is both a subject and a caregiver; duplicates scopes |

### Password-reset delivery
| Option | Pros | Cons |
|---|---|---|
| **A. `EmailSender` interface, `LoggingEmailSender` now (chosen)** | SES drops in later with zero changes to `AuthService`/router; matches DIP already used for repositories | Reset emails don't actually send until SES impl is added |
| B. Hardcode an SES call now | One less interface | SES isn't configured yet (no verified domain/API keys) — would ship dead/untestable code today |

### Session/token invalidation
| Option | Pros | Cons |
|---|---|---|
| **A. JWT + `token_version` (chosen)** | No new table, no cleanup job; matches existing stateless-JWT pattern | Can't revoke a *single* device, only "all sessions for this user" |
| B. DB-backed refresh-token sessions table | Per-device revocation | New table + expiry cleanup job for a capability (per-device logout) nothing has asked for yet |

## Trade-off Analysis
Every "chosen" column above is the option that avoids inventing a mechanism (role enum, sessions table, live SES integration) the current feature set doesn't need, while the one place we *do* pay a small cost now (the `user_id` FK / 1:many shape) is paying for a migration we already know is coming (FR-12), not a hypothetical one. The email interface is the one abstraction added pre-emptively, and it's justified because the user confirmed SES is a near-term, named follow-up — not speculative.

## Consequences
- New table `users`; new column `profiles.user_id` (`NOT NULL`) — one Alembic revision. No existing data to backfill (no auth rows exist yet).
- New dependency: `bcrypt` (password hashing) — `python-jose` (already a dependency) covers our own JWT signing/verification too, no new JWT library.
- `app/core/config.py`: drop `supabase_jwt_secret`; add `auth_jwt_secret`, `auth_access_token_expire_minutes`, `auth_refresh_token_expire_days`.
- `app/core/security.py`: `get_current_profile_id` reimplemented to decode our JWT, look up the token's user, resolve their one profile, and check `token_version`. Supabase decode path and `X-Debug-Profile-Id` deleted (`backend/CLAUDE.md`'s security.py non-negotiable note needs updating alongside this).
- New router `app/api/v1/routers/auth.py`: `POST /auth/signup`, `/auth/login`, `/auth/refresh`, `/auth/forgot-password`, `/auth/reset-password`.
- `POST /profiles` (today: "create the profile row for the caller's own auth identity") becomes "create the first/next profile owned by the caller's user" — still creates at most one profile per user for now; a second call is a latent multi-profile path FR-12 will formalize, not one this ADR builds UI/selection for.
- Rate-limiting `/auth/forgot-password` and login attempts is a known gap, not built now (no rate-limiting exists anywhere in the app yet) — `# ponytail` marker at the endpoint, add if abuse shows up.
- Mobile: needs login/signup/forgot-password/reset-password screens and token storage (`expo-secure-store`) — separate `add-feature`-style pass, not part of this ADR's backend action items below.

## Action Items
1. [ ] `app/models/user.py` — `User` model; add `user_id` FK to `app/models/profile.py`.
2. [ ] Alembic revision: `users` table + `profiles.user_id` column.
3. [ ] `app/schemas/auth.py` — `SignupRequest`, `LoginRequest`, `TokenResponse`, `ForgotPasswordRequest`, `ResetPasswordRequest`.
4. [ ] `app/repositories/user.py` — `UserRepository` extends `SQLAlchemyRepository[User]`, add `get_by_email`.
5. [ ] `app/core/security.py` — password hashing helpers (bcrypt), our-own JWT encode/decode, rewritten `get_current_profile_id`; delete Supabase decode + debug-header path.
6. [ ] `app/core/email.py` — `EmailSender` ABC + `LoggingEmailSender`.
7. [ ] `app/services/auth.py` — `AuthService`: signup, login, refresh, forgot_password, reset_password.
8. [ ] `app/api/deps.py` — wire `get_auth_service`.
9. [ ] `app/api/v1/routers/auth.py` — the five endpoints; register in `app/api/v1/router.py`.
10. [ ] Unit tests against a fake `UserRepository` + fake `EmailSender` for `AuthService` (password verify, token_version bump on reset, expired-token rejection).
11. [ ] Update `backend/CLAUDE.md`'s security.py non-negotiable note (Supabase bypass description is stale once this lands).
12. [ ] `backend/.env.example` — replace `SUPABASE_JWT_SECRET` with `AUTH_JWT_SECRET` (+ expiry settings).

---

# ADR-007: ML Pipeline Phase 0 — Repo Layout, Data Versioning, Compute Strategy

**Status:** Accepted
**Date:** 2026-07-27
**Deciders:** Tirth Shah

## Context
PillCheck's actual core — pill detection/recognition (PRD F1-F3, §10, §12) — had zero code before this ADR; `backend/` and `mobile/` only cover auth/regimen/design-system scaffolding. PRD §14 Phase 0 scopes "repo scaffolding, data ingest, eval harness reproducing the ePillID baseline protocol." This ADR covers where that code lives, how datasets are versioned, and the compute split — bundled as one decision (same style as ADR-006) since they're one feature: standing up Phase 0.

User-confirmed constraints going in: no GPU available yet (CPU-only/undecided), and DVC (PRD §12's stated tool) is skipped in favor of a simpler approach for a solo-maintained project.

## Decision

1. **New top-level `ml/` package**, sibling to `backend/`/`mobile/`, own `CLAUDE.md`, separate `uv` environment (`pyproject.toml`) — heavy CV/ML deps (torch, timm) don't belong in the FastAPI service's env.
2. **No DVC.** `ml/data/manifests/*.json` commits source URLs + sha256 + license notes per dataset; `ml/data/raw/` and `ml/data/processed/` are gitignored and rebuilt by scripts. Revisit DVC only if datasets start mutating or need cross-machine sharing — neither is true yet.
3. **Compute split:** local CPU for data ingestion + eval (inference-only, confirmed cheap enough — the full Phase 0 baseline eval, 9,804-image gallery + 745-query test fold, ran in ~2m20s on a CPU-only laptop). GPU-training phases (Phase 1 encoder, Phase 2 detector) are explicitly deferred to a rented/free GPU (e.g. Colab) — not solved now since Phase 0 needs no training.
4. **Detector license choice (PRD Q2, YOLOv8-AGPL vs RT-DETR) is deliberately not decided here** — PRD already scopes it as "blocking before Phase 2," and Phase 0 does no detection work.
5. **Retrieval-based eval, not classification.** `ml/eval/metrics.py` measures top-k via nearest-embedding retrieval against a reference gallery (cosine similarity, plain numpy), matching the production architecture's ANN-lookup design (PRD §10.1) — appropriate since pill ID is low-shot (~1 reference image per class in ePillID).

## Options Considered

### Repo layout
| Option | Pros | Cons |
|---|---|---|
| **A. New `ml/` top-level package (chosen)** | Matches existing `backend/`/`mobile/` per-area convention; clean env separation | One more top-level dir |
| B. Put ML code inside `backend/` | Fewer top-level dirs | Backend's FastAPI env would carry torch/timm for no reason; conflates a request-serving service with an offline data/training pipeline |

### Data versioning
| Option | Pros | Cons |
|---|---|---|
| **A. Checksum-pinned manifests, no DVC (chosen)** | Zero new tooling/remote to maintain; datasets are public and stably re-downloadable | No diffing/versioning if a dataset is later locally modified |
| B. DVC (PRD §12) | Matches the PRD's stated tool; real versioning + remote storage | Needs a configured remote (S3/GDrive) and adds a tool with no current job to do — over-provisioning for a solo project re-downloading stable public data |

### Compute for Phase 0
| Option | Pros | Cons |
|---|---|---|
| **A. Local CPU now, GPU deferred to when training starts (chosen)** | Phase 0 is inference-only — confirmed CPU-feasible by actually running it; no cost/setup until it's needed | Phase 1 will need a real GPU plan, not solved yet |
| B. Set up a GPU environment now | Ready before Phase 1 | Solving a problem Phase 0 doesn't have — premature given no GPU is confirmed available |

## Trade-off Analysis
Every "chosen" option avoids standing up infrastructure (DVC remote, GPU environment, a detector-license decision) that Phase 0's actual scope doesn't need yet, while still shipping the one thing Phase 0 requires: a working, reproducible data-ingest-to-eval pipeline. Where PRD §12 names a specific tool (DVC) and this ADR deviates, the deviation is recorded with its trigger condition, not silently dropped.

## Consequences (including findings discovered while scaffolding)

- `ml/scripts/download_epillid.py` and `download_ndc.py` are fully automated (real, confirmed URLs — ePillID's GitHub release asset, and openFDA's `/download.json` metadata endpoint resolved at run time so a repartition doesn't silently break the script). Both were run for real; checksums are pinned in their manifests.
- `ml/scripts/download_c3pi.py` and `download_pillbox.py` **cannot** auto-resolve a download URL — C3PI and Pillbox are both discontinued NLM datasets with no clean bulk-download API found by research. Both scripts refuse to guess and print where to resolve the link manually (`data/manifests/c3pi.json` / `pillbox.json`). This is a real, currently-open gap, not an oversight.
- **FAISS + torch segfault together on macOS ARM** (a libomp conflict — hit directly during scaffolding, confirmed by isolating it, not assumed). `ml/eval/metrics.py` uses plain numpy instead; FAISS was also dropped from `ml/pyproject.toml`'s dependencies. Revisit FAISS if a later phase's gallery size actually needs approximate search — Phase 0/1 scale (thousands of vectors) doesn't.
- **The live openFDA NDC directory cannot backfill ePillID's images**, confirmed empirically: ~0.5% of ePillID's package NDCs are still listed in the 2026 NDC export (checked at both package_ndc and product_ndc granularity) — most were delisted since ePillID's images are ~2016-2018 vintage. `join_metadata.py`'s NDC join is still correct and will matter for FR-5 (a user adding a *current* prescription), it just can't enrich these specific historical images. Real appearance metadata (SPLIMPRINT/SPLSHAPE/SPLCOLOR/SPLSIZE) for ePillID's pills has to come from Pillbox's own archived records (gap above), not the live NDC directory — confirmed the two are genuinely separate sources (a live NDC record has no imprint/shape/color/size fields at all).
- Root `CLAUDE.md`'s Structure table now lists `ml/`.
- Phase 0 exit criterion result: `make eval-baseline` (frozen `resnet18`, no fine-tuning, official ePillID test fold 4) scores top-1 14.6% / top-5 34.4%. This is a sanity-check number confirming the harness works end-to-end, not the paper's published SOTA (which needs their trained multi-head metric model) — pin the actual comparison target once the specific baseline row from the paper is chosen.

## Action Items
1. [x] Scaffold `ml/` (`CLAUDE.md`, `README.md`, `pyproject.toml`, `Makefile`, `data/manifests/`, `scripts/`, `eval/`).
2. [x] `download_epillid.py`, `download_ndc.py` — implemented and run for real; checksums pinned.
3. [ ] Resolve `c3pi.json` / `pillbox.json` download URLs manually, then run `download_c3pi.py` / `download_pillbox.py`.
4. [x] `join_metadata.py`, `test_join.py`, `build_splits.py` — implemented and run for real against downloaded data.
5. [x] `eval/harness.py`, `eval/baseline.py`, `eval/metrics.py` — implemented and run for real; Phase 0 exit-criterion number recorded above.
6. [ ] Once Pillbox metadata is resolved, extend `join_metadata.py` to populate imprint/shape/color/size.
7. [ ] Pin the specific ePillID paper baseline row to compare against for the "±1pt" exit criterion.

---

# ADR-008: Encoder Training Compute — Kaggle GPU, Backbone, Code/Data Transfer

**Status:** Accepted
**Date:** 2026-07-27
**Deciders:** Tirth Shah

## Context
ADR-007 flagged "no GPU confirmed" as a Phase 1 risk and named Colab as the fallback without committing to it. The user has Kaggle GPU-provisioned instances already available, which resolves that open item. Per the user's explicit scope choice, this ADR covers only the GPU-critical path of PRD Phase 1: training the ArcFace metric-learning encoder and building the reference index from it. OCR fusion, calibration/abstention, and the Gradio demo (also Phase 1 items) need no GPU and are deliberately deferred to a separate pass.

## Decision

1. **Compute: Kaggle Notebooks, superseding ADR-007's Colab placeholder.** GPU-provisioned Kaggle instances the user already has access to; no new environment to provision.
2. **Backbone: `convnext_tiny` (timm) + `ArcFaceLoss` (`pytorch-metric-learning`).** PRD §12 leaves ConvNeXt-T vs. EfficientNetV2-S open; with a real GPU now available, accuracy (G1's primary metric) is prioritized over footprint — footprint is addressed at Phase 3 export time via INT8 quantization regardless of backbone.
3. **Training label = appearance class (`pilltype_id` + side), not `pilltype_id` alone** — matches the paper's own 9,804-class framing and gives the encoder more separating signal. Eval stays at the `pilltype_id` level (`eval/harness.py`, unchanged) since side doesn't matter for the product's MATCH decision.
4. **Train/held-out split reuses ePillID's own fold files as-is**: train on all reference images + consumer folds 0-3; fold 4 (the same fold the Phase 0 baseline was scored on) stays untouched, so the before/after comparison is apples-to-apples. No new split-generation code.
5. **Code reaches Kaggle as an uploaded Kaggle Dataset, not `git clone`** — avoids any credential/token handling regardless of the repo's visibility. `kaggle/train_encoder.ipynb` copies the (read-only) uploaded code to `/kaggle/working` first, since everything downstream (scripts, training, path resolution) is unmodified from how it runs locally.
6. **Data reaches Kaggle by re-running `download_epillid.py`** inside the notebook (internet on) — reuses the already-working Phase 0 script instead of a separate upload path for a dataset that downloads in seconds on Kaggle's connection.
7. **Checkpointing is real, not speculative**: `train/encoder.py` saves every epoch and accepts `--resume-from`, since Kaggle GPU sessions cap at ~9h.
8. **FAISS is not used anywhere in this pipeline, including index-building** (`scripts/build_reference_index.py`) — see Consequences; confirmed empirically, not assumed, that this is a real conflict rather than a workaround-able ordering issue.
9. **Getting the trained checkpoint off Kaggle is a manual step** (download via the notebook's Output tab) — no `kaggle` CLI/API-token automation, since that credential is the user's to hold.

## Options Considered

### Backbone
| Option | Pros | Cons |
|---|---|---|
| **A. `convnext_tiny` (chosen)** | Strong fine-grained accuracy; PRD-sanctioned option; GPU now available so training cost isn't the constraint | Larger/slower than EfficientNetV2-S, both on CPU (measured: ~10x slower than resnet18 per batch) and likely at mobile export time |
| B. `efficientnetv2_rw_s` | Designed for the 150MB/on-device footprint budget from the start | Deferred: footprint is a Phase 3 (quantization/export) problem, not a Phase 1 (accuracy) one — optimizing for it now is premature |

### Reference index implementation
| Option | Pros | Cons |
|---|---|---|
| **A. Plain numpy embeddings + labels, no FAISS (chosen)** | Verified during implementation that `import faiss` alone segfaults (OMP Error #15) once torch has been imported in the same process — even with zero concurrent use, contrary to this ADR's own earlier assumption that sequential use would be safe. Numpy is correct and fast enough at ~10k vectors. | No approximate-search structure — irrelevant at this scale |
| B. FAISS `IndexFlatIP` in the same process as the embedding step | Matches "FAISS" as named in PRD §12 | Reproducibly segfaults on this machine; would require running index-building on Kaggle/Linux only, adding a platform constraint for no benefit at this scale |

### Code transfer to Kaggle
| Option | Pros | Cons |
|---|---|---|
| **A. Upload `ml/` as a Kaggle Dataset (chosen)** | Zero credential/token handling; works regardless of repo visibility | Manual re-upload when code changes |
| B. `git clone` inside the notebook | No manual upload step; always current | Needs a PAT/deploy key if the repo is private — credential handling that's the user's to configure, not something to build assuming a status (public/private) that isn't confirmed |

## Trade-off Analysis
Every choice either reuses something already built (Phase 0's download script, the existing eval harness's retrieval metric) or avoids standing up a mechanism (git-clone auth, FAISS) that either isn't needed yet or was proven broken during this implementation. The one real cost accepted is `convnext_tiny`'s CPU slowness for local smoke-testing/eval — mitigated with `--limit` flags on the affected scripts rather than switching backbones to chase local CPU speed, since the actual constraint (training) is solved by moving to Kaggle GPU, not by picking a leaner model.

## Consequences
- New `ml/train/` (`dataset.py`, `encoder.py`) and `ml/configs/encoder.yaml` — Phase 0's `CLAUDE.md` note against scaffolding `train/`/`configs/` speculatively no longer applies; this is the phase that needs them.
- `ml/eval/trained_encoder.py` — thin loader giving a trained checkpoint the same `(model, transform)` shape `eval/baseline.py` returns; `eval/harness.py` gained a `--checkpoint` flag and is otherwise unchanged.
- `ml/scripts/build_reference_index.py` added; produces `gallery_embeddings.npy` + `gallery_labels.npy`, not a FAISS index file (see Options above).
- `ml/pyproject.toml`: added `pytorch-metric-learning`. `faiss-cpu` was tried and removed again in the same session once the segfault was confirmed — it is not a dependency of this pipeline as of this ADR.
- `kaggle/train_encoder.ipynb` added — the actual notebook to run on Kaggle (GPU + internet on, copies input dataset to a writable working dir, installs `timm`/`pytorch-metric-learning`, downloads ePillID, trains, points to where the checkpoint ends up).
- Local CPU smoke tests passed for the full loop with an intentionally undertrained checkpoint (1 epoch, 64 samples): `train/encoder.py` → `eval/harness.py --checkpoint` → `scripts/build_reference_index.py --checkpoint`, all with `--limit`/`--limit-gallery` for speed. These prove the code paths work; they are not a real accuracy result.
- **The actual GPU training run on Kaggle has not happened yet** — that's the one step in this pipeline only the user can execute (their GPU quota, their session). The before/after comparison against the Phase 0 baseline (top-1 14.6% / top-5 34.4%) is pending that run.

## Action Items
1. [x] `ml/train/dataset.py`, `encoder.py`, `ml/configs/encoder.yaml` — implemented, local CPU smoke test passed.
2. [x] `ml/eval/trained_encoder.py`, `--checkpoint` flag on `eval/harness.py` — implemented, smoke test passed.
3. [x] `ml/scripts/build_reference_index.py` — implemented, smoke test passed.
4. [x] `kaggle/train_encoder.ipynb` — written; not yet run on Kaggle.
5. [ ] **User: upload `ml/` (scripts/train/eval/configs) as a Kaggle Dataset, run `kaggle/train_encoder.ipynb` on a GPU instance, download the resulting checkpoint into `ml/outputs/encoder/latest.pt`.**
6. [ ] Run `build_reference_index.py` and `eval/harness.py --checkpoint` on the real trained checkpoint; record the resulting top-1/top-5 here against the 14.6%/34.4% baseline.
7. [ ] Follow-up pass (separate from this ADR): OCR fusion, calibration/abstention, Gradio demo.
