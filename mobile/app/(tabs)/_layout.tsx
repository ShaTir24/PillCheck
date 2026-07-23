import { Tabs } from "expo-router";

import { colors, fonts, palette } from "../../src/constants/theme";

// PRD §6 core functionality map: Home (F1/F3), Verify (F1/F2/F3), History (F5),
// Regimen (F4), Settings (F5 caregiver + F8 accessibility).
export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerTitleAlign: "center",
        headerStyle: { backgroundColor: palette.graphite },
        headerTitleStyle: { color: colors.background, fontFamily: fonts.headingSemiBold },
        headerTintColor: colors.background,
        tabBarActiveTintColor: palette.operationalMint,
        tabBarInactiveTintColor: palette.graphite60,
        tabBarStyle: { backgroundColor: colors.surface, borderTopColor: colors.border },
        tabBarLabelStyle: { fontFamily: fonts.bodyMedium, fontSize: 12 },
      }}
    >
      <Tabs.Screen name="index" options={{ title: "Home" }} />
      <Tabs.Screen name="verify" options={{ title: "Verify" }} />
      <Tabs.Screen name="history" options={{ title: "History" }} />
      <Tabs.Screen name="regimen" options={{ title: "Regimen" }} />
      <Tabs.Screen name="settings" options={{ title: "Settings" }} />
    </Tabs>
  );
}
