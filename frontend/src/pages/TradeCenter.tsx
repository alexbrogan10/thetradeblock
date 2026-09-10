import { useEffect, useState } from "react";
import { TeamAssetPanel } from "../components/trade/TeamAssetPanel";
import { TradeAnalysisView } from "../components/trade/TradeAnalysisView";
import { SensitivityPanel } from "../components/trade/SensitivityPanel";
import { api } from "../services/api";
import type { Team, TradeAnalysisResult } from "../types";

function toggle(list: number[], id: number): number[] {
  return list.includes(id) ? list.filter((x) => x !== id) : [...list, id];
}

export function TradeCenter() {
  const [teams, setTeams] = useState<Team[]>([]);

  const [teamAId, setTeamAId] = useState<number | null>(null);
  const [teamAPlayers, setTeamAPlayers] = useState<number[]>([]);
  const [teamAPicks, setTeamAPicks] = useState<number[]>([]);

  const [teamBId, setTeamBId] = useState<number | null>(null);
  const [teamBPlayers, setTeamBPlayers] = useState<number[]>([]);
  const [teamBPicks, setTeamBPicks] = useState<number[]>([]);

  const [result, setResult] = useState<TradeAnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [saveStatus, setSaveStatus] = useState<string | null>(null);

  useEffect(() => {
    api.getTeams().then(setTeams).catch(() => {});
  }, []);

  const canAnalyze =
    teamAId !== null &&
    teamBId !== null &&
    teamAId !== teamBId &&
    (teamAPlayers.length || teamAPicks.length || teamBPlayers.length || teamBPicks.length) > 0;

  async function handleAnalyze() {
    if (!teamAId || !teamBId) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const analysis = await api.analyzeTrade({
        team_a: { team_id: teamAId, player_ids: teamAPlayers, draft_pick_ids: teamAPicks },
        team_b: { team_id: teamBId, player_ids: teamBPlayers, draft_pick_ids: teamBPicks },
      });
      setResult(analysis);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }

  async function handleSaveScenario() {
    if (!teamAId || !teamBId) return;
    const name = window.prompt("Name this scenario:", "Untitled Scenario");
    if (name === null) return;
    setSaveStatus("Saving…");
    try {
      const summary = await api.saveScenario({
        name,
        team_a: { team_id: teamAId, player_ids: teamAPlayers, draft_pick_ids: teamAPicks },
        team_b: { team_id: teamBId, player_ids: teamBPlayers, draft_pick_ids: teamBPicks },
      });
      setSaveStatus(`Saved as "${summary.name}". View it under Scenarios.`);
    } catch (e) {
      setSaveStatus(`Failed to save: ${(e as Error).message}`);
    }
  }

  function reset() {
    setTeamAId(null);
    setTeamAPlayers([]);
    setTeamAPicks([]);
    setTeamBId(null);
    setTeamBPlayers([]);
    setTeamBPicks([]);
    setResult(null);
    setError(null);
    setSaveStatus(null);
  }

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Trade Center</h1>
          <p className="text-sm text-slate-500">
            Select two teams, add players and/or draft picks to each side, then analyze the
            hypothetical trade.
          </p>
        </div>
        <button
          onClick={reset}
          className="rounded border border-slate-300 px-3 py-1.5 text-sm text-slate-600 hover:bg-slate-50"
        >
          Reset
        </button>
      </header>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <TeamAssetPanel
          label="Team A"
          teams={teams}
          teamId={teamAId}
          onTeamChange={(id) => {
            setTeamAId(id);
            setTeamAPlayers([]);
            setTeamAPicks([]);
          }}
          selectedPlayerIds={teamAPlayers}
          onPlayerToggle={(id) => setTeamAPlayers((prev) => toggle(prev, id))}
          selectedPickIds={teamAPicks}
          onPickToggle={(id) => setTeamAPicks((prev) => toggle(prev, id))}
          disabledTeamId={teamBId}
        />
        <TeamAssetPanel
          label="Team B"
          teams={teams}
          teamId={teamBId}
          onTeamChange={(id) => {
            setTeamBId(id);
            setTeamBPlayers([]);
            setTeamBPicks([]);
          }}
          selectedPlayerIds={teamBPlayers}
          onPlayerToggle={(id) => setTeamBPlayers((prev) => toggle(prev, id))}
          selectedPickIds={teamBPicks}
          onPickToggle={(id) => setTeamBPicks((prev) => toggle(prev, id))}
          disabledTeamId={teamAId}
        />
      </div>

      <div className="flex justify-center">
        <button
          disabled={!canAnalyze || loading}
          onClick={handleAnalyze}
          className="rounded bg-slate-900 px-6 py-2.5 text-sm font-semibold text-white shadow disabled:cursor-not-allowed disabled:opacity-40"
        >
          {loading ? "Analyzing…" : "Analyze Trade"}
        </button>
      </div>

      {error && (
        <div className="rounded border border-rose-300 bg-rose-50 p-3 text-sm text-rose-800">
          {error}
        </div>
      )}

      {result && teamAId && teamBId && (
        <>
          <div className="flex items-center justify-center gap-3">
            <button
              onClick={handleSaveScenario}
              className="rounded border border-slate-300 px-4 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              Save Scenario
            </button>
            {saveStatus && <span className="text-xs text-slate-500">{saveStatus}</span>}
          </div>
          <TradeAnalysisView result={result} />
          <SensitivityPanel
            teamAId={teamAId}
            teamAPlayers={teamAPlayers}
            teamAPicks={teamAPicks}
            teamBId={teamBId}
            teamBPlayers={teamBPlayers}
            teamBPicks={teamBPicks}
          />
        </>
      )}
    </div>
  );
}
