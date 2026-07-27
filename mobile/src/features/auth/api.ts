import { useMutation } from "@tanstack/react-query";

import { apiClient } from "../../lib/api/client";
import { useAuthStore } from "../../store/useAuthStore";
import type { TokenPair } from "../../types/api";

interface Credentials {
  email: string;
  password: string;
}

function useAuthenticateMutation(path: "/auth/signup" | "/auth/login") {
  const setSession = useAuthStore((s) => s.setSession);
  return useMutation({
    mutationFn: async (data: Credentials) => (await apiClient.post<TokenPair>(path, data)).data,
    onSuccess: (tokens) => setSession(tokens.access_token, tokens.refresh_token),
  });
}

export function useSignup() {
  return useAuthenticateMutation("/auth/signup");
}

export function useLogin() {
  return useAuthenticateMutation("/auth/login");
}

export function useForgotPassword() {
  return useMutation({
    mutationFn: async (data: { email: string }) =>
      (await apiClient.post("/auth/forgot-password", data)).data,
  });
}

export function useResetPassword() {
  return useMutation({
    mutationFn: async (data: { token: string; new_password: string }) =>
      (await apiClient.post("/auth/reset-password", data)).data,
  });
}
