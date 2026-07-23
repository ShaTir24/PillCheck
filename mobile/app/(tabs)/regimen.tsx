import { useState } from "react";
import { FlatList, StyleSheet, TextInput, View } from "react-native";

import { Button } from "../../src/components/ui/Button";
import { Surface } from "../../src/components/ui/Surface";
import { Heading, Text } from "../../src/components/ui/Typography";
import { colors, fonts, radius } from "../../src/constants/theme";
import { useCreateMedication, useMedications } from "../../src/features/regimen/api";

// FR-5 regimen management. Reference-appearance picking ("Does your pill look
// like this?", UF-4) and schedule-window editing are the next slice to add
// here — this screen covers the medication list + bare create for now.
export default function RegimenScreen() {
  const { data: medications, isLoading } = useMedications();
  const createMedication = useCreateMedication();
  const [drugName, setDrugName] = useState("");

  return (
    <Surface>
      <Heading level={2}>Your medications</Heading>
      {isLoading && <Text>Loading…</Text>}
      <FlatList
        data={medications ?? []}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View style={styles.listItem}>
            <Text variant="bodyMedium">
              {item.drug_name} {item.strength}
            </Text>
          </View>
        )}
        ListEmptyComponent={!isLoading ? <Text>No medications yet.</Text> : null}
      />
      <TextInput
        style={styles.input}
        placeholder="Medication name"
        placeholderTextColor={colors.textMuted}
        value={drugName}
        onChangeText={setDrugName}
        accessibilityLabel="Medication name"
      />
      <Button
        label="Add medication"
        disabled={!drugName || createMedication.isPending}
        onPress={() =>
          createMedication.mutate(
            { drug_name: drugName, strength: null, form: null, ndc: null },
            { onSuccess: () => setDrugName("") }
          )
        }
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
  input: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.sm,
    padding: 12,
    fontSize: 16,
    fontFamily: fonts.body,
    minHeight: 48,
    color: colors.text,
  },
});
