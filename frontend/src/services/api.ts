import type {
  ComparableTrade,
  DashboardOverview,
  DraftCapital,
  DraftPick,
  Player,
  PlayerDetail,
  ScenarioComparisonRow,
  ScenarioDetail,
  ScenarioSummary,
  SensitivityResult,
  SimilarPlayer,
  Team,
  TeamNeeds,
  Timeline,
  TradeAnalysisResult,
  TradeTarget,
  ValueDiscrepancy,
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

type TradeSidePayload = { team_id: number; player_ids: number[]; draft_pick_ids: number[] };

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
  analyzeTrade: (payload: { team_a: TradeSidePayload; team_b: TradeSidePayload }) =>
    request<TradeAnalysisResult>("/api/trades/analyze", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  getDashboard: () => request<DashboardOverview>("/api/analytics/dashboard"),
  getTeamNeeds: (teamId: number) => request<TeamNeeds>(`/api/team/${teamId}/needs`),
  getTeamTimeline: (teamId: number) => request<Timeline>(`/api/team/${teamId}/timeline`),
  getTeamDraftCapital: (teamId: number) => request<DraftCapital>(`/api/team/${teamId}/draft-capital`),
  getAllTeamsDraftCapital: () => request<DraftCapital[]>("/api/analytics/draft-capital"),

  saveScenario: (payload: { name: string; team_a: TradeSidePayload; team_b: TradeSidePayload }) =>
    request<ScenarioSummary>("/api/trades/scenarios", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
  listScenarios: () => request<ScenarioSummary[]>("/api/trades/scenarios"),
  getScenario: (id: number) => request<ScenarioDetail>(`/api/trades/scenarios/${id}`),
  deleteScenario: (id: number) =>
    request<{ status: string }>(`/api/trades/scenarios/${id}`, { method: "DELETE" }),
  compareScenarios: (scenario_ids: number[], perspective_team_id: number) =>
    request<ScenarioComparisonRow[]>("/api/trades/scenarios/compare", {
      method: "POST",
      body: JSON.stringify({ scenario_ids, perspective_team_id }),
    }),

  getSensitivity: (payload: {
    team_a: TradeSidePayload;
    team_b: TradeSidePayload;
    perspective_team_id: number;
  }) =>
    request<SensitivityResult>("/api/trades/sensitivity", {
      method: "POST",
      body: JSON.stringify(payload),
    }),

  getValueDiscrepancies: (params: { min_discrepancy?: number; position?: string } = {}) => {
    const qs = new URLSearchParams();
    if (params.min_discrepancy !== undefined) qs.set("min_discrepancy", String(params.min_discrepancy));
    if (params.position) qs.set("position", params.position);
    const query = qs.toString();
    return request<ValueDiscrepancy[]>(`/api/analytics/value-discrepancies${query ? `?${query}` : ""}`);
  },

  getComparableTrades: (params: { position?: string; age_min?: number; age_max?: number; limit?: number } = {}) => {
    const qs = new URLSearchParams();
    if (params.position) qs.set("position", params.position);
    if (params.age_min !== undefined) qs.set("age_min", String(params.age_min));
    if (params.age_max !== undefined) qs.set("age_max", String(params.age_max));
    if (params.limit !== undefined) qs.set("limit", String(params.limit));
    const query = qs.toString();
    return request<ComparableTrade[]>(`/api/historical-trades/comparable${query ? `?${query}` : ""}`);
  },
  getSimilarPlayers: (playerId: number, topN = 5) =>
    request<SimilarPlayer[]>(`/api/players/${playerId}/similar?top_n=${topN}`),

  findTradeTargets: (payload: {
    team_id: number;
    position: string;
    max_acquisition_cost?: number;
    age_preference?: "young" | "prime" | "veteran";
    risk_tolerance?: "Low" | "Moderate" | "High";
  }) =>
    request<TradeTarget[]>("/api/trades/finder", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
