import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { chartPalette } from "@/lib/theme";

type Row = {
  responsavel?: string;
  antes_8?: number;
  entre_8_14?: number;
  apos_14?: number;
};

export default function DistribuicaoHorarioChart({ data }: { data: Row[] }) {
  return (
    <div className="card p-4">
      <h3 className="mb-3 text-sm font-semibold text-fg-navy/80">
        Distribuição por horário
      </h3>
      <div className="h-72 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis dataKey="responsavel" tick={{ fontSize: 11 }} interval={0} angle={-30} textAnchor="end" height={70} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="antes_8" name="Antes 8h" fill={chartPalette[0]} stackId="a" />
            <Bar dataKey="entre_8_14" name="8h–14h" fill={chartPalette[1]} stackId="a" />
            <Bar dataKey="apos_14" name="Após 14h" fill={chartPalette[2]} stackId="a" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
