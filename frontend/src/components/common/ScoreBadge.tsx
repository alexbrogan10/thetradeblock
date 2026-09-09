export function ScoreBadge({ score, label }: { score: number; label?: string }) {
  const color =
    score >= 75
      ? "bg-emerald-100 text-emerald-800"
      : score >= 55
      ? "bg-sky-100 text-sky-800"
      : score >= 40
      ? "bg-amber-100 text-amber-800"
      : "bg-rose-100 text-rose-800";
  return (
    <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ${color}`}>
      {label && <span className="font-normal opacity-70">{label}</span>}
      {score.toFixed(0)}
    </span>
  );
}

const ASSESSMENT_COLOR: Record<string, string> = {
  "Strongly Favorable": "bg-emerald-600 text-white",
  Favorable: "bg-emerald-100 text-emerald-800",
  "Potentially Favorable": "bg-sky-100 text-sky-800",
  Balanced: "bg-slate-200 text-slate-800",
  "Potentially Unfavorable": "bg-amber-100 text-amber-800",
  Unfavorable: "bg-rose-100 text-rose-800",
  "Strongly Unfavorable": "bg-rose-600 text-white",
};

export function AssessmentBadge({ assessment }: { assessment: string }) {
  return (
    <span
      className={`inline-flex items-center rounded px-3 py-1 text-sm font-semibold ${
        ASSESSMENT_COLOR[assessment] || "bg-slate-200 text-slate-800"
      }`}
    >
      {assessment}
    </span>
  );
}

const RISK_COLOR: Record<string, string> = {
  Low: "bg-emerald-100 text-emerald-800",
  Moderate: "bg-amber-100 text-amber-800",
  High: "bg-rose-100 text-rose-800",
};

export function RiskBadge({ level }: { level: string }) {
  return (
    <span className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-semibold ${RISK_COLOR[level] || ""}`}>
      {level} Risk
    </span>
  );
}
