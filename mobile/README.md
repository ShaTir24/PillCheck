# PillCheck mobile

Expo (managed) + TypeScript + Expo Router, Zustand + TanStack Query for state (see [`../DECISIONS.md`](../DECISIONS.md) ADR-004/005). Layering and conventions: [`CLAUDE.md`](CLAUDE.md).

## Local dev

```bash
cp .env.example .env   # EXPO_PUBLIC_API_URL — point at the backend (see ../backend/README.md)
npm install
npm start
```

No auth configured locally — call `useAuthStore.getState().setDebugProfileId(<any-uuid>)` (e.g. from a debug menu) instead of signing in; mirrors the backend's `X-Debug-Profile-Id` bypass.

## Checks

```bash
npm run typecheck
npm run lint
npx expo-doctor
```
