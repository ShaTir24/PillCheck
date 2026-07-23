import { FlatList, Text, View } from "react-native";

import { useDoseEvents } from "../../src/features/history/api";
import { styles } from "../../src/constants/styles";
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
    <View style={styles.screen}>
      {isLoading && <Text>Loading…</Text>}
      <FlatList
        data={events ?? []}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View style={styles.listItem}>
            <Text>{RESULT_LABEL[item.result]}</Text>
            <Text>{new Date(item.ts).toLocaleString()}</Text>
          </View>
        )}
        ListEmptyComponent={!isLoading ? <Text>No verifications yet.</Text> : null}
      />
    </View>
  );
}
