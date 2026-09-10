#!/usr/bin/env python3
"""Loads data/raw/*.csv into PostgreSQL and computes an initial snapshot
of player valuations (Section 35 - Data Pipeline).

Pipeline stages implemented here:
  1. Load raw CSVs
  2. Validate required columns / drop rows with missing required fields
  3. Standardize position codes (uppercase, trimmed)
  4. Load teams -> players -> stats -> contracts -> draft picks
  5. Compute and persist a PlayerValuation snapshot per player
     (model version stamped for auditability, Section 40)

Run from the backend/ directory (or with PYTHONPATH set to backend/) so
`app` is importable, e.g.:

    cd backend && python ../scripts/seed_demo_data.py
"""
import ast
import sys
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "backend"))

from app.analytics.player_valuation import (  # noqa: E402
    MODEL_VERSION,
    compute_position_average_aav,
    evaluate_player,
)
from app.database.base import Base  # noqa: E402
from app.database.session import SessionLocal, engine  # noqa: E402
import app.models as _all_models  # noqa: E402,F401  (registers every model on Base.metadata)
from app.models.contract import Contract  # noqa: E402
from app.models.draft_pick import DraftPick  # noqa: E402
from app.models.historical_trade import HistoricalTrade, TradeAsset  # noqa: E402
from app.models.model_version import ModelVersion  # noqa: E402
from app.models.player import Player  # noqa: E402
from app.models.player_statistic import PlayerStatistic  # noqa: E402
from app.models.team import Team  # noqa: E402
from app.models.valuation import PlayerValuation  # noqa: E402
from app.analytics.position_tables import PRODUCTION_WEIGHTS  # noqa: E402
from app.config import settings  # noqa: E402

RAW_DIR = REPO_ROOT / "data" / "raw"


def load_csv(name: str) -> pd.DataFrame:
    path = RAW_DIR / name
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Run scripts/generate_demo_data.py first."
        )
    return pd.read_csv(path)


def parse_stats_json(raw: str) -> dict:
    if pd.isna(raw):
        return {}
    try:
        return ast.literal_eval(raw)
    except (ValueError, SyntaxError):
        return {}


def main():
    print("Creating tables (if not already present)...")
    Base.metadata.create_all(bind=engine)

    teams_df = load_csv("teams.csv")
    players_df = load_csv("players.csv")
    stats_df = load_csv("player_stats.csv")
    contracts_df = load_csv("contracts.csv")
    draft_df = load_csv("draft_picks.csv")
    historical_trades_df = load_csv("historical_trades.csv")
    historical_assets_df = load_csv("historical_trade_assets.csv")

    players_df["position"] = players_df["position"].str.upper().str.strip()

    db = SessionLocal()
    try:
        print("Clearing existing demo data...")
        # Delete in reverse dependency order so FK constraints never block a
        # re-seed, regardless of what a prior session (e.g. saved trade
        # scenarios) left behind.
        for table in reversed(Base.metadata.sorted_tables):
            db.execute(table.delete())
        db.commit()

        print(f"Loading {len(teams_df)} teams...")
        for row in teams_df.itertuples():
            db.add(
                Team(
                    id=row.id,
                    name=row.name,
                    abbreviation=row.abbreviation,
                    conference=row.conference,
                    division=row.division,
                )
            )
        db.commit()

        print(f"Loading {len(players_df)} players...")
        for row in players_df.itertuples():
            db.add(
                Player(
                    id=row.id,
                    name=row.name,
                    position=row.position,
                    team_id=None if pd.isna(row.team_id) else int(row.team_id),
                    age=int(row.age),
                    height_in=None if pd.isna(row.height_in) else int(row.height_in),
                    weight_lb=None if pd.isna(row.weight_lb) else int(row.weight_lb),
                    experience=int(row.experience),
                    status=row.status,
                )
            )
        db.commit()

        print(f"Loading {len(stats_df)} player-season stat lines...")
        for row in stats_df.itertuples():
            db.add(
                PlayerStatistic(
                    id=row.id,
                    player_id=row.player_id,
                    season=int(row.season),
                    games=int(row.games),
                    games_started=int(row.games_started),
                    stats=parse_stats_json(row.stats_json),
                )
            )
        db.commit()

        print(f"Loading {len(contracts_df)} contracts...")
        for row in contracts_df.itertuples():
            db.add(
                Contract(
                    id=row.id,
                    player_id=row.player_id,
                    years_remaining=int(row.years_remaining),
                    annual_value=float(row.annual_value),
                    guaranteed_money=float(row.guaranteed_money),
                    cap_hit=float(row.cap_hit),
                    contract_status=row.contract_status,
                )
            )
        db.commit()

        print(f"Loading {len(draft_df)} draft picks...")
        for row in draft_df.itertuples():
            overall_pick = None if pd.isna(row.overall_pick) else int(row.overall_pick)
            db.add(
                DraftPick(
                    id=row.id,
                    year=int(row.year),
                    round=int(row.round),
                    overall_pick=overall_pick,
                    original_team_id=int(row.original_team_id),
                    current_team_id=int(row.current_team_id),
                    estimated_value=0.0,
                )
            )
        db.commit()

        print(f"Loading {len(historical_trades_df)} historical trades...")
        for row in historical_trades_df.itertuples():
            db.add(
                HistoricalTrade(
                    id=row.id,
                    date=row.date,
                    team_a_id=int(row.team_a_id),
                    team_b_id=int(row.team_b_id),
                    notes=row.notes,
                )
            )
        db.commit()

        print(f"Loading {len(historical_assets_df)} historical trade assets...")
        for row in historical_assets_df.itertuples():
            db.add(
                TradeAsset(
                    id=row.id,
                    trade_id=int(row.trade_id),
                    team_from_id=int(row.team_from_id),
                    team_to_id=int(row.team_to_id),
                    asset_type=row.asset_type,
                    asset_id=int(row.asset_id),
                    label=row.label,
                    player_age_at_trade=None if pd.isna(row.player_age_at_trade) else int(row.player_age_at_trade),
                    player_position_at_trade=row.player_position_at_trade,
                    value_at_trade=float(row.value_at_trade),
                )
            )
        db.commit()

        from app.analytics.draft_pick_valuation import evaluate_draft_pick

        print("Computing draft-pick estimated values...")
        for pick in db.query(DraftPick).all():
            pick.estimated_value = evaluate_draft_pick(
                pick.year, pick.round, pick.overall_pick
            ).average_value
        db.commit()

        print("Computing initial player valuation snapshots...")
        league_avg_aav = compute_position_average_aav(db)
        players = db.query(Player).all()
        for player in players:
            seasons = (
                db.query(PlayerStatistic)
                .filter(PlayerStatistic.player_id == player.id)
                .all()
            )
            contract = (
                db.query(Contract).filter(Contract.player_id == player.id).first()
            )
            result = evaluate_player(player, seasons, contract, league_avg_aav)
            db.add(
                PlayerValuation(
                    player_id=player.id,
                    model_version=MODEL_VERSION,
                    valuation=result.valuation,
                    performance_score=result.performance_score,
                    projection_score=result.projection_score,
                    age_score=result.age_score,
                    position_score=result.position_score,
                    contract_score=result.contract_score,
                    availability_score=result.availability_score,
                    scarcity_score=result.scarcity_score,
                    trajectory_score=result.trajectory_score,
                    confidence=result.confidence,
                )
            )
        db.commit()

        print("Registering heuristic model versions (Section 39)...")
        db.add(
            ModelVersion(
                model_name="player-valuation",
                version="v1.0",
                features=list(PRODUCTION_WEIGHTS.keys()),
                parameters={
                    "weight_recent_performance": settings.weight_recent_performance,
                    "weight_projected_performance": settings.weight_projected_performance,
                    "weight_age": settings.weight_age,
                    "weight_position_value": settings.weight_position_value,
                    "weight_contract_efficiency": settings.weight_contract_efficiency,
                    "weight_availability": settings.weight_availability,
                    "weight_positional_scarcity": settings.weight_positional_scarcity,
                    "weight_trajectory": settings.weight_trajectory,
                },
                evaluation_metrics={},
                dataset_version="demo-synthetic-v1",
                limitations=[
                    "A transparent weighted-formula model, not fit against real outcome "
                    "data -- there are no accuracy metrics to report (see "
                    "docs/valuation_methodology.md).",
                ],
            )
        )
        db.add(
            ModelVersion(
                model_name="draft-pick-traditional",
                version="v1.0",
                features=["round", "overall_pick", "year"],
                parameters={"base": 3000.0, "decay": 0.075},
                evaluation_metrics={},
                dataset_version="demo-synthetic-v1",
                limitations=[
                    "An original approximation of public draft-chart shapes, not a "
                    "reproduction of any real team's proprietary chart (see "
                    "docs/draft_capital_methodology.md).",
                ],
            )
        )
        db.commit()

        print("Done. Demo data loaded successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
