import { useMemo, useState } from "react";

import FiltersBar from "@/components/FiltersBar";
import RankingTable from "@/components/RankingTable";
import { useRanking } from "@/hooks/useRanking";

export default function Ranking() {
  const [filtro, setFiltro] = useState({ grupo: "", mesAno: "" });
  const { data = [], isLoading } = useRanking({
    grupo: filtro.grupo || undefined,
    mesAno: filtro.mesAno || undefined,
  });

  const grupos = useMemo(
    () => Array.from(new Set(data.map((r) => r.grupo))).sort(),
    [data],
  );
  const mesesAno = useMemo(
    () => Array.from(new Set(data.map((r) => r.mes_ano))).sort().reverse(),
    [data],
  );

  return (
    <div className="flex flex-col gap-4">
      <div>
        <h2 className="text-xl font-semibold">Ranking Gamificado</h2>
        <p className="text-xs text-fg-navy/60">
          Pontos por assunto × fator de aproveitamento.
        </p>
      </div>

      <FiltersBar
        grupos={grupos}
        mesesAno={mesesAno}
        grupo={filtro.grupo}
        mesAno={filtro.mesAno}
        onChange={setFiltro}
      />

      {isLoading ? <div>Carregando…</div> : <RankingTable rows={data} />}
    </div>
  );
}
