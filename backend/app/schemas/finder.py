from typing import Literal

from pydantic import BaseModel


class TradeFinderRequest(BaseModel):
    team_id: int
    position: str
    max_acquisition_cost: float | None = None
    age_preference: Literal["young", "prime", "veteran"] | None = None
    risk_tolerance: Literal["Low", "Moderate", "High"] | None = None


class TradeTargetOut(BaseModel):
    player_id: int
    name: str
    position: str
    team: str | None
    age: int
    fit_score: float
    fit_explanation: str
    analytical_value: float
    estimated_cost_low: str
    estimated_cost_high: str
    cost_confidence: str
    contract_fit_note: str
    risk_level: str
