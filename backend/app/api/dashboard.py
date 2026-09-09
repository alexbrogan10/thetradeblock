"""Front Office Dashboard aggregate endpoints (Section 6).

Everything here is derived from whatever data is loaded (demo or real) --
nothing is hard-coded, and no output implies a trade "will happen."
"""
from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.analytics.draft_pick_valuation import evaluate_draft_pick
from app.analytics.player_valuation import compute_position_average_aav, evaluate_player
from app.config import settings
from app.database.session import get_db
from app.models.contract import Contract
from app.models.draft_pick import DraftPick
from app.models.player import Player
from app.models.player_statistic import PlayerStatistic
from app.models.team import Team

router = APIRouter(prefix="/api/analytics", tags=["dashboard"])


@router.get("/dashboard")
def dashboard_overview(db: Session = Depends(get_db)):
    players = db.query(Player).filter(Player.status == "active").all()
    league_avg_aav = compute_position_average_aav(db)

    valuations = []
    for player in players:
        seasons = db.query(PlayerStatistic).filter(PlayerStatistic.player_id == player.id).all()
        contract = db.query(Contract).filter(Contract.player_id == player.id).first()
        result = evaluate_player(player, seasons, contract, league_avg_aav)
        valuations.append((player, result))

    valuations.sort(key=lambda pv: pv[1].valuation, reverse=True)
    top_players = [
        {
            "player_id": p.id,
            "name": p.name,
            "position": p.position,
            "team": p.team.abbreviation if p.team else None,
            "valuation": v.valuation,
            "confidence": v.confidence,
        }
        for p, v in valuations[:10]
    ]

    position_totals = defaultdict(list)
    for p, v in valuations:
        position_totals[p.position].append(v.valuation)
    positions_by_value = sorted(
        (
            {"position": pos, "average_valuation": round(sum(vals) / len(vals), 1), "count": len(vals)}
            for pos, vals in position_totals.items()
        ),
        key=lambda x: x["average_valuation"],
        reverse=True,
    )

    discrepancies = []
    for p, v in valuations:
        contract = db.query(Contract).filter(Contract.player_id == p.id).first()
        if contract and contract.annual_value > 0:
            expected_score_for_pay = min(100.0, (contract.annual_value / max(league_avg_aav.get(p.position, 8.0), 0.1)) * 50)
            discrepancy = v.valuation - expected_score_for_pay
            if abs(discrepancy) >= 12:
                discrepancies.append(
                    {
                        "player_id": p.id,
                        "name": p.name,
                        "position": p.position,
                        "team": p.team.abbreviation if p.team else None,
                        "analytical_value": v.valuation,
                        "expected_value_for_cost": round(expected_score_for_pay, 1),
                        "potential_discrepancy": round(discrepancy, 1),
                    }
                )
    discrepancies.sort(key=lambda d: abs(d["potential_discrepancy"]), reverse=True)

    teams = db.query(Team).all()
    draft_capital_by_team = []
    for team in teams:
        picks = db.query(DraftPick).filter(DraftPick.current_team_id == team.id).all()
        total_value = sum(
            evaluate_draft_pick(pk.year, pk.round, pk.overall_pick).average_value for pk in picks
        )
        draft_capital_by_team.append(
            {"team_id": team.id, "team": team.abbreviation, "pick_count": len(picks), "estimated_total_value": round(total_value, 0)}
        )
    draft_capital_by_team.sort(key=lambda t: t["estimated_total_value"], reverse=True)

    alerts = []
    for d in discrepancies[:5]:
        direction = "above" if d["potential_discrepancy"] > 0 else "below"
        alerts.append(
            f"Model identifies a potential value discrepancy for {d['name']} "
            f"({d['position']}, {d['team']}): analytical value is {direction} what the "
            "current contract cost would imply."
        )
    for p, v in valuations:
        if v.confidence < 45:
            alerts.append(f"Low-confidence valuation for {p.name} — limited underlying data.")
    for p, v in valuations:
        contract = db.query(Contract).filter(Contract.player_id == p.id).first()
        if contract and contract.years_remaining <= 1 and v.valuation >= 70:
            alerts.append(f"{p.name} ({p.team.abbreviation if p.team else '—'}) is a high-value player entering the final year of his contract — worth further evaluation.")

    return {
        "demo_mode": settings.demo_mode,
        "player_valuation_model_version": settings.player_valuation_model_version,
        "trade_market": {
            "highest_value_players": top_players,
            "positions_commanding_value": positions_by_value,
        },
        "team_opportunities": {
            "draft_capital_by_team": draft_capital_by_team[:8],
            "limited_draft_capital_teams": sorted(draft_capital_by_team, key=lambda t: t["estimated_total_value"])[:5],
        },
        "model_alerts": alerts[:12] or ["No significant alerts identified from current data."],
        "value_discrepancies": discrepancies[:10],
    }
