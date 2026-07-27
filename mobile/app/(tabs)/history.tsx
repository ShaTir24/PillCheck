import { FlatList, StyleSheet } from "react-native";

import { Card } from "../../src/components/ui/Card";
import { Surface } from "../../src/components/ui/Surface";
import { Heading, Text } from "../../src/components/ui/Typography";
import { colors, spacing } from "../../src/constants/theme";
import { useDoseEvents } from "../../src/features/history/api";
import type { DoseEvent } from "../../src/types/api";

// Color-coded per result (FR-9) — a decorative accent, never the only
// signal; the text label always carries the same information (WCAG 1.4.1).
const RESULT_STYLE: Record<DoseEvent["result"], { label: string; color: string }> = {
  match: { label: "Match", color: colors.success },
  mismatch: { label: "Mismatch", color: colors.danger },
  cannot_identify: { label: "Could not identify", color: colors.warning },
  manual_taken: { label: "Marked taken manually", color: colors.graphite60 },
};

export default function HistoryScreen() {
  const { data: events, isLoading } = useDoseEvents();

  return (
    <Surface>
      <Heading level={2}>Verification history</Heading>
      {isLoading && <Text color={colors.textMuted}>Loading…</Text>}
      <FlatList
        data={events ?? []}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        renderItem={({ item }) => {
          const { label, color } = RESULT_STYLE[item.result];
          return (
            <Card accentColor={color}>
              <Text variant="bodyMedium">{label}</Text>
              <Text variant="caption" color={colors.textMuted}>
                {new Date(item.ts).toLocaleString()}
              </Text>
            </Card>
          );
        }}
        ListEmptyComponent={
          !isLoading ? (
            <Text color={colors.textMuted}>No verifications yet — results will show up here.</Text>
          ) : null
        }
      />
    </Surface>
  );
}

const styles = StyleSheet.create({
  list: { gap: spacing.sm },
});
