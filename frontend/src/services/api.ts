import type {
  DashboardOverview,
  DraftCapital,
  DraftPick,
  Player,
  PlayerDetail,
  Team,
  TeamNeeds,
  Timeline,
  TradeAnalysisResult,
} from "../types";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export const api = {
  getTeams: () => request<Team[]>("/api/teams"),
  getTeam: (id: number) => request<Team>(`/api/teams/${id}`),
  getPlayers: (params: { team_id?: number; position?: string } = {}) => {
    const qs = new URLSearchParams();
    if (params.team_id) qs.set("team_id", String(params.team_id));
    if (params.position) qs.set("position", params.position);
    const query = qs.toString();
    return request<Player[]>(`/api/players${query ? `?${query}` : ""}`);
  },
  getPlayer: (id: number) => request<PlayerDetail>(`/api/players/${id}`),
  getDraftPicks: (params: { team_id?: number; year?: number } = {}) => {
    const qs = new URLSearchParams();
    if (params.team_id) qs.set("team_id", String(params.team_id));
    if (params.year) qs.set("year", String(params.year));
    const query = qs.toString();
    return request<DraftPick[]>(`/api/draft-picks${query ? `?${query}` : ""}`);
  },
  analyzeTrade: (payload: {
    team_a: { team_id: number; player_ids: number[]; draft_pick_ids: number[] };
    team_b: { team_id: number; player_ids: number[]; draft_pick_ids: number[] };
  }) =>
    request<TradeAnalysisResult>("/api/trades/analyze", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getDashboard: () => request<DashboardOverview>("/api/analytics/dashboard"),
  getTeamNeeds: (teamId: number) => request<TeamNeeds>(`/api/team/${teamId}/needs`),
  getTeamTimeline: (teamId: number) => request<Timeline>(`/api/team/${teamId}/timeline`),
  getTeamDraftCapital: (teamId: number) => request<DraftCapital>(`/api/team/${teamId}/draft-capital`),
  getAllTeamsDraftCapital: () => request<DraftCapital[]>("/api/analytics/draft-capital"),
};
