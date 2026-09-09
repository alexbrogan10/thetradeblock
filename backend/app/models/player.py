from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    position: Mapped[str] = mapped_column(String(8), nullable=False)
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), nullable=True)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    height_in: Mapped[int | None] = mapped_column(Integer, nullable=True)
    weight_lb: Mapped[int | None] = mapped_column(Integer, nullable=True)
    experience: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(16), default="active")

    team: Mapped["Team"] = relationship(back_populates="players")
    statistics: Mapped[list["PlayerStatistic"]] = relationship(
        back_populates="player", cascade="all, delete-orphan"
    )
    contract: Mapped["Contract"] = relationship(
        back_populates="player", uselist=False, cascade="all, delete-orphan"
    )
    valuations: Mapped[list["PlayerValuation"]] = relationship(
        back_populates="player", cascade="all, delete-orphan"
    )
