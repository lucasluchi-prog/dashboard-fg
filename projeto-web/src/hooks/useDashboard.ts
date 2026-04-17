import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/api/client";
import type { DashboardData } from "@/api/types";

export function useDashboard() {
  return useQuery<DashboardData>({
    queryKey: ["dashboard"],
    queryFn: async () => {
      const { data } = await apiClient.get<DashboardData>("/api/dashboard");
      return data;
    },
  });
}
