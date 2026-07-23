import { create } from "zustand";

interface AuthState {
  accessToken: string | null;
  profileId: string | null;
  /** Local-dev-only, see src/lib/api/client.ts. Never set in a real build. */
  debugProfileId: string | null;
  setSession: (accessToken: string, profileId: string) => void;
  setDebugProfileId: (id: string | null) => void;
  clearSession: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  profileId: null,
  debugProfileId: null,
  setSession: (accessToken, profileId) => set({ accessToken, profileId }),
  setDebugProfileId: (debugProfileId) => set({ debugProfileId }),
  clearSession: () => set({ accessToken: null, profileId: null }),
}));
