type Props = {
  label: string;
  value: string | number;
  hint?: string;
  accent?: "navy" | "mustard" | "neutral";
};

const accents = {
  navy: "border-fg-navy bg-fg-navy text-fg-cream",
  mustard: "border-fg-mustard bg-fg-mustard text-fg-navy-dark",
  neutral: "border-fg-navy/10 bg-white text-fg-navy",
};

export default function KpiCard({ label, value, hint, accent = "neutral" }: Props) {
  return (
    <div className={`card border p-4 ${accents[accent]}`}>
      <div className="text-xs font-medium uppercase tracking-wide opacity-70">{label}</div>
      <div className="mt-2 text-2xl font-semibold">{value}</div>
      {hint && <div className="mt-1 text-xs opacity-70">{hint}</div>}
    </div>
  );
}
