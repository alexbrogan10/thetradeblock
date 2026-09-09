from pydantic import BaseModel, ConfigDict

from app.schemas.team import TeamOut


class ContractOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    years_remaining: int
    annual_value: float
    guaranteed_money: float
    cap_hit: float
    contract_status: str


class PlayerValuationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())

    model_version: str
    valuation: float
    performance_score: float
    projection_score: float
    age_score: float
    position_score: float
    contract_score: float
    availability_score: float
    scarcity_score: float
    trajectory_score: float
    confidence: float


class PlayerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    position: str
    age: int
    experience: int
    status: str
    team: TeamOut | None = None
    contract: ContractOut | None = None


class PlayerDetailOut(PlayerOut):
    valuation: PlayerValuationOut | None = None
    valuation_explanation: dict | None = None
