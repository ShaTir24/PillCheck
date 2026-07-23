import type { ReactNode } from "react";
import { Text as RNText, type TextProps } from "react-native";

import { colors, typography } from "../../constants/theme";

type Variant = keyof typeof typography;

interface AppTextProps extends TextProps {
  variant?: Variant;
  color?: string;
  children: ReactNode;
}

/** The only place fontFamily/fontSize should be set — screens pick a variant,
 * never raw fontSize/fontWeight (see mobile/CLAUDE.md). */
export function Text({ variant = "body", color = colors.text, style, children, ...rest }: AppTextProps) {
  return (
    <RNText style={[typography[variant], { color }, style]} {...rest}>
      {children}
    </RNText>
  );
}

export function Heading({
  level = 1,
  ...rest
}: Omit<AppTextProps, "variant"> & { level?: 1 | 2 | 3 }) {
  return <Text variant={`h${level}` as Variant} {...rest} />;
}
