from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class TeamNeed(Base):
    """A stored snapshot of the Team Needs Engine's output (Section 18).

    The live API always recomputes needs on demand from current roster
    state (see app/analytics/team_needs.py) so this table is a
    reproducibility snapshot, not the source of truth -- mirrors the
    PlayerValuation pattern (Section 40 - Auditability).
    """

    __tablename__ = "team_needs"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    position: Mapped[str] = mapped_column(String(8), nullable=False)
    priority: Mapped[str] = mapped_column(String(24), nullable=False)
    need_score: Mapped[float] = mapped_column(Float, nullable=False)
    current_depth: Mapped[int] = mapped_column(Integer, default=0)
    future_need: Mapped[str] = mapped_column(String(24), default="Unknown")
    computed_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

    team: Mapped["Team"] = relationship()
