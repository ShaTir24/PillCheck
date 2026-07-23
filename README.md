# PillCheck

Camera-based medication adherence verifier. Point a phone camera at the pill(s) in hand; the system identifies each pill (shape + color + size + imprint) and checks it against the user's schedule, returning **MATCH / MISMATCH / CANNOT IDENTIFY** — with pill-image inference on-device for privacy.

Roughly half of patients on chronic medication don't take their medicines as prescribed, and polypharmacy patients routinely confuse visually similar pills. Existing consumer tools (Medisafe) are reminder-based and trust a self-report; clinical tools (AiCure) verify ingestion but aren't consumer-grade. PillCheck closes that gap for the "is this handful actually tonight's dose?" moment.

Full spec: [docs/PRD.md](docs/PRD.md). Architecture rationale: [DECISIONS.md](DECISIONS.md).

## Structure

- [`backend/`](backend/) — FastAPI + SQLAlchemy(async) + Alembic, Postgres via Supabase. Owns regimen/schedule/dose-event data, not the pill-recognition pipeline (that's on-device, Phase 1/2 of the PRD).
- [`mobile/`](mobile/) — Expo + TypeScript + Expo Router, the React Native client.
- [`docs/PRD.md`](docs/PRD.md) — product spec.
- [`DECISIONS.md`](DECISIONS.md) — ADR log for stack/architecture choices.

Conventions for changing either project: [backend/CLAUDE.md](backend/CLAUDE.md), [mobile/CLAUDE.md](mobile/CLAUDE.md).

## Local setup

Prerequisites: [uv](https://docs.astral.sh/uv/), Docker, Node.js, and either the [Expo Go](https://expo.dev/go) app on your phone or an iOS/Android simulator.

**1. Backend**

```bash
cd backend
cp .env.example .env
docker-compose up -d postgres   # local Postgres on :5433 (5432 may already be taken)
uv sync --dev
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

API is now up at `http://localhost:8000` (`/health` for a smoke check, `/docs` for the OpenAPI UI). No auth is configured locally — endpoints take an `X-Debug-Profile-Id: <any-uuid>` header instead of a bearer token (see [backend/app/core/security.py](backend/app/core/security.py)).

**2. Mobile** (separate terminal)

```bash
cd mobile
cp .env.example .env   # EXPO_PUBLIC_API_URL already points at localhost:8000
npm install
npm start
```

Scan the QR code with Expo Go, or press `i`/`a` for a simulator. To exercise a screen that talks to the backend, set a debug profile id from the JS debugger console: `useAuthStore.getState().setDebugProfileId('<any-uuid>')`, matching the header above.

Full setup/check details for each side: [backend/README.md](backend/README.md), [mobile/README.md](mobile/README.md).
