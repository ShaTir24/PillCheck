/**
 * PillCheck design tokens. Source of truth: the style guide palette (see
 * .claude/skills/mobile-design-system/SKILL.md for the full spec, including
 * the derived text-contrast rules below). Every screen should use these
 * tokens, not hardcoded hex/font values — see mobile/CLAUDE.md.
 */

// ---- Palette -----------------------------------------------------------

export const palette = {
  // Primary swatches
  graphite: "#111827",
  aquaMint: "#7AD3B3",
  operationalMint: "#67BFA7",
  warmBeige: "#D8C7A3",
  warmCloud: "#F7F5F0",

  // Supporting palette
  graphite80: "#2D3748",
  graphite60: "#4A5568",
  graphite20: "#CBD5E0",
  mint20: "#C8EDE1",
  beige40: "#E8DCC8",
  errorRed: "#E53E3E",
  warningAmber: "#D69E2E",
  successGreen: "#38A169",

  white: "#FFFFFF",
};

/**
 * Every background paired with the text color that clears WCAG AA (4.5:1
 * normal text) against it — measured, not guessed (PRD FR-8 is a hard
 * requirement, and the raw palette alone doesn't guarantee this: white text
 * on Aqua Mint is ~1.8:1, for example). Always read text color from here
 * rather than pairing palette values ad hoc.
 */
export const surfaces = {
  primary: { bg: palette.graphite, on: palette.warmCloud }, // 16.3:1
  accent: { bg: palette.aquaMint, on: palette.graphite }, // 10.0:1
  operational: { bg: palette.operationalMint, on: palette.graphite }, // 8.1:1
  secondary: { bg: palette.warmBeige, on: palette.graphite }, // 10.7:1
  background: { bg: palette.warmCloud, on: palette.graphite }, // 16.3:1
  warning: { bg: palette.warningAmber, on: palette.graphite }, // 7.4:1
  success: { bg: palette.successGreen, on: palette.graphite }, // 5.5:1 (white on this is only 3.2:1 — fails)
  /**
   * Error Red fails AA for *small* text against both white (4.1:1) and
   * graphite (4.3:1) — it's a hair under 4.5:1 either way. Only use it as:
   * a background for large/bold labels (white text; 4.1:1 clears the 3:1
   * large-text threshold), an icon/border accent, or a chip background with
   * graphite text kept short. Never small red-on-white or red-on-cloud body
   * text — pair an error message with graphite text + a red accent instead.
   */
  danger: { bg: palette.errorRed, on: palette.white },
};

export const colors = {
  ...palette,
  text: palette.graphite,
  textMuted: palette.graphite60,
  border: palette.graphite20,
  background: palette.warmCloud,
  surface: palette.white,
  primary: palette.aquaMint,
  primaryText: palette.graphite,
  danger: palette.errorRed,
  warning: palette.warningAmber,
  success: palette.successGreen,
};

// ---- Typography ----------------------------------------------------------
// Heading: Playfair Display. Body/UI: Inter. Loaded via expo-font in
// app/_layout.tsx — these string literals must match the useFonts() keys.

export const fonts = {
  headingRegular: "PlayfairDisplay_400Regular",
  headingSemiBold: "PlayfairDisplay_600SemiBold",
  headingBold: "PlayfairDisplay_700Bold",
  body: "Inter_400Regular",
  bodyMedium: "Inter_500Medium",
  bodySemiBold: "Inter_600SemiBold",
  bodyBold: "Inter_700Bold",
};

export const typography = {
  h1: { fontFamily: fonts.headingBold, fontSize: 28, lineHeight: 34 },
  h2: { fontFamily: fonts.headingSemiBold, fontSize: 22, lineHeight: 28 },
  h3: { fontFamily: fonts.headingSemiBold, fontSize: 18, lineHeight: 24 },
  body: { fontFamily: fonts.body, fontSize: 16, lineHeight: 22 },
  bodyMedium: { fontFamily: fonts.bodyMedium, fontSize: 16, lineHeight: 22 },
  label: { fontFamily: fonts.bodySemiBold, fontSize: 14, lineHeight: 18 },
  caption: { fontFamily: fonts.body, fontSize: 13, lineHeight: 17 },
  button: { fontFamily: fonts.bodySemiBold, fontSize: 16, lineHeight: 20 },
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
};

export const radius = {
  sm: 8,
  md: 12,
  lg: 16,
  pill: 999,
};
