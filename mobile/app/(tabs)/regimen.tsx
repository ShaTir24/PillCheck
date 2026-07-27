import { useState } from "react";
import { FlatList, StyleSheet, TextInput } from "react-native";

import { Button } from "../../src/components/ui/Button";
import { Card } from "../../src/components/ui/Card";
import { Surface } from "../../src/components/ui/Surface";
import { Heading, Text } from "../../src/components/ui/Typography";
import { colors, fonts, radius, spacing } from "../../src/constants/theme";
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
      {isLoading && <Text color={colors.textMuted}>Loading…</Text>}
      <FlatList
        data={medications ?? []}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.list}
        renderItem={({ item }) => (
          <Card>
            <Text variant="bodyMedium">
              {item.drug_name}
              {item.strength ? ` ${item.strength}` : ""}
            </Text>
          </Card>
        )}
        ListEmptyComponent={
          !isLoading ? (
            <Text color={colors.textMuted}>No medications yet — add your first one below.</Text>
          ) : null
        }
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
  list: { gap: spacing.sm },
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
