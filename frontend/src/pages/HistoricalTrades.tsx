import { useEffect, useState } from "react";
import { Card } from "../components/common/Card";
import { ScoreBadge } from "../components/common/ScoreBadge";
import { api } from "../services/api";
import type { ComparableTrade, MLProjection, Player, SimilarPlayer, Team } from "../types";

const POSITIONS = ["", "QB", "RB", "WR", "TE", "OT", "IOL", "EDGE", "DT", "LB", "CB", "S", "K", "P", "LS"];

function ComparableTradeSearch() {
  const [position, setPosition] = useState("WR");
  const [ageMin, setAgeMin] = useState(25);
  const [ageMax, setAgeMax] = useState(28);
  const [results, setResults] = useState<ComparableTrade[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function search() {
    setError(null);
    try {
      const r = await api.getComparableTrades({
        position: position || undefined,
        age_min: ageMin,
        age_max: ageMax,
      });
      setResults(r);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  useEffect(() => {
    search();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <Card title="Comparable Trade Search">
      <p className="mb-3 text-xs text-slate-500">
        e.g. "Find WR trades involving players ages 25-28." All trades in this demo dataset are
        synthetic (see the data pipeline docs) — comparable trades are decision-support context,
        not a guarantee of future outcomes.
      </p>
      <div className="mb-4 flex flex-wrap items-end gap-3">
        <div>
          <label className="mb-1 block text-xs font-medium text-slate-500">Position</label>
          <select
            className="rounded border border-slate-300 px-2 py-1.5 text-sm"
            value={position}
            onChange={(e) => setPosition(e.target.value)}
          >
            {POSITIONS.map((p) => (
              <option key={p} value={p}>
                {p || "Any"}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-slate-500">Age Min</label>
          <input
            type="number"
            className="w-20 rounded border border-slate-300 px-2 py-1.5 text-sm"
            value={ageMin}
            onChange={(e) => setAgeMin(Number(e.target.value))}
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-slate-500">Age Max</label>
          <input
            type="number"
            className="w-20 rounded border border-slate-300 px-2 py-1.5 text-sm"
            value={ageMax}
            onChange={(e) => setAgeMax(Number(e.target.value))}
          />
        </div>
        <button onClick={search} className="rounded bg-slate-900 px-4 py-1.5 text-sm font-semibold text-white">
          Search
        </button>
      </div>

      {error && <p className="text-sm text-rose-600">{error}</p>}

      {results && (
        <div className="divide-y divide-slate-100">
          {results.map((t) => (
            <div key={t.trade_id} className="py-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="font-medium text-slate-800">
                  {t.date} · {t.team_a} ↔ {t.team_b} · {t.matching_player}
                </div>
                <ScoreBadge score={t.similarity_score} label="Similarity" />
              </div>
              <div className="mt-1 text-xs text-slate-500">
                Other assets in trade: {t.other_assets.join(", ") || "None recorded"}
              </div>
              <div className="mt-1 text-xs text-emerald-700">Similarities: {t.similarities.join(" ")}</div>
              <div className="text-xs text-amber-700">Differences: {t.differences.join(" ")}</div>
              <div className="mt-1 text-xs italic text-slate-400">Outcome note: {t.outcome_note}</div>
            </div>
          ))}
          {results.length === 0 && <p className="py-4 text-sm text-slate-400">No comparable trades found.</p>}
        </div>
      )}
    </Card>
  );
}

function PlayerSimilarityLookup() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [teamId, setTeamId] = useState<number | null>(null);
  const [players, setPlayers] = useState<Player[]>([]);
  const [playerId, setPlayerId] = useState<number | null>(null);
  const [results, setResults] = useState<SimilarPlayer[] | null>(null);
  const [projection, setProjection] = useState<MLProjection | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getTeams().then(setTeams).catch(() => {});
  }, []);

  useEffect(() => {
    if (teamId) api.getPlayers({ team_id: teamId }).then(setPlayers).catch(() => {});
    else setPlayers([]);
    setPlayerId(null);
    setResults(null);
    setProjection(null);
  }, [teamId]);

  async function lookup() {
    if (!playerId) return;
    setError(null);
    try {
      const [similar, proj] = await Promise.all([
        api.getSimilarPlayers(playerId),
        api.getMLProjection(playerId),
      ]);
      setResults(similar);
      setProjection(proj);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <Card title="Player Similarity">
      <p className="mb-3 text-xs text-slate-500">
        Uses k-nearest-neighbors over a standardized feature vector (age, production, projection,
        contract terms) within the same position. A comparable player "has a similar statistical
        and contractual profile" — this is not a prediction that one player will become another.
      </p>
      <div className="mb-4 flex flex-wrap items-end gap-3">
        <div>
          <label className="mb-1 block text-xs font-medium text-slate-500">Team</label>
          <select
            className="rounded border border-slate-300 px-2 py-1.5 text-sm"
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
          <label className="mb-1 block text-xs font-medium text-slate-500">Player</label>
          <select
            className="rounded border border-slate-300 px-2 py-1.5 text-sm"
            value={playerId ?? ""}
            onChange={(e) => setPlayerId(e.target.value ? Number(e.target.value) : null)}
            disabled={!teamId}
          >
            <option value="">Select…</option>
            {players.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.position})
              </option>
            ))}
          </select>
        </div>
        <button
          onClick={lookup}
          disabled={!playerId}
          className="rounded bg-slate-900 px-4 py-1.5 text-sm font-semibold text-white disabled:opacity-40"
        >
          Find Similar Players
        </button>
      </div>

      {error && <p className="text-sm text-rose-600">{error}</p>}

      {projection && (
        <div className="mb-4 rounded border border-slate-200 bg-slate-50 p-3">
          <h4 className="mb-1 text-xs font-semibold uppercase text-slate-400">
            ML Performance Projection (Next Season)
          </h4>
          {projection.available ? (
            <>
              <div className="text-sm">
                Predicted performance score:{" "}
                <span className="font-semibold text-slate-800">{projection.predicted_performance_score}</span>
                <span className="text-xs text-slate-400"> ({projection.model_version})</span>
              </div>
              <div className="mt-1 text-xs text-slate-500">
                Top drivers:{" "}
                {projection.top_features?.map((f) => `${f.feature} (${f.importance})`).join(", ")}
              </div>
              <p className="mt-1 text-xs italic text-slate-400">{projection.note}</p>
            </>
          ) : (
            <p className="text-xs text-slate-400">{projection.note}</p>
          )}
        </div>
      )}

      {results && (
        <div className="divide-y divide-slate-100">
          {results.map((r) => (
            <div key={r.player_id} className="flex flex-wrap items-center justify-between gap-2 py-2">
              <div>
                <span className="font-medium text-slate-800">{r.name}</span>{" "}
                <span className="text-xs text-slate-400">
                  {r.position} · {r.team} · Age {r.age} · Value {r.valuation}
                </span>
                <div className="text-xs text-slate-500">{r.explanation}</div>
              </div>
              <ScoreBadge score={r.similarity_pct} label="Similarity" />
            </div>
          ))}
          {results.length === 0 && (
            <p className="py-4 text-sm text-slate-400">Not enough comparable players at this position yet.</p>
          )}
        </div>
      )}
    </Card>
  );
}

export function HistoricalTradesPage() {
  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-900">Historical Trades &amp; Player Similarity</h1>
        <p className="text-sm text-slate-500">
          Search for comparable historical trades, or find players with a similar statistical and
          contractual profile.
        </p>
      </header>
      <ComparableTradeSearch />
      <PlayerSimilarityLookup />
    </div>
  );
}
