import type { ReactNode } from "react";
import { StyleSheet, View } from "react-native";

import { colors, radius, spacing } from "../../constants/theme";

interface CardProps {
  children?: ReactNode;
  /** Left-border accent (e.g. a dose-event result color) — decorative, never
   * the only signal; always pair with a text label (WCAG 1.4.1). */
  accentColor?: string;
}

/** Row/section container for list items on the light (background) surface —
 * see mobile-design-system skill: functional screens stay on the light
 * canvas, so visual structure comes from card grouping, not celestial chrome. */
export function Card({ children, accentColor }: CardProps) {
  return (
    <View style={[styles.card, accentColor ? { borderLeftWidth: 4, borderLeftColor: accentColor } : null]}>
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    padding: spacing.md,
    gap: spacing.xs,
  },
});
