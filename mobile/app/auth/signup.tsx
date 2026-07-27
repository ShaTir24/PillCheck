import { Link, router } from "expo-router";
import { useState } from "react";
import { StyleSheet, TextInput } from "react-native";

import { Button } from "../../src/components/ui/Button";
import { Surface } from "../../src/components/ui/Surface";
import { Heading, Text } from "../../src/components/ui/Typography";
import { fonts, palette, radius, surfaces } from "../../src/constants/theme";
import { useSignup } from "../../src/features/auth/api";

const onPrimary = surfaces.primary.on;

export default function SignupScreen() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const signup = useSignup();

  const handleSubmit = () => {
    signup.mutate(
      { email, password },
      { onSuccess: () => router.replace("/(tabs)") }
    );
  };

  return (
    <Surface variant="primary" celestial>
      <Heading level={1} color={onPrimary}>
        Create your account
      </Heading>
      <TextInput
        style={styles.input}
        placeholder="Email"
        placeholderTextColor={palette.graphite60}
        value={email}
        onChangeText={setEmail}
        autoCapitalize="none"
        keyboardType="email-address"
        accessibilityLabel="Email"
      />
      <TextInput
        style={styles.input}
        placeholder="Password (min. 8 characters)"
        placeholderTextColor={palette.graphite60}
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        accessibilityLabel="Password"
      />
      <Button
        label={signup.isPending ? "Creating account…" : "Sign up"}
        onPress={handleSubmit}
        disabled={!email || password.length < 8 || signup.isPending}
      />
      {signup.isError && (
        <Text color={surfaces.danger.bg}>
          Couldn&apos;t create that account. Email may already be registered.
        </Text>
      )}
      <Link href="/auth/login">
        <Text color={onPrimary}>Already have an account? Log in</Text>
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
