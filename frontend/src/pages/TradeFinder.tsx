import { useEffect, useState } from "react";
import { Card } from "../components/common/Card";
import { RiskBadge, ScoreBadge } from "../components/common/ScoreBadge";
import { api } from "../services/api";
import type { Team, TradeTarget } from "../types";

const POSITIONS = ["QB", "RB", "WR", "TE", "OT", "IOL", "EDGE", "DT", "LB", "CB", "S", "K", "P", "LS"];

export function TradeFinderPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [teamId, setTeamId] = useState<number | null>(null);
  const [position, setPosition] = useState("WR");
  const [maxCost, setMaxCost] = useState<string>("");
  const [agePref, setAgePref] = useState<string>("");
  const [riskTolerance, setRiskTolerance] = useState<string>("");
  const [results, setResults] = useState<TradeTarget[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getTeams().then(setTeams).catch(() => {});
  }, []);

  async function handleSearch() {
    if (!teamId) return;
    setLoading(true);
    setError(null);
    try {
      const targets = await api.findTradeTargets({
        team_id: teamId,
        position,
        max_acquisition_cost: maxCost ? Number(maxCost) : undefined,
        age_preference: (agePref || undefined) as "young" | "prime" | "veteran" | undefined,
        risk_tolerance: (riskTolerance || undefined) as "Low" | "Moderate" | "High" | undefined,
      });
      setResults(targets);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-900">Trade Finder</h1>
        <p className="text-sm text-slate-500">
          Analytical matches for a stated need — not predictions that a specific trade will
          actually happen.
        </p>
      </header>

      <Card title="Search Criteria">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3 lg:grid-cols-5">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">Team</label>
            <select
              className="w-full rounded border border-slate-300 px-2 py-1.5 text-sm"
              value={teamId ?? ""}
              onChange={(e) => setTeamId(e.target.value ? Number(e.target.value) : null)}
            >
              <option value="">Select…</option>
              {teams.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">Position Needed</label>
            <select
              className="w-full rounded border border-slate-300 px-2 py-1.5 text-sm"
              value={position}
              onChange={(e) => setPosition(e.target.value)}
            >
              {POSITIONS.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">Max Acquisition Cost (0-100)</label>
            <input
              type="number"
              min={0}
              max={100}
              className="w-full rounded border border-slate-300 px-2 py-1.5 text-sm"
              value={maxCost}
              onChange={(e) => setMaxCost(e.target.value)}
              placeholder="Any"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">Age Preference</label>
            <select
              className="w-full rounded border border-slate-300 px-2 py-1.5 text-sm"
              value={agePref}
              onChange={(e) => setAgePref(e.target.value)}
            >
              <option value="">Any</option>
              <option value="young">Young (≤25)</option>
              <option value="prime">Prime (26-29)</option>
              <option value="veteran">Veteran (30+)</option>
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">Risk Tolerance</label>
            <select
              className="w-full rounded border border-slate-300 px-2 py-1.5 text-sm"
              value={riskTolerance}
              onChange={(e) => setRiskTolerance(e.target.value)}
            >
              <option value="">Any</option>
              <option value="Low">Low only</option>
              <option value="Moderate">Low or Moderate</option>
              <option value="High">Any (including High)</option>
            </select>
          </div>
        </div>
        <div className="mt-4 flex justify-center">
          <button
            onClick={handleSearch}
            disabled={!teamId || loading}
            className="rounded bg-slate-900 px-6 py-2 text-sm font-semibold text-white shadow disabled:opacity-40"
          >
            {loading ? "Searching…" : "Find Potential Targets"}
          </button>
        </div>
      </Card>

      {error && (
        <div className="rounded border border-rose-300 bg-rose-50 p-3 text-sm text-rose-800">{error}</div>
      )}

      {results && (
        <Card title={`Potential Targets (${results.length})`}>
          {results.length === 0 ? (
            <p className="text-sm text-slate-400">No matches found for these criteria.</p>
          ) : (
            <div className="divide-y divide-slate-100">
              {results.map((r, i) => (
                <div key={r.player_id} className="flex flex-wrap items-center justify-between gap-2 py-3">
                  <div>
                    <div className="font-medium text-slate-800">
                      {i + 1}. {r.name} <span className="text-xs text-slate-400">{r.position} · {r.team} · Age {r.age}</span>
                    </div>
                    <div className="mt-1 text-xs text-slate-500">{r.fit_explanation}</div>
                    <div className="mt-1 text-xs text-slate-400">{r.contract_fit_note}</div>
                  </div>
                  <div className="flex flex-shrink-0 items-center gap-2">
                    <ScoreBadge score={r.fit_score} label="Fit" />
                    <RiskBadge level={r.risk_level} />
                    <span className="text-xs text-slate-500">
                      Est. cost: {r.estimated_cost_low} – {r.estimated_cost_high} ({r.cost_confidence} confidence)
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      )}
    </div>
  );
}
