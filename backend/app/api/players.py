from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.analytics.player_valuation import compute_position_average_aav, evaluate_player
from app.config import settings
from app.database.session import get_db
from app.models.contract import Contract
from app.models.player import Player
from app.models.player_statistic import PlayerStatistic
from app.schemas.player import PlayerDetailOut, PlayerOut

router = APIRouter(prefix="/api/players", tags=["players"])


@router.get("", response_model=list[PlayerOut])
def list_players(
    team_id: int | None = None,
    position: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Player)
    if team_id is not None:
        query = query.filter(Player.team_id == team_id)
    if position is not None:
        query = query.filter(Player.position == position.upper())
    return query.order_by(Player.name).all()


@router.get("/{player_id}", response_model=PlayerDetailOut)
def get_player(player_id: int, db: Session = Depends(get_db)):
    player = db.get(Player, player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    seasons = db.query(PlayerStatistic).filter(PlayerStatistic.player_id == player_id).all()
    contract = db.query(Contract).filter(Contract.player_id == player_id).first()
    league_avg_aav = compute_position_average_aav(db)
    result = evaluate_player(player, seasons, contract, league_avg_aav)

    out = PlayerOut.model_validate(player).model_dump()
    out["valuation"] = {
        "model_version": settings.player_valuation_model_version,
        "valuation": result.valuation,
        "performance_score": result.performance_score,
        "projection_score": result.projection_score,
        "age_score": result.age_score,
        "position_score": result.position_score,
        "contract_score": result.contract_score,
        "availability_score": result.availability_score,
        "scarcity_score": result.scarcity_score,
        "trajectory_score": result.trajectory_score,
        "confidence": result.confidence,
    }
    out["valuation_explanation"] = {
        "positive_drivers": result.positive_drivers,
        "negative_drivers": result.negative_drivers,
        "notes": result.notes,
    }
    return out
