import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "../../lib/api/client";
import type { Profile } from "../../types/api";

export function useMyProfile() {
  return useQuery({
    queryKey: ["profile", "me"],
    queryFn: async () => (await apiClient.get<Profile>("/profiles/me")).data,
    retry: false, // 404 is expected before the profile is created
  });
}

export function useCreateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: { display_name: string }) =>
      (await apiClient.post<Profile>("/profiles", data)).data,
    onSuccess: (profile) => {
      queryClient.setQueryData(["profile", "me"], profile);
    },
  });
}
