from sqlalchemy import DateTime, Float, ForeignKey, Integer, JSON, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class TradeScenario(Base):
    """A saved hypothetical trade (Section 26 - Trade Simulator).

    Stores the model version and assumptions used so the scenario can be
    reproduced later even if the models change (Section 40 -
    Auditability).
    """

    __tablename__ = "trade_scenarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), default="Untitled Scenario")
    team_a_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    team_b_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    model_version: Mapped[str] = mapped_column(String(64), nullable=False)
    assumptions: Mapped[dict] = mapped_column(JSON, default=dict)
    recommendation: Mapped[dict] = mapped_column(JSON, default=dict)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)

    team_a: Mapped["Team"] = relationship(foreign_keys=[team_a_id])
    team_b: Mapped["Team"] = relationship(foreign_keys=[team_b_id])
    assets: Mapped[list["ScenarioAsset"]] = relationship(
        back_populates="scenario", cascade="all, delete-orphan"
    )


class ScenarioAsset(Base):
    __tablename__ = "scenario_assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenario_id: Mapped[int] = mapped_column(ForeignKey("trade_scenarios.id"), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(16), nullable=False)
    asset_id: Mapped[int] = mapped_column(Integer, nullable=False)
    team_from_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    team_to_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    estimated_value: Mapped[float] = mapped_column(Float, default=0.0)

    scenario: Mapped["TradeScenario"] = relationship(back_populates="assets")
