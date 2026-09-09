from pydantic import BaseModel, ConfigDict

from app.schemas.team import TeamOut


class DraftPickOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    year: int
    round: int
    overall_pick: int | None
    original_team: TeamOut
    current_team: TeamOut
    estimated_value: float


class DraftPickValueBreakdown(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    pick_label: str
    traditional_value: float
    historical_value: float
    expected_value: float
    model_agreement: str
