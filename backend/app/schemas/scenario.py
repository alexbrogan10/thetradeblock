from pydantic import BaseModel, ConfigDict

from app.schemas.trade import TradeAnalysisResult, TradeSideInput


class ScenarioSaveRequest(BaseModel):
    name: str = "Untitled Scenario"
    team_a: TradeSideInput
    team_b: TradeSideInput


class ScenarioSummaryOut(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    id: int
    name: str
    team_a_name: str
    team_b_name: str
    team_a_assessment: str
    team_b_assessment: str
    confidence: float
    model_version: str
    created_at: str


class ScenarioDetailOut(TradeAnalysisResult):
    id: int
    name: str
    created_at: str


class ScenarioCompareRequest(BaseModel):
    scenario_ids: list[int]
    perspective_team_id: int


class ScenarioComparisonRowOut(BaseModel):
    scenario_id: int
    name: str
    applicable: bool
    note: str = ""
    assessment: str | None = None
    asset_value_delta: float | None = None
    draft_capital_delta: float | None = None
    financial_impact: float | None = None
    roster_fit_score: float | None = None
    risk_level: str | None = None
    timeline_alignment: float | None = None
    confidence: float | None = None
