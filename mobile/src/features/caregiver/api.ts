import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "../../lib/api/client";
import type { CaregiverLink } from "../../types/api";

export function useCaregiverLinks() {
  return useQuery({
    queryKey: ["caregiver-links"],
    queryFn: async () => (await apiClient.get<CaregiverLink[]>("/caregiver-links")).data,
  });
}

export function useInviteCaregiver() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (scopes: string[] = ["summary:read"]) =>
      (await apiClient.post<CaregiverLink>("/caregiver-links", { scopes })).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["caregiver-links"] }),
  });
}

/** UF-5: one-tap revoke, always available to the subject. */
export function useRevokeCaregiverLink() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (linkId: string) =>
      (await apiClient.post<CaregiverLink>(`/caregiver-links/${linkId}/revoke`)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["caregiver-links"] }),
  });
}
