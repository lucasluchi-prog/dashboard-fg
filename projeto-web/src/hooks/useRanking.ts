import { useQuery } from "@tanstack/react-query";

import { apiClient } from "@/api/client";
import type { RankingItem } from "@/api/types";

export function useRanking(filtros?: { grupo?: string; mesAno?: string }) {
  return useQuery<RankingItem[]>({
    queryKey: ["ranking", filtros],
    queryFn: async () => {
      const params: Record<string, string> = {};
      if (filtros?.grupo) params.grupo = filtros.grupo;
      if (filtros?.mesAno) params.mes_ano = filtros.mesAno;
      const { data } = await apiClient.get<RankingItem[]>("/api/ranking", { params });
      return data;
    },
  });
}
