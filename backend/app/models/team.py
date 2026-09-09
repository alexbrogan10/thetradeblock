from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    abbreviation: Mapped[str] = mapped_column(String(4), unique=True, nullable=False)
    conference: Mapped[str] = mapped_column(String(3), nullable=False)  # AFC / NFC
    division: Mapped[str] = mapped_column(String(16), nullable=False)  # e.g. "East"

    players: Mapped[list["Player"]] = relationship(back_populates="team")
