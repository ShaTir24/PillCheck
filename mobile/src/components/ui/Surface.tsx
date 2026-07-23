import type { ReactNode } from "react";
import { StyleSheet, View, useWindowDimensions } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";

import { surfaces } from "../../constants/theme";
import { CelestialBackground } from "./CelestialBackground";

type SurfaceVariant = keyof typeof surfaces;

interface SurfaceProps {
  variant?: SurfaceVariant;
  /** Only meaningful on the `primary` (dark) surface — see CelestialBackground. */
  celestial?: boolean;
  children?: ReactNode;
}

/**
 * Screen-level background + safe-area wrapper. Use this instead of a bare
 * `View` at the root of a route so every screen picks colors from the theme
 * (and the celestial motif, where it belongs) consistently rather than each
 * screen hand-rolling its own background handling.
 */
export function Surface({ variant = "background", celestial = false, children }: SurfaceProps) {
  const { width, height } = useWindowDimensions();
  const { bg } = surfaces[variant];

  return (
    <SafeAreaView style={[styles.fill, { backgroundColor: bg }]}>
      {celestial && <CelestialBackground width={width} height={height} />}
      <View style={styles.content}>{children}</View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  fill: { flex: 1 },
  content: { flex: 1, padding: 20, gap: 12 },
});
