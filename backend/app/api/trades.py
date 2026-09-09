from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

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
