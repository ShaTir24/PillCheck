import { Tabs } from "expo-router";

// PRD §6 core functionality map: Home (F1/F3), Verify (F1/F2/F3), History (F5),
// Regimen (F4), Settings (F5 caregiver + F8 accessibility).
export default function TabsLayout() {
  return (
    <Tabs screenOptions={{ headerTitleAlign: "center" }}>
      <Tabs.Screen name="index" options={{ title: "Home" }} />
      <Tabs.Screen name="verify" options={{ title: "Verify" }} />
      <Tabs.Screen name="history" options={{ title: "History" }} />
      <Tabs.Screen name="regimen" options={{ title: "Regimen" }} />
      <Tabs.Screen name="settings" options={{ title: "Settings" }} />
    </Tabs>
  );
}
