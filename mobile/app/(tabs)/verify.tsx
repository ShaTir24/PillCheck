import { CameraView, useCameraPermissions } from "expo-camera";
import { Pressable, Text, View } from "react-native";

import { useRecordDoseEvent } from "../../src/features/verify/api";
import { styles } from "../../src/constants/styles";

// FR-1/FR-2/FR-3 (guided capture, detection, recognition) and the on-device
// decision engine (FR-4) are the Phase 1/2 CV pipeline — not built here. This
// screen wires the capture UI and result-recording call so that pipeline has
// a real integration point to slot into (see .claude/skills/add-feature).
export default function VerifyScreen() {
  const [permission, requestPermission] = useCameraPermissions();
  const recordDoseEvent = useRecordDoseEvent();

  if (!permission) {
    return <View style={styles.screen} />;
  }

  if (!permission.granted) {
    return (
      <View style={styles.screen}>
        <Text>PillCheck needs camera access to verify your pills.</Text>
        <Pressable style={styles.button} onPress={requestPermission} accessibilityRole="button">
          <Text style={styles.buttonText}>Grant camera access</Text>
        </Pressable>
      </View>
    );
  }

  return (
    <View style={styles.screen}>
      <CameraView style={{ flex: 1, borderRadius: 12 }} facing="back" />
      {/* Placeholder for FR-1's quality-gate-driven auto-capture; wire up
          once the on-device blur/exposure checks land. */}
      <Pressable
        style={styles.button}
        accessibilityRole="button"
        disabled={recordDoseEvent.isPending}
        onPress={() =>
          recordDoseEvent.mutate({ result: "cannot_identify", quality: { placeholder: true } })
        }
      >
        <Text style={styles.buttonText}>
          {recordDoseEvent.isPending ? "Recording…" : "Simulate capture (dev)"}
        </Text>
      </Pressable>
    </View>
  );
}
