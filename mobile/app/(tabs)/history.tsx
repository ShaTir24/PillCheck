import { FlatList, StyleSheet, View } from "react-native";

import { Surface } from "../../src/components/ui/Surface";
import { Text } from "../../src/components/ui/Typography";
import { colors } from "../../src/constants/theme";
import { useDoseEvents } from "../../src/features/history/api";
import type { DoseEvent } from "../../src/types/api";

const RESULT_LABEL: Record<DoseEvent["result"], string> = {
  match: "Match",
  mismatch: "Mismatch",
  cannot_identify: "Could not identify",
  manual_taken: "Marked taken manually",
};

export default function HistoryScreen() {
  const { data: events, isLoading } = useDoseEvents();

  return (
    <Surface>
      {isLoading && <Text>Loading…</Text>}
      <FlatList
        data={events ?? []}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View style={styles.listItem}>
            <Text variant="bodyMedium">{RESULT_LABEL[item.result]}</Text>
            <Text variant="caption" color={colors.textMuted}>
              {new Date(item.ts).toLocaleString()}
            </Text>
          </View>
        )}
        ListEmptyComponent={!isLoading ? <Text>No verifications yet.</Text> : null}
      />
    </Surface>
  );
}

const styles = StyleSheet.create({
  listItem: {
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
});
