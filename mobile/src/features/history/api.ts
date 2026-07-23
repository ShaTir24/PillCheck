import { useQuery } from "@tanstack/react-query";

import { apiClient } from "../../lib/api/client";
import type { DoseEvent } from "../../types/api";

export function useDoseEvents(limit = 50) {
  return useQuery({
    queryKey: ["dose-events", limit],
    queryFn: async () =>
      (await apiClient.get<DoseEvent[]>("/dose-events", { params: { limit } })).data,
  });
}
