from sqlalchemy import Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class HistoricalTrade(Base):
    """Section 24 - Historical Trade Database.

    In the demo configuration these are entirely synthetic trades
    (clearly labeled), generated the same way as the rest of the demo
    dataset. See data/raw/README.md.
    """

    __tablename__ = "historical_trades"

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[str] = mapped_column(Date, nullable=False)
    team_a_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    team_b_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    notes: Mapped[str] = mapped_column(String(512), default="")

    team_a: Mapped["Team"] = relationship(foreign_keys=[team_a_id])
    team_b: Mapped["Team"] = relationship(foreign_keys=[team_b_id])
    assets: Mapped[list["TradeAsset"]] = relationship(
        back_populates="trade", cascade="all, delete-orphan"
    )


class TradeAsset(Base):
    __tablename__ = "trade_assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    trade_id: Mapped[int] = mapped_column(ForeignKey("historical_trades.id"), nullable=False)
    team_from_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    team_to_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(16), nullable=False)  # "player" | "draft_pick"
    asset_id: Mapped[int] = mapped_column(Integer, nullable=False)
    # Denormalized snapshot fields so the historical record survives a
    # player being retired/removed or a pick's value model changing.
    label: Mapped[str] = mapped_column(String(128), default="")
    player_age_at_trade: Mapped[int | None] = mapped_column(Integer, nullable=True)
    player_position_at_trade: Mapped[str | None] = mapped_column(String(8), nullable=True)
    value_at_trade: Mapped[float] = mapped_column(Float, default=0)

    trade: Mapped["HistoricalTrade"] = relationship(back_populates="assets")
