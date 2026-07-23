import { useState } from "react";
import { FlatList, Pressable, Text, TextInput, View } from "react-native";

import { useCreateMedication, useMedications } from "../../src/features/regimen/api";
import { styles } from "../../src/constants/styles";

// FR-5 regimen management. Reference-appearance picking ("Does your pill look
// like this?", UF-4) and schedule-window editing are the next slice to add
// here — this screen covers the medication list + bare create for now.
export default function RegimenScreen() {
  const { data: medications, isLoading } = useMedications();
  const createMedication = useCreateMedication();
  const [drugName, setDrugName] = useState("");

  return (
    <View style={styles.screen}>
      <Text style={styles.title}>Your medications</Text>
      {isLoading && <Text>Loading…</Text>}
      <FlatList
        data={medications ?? []}
        keyExtractor={(item) => item.id}
        renderItem={({ item }) => (
          <View style={styles.listItem}>
            <Text>
              {item.drug_name} {item.strength}
            </Text>
          </View>
        )}
        ListEmptyComponent={!isLoading ? <Text>No medications yet.</Text> : null}
      />
      <TextInput
        style={styles.input}
        placeholder="Medication name"
        value={drugName}
        onChangeText={setDrugName}
        accessibilityLabel="Medication name"
      />
      <Pressable
        style={styles.button}
        disabled={!drugName || createMedication.isPending}
        accessibilityRole="button"
        onPress={() =>
          createMedication.mutate(
            { drug_name: drugName, strength: null, form: null, ndc: null },
            { onSuccess: () => setDrugName("") }
          )
        }
      >
        <Text style={styles.buttonText}>Add medication</Text>
      </Pressable>
    </View>
  );
}
