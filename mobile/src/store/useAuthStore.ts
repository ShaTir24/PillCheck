import * as SecureStore from "expo-secure-store";
import { Platform } from "react-native";
import { create } from "zustand";

const ACCESS_TOKEN_KEY = "pillcheck.accessToken";
const REFRESH_TOKEN_KEY = "pillcheck.refreshToken";

// expo-secure-store has no web implementation (it's a native keychain/keystore
// wrapper) — this app also ships a web target (see mobile/CLAUDE.md CORS note),
// so web falls back to localStorage instead of crashing.
const tokenStorage = {
  async get(key: string): Promise<string | null> {
    return Platform.OS === "web" ? localStorage.getItem(key) : SecureStore.getItemAsync(key);
  },
  async set(key: string, value: string): Promise<void> {
    if (Platform.OS === "web") {
      localStorage.setItem(key, value);
      return;
    }
    await SecureStore.setItemAsync(key, value);
  },
  async delete(key: string): Promise<void> {
    if (Platform.OS === "web") {
      localStorage.removeItem(key);
      return;
    }
    await SecureStore.deleteItemAsync(key);
  },
};

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  /** False until hydrate() has loaded any persisted session from storage. */
  isHydrated: boolean;
  setSession: (accessToken: string, refreshToken: string) => void;
  clearSession: () => void;
  hydrate: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  refreshToken: null,
  isHydrated: false,
  setSession: (accessToken, refreshToken) => {
    set({ accessToken, refreshToken });
    tokenStorage.set(ACCESS_TOKEN_KEY, accessToken);
    tokenStorage.set(REFRESH_TOKEN_KEY, refreshToken);
  },
  clearSession: () => {
    set({ accessToken: null, refreshToken: null });
    tokenStorage.delete(ACCESS_TOKEN_KEY);
    tokenStorage.delete(REFRESH_TOKEN_KEY);
  },
  hydrate: async () => {
    const [accessToken, refreshToken] = await Promise.all([
      tokenStorage.get(ACCESS_TOKEN_KEY),
      tokenStorage.get(REFRESH_TOKEN_KEY),
    ]);
    set({ accessToken, refreshToken, isHydrated: true });
  },
}));
