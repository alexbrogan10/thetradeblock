from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.analytics.trade_finder import find_trade_targets
from app.database.session import get_db
from app.schemas.finder import TradeFinderRequest, TradeTargetOut

router = APIRouter(prefix="/api/trades", tags=["trade-finder"])


@router.post("/finder", response_model=list[TradeTargetOut])
def trade_finder(request: TradeFinderRequest, db: Session = Depends(get_db)):
    try:
        results = find_trade_targets(
            db,
            team_id=request.team_id,
            position=request.position,
            max_acquisition_cost=request.max_acquisition_cost,
            age_preference=request.age_preference,
            risk_tolerance=request.risk_tolerance,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return [r.__dict__ for r in results]
