import { router, useLocalSearchParams } from "expo-router";
import { useState } from "react";
import { StyleSheet, TextInput } from "react-native";

import { Button } from "../../src/components/ui/Button";
import { Surface } from "../../src/components/ui/Surface";
import { Heading, Text } from "../../src/components/ui/Typography";
import { fonts, palette, radius, surfaces } from "../../src/constants/theme";
import { useResetPassword } from "../../src/features/auth/api";

const onPrimary = surfaces.primary.on;

// Reached via the deep link the backend emails (pillcheck://auth/reset-password?token=...,
// see backend/app/api/v1/routers/auth.py _RESET_LINK_BASE). The token field stays editable
// since there's no email provider wired up yet (ADR-006) — a tester pastes it in by hand.
export default function ResetPasswordScreen() {
  const params = useLocalSearchParams<{ token?: string }>();
  const [token, setToken] = useState(params.token ?? "");
  const [newPassword, setNewPassword] = useState("");
  const resetPassword = useResetPassword();

  const handleSubmit = () => {
    resetPassword.mutate(
      { token, new_password: newPassword },
      { onSuccess: () => router.replace("/auth/login") }
    );
  };

  return (
    <Surface variant="primary" celestial>
      <Heading level={1} color={onPrimary}>
        Set a new password
      </Heading>
      <TextInput
        style={styles.input}
        placeholder="Reset token"
        placeholderTextColor={palette.graphite60}
        value={token}
        onChangeText={setToken}
        autoCapitalize="none"
        accessibilityLabel="Reset token"
      />
      <TextInput
        style={styles.input}
        placeholder="New password (min. 8 characters)"
        placeholderTextColor={palette.graphite60}
        value={newPassword}
        onChangeText={setNewPassword}
        secureTextEntry
        accessibilityLabel="New password"
      />
      <Button
        label={resetPassword.isPending ? "Saving…" : "Reset password"}
        onPress={handleSubmit}
        disabled={!token || newPassword.length < 8 || resetPassword.isPending}
      />
      {resetPassword.isError && (
        <Text color={surfaces.danger.bg}>That reset link is invalid or expired.</Text>
      )}
    </Surface>
  );
}

const styles = StyleSheet.create({
  input: {
    borderWidth: 1,
    borderColor: palette.graphite60,
    borderRadius: radius.sm,
    padding: 12,
    fontSize: 16,
    fontFamily: fonts.body,
    minHeight: 48,
    color: palette.warmCloud,
  },
});
