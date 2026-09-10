"""Team-scoped analytics endpoints (Section 46): needs, competitive
window, draft capital dashboard, and roster impact."""
from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.analytics.competitive_window import classify_team_timeline
from app.analytics.draft_pick_valuation import evaluate_draft_pick
from app.analytics.player_valuation import compute_position_average_aav
from app.analytics.roster_impact import compute_roster_impact
from app.analytics.team_needs import evaluate_team_needs
from app.analytics.trade_finder import find_trade_targets
from app.database.session import get_db
from app.models.draft_pick import DraftPick
from app.models.player import Player
from app.models.team import Team
from app.schemas.finder import TradeTargetOut
from app.schemas.team import (
    DraftCapitalOut,
    DraftCapitalYearOut,
    RosterImpactOut,
    TeamNeedsOut,
    TimelineOut,
)

router = APIRouter(prefix="/api/team", tags=["team"])


def _get_team_or_404(db: Session, team_id: int) -> Team:
    team = db.get(Team, team_id)
    if team is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.get("/{team_id}/needs", response_model=TeamNeedsOut)
def get_team_needs(team_id: int, db: Session = Depends(get_db)):
    team = _get_team_or_404(db, team_id)
    needs = evaluate_team_needs(db, team_id)
    return {"team": team, "needs": needs}


@router.get("/{team_id}/timeline", response_model=TimelineOut)
def get_team_timeline(team_id: int, db: Session = Depends(get_db)):
    team = _get_team_or_404(db, team_id)
    result = classify_team_timeline(db, team)
    return {"team": team, **result.__dict__}


def _build_draft_capital(team: Team, picks: list[DraftPick]) -> dict:
    by_year: dict[int, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    value_by_year: dict[int, float] = defaultdict(float)
    total_value = 0.0
    for pick in picks:
        valuation = evaluate_draft_pick(pick.year, pick.round, pick.overall_pick)
        by_year[pick.year][f"round_{pick.round}"] += 1
        value_by_year[pick.year] += valuation.average_value
        total_value += valuation.average_value

    years_out = [
        DraftCapitalYearOut(
            year=year,
            by_round=dict(sorted(rounds.items())),
            estimated_value=round(value_by_year[year], 0),
        )
        for year, rounds in sorted(by_year.items())
    ]

    return {
        "team": team,
        "total_picks": len(picks),
        "estimated_total_value": round(total_value, 0),
        "by_year": years_out,
    }


@router.get("/{team_id}/draft-capital", response_model=DraftCapitalOut)
def get_team_draft_capital(team_id: int, db: Session = Depends(get_db)):
    team = _get_team_or_404(db, team_id)
    picks = db.query(DraftPick).filter(DraftPick.current_team_id == team_id).all()
    return _build_draft_capital(team, picks)


@router.get("/{team_id}/trade-matches")
def get_trade_matches(team_id: int, db: Session = Depends(get_db)):
    """Section 38 - Trade Matching: automatically surfaces analytical
    fits for whichever positions the Team Needs Engine currently grades
    Critical or Major Need, reusing the same Trade Finder used when a
    user manually searches by position (Section 23) -- so this is never
    a second, independently-drifting notion of "fit.\""""
    team = _get_team_or_404(db, team_id)
    needs = evaluate_team_needs(db, team_id)
    priority_needs = [n for n in needs if n.priority in ("Critical Need", "Major Need")]

    matches = []
    for need in priority_needs:
        targets = find_trade_targets(db, team_id=team_id, position=need.position, limit=3)
        if targets:
            matches.append(
                {
                    "position": need.position,
                    "priority": need.priority,
                    "need_score": need.need_score,
                    "targets": [TradeTargetOut(**t.__dict__).model_dump() for t in targets],
                }
            )

    return {"team": team, "matches": matches}


@router.get("/{team_id}/roster-impact", response_model=RosterImpactOut)
def get_roster_impact(
    team_id: int,
    players_out: str = Query("", description="Comma-separated player ids leaving the roster"),
    players_in: str = Query("", description="Comma-separated player ids joining the roster"),
    db: Session = Depends(get_db),
):
    team = _get_team_or_404(db, team_id)

    out_ids = [int(x) for x in players_out.split(",") if x.strip()]
    in_ids = [int(x) for x in players_in.split(",") if x.strip()]
    received_players = db.query(Player).filter(Player.id.in_(in_ids)).all() if in_ids else []

    league_avg_aav = compute_position_average_aav(db)
    impact = compute_roster_impact(db, team_id, out_ids, received_players, league_avg_aav)
    return {
        "team": team,
        "impact": [{"position": r.position, "before": r.before, "after": r.after, "change": r.change} for r in impact],
    }
