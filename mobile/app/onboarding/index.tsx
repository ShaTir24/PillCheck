import { router } from "expo-router";
import { useState } from "react";
import { Pressable, Text, TextInput, View } from "react-native";

import { useCreateProfile } from "../../src/features/onboarding/api";
import { styles } from "../../src/constants/styles";

// UF-4 first-run regimen setup, profile step only. The disclaimer + privacy
// explainer (PRD §8 compliance posture) and medication add flow are separate
// screens to build next under src/features/onboarding and src/features/regimen.
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
    <View style={styles.screen}>
      <Text style={styles.title}>Welcome to PillCheck</Text>
      <Text>
        PillCheck is an assistive tool, not a medical device. Always confirm with your
        pharmacist.
      </Text>
      <TextInput
        style={styles.input}
        placeholder="Your name"
        value={displayName}
        onChangeText={setDisplayName}
        accessibilityLabel="Your name"
      />
      <Pressable
        style={styles.button}
        onPress={handleSubmit}
        disabled={!displayName || createProfile.isPending}
        accessibilityRole="button"
      >
        <Text style={styles.buttonText}>
          {createProfile.isPending ? "Setting up…" : "Continue"}
        </Text>
      </Pressable>
      {createProfile.isError && <Text>Something went wrong. Try again.</Text>}
    </View>
  );
}
