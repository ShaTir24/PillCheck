# PillCheck mobile — conventions

Expo (managed) + TypeScript + Expo Router. Rationale: [`../DECISIONS.md`](../DECISIONS.md) ADR-004/005.

## Structure

```
app/            Expo Router routes only — thin screens, no business logic.
  (tabs)/       Home, Verify, History, Regimen, Settings (PRD §6 core functions).
  onboarding/   First-run flow (UF-4), outside the tab bar.
src/
  features/<domain>/api.ts   TanStack Query hooks per backend entity (1:1 with backend routers).
  lib/api/client.ts          Single axios instance — every feature imports this, nothing creates its own.
  lib/queryClient.ts         Single QueryClient instance.
  store/                     Zustand — cross-screen client state only (currently: auth identity).
  types/api.ts                TS types mirroring backend/app/schemas/*.py Read models.
  constants/theme.ts           Design tokens: palette, WCAG-AA-checked text/bg pairings, typography, spacing.
  components/ui/               Surface, Text/Heading, Button, CelestialBackground — see the design-system skill.
```

Imports are relative (`../../lib/...`), not `@/...` — no path-alias Metro/Babel config is wired up, and adding one isn't worth it at this size. If the codebase grows past comfortable relative paths, this is a two-line decision to add `babel-plugin-module-resolver`, not a redesign.

## Adding a feature

Follow `.claude/skills/add-feature/SKILL.md` at the project root. Short version for a screen consuming an existing backend entity:

1. `src/types/api.ts` — type already exists if the backend entity does; keep it in sync by hand when backend schema fields change.
2. `src/features/<domain>/api.ts` — TanStack Query hook(s) calling `apiClient`. Query key convention: `[entityPluralName, ...idsOrFilters]`, e.g. `["medications", medicationId, "schedules"]` — match what's already there.
3. Route file in `app/` — screen composes the hook + `src/components/ui` (`Surface`, `Text`/`Heading`, `Button`) per the `mobile-design-system` skill. If the screen has real presentational complexity, extract it to `src/features/<domain>/` as a component; don't grow the route file past "layout + hook wiring."
4. Register in the relevant `_layout.tsx` if it's a new route.

## Design system

Colors, typography, and the celestial-background motif are governed by the `mobile-design-system` skill and `src/constants/theme.ts` — read that skill before touching any screen's visual styling. In short: never write a raw hex color or `fontFamily`/`fontSize` in a screen; always go through `theme.ts` tokens or the `src/components/ui` primitives.

## Non-negotiables

- **State split**: server data (anything from the backend) → TanStack Query. Local/session UI state (active profile, in-flight capture) → Zustand. Don't hand-roll caching/loading state with `useState` + `useEffect` for anything that's actually server data — that's what TanStack Query is there to avoid re-solving.
- **`apiClient` is the only HTTP client.** Don't call `fetch`/`axios` directly from a feature or screen — the auth-header interceptor (bearer token or the local `X-Debug-Profile-Id` fallback) only runs through it.
- The on-device CV pipeline (detection/recognition/decision engine, PRD Phase 1/2) is **not** built yet. `app/(tabs)/verify.tsx` has a placeholder "Simulate capture" button calling `useRecordDoseEvent` directly — when the real pipeline lands, it produces the `result`/`per_pill`/`quality` payload that already flows into that same hook. Don't restructure the API/hook to accommodate it; the shape is already right (mirrors `backend/app/schemas/dose_event.py`).
- Camera permission strings live in `app.json` (`NSCameraUsageDescription`, the `expo-camera` plugin config) — update both if the copy changes, they're currently duplicated by necessity (iOS Info.plist vs. Android runtime prompt).
- Run `npm run typecheck && npx eslint . && npx expo-doctor` before considering a change done. All three are clean on the current codebase.
