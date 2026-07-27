import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";

import { useAuthStore } from "../../store/useAuthStore";

// EXPO_PUBLIC_ prefix is required for Expo to inline the value into the client bundle.
const API_URL = process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export const apiClient = axios.create({ baseURL: API_URL });

apiClient.interceptors.request.use((config) => {
  const { accessToken } = useAuthStore.getState();
  if (accessToken) {
    config.headers.Authorization = `Bearer ${accessToken}`;
  }
  return config;
});

type RetryableConfig = InternalAxiosRequestConfig & { _retried?: boolean };

// Dedupes concurrent 401s onto a single in-flight refresh call.
let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const { refreshToken, setSession, clearSession } = useAuthStore.getState();
  if (!refreshToken) return null;
  try {
    // Bare axios, not apiClient — going through apiClient here would re-enter
    // this same response interceptor on a 401.
    const { data } = await axios.post(`${API_URL}/auth/refresh`, { refresh_token: refreshToken });
    setSession(data.access_token, data.refresh_token);
    return data.access_token as string;
  } catch {
    clearSession();
    return null;
  }
}

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const config = error.config as RetryableConfig | undefined;
    const isAuthEndpoint = config?.url?.startsWith("/auth/");
    if (error.response?.status !== 401 || !config || config._retried || isAuthEndpoint) {
      return Promise.reject(error);
    }
    config._retried = true;
    refreshPromise ??= refreshAccessToken();
    const newAccessToken = await refreshPromise;
    refreshPromise = null;
    if (!newAccessToken) {
      return Promise.reject(error);
    }
    config.headers.Authorization = `Bearer ${newAccessToken}`;
    return apiClient(config);
  }
);
