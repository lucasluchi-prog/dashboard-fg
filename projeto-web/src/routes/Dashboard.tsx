import { useMemo, useState } from "react";

import DistribuicaoAssuntoChart from "@/components/DistribuicaoAssuntoChart";
import DistribuicaoHorarioChart from "@/components/DistribuicaoHorarioChart";
import FiltersBar from "@/components/FiltersBar";
import KpiCard from "@/components/KpiCard";
import ProdutividadeTable from "@/components/ProdutividadeTable";
import { useDashboard } from "@/hooks/useDashboard";
import { formatDecimal, formatInt, formatPercent } from "@/lib/formatters";

export default function Dashboard() {
  const { data, isLoading, error } = useDashboard();
  const [filtro, setFiltro] = useState({ grupo: "", mesAno: "" });

  const grupos = useMemo(
    () => Array.from(new Set((data?.produtividade ?? []).map((p) => p.grupo))).sort(),
    [data],
  );
  const mesesAno = useMemo(
    () =>
      Array.from(new Set((data?.produtividade ?? []).map((p) => p.mes_ano))).sort().reverse(),
    [data],
  );

  const rows = useMemo(() => {
    if (!data?.produtividade) return [];
    return data.produtividade.filter(
      (r) =>
        (!filtro.grupo || r.grupo === filtro.grupo) &&
        (!filtro.mesAno || r.mes_ano === filtro.mesAno),
    );
  }, [data, filtro]);

  const kpis = useMemo(() => {
    const total = rows.reduce((s, r) => s + r.total_concluidas, 0);
    const atrib = rows.reduce((s, r) => s + r.total_atribuidas, 0);
    const prazo = rows.reduce((s, r) => s + r.prazos_no_prazo, 0);
    const atraso = rows.reduce((s, r) => s + r.prazos_em_atraso, 0);
    const taxa = atrib > 0 ? total / atrib : 0;
    const ppd = atraso + prazo > 0 ? prazo / (atraso + prazo) : 0;
    return { total, atrib, taxa, ppd };
  }, [rows]);

  if (isLoading) return <div>Carregando…</div>;
  if (error) return <div className="text-red-600">Erro ao carregar dados.</div>;

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-end justify-between">
        <div>
          <h2 className="text-xl font-semibold">Produtividade</h2>
          <p className="text-xs text-fg-navy/60">
            Atualizado em {data?.updatedAt ?? "—"}
          </p>
        </div>
      </div>

      <FiltersBar
        grupos={grupos}
        mesesAno={mesesAno}
        grupo={filtro.grupo}
        mesAno={filtro.mesAno}
        onChange={setFiltro}
      />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          label="Concluídas"
          value={formatInt(kpis.total)}
          hint={`${formatInt(kpis.atrib)} atribuídas`}
          accent="navy"
        />
        <KpiCard label="Taxa de conclusão" value={formatPercent(kpis.taxa)} accent="mustard" />
        <KpiCard label="Cumprimento de prazo" value={formatPercent(kpis.ppd)} />
        <KpiCard
          label="Ativ/dia útil (média)"
          value={formatDecimal(
            rows.length > 0
              ? rows.reduce((s, r) => s + r.atividades_por_dia_util, 0) / rows.length
              : 0,
          )}
        />
      </div>

      <ProdutividadeTable rows={rows} />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <DistribuicaoHorarioChart data={data?.distribuicaoHorario ?? []} />
        <DistribuicaoAssuntoChart data={data?.distribuicaoAssunto ?? []} />
      </div>
    </div>
  );
}
