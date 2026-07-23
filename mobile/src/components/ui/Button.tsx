import { Pressable, StyleSheet, type PressableProps } from "react-native";

import { radius, surfaces, typography } from "../../constants/theme";
import { Text } from "./Typography";

interface ButtonProps extends Omit<PressableProps, "style"> {
  label: string;
  variant?: "primary" | "operational" | "danger";
}

const VARIANT_BG: Record<NonNullable<ButtonProps["variant"]>, string> = {
  primary: surfaces.accent.bg,
  operational: surfaces.operational.bg,
  danger: surfaces.danger.bg,
};

const VARIANT_TEXT: Record<NonNullable<ButtonProps["variant"]>, string> = {
  primary: surfaces.accent.on,
  operational: surfaces.operational.on,
  danger: surfaces.danger.on,
};

/** Standard CTA. Always pairs the theme's pre-checked accessible text color
 * with its background — see theme.ts `surfaces` for why this matters (raw
 * white-on-mint fails WCAG AA). */
export function Button({ label, variant = "primary", disabled, ...rest }: ButtonProps) {
  return (
    <Pressable
      accessibilityRole="button"
      disabled={disabled}
      style={[
        styles.base,
        { backgroundColor: VARIANT_BG[variant] },
        disabled && styles.disabled,
      ]}
      {...rest}
    >
      <Text style={[typography.button, { color: VARIANT_TEXT[variant] }]}>{label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  base: {
    borderRadius: radius.sm,
    paddingVertical: 14,
    alignItems: "center",
    justifyContent: "center",
    minHeight: 48,
  },
  disabled: {
    opacity: 0.5,
  },
});
