from sqlalchemy import Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class DraftPick(Base):
    __tablename__ = "draft_picks"

    id: Mapped[int] = mapped_column(primary_key=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    round: Mapped[int] = mapped_column(Integer, nullable=False)
    # Overall pick number is unknown for future drafts until slotting is
    # determined by standings; nullable represents that explicitly rather
    # than guessing a number.
    overall_pick: Mapped[int | None] = mapped_column(Integer, nullable=True)
    original_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    current_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"))
    estimated_value: Mapped[float] = mapped_column(Float, default=0.0)

    original_team: Mapped["Team"] = relationship(foreign_keys=[original_team_id])
    current_team: Mapped["Team"] = relationship(foreign_keys=[current_team_id])
