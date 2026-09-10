from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.analytics.sensitivity import compute_sensitivity
from app.analytics.trade_engine import TradeValidationError, analyze_trade
from app.database.session import get_db
from app.schemas.trade import TradeAnalysisResult, TradeAnalyzeRequest

router = APIRouter(prefix="/api/trades", tags=["trades"])


@router.post("/analyze", response_model=TradeAnalysisResult)
def analyze(request: TradeAnalyzeRequest, db: Session = Depends(get_db)):
    try:
        result = analyze_trade(db, request.team_a, request.team_b)
    except TradeValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return result


class SensitivityRequest(TradeAnalyzeRequest):
    perspective_team_id: int


@router.post("/sensitivity")
def sensitivity(request: SensitivityRequest, db: Session = Depends(get_db)):
    if request.perspective_team_id not in (request.team_a.team_id, request.team_b.team_id):
        raise HTTPException(
            status_code=400, detail="perspective_team_id must be team_a or team_b's team_id."
        )
    try:
        return compute_sensitivity(db, request.team_a, request.team_b, request.perspective_team_id)
    except TradeValidationError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
