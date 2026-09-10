import { useEffect, useMemo, useState } from "react";
import { Card } from "../components/common/Card";
import { ScoreBadge } from "../components/common/ScoreBadge";
import { api } from "../services/api";
import type { Player, PlayerDetail, Team } from "../types";

const POSITIONS = ["", "QB", "RB", "WR", "TE", "OT", "IOL", "EDGE", "DT", "LB", "CB", "S", "K", "P", "LS"];

function PlayerRow({ player }: { player: Player }) {
  const [expanded, setExpanded] = useState(false);
  const [detail, setDetail] = useState<PlayerDetail | null>(null);
  const [loading, setLoading] = useState(false);

  async function toggle() {
    if (!expanded && !detail) {
      setLoading(true);
      try {
        const d = await api.getPlayer(player.id);
        setDetail(d);
      } finally {
        setLoading(false);
      }
    }
    setExpanded(!expanded);
  }

  return (
    <div className="border-b border-slate-100">
      <button onClick={toggle} className="flex w-full items-center justify-between gap-2 py-2 text-left hover:bg-slate-50">
        <div>
          <span className="font-medium text-slate-800">{player.name}</span>{" "}
          <span className="text-xs text-slate-400">
            {player.position} · {player.team?.abbreviation ?? "FA"} · Age {player.age}
          </span>
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-400">
          {player.contract && <span>${player.contract.annual_value}M/yr</span>}
          <span>{expanded ? "▾" : "▸"}</span>
        </div>
      </button>
      {expanded && (
        <div className="pb-3 pl-2">
          {loading && <p className="text-xs text-slate-400">Loading valuation…</p>}
          {detail?.valuation && (
            <div className="flex flex-wrap items-center gap-3">
              <ScoreBadge score={detail.valuation.valuation} label="Trade Value" />
              <span className="text-xs text-slate-500">
                Performance {detail.valuation.performance_score} · Projection {detail.valuation.projection_score} ·
                Age {detail.valuation.age_score} · Contract {detail.valuation.contract_score} · Confidence{" "}
                {detail.valuation.confidence}%
              </span>
            </div>
          )}
          {detail?.valuation_explanation && (
            <ul className="mt-1 list-inside list-disc text-xs text-slate-500">
              {[...detail.valuation_explanation.positive_drivers, ...detail.valuation_explanation.negative_drivers].map(
                (d, i) => (
                  <li key={i}>{d}</li>
                )
              )}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}

export function PlayersPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [teamId, setTeamId] = useState<number | null>(null);
  const [position, setPosition] = useState("");
  const [search, setSearch] = useState("");
  const [players, setPlayers] = useState<Player[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.getTeams().then(setTeams).catch(() => {});
  }, []);

  useEffect(() => {
    api
      .getPlayers({ team_id: teamId ?? undefined, position: position || undefined })
      .then(setPlayers)
      .catch((e) => setError(e.message));
  }, [teamId, position]);

  const filtered = useMemo(
    () => players.filter((p) => p.name.toLowerCase().includes(search.toLowerCase())),
    [players, search]
  );

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-900">Players</h1>
        <p className="text-sm text-slate-500">
          Browse the full player database. Expand a player to see their explainable trade value.
        </p>
      </header>

      <Card>
        <div className="flex flex-wrap items-end gap-3">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">Team</label>
            <select
              className="rounded border border-slate-300 px-2 py-1.5 text-sm"
              value={teamId ?? ""}
              onChange={(e) => setTeamId(e.target.value ? Number(e.target.value) : null)}
            >
              <option value="">All teams</option>
              {teams.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">Position</label>
            <select
              className="rounded border border-slate-300 px-2 py-1.5 text-sm"
              value={position}
              onChange={(e) => setPosition(e.target.value)}
            >
              {POSITIONS.map((p) => (
                <option key={p} value={p}>
                  {p || "All"}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-500">Search by name</label>
            <input
              type="text"
              className="rounded border border-slate-300 px-2 py-1.5 text-sm"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Player name…"
            />
          </div>
          <span className="text-xs text-slate-400">{filtered.length} players</span>
        </div>
      </Card>

      {error && <div className="rounded border border-rose-300 bg-rose-50 p-3 text-sm text-rose-800">{error}</div>}

      <Card>
        <div>
          {filtered.map((p) => (
            <PlayerRow key={p.id} player={p} />
          ))}
          {filtered.length === 0 && <p className="py-4 text-sm text-slate-400">No players match these filters.</p>}
        </div>
      </Card>
    </div>
  );
}
