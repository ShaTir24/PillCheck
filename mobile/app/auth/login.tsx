import { Link, router } from "expo-router";
import { useState } from "react";
import { StyleSheet, TextInput } from "react-native";

import { Button } from "../../src/components/ui/Button";
import { Surface } from "../../src/components/ui/Surface";
import { Heading, Text } from "../../src/components/ui/Typography";
import { fonts, palette, radius, surfaces } from "../../src/constants/theme";
import { useLogin } from "../../src/features/auth/api";

const onPrimary = surfaces.primary.on;

export default function LoginScreen() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const login = useLogin();

  const handleSubmit = () => {
    login.mutate(
      { email, password },
      { onSuccess: () => router.replace("/(tabs)") }
    );
  };

  return (
    <Surface variant="primary" celestial>
      <Heading level={1} color={onPrimary}>
        Welcome back
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
        placeholder="Password"
        placeholderTextColor={palette.graphite60}
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        accessibilityLabel="Password"
      />
      <Button
        label={login.isPending ? "Signing in…" : "Log in"}
        onPress={handleSubmit}
        disabled={!email || !password || login.isPending}
      />
      {login.isError && (
        <Text color={surfaces.danger.bg}>Invalid email or password.</Text>
      )}
      <Link href="/auth/forgot-password">
        <Text color={onPrimary}>Forgot password?</Text>
      </Link>
      <Link href="/auth/signup">
        <Text color={onPrimary}>Don&apos;t have an account? Sign up</Text>
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
