import axios from "axios";

import { useAuthStore } from "../../store/useAuthStore";

// EXPO_PUBLIC_ prefix is required for Expo to inline the value into the client bundle.
const API_URL = process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export const apiClient = axios.create({ baseURL: API_URL });

apiClient.interceptors.request.use((config) => {
  const { accessToken, debugProfileId } = useAuthStore.getState();
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  } else if (debugProfileId) {
    // Local-dev-only escape hatch — mirrors backend/app/core/security.py's
    // X-Debug-Profile-Id bypass, which only exists while SUPABASE_JWT_SECRET
    // is unset. Never sent once a real access token is available.
    config.headers["X-Debug-Profile-Id"] = debugProfileId;
  }
  return config;
});
