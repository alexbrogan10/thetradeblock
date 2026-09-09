import { useState } from "react";
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

function TeamAnalysisCard({ analysis }: { analysis: TeamAnalysis }) {
  return (
    <Card
      title={analysis.team_name}
      actions={<AssessmentBadge assessment={analysis.assessment} />}
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
