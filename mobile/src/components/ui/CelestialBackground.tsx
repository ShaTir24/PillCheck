import Svg, { Circle } from "react-native-svg";
import { StyleSheet, View } from "react-native";

import { palette } from "../../constants/theme";

interface CelestialBackgroundProps {
  width: number;
  height: number;
}

// Decorative only — matches the style guide's dark-surface motif (faint
// orbit rings + scattered dots). Reserved for Graphite/dark surfaces (brand
// moments: onboarding, tab header) — never behind functional content, so it
// can't interfere with the WCAG AA contrast FR-8 requires there.
export function CelestialBackground({ width, height }: CelestialBackgroundProps) {
  const cx = width * 0.82;
  const cy = height * 0.18;

  return (
    <View style={StyleSheet.absoluteFill} pointerEvents="none">
      <Svg width={width} height={height}>
        <Circle cx={cx} cy={cy} r={70} stroke={palette.graphite80} strokeWidth={1} fill="none" opacity={0.5} />
        <Circle cx={cx} cy={cy} r={110} stroke={palette.graphite80} strokeWidth={1} fill="none" opacity={0.35} />
        <Circle cx={cx} cy={cy} r={150} stroke={palette.graphite80} strokeWidth={1} fill="none" opacity={0.2} />
        <Circle cx={cx} cy={cy} r={10} fill={palette.aquaMint} opacity={0.6} />

        {DOTS.map(([dx, dy, r, o], i) => (
          <Circle
            key={i}
            cx={width * dx}
            cy={height * dy}
            r={r}
            fill={palette.graphite20}
            opacity={o}
          />
        ))}
      </Svg>
    </View>
  );
}

// Fixed relative positions (fraction of width/height) so the scatter looks
// intentional rather than random on every render.
const DOTS: [number, number, number, number][] = [
  [0.1, 0.12, 1.5, 0.5],
  [0.22, 0.3, 1, 0.35],
  [0.06, 0.45, 1.5, 0.4],
  [0.35, 0.08, 1, 0.3],
  [0.5, 0.22, 1.5, 0.25],
  [0.65, 0.4, 1, 0.3],
  [0.85, 0.55, 1.5, 0.4],
  [0.15, 0.65, 1, 0.25],
  [0.4, 0.5, 1, 0.2],
  [0.92, 0.15, 1, 0.35],
];
