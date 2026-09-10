from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.analytics.player_similarity import find_similar_players
from app.analytics.player_valuation import compute_position_average_aav, evaluate_player
from app.config import settings
from app.database.session import get_db
from app.ml.features import build_feature_row
from app.ml.performance_projection import predict_next_season_performance
from app.models.contract import Contract
from app.models.model_version import ModelVersion
from app.models.player import Player
from app.models.player_statistic import PlayerStatistic
from app.schemas.historical import SimilarPlayerOut
from app.schemas.ml import MLProjectionOut
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


@router.get("/{player_id}/similar", response_model=list[SimilarPlayerOut])
def get_similar_players(player_id: int, top_n: int = 5, db: Session = Depends(get_db)):
    try:
        results = find_similar_players(db, player_id, top_n=top_n)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return [r.__dict__ for r in results]


@router.get("/{player_id}/projection", response_model=MLProjectionOut)
def get_ml_projection(player_id: int, db: Session = Depends(get_db)):
    """Section 38 - ML Player Performance Projection. Separate from (and
    does not replace) the transparent heuristic projection used in the
    core valuation -- see docs/ml_documentation.md. Returns
    available=False with an explanatory note if the model hasn't been
    trained yet (scripts/train_performance_projection.py)."""
    player = db.get(Player, player_id)
    if player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    seasons = (
        db.query(PlayerStatistic)
        .filter(PlayerStatistic.player_id == player_id)
        .order_by(PlayerStatistic.season)
        .all()
    )
    contract = db.query(Contract).filter(Contract.player_id == player_id).first()
    latest_season = seasons[-1] if seasons else None

    feature_row = build_feature_row(player, latest_season, contract)
    prediction = predict_next_season_performance(feature_row)

    if prediction is None:
        return {
            "available": False,
            "note": (
                "ML projection model has not been trained yet. Run "
                "scripts/train_performance_projection.py after seeding demo data."
            ),
        }

    model_version = db.query(ModelVersion).filter(ModelVersion.model_name == "player-performance-projection").first()
    return {
        "available": True,
        "predicted_performance_score": prediction["predicted_performance_score"],
        "top_features": prediction["top_features"],
        "model_version": f"{model_version.model_name}-{model_version.version}" if model_version else None,
        "note": (
            "Model estimate based on a synthetic training set; not validated against "
            "real-world outcomes. Supports, but does not replace, the transparent "
            "heuristic projection used in the core valuation."
        ),
    }
