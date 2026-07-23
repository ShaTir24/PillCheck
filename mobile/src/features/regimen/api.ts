import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { apiClient } from "../../lib/api/client";
import type { Medication, Schedule } from "../../types/api";

export function useMedications() {
  return useQuery({
    queryKey: ["medications"],
    queryFn: async () => (await apiClient.get<Medication[]>("/medications")).data,
  });
}

export function useCreateMedication() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (data: Pick<Medication, "drug_name" | "strength" | "form" | "ndc">) =>
      (await apiClient.post<Medication>("/medications", data)).data,
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["medications"] }),
  });
}

export function useSchedules(medicationId: string) {
  return useQuery({
    queryKey: ["medications", medicationId, "schedules"],
    queryFn: async () =>
      (await apiClient.get<Schedule[]>(`/medications/${medicationId}/schedules`)).data,
    enabled: !!medicationId,
  });
}

export function useCreateSchedule(medicationId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (
      data: Pick<Schedule, "window_label" | "time_of_day" | "days_of_week" | "dose_count">
    ) => (await apiClient.post<Schedule>(`/medications/${medicationId}/schedules`, data)).data,
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["medications", medicationId, "schedules"] }),
  });
}
