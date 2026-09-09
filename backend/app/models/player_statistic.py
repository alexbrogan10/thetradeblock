from sqlalchemy import ForeignKey, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class PlayerStatistic(Base):
    """One season of a player's stat line.

    Position-specific counting stats live in the ``stats`` JSON column
    rather than as dozens of position-specific columns. This keeps the
    schema stable as new positions/stats are added and mirrors how the
    analytics layer already treats positions differently (see
    app/analytics/player_valuation.py). Known keys per position are
    documented in data/raw/README.md.
    """

    __tablename__ = "player_statistics"

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), nullable=False)
    season: Mapped[int] = mapped_column(Integer, nullable=False)
    games: Mapped[int] = mapped_column(Integer, default=0)
    games_started: Mapped[int] = mapped_column(Integer, default=0)
    stats: Mapped[dict] = mapped_column(JSON, default=dict)

    player: Mapped["Player"] = relationship(back_populates="statistics")
