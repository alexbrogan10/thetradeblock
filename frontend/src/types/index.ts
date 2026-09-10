export interface Team {
  id: number;
  name: string;
  abbreviation: string;
  conference: string;
  division: string;
}

export interface Contract {
  years_remaining: number;
  annual_value: number;
  guaranteed_money: number;
  cap_hit: number;
  contract_status: string;
}

export interface PlayerValuation {
  model_version: string;
  valuation: number;
  performance_score: number;
  projection_score: number;
  age_score: number;
  position_score: number;
  contract_score: number;
  availability_score: number;
  scarcity_score: number;
  trajectory_score: number;
  confidence: number;
}

export interface Player {
  id: number;
  name: string;
  position: string;
  age: number;
  experience: number;
  status: string;
  team: Team | null;
  contract: Contract | null;
}

export interface PlayerDetail extends Player {
  valuation: PlayerValuation | null;
  valuation_explanation: {
    positive_drivers: string[];
    negative_drivers: string[];
    notes: string[];
  } | null;
}

export interface DraftPick {
  id: number;
  year: number;
  round: number;
  overall_pick: number | null;
  original_team: Team;
  current_team: Team;
  estimated_value: number;
}

export interface AssetValue {
  asset_type: "player" | "draft_pick";
  asset_id: number;
  label: string;
  value: number;
}

export interface ContractImpact {
  cap_added_this_year: number;
  cap_freed_this_year: number;
  dead_cap_incurred: number;
  net_cap_impact_this_year: number;
  future_cap_added_3yr: number;
  future_cap_freed_3yr: number;
  net_multi_year_impact: number;
  note: string;
}

export interface PositionImpact {
  position: string;
  before: number;
  after: number;
  change: number;
}

export interface PositionNeed {
  position: string;
  priority: "Critical Need" | "Major Need" | "Moderate Need" | "Minor Need" | "Strong Position";
  need_score: number;
  current_depth: number;
  starter_quality: number | null;
  future_need: string;
  reasons: string[];
}

export interface TeamNeeds {
  team: Team;
  needs: PositionNeed[];
}

export interface Timeline {
  team: Team;
  classification: "Rebuilding" | "Developing" | "Competitive" | "Contender" | "Win Now";
  timeline_score: number;
  team_strength: number;
  average_age: number;
  veteran_pct: number;
  young_pct: number;
  draft_capital_percentile: number;
  reasons: string[];
}

export interface DraftCapitalYear {
  year: number;
  by_round: Record<string, number>;
  estimated_value: number;
}

export interface DraftCapital {
  team: Team;
  total_picks: number;
  estimated_total_value: number;
  by_year: DraftCapitalYear[];
}

export interface TeamAnalysis {
  team_id: number;
  team_name: string;
  gives: AssetValue[];
  receives: AssetValue[];
  player_value_given: number;
  player_value_received: number;
  draft_capital_given: number;
  draft_capital_received: number;
  asset_value_delta: number;
  roster_fit_score: number;
  draft_capital_delta: number;
  financial_impact: number;
  cap_given: number;
  cap_received: number;
  dead_cap_incurred: number;
  risk_level: "Low" | "Moderate" | "High";
  risk_drivers: string[];
  risk_mitigators: string[];
  timeline_alignment: number;
  competitive_window: "Rebuilding" | "Developing" | "Competitive" | "Contender" | "Win Now";
  opportunity_cost_notes: string[];
  contract_impact: ContractImpact;
  roster_impact: PositionImpact[];
  team_fit_explanations: string[];
  assessment:
    | "Strongly Favorable"
    | "Favorable"
    | "Potentially Favorable"
    | "Balanced"
    | "Potentially Unfavorable"
    | "Unfavorable"
    | "Strongly Unfavorable";
  positive_drivers: string[];
  negative_drivers: string[];
  what_could_change_this: string[];
}

export interface TradeAnalysisResult {
  team_a: TeamAnalysis;
  team_b: TeamAnalysis;
  confidence: number;
  confidence_limitations: string[];
  player_valuation_model_version: string;
  draft_pick_model_version: string;
  disclaimer: string;
}

export interface ScenarioSummary {
  id: number;
  name: string;
  team_a_name: string;
  team_b_name: string;
  team_a_assessment: string;
  team_b_assessment: string;
  confidence: number;
  model_version: string;
  created_at: string;
}

export interface ScenarioDetail extends TradeAnalysisResult {
  id: number;
  name: string;
  created_at: string;
}

export interface ScenarioComparisonRow {
  scenario_id: number;
  name: string;
  applicable: boolean;
  note?: string;
  assessment?: string;
  asset_value_delta?: number;
  draft_capital_delta?: number;
  financial_impact?: number;
  roster_fit_score?: number;
  risk_level?: string;
  timeline_alignment?: number;
  confidence?: number;
}

export interface SensitivityPoint {
  label: string;
  assessment: string;
  asset_value_delta: number;
  confidence: number;
}

export interface SensitivityResult {
  performance_sensitivity: SensitivityPoint[];
  draft_model_sensitivity: SensitivityPoint[];
  what_would_change_this: string[];
}

export interface ValueDiscrepancy {
  player_id: number;
  name: string;
  position: string;
  team: string | null;
  analytical_value: number;
  expected_value_for_cost: number;
  potential_discrepancy: number;
  drivers: string[];
}

export interface TradeTarget {
  player_id: number;
  name: string;
  position: string;
  team: string | null;
  age: number;
  fit_score: number;
  fit_explanation: string;
  analytical_value: number;
  estimated_cost_low: string;
  estimated_cost_high: string;
  cost_confidence: string;
  contract_fit_note: string;
  risk_level: string;
}

export interface DashboardOverview {
  demo_mode: boolean;
  player_valuation_model_version: string;
  trade_market: {
    highest_value_players: {
      player_id: number;
      name: string;
      position: string;
      team: string | null;
      valuation: number;
      confidence: number;
    }[];
    positions_commanding_value: { position: string; average_valuation: number; count: number }[];
  };
  team_opportunities: {
    draft_capital_by_team: { team_id: number; team: string; pick_count: number; estimated_total_value: number }[];
    limited_draft_capital_teams: { team_id: number; team: string; pick_count: number; estimated_total_value: number }[];
  };
  model_alerts: string[];
  value_discrepancies: {
    player_id: number;
    name: string;
    position: string;
    team: string | null;
    analytical_value: number;
    expected_value_for_cost: number;
    potential_discrepancy: number;
  }[];
}
