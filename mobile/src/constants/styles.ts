import { StyleSheet } from "react-native";

// PRD §8 accessibility NFR: WCAG 2.1 AA contrast, 48dp minimum touch target.
// Real theming (high-contrast mode per profile, dark mode) belongs in a
// ThemeProvider once FR-8's accessibility pass starts — this is the baseline.
export const colors = {
  background: "#FFFFFF",
  text: "#1A1A1A",
  primary: "#0B5FFF",
  danger: "#B3261E",
  warning: "#8A6100",
  success: "#146C2E",
};

export const styles = StyleSheet.create({
  screen: {
    flex: 1,
    padding: 20,
    gap: 12,
    backgroundColor: colors.background,
  },
  title: {
    fontSize: 22,
    fontWeight: "700",
    color: colors.text,
  },
  link: {
    color: colors.primary,
    fontSize: 17,
    minHeight: 48,
    textAlignVertical: "center",
  },
  input: {
    borderWidth: 1,
    borderColor: "#C4C4C4",
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    minHeight: 48,
  },
  button: {
    backgroundColor: colors.primary,
    borderRadius: 8,
    paddingVertical: 14,
    alignItems: "center",
    minHeight: 48,
    justifyContent: "center",
  },
  buttonText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "600",
  },
  listItem: {
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#EAEAEA",
  },
});
