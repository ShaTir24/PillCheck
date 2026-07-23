import { router } from "expo-router";

import { Button } from "../../src/components/ui/Button";
import { Surface } from "../../src/components/ui/Surface";
import { Heading, Text } from "../../src/components/ui/Typography";
import { surfaces } from "../../src/constants/theme";
import { useMyProfile } from "../../src/features/onboarding/api";

const onPrimary = surfaces.primary.on;

export default function HomeScreen() {
  const { data: profile, isLoading, isError } = useMyProfile();

  return (
    <Surface variant="primary" celestial>
      {isLoading && <Text color={onPrimary}>Loading…</Text>}
      {isError && (
        <>
          <Heading level={1} color={onPrimary}>
            Welcome to PillCheck
          </Heading>
          <Button label="Set up your profile" onPress={() => router.push("/onboarding")} />
        </>
      )}
      {profile && (
        <>
          <Heading level={1} color={onPrimary}>
            Hi, {profile.display_name}
          </Heading>
          {/* UF-1: "Verify tonight's dose (A + B)" CTA belongs here once the
              regimen/schedule-window lookup lands (FR-5 + decision engine). */}
          <Button label="Verify a dose" onPress={() => router.push("/(tabs)/verify")} />
        </>
      )}
    </Surface>
  );
}
