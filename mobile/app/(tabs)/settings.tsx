import { FlatList, Pressable, StyleSheet, View } from "react-native";

import { Button } from "../../src/components/ui/Button";
import { Surface } from "../../src/components/ui/Surface";
import { Heading, Text } from "../../src/components/ui/Typography";
import { colors, surfaces } from "../../src/constants/theme";
import {
  useCaregiverLinks,
  useInviteCaregiver,
  useRevokeCaregiverLink,
} from "../../src/features/caregiver/api";

// UF-5 caregiver link management: sharing state always visible to the
// subject, one-tap revoke. Accessibility toggles (FR-8: high-contrast, voice
// output) belong here too once a profile-update mutation is wired up.
export default function SettingsScreen() {
  const { data: links, isLoading } = useCaregiverLinks();
  const inviteCaregiver = useInviteCaregiver();
  const revokeCaregiverLink = useRevokeCaregiverLink();

  return (
    <Surface>
      <Heading level={2}>Caregiver sharing</Heading>
      {isLoading && <Text>Loading…</Text>}
      <FlatList
        data={links ?? []}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View style={styles.listItem}>
            <Text variant="bodyMedium">Status: {item.status}</Text>
            {item.status !== "revoked" && (
              <Pressable
                accessibilityRole="button"
                onPress={() => revokeCaregiverLink.mutate(item.id)}
              >
                <Text color={surfaces.danger.bg} variant="label">
                  Revoke
                </Text>
              </Pressable>
            )}
          </View>
        )}
        ListEmptyComponent={!isLoading ? <Text>No caregivers linked.</Text> : null}
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
  listItem: {
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    gap: 4,
  },
});
