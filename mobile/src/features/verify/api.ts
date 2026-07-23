import { useMutation, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "../../lib/api/client";
import type { DoseEvent, DoseEventResult, PerPillResult } from "../../types/api";

interface RecordDoseEventInput {
  result: DoseEventResult;
  scheduled_window_id?: string | null;
  per_pill?: PerPillResult[];
  quality?: Record<string, unknown>;
  image_uri?: string | null;
}

/** FR-9: persists a result the on-device decision engine already reached —
 * this hook does not run recognition itself (that's the CV pipeline, Phase 1/2). */
export function useRecordDoseEvent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: RecordDoseEventInput) =>
      (await apiClient.post<DoseEvent>("/dose-events", data)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["dose-events"] }),
  });
}
