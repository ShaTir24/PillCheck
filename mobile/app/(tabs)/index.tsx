import { Link } from "expo-router";
import { Text, View } from "react-native";

import { useMyProfile } from "../../src/features/onboarding/api";
import { styles } from "../../src/constants/styles";

export default function HomeScreen() {
  const { data: profile, isLoading, isError } = useMyProfile();

  return (
    <View style={styles.screen}>
      {isLoading && <Text>Loading…</Text>}
      {isError && (
        <>
          <Text style={styles.title}>Welcome to PillCheck</Text>
          <Link href="/onboarding" style={styles.link}>
            Set up your profile
          </Link>
        </>
      )}
      {profile && (
        <>
          <Text style={styles.title}>Hi, {profile.display_name}</Text>
          {/* UF-1: "Verify tonight's dose (A + B)" CTA belongs here once the
              regimen/schedule-window lookup lands (FR-5 + decision engine). */}
          <Link href="/(tabs)/verify" style={styles.link}>
            Verify a dose →
          </Link>
        </>
      )}
    </View>
  );
}
