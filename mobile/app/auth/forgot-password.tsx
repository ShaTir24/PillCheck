import { Link } from "expo-router";
import { useState } from "react";
import { StyleSheet, TextInput } from "react-native";

import { Button } from "../../src/components/ui/Button";
import { Surface } from "../../src/components/ui/Surface";
import { Heading, Text } from "../../src/components/ui/Typography";
import { fonts, palette, radius, surfaces } from "../../src/constants/theme";
import { useForgotPassword } from "../../src/features/auth/api";

const onPrimary = surfaces.primary.on;

export default function ForgotPasswordScreen() {
  const [email, setEmail] = useState("");
  const forgotPassword = useForgotPassword();

  return (
    <Surface variant="primary" celestial>
      <Heading level={1} color={onPrimary}>
        Reset your password
      </Heading>
      <Text color={onPrimary}>
        Enter your account email and we&apos;ll send a link to reset your password.
      </Text>
      <TextInput
        style={styles.input}
        placeholder="Email"
        placeholderTextColor={palette.graphite60}
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
        accessibilityLabel="Email"
        editable={!forgotPassword.isSuccess}
      />
      <Button
        label={forgotPassword.isPending ? "Sending…" : "Send reset link"}
        onPress={() => forgotPassword.mutate({ email })}
        disabled={!email || forgotPassword.isPending || forgotPassword.isSuccess}
      />
      {forgotPassword.isSuccess && (
        <Text color={onPrimary}>
          If that email is registered, a reset link is on its way.
        </Text>
      )}
      <Link href="/auth/login">
        <Text color={onPrimary}>Back to login</Text>
      </Link>
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
