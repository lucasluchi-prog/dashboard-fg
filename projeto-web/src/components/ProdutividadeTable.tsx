import type { ProdutividadeItem } from "@/api/types";
import { formatDecimal, formatInt, formatPercent } from "@/lib/formatters";

export default function ProdutividadeTable({ rows }: { rows: ProdutividadeItem[] }) {
  return (
    <div className="card overflow-hidden">
      <div className="max-h-[600px] overflow-auto">
        <table className="min-w-full divide-y divide-fg-navy/10 text-sm">
          <thead className="sticky top-0 bg-fg-navy text-fg-cream">
            <tr>
              <Th>Responsável</Th>
              <Th>Grupo</Th>
              <Th>Mês/Ano</Th>
              <Th className="text-right">Concluídas</Th>
              <Th className="text-right">Atribuídas</Th>
              <Th className="text-right">Taxa</Th>
              <Th className="text-right">No Prazo</Th>
              <Th className="text-right">Em Atraso</Th>
              <Th className="text-right">Ativ/Dia útil</Th>
            </tr>
          </thead>
          <tbody className="divide-y divide-fg-navy/10 bg-white">
            {rows.length === 0 ? (
              <tr>
                <td colSpan={9} className="px-4 py-6 text-center text-fg-navy/60">
                  Nenhum dado para os filtros atuais.
                </td>
              </tr>
            ) : (
              rows.map((r, i) => (
                <tr key={`${r.responsavel}-${r.mes_ano}-${i}`}>
                  <Td>{r.responsavel}</Td>
                  <Td>{r.grupo}</Td>
                  <Td>{r.mes_ano}</Td>
                  <Td className="text-right">{formatInt(r.total_concluidas)}</Td>
                  <Td className="text-right">{formatInt(r.total_atribuidas)}</Td>
                  <Td className="text-right">{formatPercent(r.taxa_conclusao)}</Td>
                  <Td className="text-right">{formatInt(r.prazos_no_prazo)}</Td>
                  <Td className="text-right">{formatInt(r.prazos_em_atraso)}</Td>
                  <Td className="text-right">{formatDecimal(r.atividades_por_dia_util)}</Td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function Th({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <th
      className={`whitespace-nowrap px-3 py-2 text-left text-xs font-semibold uppercase tracking-wide ${className}`}
    >
      {children}
    </th>
  );
}

function Td({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <td className={`whitespace-nowrap px-3 py-2 ${className}`}>{children}</td>;
}
