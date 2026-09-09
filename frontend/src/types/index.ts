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
  opportunity_cost_notes: string[];
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
