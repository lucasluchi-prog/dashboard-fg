import type { RankingItem } from "@/api/types";
import { formatDecimal, formatInt, formatPercent } from "@/lib/formatters";

export default function RankingTable({ rows }: { rows: RankingItem[] }) {
  return (
    <div className="card overflow-hidden">
      <div className="max-h-[700px] overflow-auto">
        <table className="min-w-full divide-y divide-fg-navy/10 text-sm">
          <thead className="sticky top-0 bg-fg-navy text-fg-cream">
            <tr>
              <th className="w-12 px-3 py-2 text-left text-xs font-semibold uppercase">#</th>
              <th className="px-3 py-2 text-left text-xs font-semibold uppercase">Responsável</th>
              <th className="px-3 py-2 text-left text-xs font-semibold uppercase">Grupo</th>
              <th className="px-3 py-2 text-left text-xs font-semibold uppercase">Mês/Ano</th>
              <th className="px-3 py-2 text-right text-xs font-semibold uppercase">Pontos</th>
              <th className="px-3 py-2 text-right text-xs font-semibold uppercase">Atividades</th>
              <th className="px-3 py-2 text-right text-xs font-semibold uppercase">Aprov.</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-fg-navy/10 bg-white">
            {rows.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-6 text-center text-fg-navy/60">
                  Sem ranking para esse filtro.
                </td>
              </tr>
            ) : (
              rows.map((r) => (
                <tr key={`${r.responsavel}-${r.mes_ano}`}>
                  <td className="px-3 py-2 font-semibold">{r.posicao}</td>
                  <td className="px-3 py-2">{r.responsavel}</td>
                  <td className="px-3 py-2">{r.grupo}</td>
                  <td className="px-3 py-2">{r.mes_ano}</td>
                  <td className="px-3 py-2 text-right">{formatDecimal(r.pontos_totais)}</td>
                  <td className="px-3 py-2 text-right">{formatInt(r.total_atividades)}</td>
                  <td className="px-3 py-2 text-right">
                    {formatPercent(r.aproveitamento_medio / 100)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
