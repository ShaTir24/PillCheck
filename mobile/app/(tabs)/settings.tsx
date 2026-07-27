import { useQueryClient } from "@tanstack/react-query";
import { FlatList, StyleSheet } from "react-native";

import { Button } from "../../src/components/ui/Button";
import { Card } from "../../src/components/ui/Card";
import { Surface } from "../../src/components/ui/Surface";
import { Heading, Text } from "../../src/components/ui/Typography";
import { colors, spacing } from "../../src/constants/theme";
import {
  useCaregiverLinks,
  useInviteCaregiver,
  useRevokeCaregiverLink,
} from "../../src/features/caregiver/api";
import { useMyProfile } from "../../src/features/onboarding/api";
import { useAuthStore } from "../../src/store/useAuthStore";

// UF-5 caregiver link management: sharing state always visible to the
// subject, one-tap revoke. Accessibility toggles (FR-8: high-contrast, voice
// output) belong here too once a profile-update mutation is wired up.
export default function SettingsScreen() {
  const { data: profile } = useMyProfile();
  const { data: links, isLoading } = useCaregiverLinks();
  const inviteCaregiver = useInviteCaregiver();
  const revokeCaregiverLink = useRevokeCaregiverLink();
  const clearSession = useAuthStore((s) => s.clearSession);
  const queryClient = useQueryClient();

  const handleLogout = () => {
    clearSession();
    queryClient.clear();
  };

  return (
    <Surface>
      <Heading level={2}>Account</Heading>
      <Card>
        <Text variant="bodyMedium">{profile?.display_name ?? "…"}</Text>
        <Button label="Log out" variant="danger" onPress={handleLogout} />
      </Card>

      <Heading level={2}>Caregiver sharing</Heading>
      {isLoading && <Text color={colors.textMuted}>Loading…</Text>}
      <FlatList
        data={links ?? []}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        renderItem={({ item }) => (
          <Card>
            <Text variant="bodyMedium">Status: {item.status}</Text>
            {item.status !== "revoked" && (
              <Button
                label={revokeCaregiverLink.isPending ? "Revoking…" : "Revoke"}
                variant="danger"
                onPress={() => revokeCaregiverLink.mutate(item.id)}
              />
            )}
          </Card>
        )}
        ListEmptyComponent={
          !isLoading ? <Text color={colors.textMuted}>No caregivers linked.</Text> : null
        }
      />
      <Button
        label="Invite a caregiver"
        variant="operational"
        disabled={inviteCaregiver.isPending}
        onPress={() => inviteCaregiver.mutate(["summary:read"])}
      />
    </Surface>
  );
}

const styles = StyleSheet.create({
  list: { gap: spacing.sm },
});
