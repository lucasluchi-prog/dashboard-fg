type Props = {
  grupos: string[];
  mesesAno: string[];
  grupo: string;
  mesAno: string;
  onChange: (next: { grupo: string; mesAno: string }) => void;
};

export default function FiltersBar({
  grupos,
  mesesAno,
  grupo,
  mesAno,
  onChange,
}: Props) {
  return (
    <div className="card flex flex-wrap items-center gap-4 p-4">
      <div className="flex flex-col">
        <label className="text-xs font-medium text-fg-navy/70">Grupo</label>
        <select
          className="mt-1 rounded-md border border-fg-navy/20 bg-white px-3 py-2 text-sm"
          value={grupo}
          onChange={(e) => onChange({ grupo: e.target.value, mesAno })}
        >
          <option value="">Todos</option>
          {grupos.map((g) => (
            <option key={g} value={g}>
              {g}
            </option>
          ))}
        </select>
      </div>
      <div className="flex flex-col">
        <label className="text-xs font-medium text-fg-navy/70">Mês / Ano</label>
        <select
          className="mt-1 rounded-md border border-fg-navy/20 bg-white px-3 py-2 text-sm"
          value={mesAno}
          onChange={(e) => onChange({ grupo, mesAno: e.target.value })}
        >
          <option value="">Todos</option>
          {mesesAno.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
