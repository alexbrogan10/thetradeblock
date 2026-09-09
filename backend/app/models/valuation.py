from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class PlayerValuation(Base):
    """A stored, reproducible output of the player valuation model.

    Trade scenarios reference the model_version used so historical
    analyses remain auditable even if the model changes later
    (Section 40 - Auditability).
    """

    __tablename__ = "player_valuations"

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    model_version: Mapped[str] = mapped_column(String(64), nullable=False)
    valuation: Mapped[float] = mapped_column(Float, nullable=False)
    performance_score: Mapped[float] = mapped_column(Float, nullable=False)
    projection_score: Mapped[float] = mapped_column(Float, nullable=False)
    age_score: Mapped[float] = mapped_column(Float, nullable=False)
    position_score: Mapped[float] = mapped_column(Float, nullable=False)
    contract_score: Mapped[float] = mapped_column(Float, nullable=False)
    availability_score: Mapped[float] = mapped_column(Float, nullable=False)
    scarcity_score: Mapped[float] = mapped_column(Float, nullable=False)
    trajectory_score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

    player: Mapped["Player"] = relationship(back_populates="valuations")
