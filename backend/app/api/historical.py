from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.analytics.historical_trades import find_comparable_trades
from app.database.session import get_db
from app.models.historical_trade import HistoricalTrade, TradeAsset
from app.models.team import Team
from app.schemas.historical import ComparableTradeOut, HistoricalTradeDetailOut

router = APIRouter(prefix="/api/historical-trades", tags=["historical-trades"])


@router.get("/comparable", response_model=list[ComparableTradeOut])
def comparable_trades(
    position: str | None = None,
    age_min: int | None = Query(None, ge=18),
    age_max: int | None = Query(None, le=50),
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db),
):
    """Section 24 - search for historical trades comparable to a given
    profile (e.g. "WR trades involving players ages 25-28")."""
    results = find_comparable_trades(db, position=position, age_min=age_min, age_max=age_max, limit=limit)
    return [r.__dict__ for r in results]


@router.get("/{trade_id}", response_model=HistoricalTradeDetailOut)
def get_historical_trade(trade_id: int, db: Session = Depends(get_db)):
    trade = db.get(HistoricalTrade, trade_id)
    if trade is None:
        raise HTTPException(status_code=404, detail="Historical trade not found")
    assets = db.query(TradeAsset).filter(TradeAsset.trade_id == trade_id).all()
    return {
        "id": trade.id,
        "date": str(trade.date),
        "team_a": trade.team_a.abbreviation,
        "team_b": trade.team_b.abbreviation,
        "notes": trade.notes,
        "assets": [
            {
                "asset_type": a.asset_type,
                "label": a.label,
                "team_from": db.get(Team, a.team_from_id).abbreviation,
                "team_to": db.get(Team, a.team_to_id).abbreviation,
                "player_age_at_trade": a.player_age_at_trade,
                "player_position_at_trade": a.player_position_at_trade,
            }
            for a in assets
        ],
    }
