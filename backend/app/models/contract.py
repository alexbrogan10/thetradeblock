from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id"), unique=True, nullable=False
    )
    years_remaining: Mapped[int] = mapped_column(Integer, default=0)
    annual_value: Mapped[float] = mapped_column(Float, default=0.0)  # AAV, $M
    guaranteed_money: Mapped[float] = mapped_column(Float, default=0.0)  # $M
    cap_hit: Mapped[float] = mapped_column(Float, default=0.0)  # current-year, $M
    contract_status: Mapped[str] = mapped_column(String(24), default="signed")

    player: Mapped["Player"] = relationship(back_populates="contract")
