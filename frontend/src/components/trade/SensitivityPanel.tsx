import { useState } from "react";
import { Card } from "../common/Card";
import { AssessmentBadge } from "../common/ScoreBadge";
import { api } from "../../services/api";
import type { SensitivityResult } from "../../types";

export function SensitivityPanel({
  teamAId,
  teamAPlayers,
  teamAPicks,
  teamBId,
  teamBPlayers,
  teamBPicks,
}: {
  teamAId: number;
  teamAPlayers: number[];
  teamAPicks: number[];
  teamBId: number;
  teamBPlayers: number[];
  teamBPicks: number[];
}) {
  const [perspective, setPerspective] = useState<number>(teamAId);
  const [result, setResult] = useState<SensitivityResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function run() {
    setLoading(true);
    setError(null);
    try {
      const res = await api.getSensitivity({
        team_a: { team_id: teamAId, player_ids: teamAPlayers, draft_pick_ids: teamAPicks },
        team_b: { team_id: teamBId, player_ids: teamBPlayers, draft_pick_ids: teamBPicks },
        perspective_team_id: perspective,
      });
      setResult(res);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <Card title="Sensitivity Analysis">
      <p className="mb-3 text-xs text-slate-500">
        Re-runs the trade analysis under different assumptions to show what would need to be
        true for the recommendation to change (Section 28-29). Not a prediction of actual
        performance.
      </p>
      <div className="mb-3 flex items-center gap-2">
        <label className="text-xs font-medium text-slate-500">Perspective:</label>
        <select
          className="rounded border border-slate-300 px-2 py-1 text-sm"
          value={perspective}
          onChange={(e) => setPerspective(Number(e.target.value))}
        >
          <option value={teamAId}>Team A</option>
          <option value={teamBId}>Team B</option>
        </select>
        <button
          onClick={run}
          disabled={loading}
          className="rounded bg-slate-800 px-3 py-1 text-xs font-semibold text-white disabled:opacity-40"
        >
          {loading ? "Running…" : "Run Sensitivity"}
        </button>
      </div>

      {error && <p className="text-sm text-rose-600">{error}</p>}

      {result && (
        <div className="space-y-4">
          <div>
            <h4 className="mb-1 text-xs font-semibold uppercase text-slate-400">
              Performance Sensitivity
            </h4>
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
              {result.performance_sensitivity.map((p) => (
                <div key={p.label} className="rounded border border-slate-200 p-2 text-sm">
                  <div className="mb-1 text-xs text-slate-500">{p.label}</div>
                  <AssessmentBadge assessment={p.assessment} />
                  <div className="mt-1 text-xs text-slate-400">
                    Asset value delta: {p.asset_value_delta > 0 ? "+" : ""}
                    {p.asset_value_delta}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h4 className="mb-1 text-xs font-semibold uppercase text-slate-400">
              Draft-Pick Model Sensitivity
            </h4>
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
              {result.draft_model_sensitivity.map((p) => (
                <div key={p.label} className="rounded border border-slate-200 p-2 text-sm">
                  <div className="mb-1 text-xs text-slate-500">{p.label}</div>
                  <AssessmentBadge assessment={p.assessment} />
                </div>
              ))}
            </div>
          </div>

          <div>
            <h4 className="mb-1 text-xs font-semibold uppercase text-slate-400">
              What Would Change This?
            </h4>
            <ul className="list-inside list-disc space-y-1 text-sm text-slate-600">
              {result.what_would_change_this.map((w, i) => (
                <li key={i}>{w}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </Card>
  );
}
