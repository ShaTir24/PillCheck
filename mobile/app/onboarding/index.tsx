import { router } from "expo-router";
import { useState } from "react";
import { StyleSheet, TextInput } from "react-native";

import { Button } from "../../src/components/ui/Button";
import { Surface } from "../../src/components/ui/Surface";
import { Heading, Text } from "../../src/components/ui/Typography";
import { fonts, palette, radius, surfaces } from "../../src/constants/theme";
import { useCreateProfile } from "../../src/features/onboarding/api";

const onPrimary = surfaces.primary.on;

// UF-4 first-run regimen setup, profile step only. The medication add flow
// is a separate screen to build next under src/features/regimen.
export default function OnboardingScreen() {
  const [displayName, setDisplayName] = useState("");
  const createProfile = useCreateProfile();

  const handleSubmit = () => {
    createProfile.mutate(
      { display_name: displayName },
      { onSuccess: () => router.replace("/(tabs)") }
    );
  };

  return (
    <Surface variant="primary" celestial>
      <Heading level={1} color={onPrimary}>
        Welcome to PillCheck
      </Heading>
      <Text color={onPrimary}>
        PillCheck is an assistive tool, not a medical device. Always confirm with your
        pharmacist.
      </Text>
      <TextInput
        style={styles.input}
        placeholder="Your name"
        placeholderTextColor={palette.graphite60}
        value={displayName}
        onChangeText={setDisplayName}
        accessibilityLabel="Your name"
      />
      <Button
        label={createProfile.isPending ? "Setting up…" : "Continue"}
        onPress={handleSubmit}
        disabled={!displayName || createProfile.isPending}
      />
      {createProfile.isError && (
        <Text color={surfaces.danger.bg}>Something went wrong. Try again.</Text>
      )}
    </Surface>
  );
}

const styles = StyleSheet.create({
  input: {
    borderWidth: 1,
    borderColor: palette.graphite60,
    borderRadius: radius.sm,
    padding: 12,
    fontSize: 16,
    fontFamily: fonts.body,
    minHeight: 48,
    color: palette.warmCloud,
  },
});
