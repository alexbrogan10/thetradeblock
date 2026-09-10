"""Historical Trade Database search (Section 24).

Every trade in the demo dataset is synthetic (see data/raw/README.md).
Comparable-trade search never implies that historical trades guarantee
future outcomes (Rule 56) -- the "outcome" field is a short, neutral,
illustrative note, not a claim of causal effect.
"""
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.models.historical_trade import HistoricalTrade, TradeAsset


@dataclass
class ComparableTrade:
    trade_id: int
    date: str
    team_a: str
    team_b: str
    matching_player: str
    matching_position: str
    matching_age_at_trade: int
    similarity_score: float
    similarities: list[str] = field(default_factory=list)
    differences: list[str] = field(default_factory=list)
    other_assets: list[str] = field(default_factory=list)
    outcome_note: str = ""


def find_comparable_trades(
    db: Session,
    position: str | None = None,
    age_min: int | None = None,
    age_max: int | None = None,
    limit: int = 10,
) -> list[ComparableTrade]:
    query = db.query(TradeAsset).filter(TradeAsset.asset_type == "player")
    if position:
        query = query.filter(TradeAsset.player_position_at_trade == position.upper())
    if age_min is not None:
        query = query.filter(TradeAsset.player_age_at_trade >= age_min)
    if age_max is not None:
        query = query.filter(TradeAsset.player_age_at_trade <= age_max)

    matching_assets = query.all()
    midpoint = None
    if age_min is not None and age_max is not None:
        midpoint = (age_min + age_max) / 2

    results = []
    for asset in matching_assets:
        trade = db.get(HistoricalTrade, asset.trade_id)
        if trade is None:
            continue

        similarities = []
        differences = []
        score = 50.0
        if position:
            similarities.append(f"Same position ({asset.player_position_at_trade}).")
            score += 20
        if midpoint is not None:
            distance = abs((asset.player_age_at_trade or midpoint) - midpoint)
            score += max(0, 20 - distance * 4)
            if distance <= 1:
                similarities.append(f"Age at trade ({asset.player_age_at_trade}) closely matches the requested range.")
            else:
                differences.append(f"Age at trade ({asset.player_age_at_trade}) is at the edge of the requested range.")
        score = max(0.0, min(100.0, score))

        other_assets = [
            a.label
            for a in db.query(TradeAsset).filter(TradeAsset.trade_id == trade.id).all()
            if a.id != asset.id
        ]

        results.append(
            ComparableTrade(
                trade_id=trade.id,
                date=str(trade.date),
                team_a=trade.team_a.abbreviation,
                team_b=trade.team_b.abbreviation,
                matching_player=asset.label,
                matching_position=asset.player_position_at_trade or "",
                matching_age_at_trade=asset.player_age_at_trade or 0,
                similarity_score=round(score, 1),
                similarities=similarities or ["Matches the requested search criteria."],
                differences=differences or ["No significant differences identified from the fields tracked."],
                other_assets=other_assets,
                outcome_note=trade.notes,
            )
        )

    results.sort(key=lambda r: r.similarity_score, reverse=True)
    return results[:limit]
