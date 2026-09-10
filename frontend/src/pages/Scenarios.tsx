import { useEffect, useState } from "react";
import { Card } from "../components/common/Card";
import { AssessmentBadge, RiskBadge } from "../components/common/ScoreBadge";
import { api } from "../services/api";
import type { ScenarioComparisonRow, ScenarioSummary, Team } from "../types";

export function ScenariosPage() {
  const [scenarios, setScenarios] = useState<ScenarioSummary[]>([]);
  const [teams, setTeams] = useState<Team[]>([]);
  const [selected, setSelected] = useState<number[]>([]);
  const [perspectiveTeam, setPerspectiveTeam] = useState<number | null>(null);
  const [comparison, setComparison] = useState<ScenarioComparisonRow[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  function refresh() {
    api.listScenarios().then(setScenarios).catch(() => {});
  }

  useEffect(() => {
    refresh();
    api.getTeams().then(setTeams).catch(() => {});
  }, []);

  function toggleSelect(id: number) {
    setSelected((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  }

  async function handleDelete(id: number) {
    await api.deleteScenario(id);
    setSelected((prev) => prev.filter((x) => x !== id));
    refresh();
  }

  async function handleCompare() {
    if (!perspectiveTeam || selected.length < 2) return;
    setError(null);
    setComparison(null);
    try {
      const rows = await api.compareScenarios(selected, perspectiveTeam);
      setComparison(rows);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-900">Trade Simulator — Saved Scenarios</h1>
        <p className="text-sm text-slate-500">
          Scenarios are saved from the Trade Center with their full analysis frozen at save time
          (Section 40 — Auditability): if the models change later, saved scenarios do not
          silently change. Select two or more to compare from one team's perspective.
        </p>
      </header>

      <Card title="Saved Scenarios">
        {scenarios.length === 0 ? (
          <p className="text-sm text-slate-400">
            No scenarios saved yet. Build a trade in the Trade Center and click "Save Scenario."
          </p>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200 text-left text-xs uppercase text-slate-400">
                <th className="py-2">
                  <span className="sr-only">Select</span>
                </th>
                <th>Name</th>
                <th>Teams</th>
                <th>Assessment (A / B)</th>
                <th>Confidence</th>
                <th>Saved</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {scenarios.map((s) => (
                <tr key={s.id} className="border-b border-slate-100">
                  <td className="py-2">
                    <input type="checkbox" checked={selected.includes(s.id)} onChange={() => toggleSelect(s.id)} />
                  </td>
                  <td className="font-medium text-slate-800">{s.name}</td>
                  <td className="text-slate-500">
                    {s.team_a_name} vs {s.team_b_name}
                  </td>
                  <td className="space-x-1">
                    <AssessmentBadge assessment={s.team_a_assessment} />
                    <AssessmentBadge assessment={s.team_b_assessment} />
                  </td>
                  <td>{s.confidence}%</td>
                  <td className="text-xs text-slate-400">{new Date(s.created_at).toLocaleString()}</td>
                  <td>
                    <button onClick={() => handleDelete(s.id)} className="text-xs text-rose-600 hover:underline">
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Card>

      {scenarios.length > 0 && (
        <Card title="Compare Scenarios">
          <div className="mb-3 flex items-center gap-2">
            <label className="text-xs font-medium text-slate-500">Perspective team:</label>
            <select
              className="rounded border border-slate-300 px-2 py-1 text-sm"
              value={perspectiveTeam ?? ""}
              onChange={(e) => setPerspectiveTeam(e.target.value ? Number(e.target.value) : null)}
            >
              <option value="">Select…</option>
              {teams.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
            <button
              onClick={handleCompare}
              disabled={!perspectiveTeam || selected.length < 2}
              className="rounded bg-slate-800 px-3 py-1 text-xs font-semibold text-white disabled:opacity-40"
            >
              Compare Selected ({selected.length})
            </button>
          </div>
          {error && <p className="text-sm text-rose-600">{error}</p>}
          {comparison && (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-200 text-left text-xs uppercase text-slate-400">
                  <th className="py-2">Scenario</th>
                  <th>Assessment</th>
                  <th>Asset Value Δ</th>
                  <th>Draft Capital Δ</th>
                  <th>Financial Impact</th>
                  <th>Roster Fit</th>
                  <th>Risk</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {comparison.map((row) => (
                  <tr key={row.scenario_id} className="border-b border-slate-100">
                    <td className="py-2 font-medium text-slate-800">{row.name}</td>
                    {row.applicable ? (
                      <>
                        <td>
                          <AssessmentBadge assessment={row.assessment!} />
                        </td>
                        <td>{row.asset_value_delta}</td>
                        <td>{row.draft_capital_delta}</td>
                        <td>{row.financial_impact}</td>
                        <td>{row.roster_fit_score}</td>
                        <td>
                          <RiskBadge level={row.risk_level!} />
                        </td>
                        <td>{row.confidence}%</td>
                      </>
                    ) : (
                      <td colSpan={6} className="text-xs italic text-slate-400">
                        {row.note}
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </Card>
      )}
    </div>
  );
}
