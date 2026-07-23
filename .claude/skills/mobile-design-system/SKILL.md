---
name: mobile-design-system
description: PillCheck mobile's color palette, typography, and celestial-background motif, and the components that implement them. Use when building or editing any screen/component under mobile/, choosing a color or text style, adding a button/heading/background, or reviewing a screen for visual consistency. All values live in mobile/src/constants/theme.ts — this skill is the reference for what they mean and how to use them correctly (including which text/background pairs are WCAG AA safe).
---

# PillCheck mobile design system

Source of truth: [`mobile/src/constants/theme.ts`](../../../mobile/src/constants/theme.ts). This skill explains what's in it and how to use it — don't hardcode a hex color or font name in a screen; import from here.

## Palette

| Token | Hex | Use for |
|---|---|---|
| `palette.graphite` | `#111827` | Primary text, dark surfaces, navigation |
| `palette.aquaMint` | `#7AD3B3` | CTAs, highlights, active states |
| `palette.operationalMint` | `#67BFA7` | Confirmed actions, in-progress states, secondary CTAs |
| `palette.warmBeige` | `#D8C7A3` | Secondary accents, hover states, borders |
| `palette.warmCloud` | `#F7F5F0` | Page canvas, card surfaces (default light background) |
| `palette.graphite80` | `#2D3748` | Dark-surface secondary elements (e.g. celestial orbit rings) |
| `palette.graphite60` | `#4A5568` | Muted text, placeholders |
| `palette.graphite20` | `#CBD5E0` | Borders, dividers |
| `palette.mint20` | `#C8EDE1` | Light chip backgrounds |
| `palette.beige40` | `#E8DCC8` | Hover states |
| `palette.errorRed` | `#E53E3E` | Destructive actions, errors (see contrast note below) |
| `palette.warningAmber` | `#D69E2E` | Warnings, alerts |
| `palette.successGreen` | `#38A169` | Confirmations, success |

## Text-on-background pairings (WCAG AA) — use `surfaces`, not raw palette pairs

The raw palette does **not** guarantee readable pairings — e.g. white text on `aquaMint` is ~1.8:1 (needs 4.5:1). `theme.ts` exports `surfaces`, which is the pre-checked `{ bg, on }` pairing for every semantic surface. **Always read both colors from the same `surfaces.<name>` entry — never mix a background from one and a text color from another.**

| Surface | bg | on (text) | Contrast |
|---|---|---|---|
| `surfaces.primary` | graphite | warmCloud | 16.3:1 |
| `surfaces.accent` | aquaMint | graphite | 10.0:1 |
| `surfaces.operational` | operationalMint | graphite | 8.1:1 |
| `surfaces.secondary` | warmBeige | graphite | 10.7:1 |
| `surfaces.background` | warmCloud | graphite | 16.3:1 |
| `surfaces.warning` | warningAmber | graphite | 7.4:1 |
| `surfaces.success` | successGreen | graphite | 5.5:1 |
| `surfaces.danger` | errorRed | white | 4.1:1 |

**`surfaces.danger` is a special case**: Error Red fails AA (4.5:1) for small text against *both* white and graphite — it sits at ~4.1–4.3:1 either way. Only use it as: a background for a large/bold button label (clears the 3:1 large-text threshold), an icon or border accent, or a short chip label. Never render small red-on-white or red-on-cloud body text for an error message — pair a graphite-text error message with a red icon/left-border accent instead.

This matters for PRD FR-8 (WCAG 2.1 AA is a hard requirement, not a nice-to-have) and persona P1 (a 72-year-old with mild visual impairment) — don't loosen a pairing to "make a color pop."

## Typography

Heading font: **Playfair Display**. Body/UI font: **Inter**. Loaded in `app/_layout.tsx` via `expo-font` + `@expo-google-fonts/*`; the app blocks on the splash screen until both load (see that file if fonts ever need a new weight — add it to both the `useFonts()` call and `theme.ts`'s `fonts` object, they must match exactly).

Use the `typography` scale (`h1`/`h2`/`h3`/`body`/`bodyMedium`/`label`/`caption`/`button`) via the `<Text>`/`<Heading>` components (below) — never set `fontFamily`/`fontSize`/`fontWeight` directly in a screen's `StyleSheet`.

## Components (`mobile/src/components/ui/`)

- **`<Surface variant celestial>`** — screen-root wrapper: safe area + background color from `surfaces`. `variant` defaults to `"background"` (light canvas). Use `variant="primary"` (dark graphite) only for brand moments — onboarding, the Home tab — not for functional/task screens (Verify, History, Regimen, Settings stay on the light canvas; that's a deliberate accessibility choice, see below).
- **`<CelestialBackground>`** — the dotted-sky + orbit-ring motif from the style guide. Rendered by `<Surface celestial>`, not used standalone. **Only valid on `surfaces.primary` (dark graphite)** — the dots/rings are graphite-tinted and would be invisible or contrast-breaking on a light surface. Don't set `celestial` on a `variant="background"` screen.
- **`<Text variant color>` / `<Heading level>`** — the only place `fontFamily` is set. Default color is `colors.text` (graphite); pass a `surfaces.<x>.on` value when on a non-default background (see Home/onboarding for the pattern of hoisting `const onPrimary = surfaces.primary.on`).
- **`<Button label variant>`** — `variant` is `"primary"` (aquaMint/accent), `"operational"` (operationalMint), or `"danger"` (errorRed, large bold label only — see contrast note). Always pulls both bg and text color from the matching `surfaces` entry; never build a custom-colored button inline.

## Why functional screens stay light, celestial stays on brand moments

The screenshot's dark, star-flecked backdrop is a style-guide showcase page — striking, but low-contrast decorative chrome is the wrong choice behind a medication-verification result a visually-impaired user needs to read correctly (PRD FR-8, the whole premise of "never confidently mis-verify" extends to "never make the result hard to read"). The split already in the codebase:

- **Dark + celestial** (`variant="primary" celestial`): Home, onboarding — first-run and "welcome back" brand moments, no safety-critical content.
- **Light, clean, no celestial** (`variant="background"`, the default): Verify, History, Regimen, Settings — anywhere a user reads a result, a medication name, or enters data.

If a new screen is unsure which it is: does getting the content wrong or missing it have a safety consequence? If yes, light canvas, no celestial.

## Non-negotiables

- No raw hex strings or `fontFamily` literals in a screen — import from `theme.ts` or use the `ui` components.
- No new background/text color pairing without checking contrast (or reusing an existing `surfaces` entry). If you add a new semantic surface, compute its contrast ratio and record it in the table above and in `theme.ts`'s comments, the way the existing ones are.
- Run `npm run typecheck && npx eslint . && npx expo-doctor` after any visual change — same bar as any other mobile change (see `mobile/CLAUDE.md`).
