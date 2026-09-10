from typing import Literal

from pydantic import BaseModel, Field


class TradeSideInput(BaseModel):
    team_id: int
    player_ids: list[int] = Field(default_factory=list)
    draft_pick_ids: list[int] = Field(default_factory=list)


class TradeAnalyzeRequest(BaseModel):
    team_a: TradeSideInput
    team_b: TradeSideInput


class AssetValueOut(BaseModel):
    asset_type: Literal["player", "draft_pick"]
    asset_id: int
    label: str
    value: float


class ContractImpactOut(BaseModel):
    cap_added_this_year: float
    cap_freed_this_year: float
    dead_cap_incurred: float
    net_cap_impact_this_year: float
    future_cap_added_3yr: float
    future_cap_freed_3yr: float
    net_multi_year_impact: float
    note: str


class PositionImpactOut(BaseModel):
    position: str
    before: float
    after: float
    change: float


class TeamAnalysisOut(BaseModel):
    team_id: int
    team_name: str

    gives: list[AssetValueOut]
    receives: list[AssetValueOut]

    player_value_given: float
    player_value_received: float
    draft_capital_given: float
    draft_capital_received: float

    asset_value_delta: float
    roster_fit_score: float
    draft_capital_delta: float
    financial_impact: float
    cap_given: float
    cap_received: float
    dead_cap_incurred: float

    risk_level: Literal["Low", "Moderate", "High"]
    risk_drivers: list[str]
    risk_mitigators: list[str]

    timeline_alignment: float
    competitive_window: str
    opportunity_cost_notes: list[str]

    contract_impact: ContractImpactOut
    roster_impact: list[PositionImpactOut]
    team_fit_explanations: list[str]

    assessment: Literal[
        "Strongly Favorable",
        "Favorable",
        "Potentially Favorable",
        "Balanced",
        "Potentially Unfavorable",
        "Unfavorable",
        "Strongly Unfavorable",
    ]
    positive_drivers: list[str]
    negative_drivers: list[str]
    what_could_change_this: list[str]


class TradeAnalysisResult(BaseModel):
    team_a: TeamAnalysisOut
    team_b: TeamAnalysisOut
    confidence: float
    confidence_limitations: list[str]
    player_valuation_model_version: str
    draft_pick_model_version: str
    disclaimer: str = (
        "Decision support only. Not a claim of objective correctness, "
        "proprietary NFL data, or an actual front-office system."
    )
