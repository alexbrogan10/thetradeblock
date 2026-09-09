from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.analytics.draft_pick_valuation import evaluate_draft_pick
from app.database.session import get_db
from app.models.draft_pick import DraftPick
from app.schemas.draft_pick import DraftPickOut, DraftPickValueBreakdown

router = APIRouter(prefix="/api/draft-picks", tags=["draft-picks"])


@router.get("", response_model=list[DraftPickOut])
def list_draft_picks(
    team_id: int | None = None,
    year: int | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(DraftPick).options(
        joinedload(DraftPick.original_team), joinedload(DraftPick.current_team)
    )
    if team_id is not None:
        query = query.filter(DraftPick.current_team_id == team_id)
    if year is not None:
        query = query.filter(DraftPick.year == year)
    return query.order_by(DraftPick.year, DraftPick.round, DraftPick.overall_pick).all()


@router.get("/{pick_id}/valuation", response_model=DraftPickValueBreakdown)
def get_draft_pick_valuation(pick_id: int, db: Session = Depends(get_db)):
    pick = db.get(DraftPick, pick_id)
    if pick is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Draft pick not found")
    result = evaluate_draft_pick(pick.year, pick.round, pick.overall_pick)
    return DraftPickValueBreakdown(
        pick_label=result.pick_label,
        traditional_value=result.traditional_value,
        historical_value=result.historical_value,
        expected_value=result.expected_value,
        model_agreement=result.model_agreement,
    )
