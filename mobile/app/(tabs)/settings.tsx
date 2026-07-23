import { FlatList, Pressable, Text, View } from "react-native";

import {
  useCaregiverLinks,
  useInviteCaregiver,
  useRevokeCaregiverLink,
} from "../../src/features/caregiver/api";
import { styles } from "../../src/constants/styles";

// UF-5 caregiver link management: sharing state always visible to the
// subject, one-tap revoke. Accessibility toggles (FR-8: high-contrast, voice
// output) belong here too once a profile-update mutation is wired up.
export default function SettingsScreen() {
  const { data: links, isLoading } = useCaregiverLinks();
  const inviteCaregiver = useInviteCaregiver();
  const revokeCaregiverLink = useRevokeCaregiverLink();

  return (
    <View style={styles.screen}>
      <Text style={styles.title}>Caregiver sharing</Text>
      {isLoading && <Text>Loading…</Text>}
      <FlatList
        data={links ?? []}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View style={styles.listItem}>
            <Text>Status: {item.status}</Text>
            {item.status !== "revoked" && (
              <Pressable
                accessibilityRole="button"
                onPress={() => revokeCaregiverLink.mutate(item.id)}
              >
                <Text style={{ color: "#B3261E" }}>Revoke</Text>
              </Pressable>
            )}
          </View>
        )}
        ListEmptyComponent={!isLoading ? <Text>No caregivers linked.</Text> : null}
      />
      <Pressable
        style={styles.button}
        accessibilityRole="button"
        disabled={inviteCaregiver.isPending}
        onPress={() => inviteCaregiver.mutate(["summary:read"])}
      >
        <Text style={styles.buttonText}>Invite a caregiver</Text>
      </Pressable>
    </View>
  );
}
