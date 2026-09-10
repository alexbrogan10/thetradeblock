from pydantic import BaseModel, ConfigDict


class TeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    abbreviation: str
    conference: str
    division: str


class PositionNeedOut(BaseModel):
    position: str
    priority: str
    need_score: float
    current_depth: int
    starter_quality: float | None
    future_need: str
    reasons: list[str]


class TeamNeedsOut(BaseModel):
    team: TeamOut
    needs: list[PositionNeedOut]


class TimelineOut(BaseModel):
    team: TeamOut
    classification: str
    timeline_score: float
    team_strength: float
    average_age: float
    veteran_pct: float
    young_pct: float
    draft_capital_percentile: float
    reasons: list[str]


class DraftCapitalYearOut(BaseModel):
    year: int
    by_round: dict[str, int]
    estimated_value: float


class DraftCapitalOut(BaseModel):
    team: TeamOut
    total_picks: int
    estimated_total_value: float
    by_year: list[DraftCapitalYearOut]


class PositionImpactSimpleOut(BaseModel):
    position: str
    before: float
    after: float
    change: float


class RosterImpactOut(BaseModel):
    team: TeamOut
    impact: list[PositionImpactSimpleOut]
