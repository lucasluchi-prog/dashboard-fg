import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

import { chartPalette } from "@/lib/theme";

type Row = { assunto?: string; total?: number };

export default function DistribuicaoAssuntoChart({ data }: { data: Row[] }) {
  const top = data
    .filter((d) => d.assunto && d.total)
    .sort((a, b) => (b.total ?? 0) - (a.total ?? 0))
    .slice(0, 10);

  return (
    <div className="card p-4">
      <h3 className="mb-3 text-sm font-semibold text-fg-navy/80">
        Top 10 assuntos
      </h3>
      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={top}
              dataKey="total"
              nameKey="assunto"
              outerRadius={100}
              label={false}
            >
              {top.map((_, i) => (
                <Cell key={i} fill={chartPalette[i % chartPalette.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend verticalAlign="bottom" layout="horizontal" wrapperStyle={{ fontSize: 11 }} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
