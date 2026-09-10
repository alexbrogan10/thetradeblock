import { useState, type ReactNode } from "react";
import { Card } from "../common/Card";
import { AssessmentBadge, RiskBadge } from "../common/ScoreBadge";
import type { TeamAnalysis, TradeAnalysisResult } from "../../types";

function Stat({ label, value, positiveGood = true }: { label: string; value: number; positiveGood?: boolean }) {
  const good = positiveGood ? value >= 0 : value <= 0;
  return (
    <div className="flex items-center justify-between border-b border-slate-100 py-1.5 text-sm last:border-b-0">
      <span className="text-slate-500">{label}</span>
      <span className={`font-semibold ${good ? "text-emerald-600" : "text-rose-600"}`}>
        {value > 0 ? "+" : ""}
        {value}
      </span>
    </div>
  );
}

const TIMELINE_COLOR: Record<string, string> = {
  "Win Now": "bg-orange-100 text-orange-800",
  Contender: "bg-emerald-100 text-emerald-800",
  Competitive: "bg-sky-100 text-sky-800",
  Developing: "bg-violet-100 text-violet-800",
  Rebuilding: "bg-slate-200 text-slate-700",
};

function TimelineBadge({ classification }: { classification: string }) {
  return (
    <span className={`inline-flex items-center rounded px-2 py-0.5 text-xs font-semibold ${TIMELINE_COLOR[classification] || ""}`}>
      {classification}
    </span>
  );
}

function RosterImpactTable({ impact }: { impact: { position: string; before: number; after: number; change: number }[] }) {
  if (impact.length === 0) {
    return <p className="text-sm text-slate-400">No positional strength changes from this trade.</p>;
  }
  return (
    <table className="w-full text-sm">
      <thead>
        <tr className="text-left text-xs uppercase text-slate-400">
          <th className="py-1">Position</th>
          <th className="text-right">Before</th>
          <th className="text-right">After</th>
          <th className="text-right">Change</th>
        </tr>
      </thead>
      <tbody>
        {impact.map((r) => (
          <tr key={r.position} className="border-t border-slate-100">
            <td className="py-1 font-medium text-slate-700">{r.position}</td>
            <td className="text-right text-slate-500">{r.before}</td>
            <td className="text-right text-slate-500">{r.after}</td>
            <td className={`text-right font-semibold ${r.change >= 0 ? "text-emerald-600" : "text-rose-600"}`}>
              {r.change > 0 ? "+" : ""}
              {r.change}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function ContractImpactPanel({
  impact,
}: {
  impact: TeamAnalysis["contract_impact"];
}) {
  return (
    <div className="space-y-1 text-sm">
      <Stat label="Cap Added This Year ($M)" value={impact.cap_added_this_year} positiveGood={false} />
      <Stat label="Cap Freed This Year ($M)" value={impact.cap_freed_this_year} />
      <Stat label="Dead Cap Incurred ($M)" value={-impact.dead_cap_incurred} />
      <Stat label="Net Cap Impact This Year ($M)" value={impact.net_cap_impact_this_year} />
      <Stat label="Net Multi-Year Impact (~3yr, $M)" value={impact.net_multi_year_impact} />
      <p className="pt-2 text-xs text-slate-500">{impact.note}</p>
    </div>
  );
}

function Expandable({ title, items }: { title: string; items: string[] }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="mt-3 border-t border-slate-100 pt-3">
      <button
        onClick={() => setOpen(!open)}
        className="text-xs font-semibold uppercase tracking-wide text-sky-700 hover:underline"
      >
        {open ? "▾" : "▸"} {title}
      </button>
      {open && (
        <ul className="mt-2 list-inside list-disc space-y-1 text-sm text-slate-600">
          {items.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

function ExpandableSection({ title, children }: { title: string; children: ReactNode }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="mt-3 border-t border-slate-100 pt-3">
      <button
        onClick={() => setOpen(!open)}
        className="text-xs font-semibold uppercase tracking-wide text-sky-700 hover:underline"
      >
        {open ? "▾" : "▸"} {title}
      </button>
      {open && <div className="mt-2">{children}</div>}
    </div>
  );
}

function TeamAnalysisCard({ analysis }: { analysis: TeamAnalysis }) {
  return (
    <Card
      title={analysis.team_name}
      actions={
        <div className="flex items-center gap-2">
          <TimelineBadge classification={analysis.competitive_window} />
          <AssessmentBadge assessment={analysis.assessment} />
        </div>
      }
    >
      <div className="grid grid-cols-2 gap-4">
        <div>
          <h4 className="mb-1 text-xs font-semibold uppercase text-slate-400">Receives</h4>
          <ul className="space-y-1 text-sm">
            {analysis.receives.map((a) => (
              <li key={`${a.asset_type}-${a.asset_id}`} className="flex justify-between gap-2">
                <span>{a.label}</span>
                <span className="flex-shrink-0 text-slate-400">{a.value}</span>
              </li>
            ))}
            {analysis.receives.length === 0 && <li className="text-slate-400">Nothing</li>}
          </ul>
        </div>
        <div>
          <h4 className="mb-1 text-xs font-semibold uppercase text-slate-400">Gives</h4>
          <ul className="space-y-1 text-sm">
            {analysis.gives.map((a) => (
              <li key={`${a.asset_type}-${a.asset_id}`} className="flex justify-between gap-2">
                <span>{a.label}</span>
                <span className="flex-shrink-0 text-slate-400">{a.value}</span>
              </li>
            ))}
            {analysis.gives.length === 0 && <li className="text-slate-400">Nothing</li>}
          </ul>
        </div>
      </div>

      <div className="mt-4">
        <Stat label="Asset Value Delta" value={analysis.asset_value_delta} />
        <Stat label="Roster Fit" value={Math.round(analysis.roster_fit_score - 50)} />
        <Stat label="Draft Capital Delta (pts)" value={Math.round(analysis.draft_capital_delta)} />
        <Stat label="Financial Impact ($M)" value={analysis.financial_impact} />
        <div className="flex items-center justify-between border-b border-slate-100 py-1.5 text-sm">
          <span className="text-slate-500">Risk</span>
          <RiskBadge level={analysis.risk_level} />
        </div>
        <Stat label="Timeline Alignment" value={Math.round(analysis.timeline_alignment - 50)} />
      </div>

      <Expandable title="Why?" items={[...analysis.positive_drivers, ...analysis.negative_drivers]} />
      <ExpandableSection title="Roster Impact (Before / After)">
        <RosterImpactTable impact={analysis.roster_impact} />
      </ExpandableSection>
      <ExpandableSection title="Contract Impact">
        <ContractImpactPanel impact={analysis.contract_impact} />
      </ExpandableSection>
      <Expandable title="Team Fit Explanation" items={analysis.team_fit_explanations} />
      <Expandable title="Risk Drivers" items={analysis.risk_drivers} />
      <Expandable title="Risk Mitigators" items={analysis.risk_mitigators} />
      <Expandable title="Opportunity Cost" items={analysis.opportunity_cost_notes.length ? analysis.opportunity_cost_notes : ["No draft capital surrendered."]} />
      <Expandable title="What Could Change This?" items={analysis.what_could_change_this} />
    </Card>
  );
}

export function TradeAnalysisView({ result }: { result: TradeAnalysisResult }) {
  return (
    <div className="space-y-4">
      <Card>
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <div className="text-sm font-semibold text-slate-500">Overall Confidence</div>
            <div className="text-2xl font-bold text-slate-900">{result.confidence}%</div>
          </div>
          <div className="max-w-md text-xs text-slate-500">
            <ul className="list-inside list-disc space-y-0.5">
              {result.confidence_limitations.map((l, i) => (
                <li key={i}>{l}</li>
              ))}
            </ul>
          </div>
        </div>
        <p className="mt-3 border-t border-slate-100 pt-3 text-xs italic text-slate-400">
          {result.disclaimer} Player model {result.player_valuation_model_version} · Draft
          pick model {result.draft_pick_model_version}.
        </p>
      </Card>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <TeamAnalysisCard analysis={result.team_a} />
        <TeamAnalysisCard analysis={result.team_b} />
      </div>
    </div>
  );
}
