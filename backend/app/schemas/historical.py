from pydantic import BaseModel


class ComparableTradeOut(BaseModel):
    trade_id: int
    date: str
    team_a: str
    team_b: str
    matching_player: str
    matching_position: str
    matching_age_at_trade: int
    similarity_score: float
    similarities: list[str]
    differences: list[str]
    other_assets: list[str]
    outcome_note: str


class HistoricalTradeAssetOut(BaseModel):
    asset_type: str
    label: str
    team_from: str
    team_to: str
    player_age_at_trade: int | None = None
    player_position_at_trade: str | None = None


class HistoricalTradeDetailOut(BaseModel):
    id: int
    date: str
    team_a: str
    team_b: str
    notes: str
    assets: list[HistoricalTradeAssetOut]


class SimilarPlayerOut(BaseModel):
    player_id: int
    name: str
    position: str
    team: str | None
    age: int
    valuation: float
    similarity_pct: float
    explanation: str
