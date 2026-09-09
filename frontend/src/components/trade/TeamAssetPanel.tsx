import { useEffect, useState } from "react";
import { Card } from "../common/Card";
import { api } from "../../services/api";
import type { DraftPick, Player, Team } from "../../types";

interface Props {
  label: string;
  teamId: number | null;
  onTeamChange: (id: number | null) => void;
  selectedPlayerIds: number[];
  onPlayerToggle: (id: number) => void;
  selectedPickIds: number[];
  onPickToggle: (id: number) => void;
  teams: Team[];
  disabledTeamId?: number | null;
}

export function TeamAssetPanel({
  label,
  teamId,
  onTeamChange,
  selectedPlayerIds,
  onPlayerToggle,
  selectedPickIds,
  onPickToggle,
  teams,
  disabledTeamId,
}: Props) {
  const [players, setPlayers] = useState<Player[]>([]);
  const [picks, setPicks] = useState<DraftPick[]>([]);
  const [positionFilter, setPositionFilter] = useState("");

  useEffect(() => {
    if (!teamId) {
      setPlayers([]);
      setPicks([]);
      return;
    }
    api.getPlayers({ team_id: teamId }).then(setPlayers).catch(() => setPlayers([]));
    api.getDraftPicks({ team_id: teamId }).then(setPicks).catch(() => setPicks([]));
  }, [teamId]);

  const positions = Array.from(new Set(players.map((p) => p.position))).sort();
  const filteredPlayers = positionFilter
    ? players.filter((p) => p.position === positionFilter)
    : players;

  return (
    <Card title={label}>
      <div className="space-y-4">
        <div>
          <label className="mb-1 block text-xs font-medium text-slate-500">Team</label>
          <select
            className="w-full rounded border border-slate-300 px-2 py-1.5 text-sm"
            value={teamId ?? ""}
            onChange={(e) => onTeamChange(e.target.value ? Number(e.target.value) : null)}
          >
            <option value="">Select a team…</option>
            {teams.map((t) => (
              <option key={t.id} value={t.id} disabled={t.id === disabledTeamId}>
                {t.name}
              </option>
            ))}
          </select>
        </div>

        {teamId && (
          <>
            <div>
              <div className="mb-1 flex items-center justify-between">
                <label className="block text-xs font-medium text-slate-500">Players</label>
                <select
                  className="rounded border border-slate-200 px-1.5 py-0.5 text-xs"
                  value={positionFilter}
                  onChange={(e) => setPositionFilter(e.target.value)}
                >
                  <option value="">All positions</option>
                  {positions.map((pos) => (
                    <option key={pos} value={pos}>
                      {pos}
                    </option>
                  ))}
                </select>
              </div>
              <div className="max-h-56 overflow-y-auto rounded border border-slate-200">
                {filteredPlayers.map((p) => (
                  <label
                    key={p.id}
                    className="flex cursor-pointer items-center justify-between border-b border-slate-100 px-2 py-1.5 text-sm last:border-b-0 hover:bg-slate-50"
                  >
                    <span className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={selectedPlayerIds.includes(p.id)}
                        onChange={() => onPlayerToggle(p.id)}
                      />
                      {p.name}
                      <span className="text-xs text-slate-400">
                        {p.position} · Age {p.age}
                      </span>
                    </span>
                    {p.contract && (
                      <span className="text-xs text-slate-400">${p.contract.annual_value}M/yr</span>
                    )}
                  </label>
                ))}
                {filteredPlayers.length === 0 && (
                  <div className="px-2 py-3 text-center text-xs text-slate-400">No players.</div>
                )}
              </div>
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-slate-500">Draft Picks</label>
              <div className="max-h-40 overflow-y-auto rounded border border-slate-200">
                {picks.map((pk) => (
                  <label
                    key={pk.id}
                    className="flex cursor-pointer items-center justify-between border-b border-slate-100 px-2 py-1.5 text-sm last:border-b-0 hover:bg-slate-50"
                  >
                    <span className="flex items-center gap-2">
                      <input
                        type="checkbox"
                        checked={selectedPickIds.includes(pk.id)}
                        onChange={() => onPickToggle(pk.id)}
                      />
                      {pk.year} Round {pk.round}
                      {pk.overall_pick ? ` (Pick ${pk.overall_pick})` : " (future)"}
                    </span>
                    <span className="text-xs text-slate-400">~{Math.round(pk.estimated_value)} pts</span>
                  </label>
                ))}
                {picks.length === 0 && (
                  <div className="px-2 py-3 text-center text-xs text-slate-400">No draft picks.</div>
                )}
              </div>
            </div>
          </>
        )}
      </div>
    </Card>
  );
}
