import { CameraView, useCameraPermissions } from "expo-camera";
import { StyleSheet } from "react-native";

import { Button } from "../../src/components/ui/Button";
import { Surface } from "../../src/components/ui/Surface";
import { Heading, Text } from "../../src/components/ui/Typography";
import { colors, radius } from "../../src/constants/theme";
import { useRecordDoseEvent } from "../../src/features/verify/api";

// FR-1/FR-2/FR-3 (guided capture, detection, recognition) and the on-device
// decision engine (FR-4) are the Phase 1/2 CV pipeline — not built here. This
// screen wires the capture UI and result-recording call so that pipeline has
// a real integration point to slot into (see .claude/skills/add-feature).
export default function VerifyScreen() {
  const [permission, requestPermission] = useCameraPermissions();
  const recordDoseEvent = useRecordDoseEvent();

  if (!permission) {
    return <Surface />;
  }

  if (!permission.granted) {
    return (
      <Surface>
        <Heading level={2}>Camera access needed</Heading>
        <Text color={colors.textMuted}>
          PillCheck needs camera access to verify your pills against tonight&apos;s dose.
        </Text>
        <Button label="Grant camera access" onPress={requestPermission} />
      </Surface>
    );
  }

  return (
    <Surface>
      <Heading level={2}>Verify your dose</Heading>
      <CameraView style={styles.camera} facing="back" />
      {/* Placeholder for FR-1's quality-gate-driven auto-capture; wire up
          once the on-device blur/exposure checks land. */}
      <Button
        label={recordDoseEvent.isPending ? "Recording…" : "Simulate capture (dev)"}
        variant="operational"
        disabled={recordDoseEvent.isPending}
        onPress={() =>
          recordDoseEvent.mutate({ result: "cannot_identify", quality: { placeholder: true } })
        }
      />
    </Surface>
  );
}

const styles = StyleSheet.create({
  camera: { flex: 1, borderRadius: radius.lg },
});
