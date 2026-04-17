import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/api/client";
import type { User } from "@/api/types";

export function useAuth() {
  const query = useQuery<User | null>({
    queryKey: ["me"],
    queryFn: async () => {
      try {
        const { data } = await apiClient.get<User>("/api/me");
        return data;
      } catch {
        return null;
      }
    },
    retry: false,
  });

  return {
    user: query.data ?? null,
    isLoading: query.isLoading,
    refetch: query.refetch,
  };
}
