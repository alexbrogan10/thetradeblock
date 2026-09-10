"""Team Needs Engine (Section 18).

Categorizes every position on a team's roster as Critical Need / Major
Need / Moderate Need / Minor Need / Strong Position, using only signals
already computed elsewhere in the app (player valuation, age, contract
status) -- never public rankings or invented scouting opinions (Rule 56
#18-19).
"""
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.analytics.player_valuation import bulk_evaluate_players, compute_position_average_aav
from app.analytics.position_tables import POSITION_VALUE
from app.models.contract import Contract
from app.models.player import Player

ALL_POSITIONS = list(POSITION_VALUE.keys())


@dataclass
class PositionNeed:
    position: str
    priority: str
    need_score: float
    current_depth: int
    starter_quality: float | None
    future_need: str
    reasons: list[str] = field(default_factory=list)


def _priority_label(score: float) -> str:
    if score >= 75:
        return "Critical Need"
    if score >= 55:
        return "Major Need"
    if score >= 35:
        return "Moderate Need"
    if score >= 15:
        return "Minor Need"
    return "Strong Position"


def evaluate_team_needs(db: Session, team_id: int) -> list[PositionNeed]:
    players = db.query(Player).filter(Player.team_id == team_id, Player.status == "active").all()
    league_avg_aav = compute_position_average_aav(db)

    by_position: dict[str, list[Player]] = {}
    for p in players:
        by_position.setdefault(p.position, []).append(p)

    valuation_by_id = bulk_evaluate_players(db, players, league_avg_aav)
    contract_by_id = {
        c.player_id: c for c in db.query(Contract).filter(Contract.player_id.in_([p.id for p in players])).all()
    } if players else {}

    results: list[PositionNeed] = []
    for position in ALL_POSITIONS:
        roster = by_position.get(position, [])
        depth = len(roster)
        reasons: list[str] = []

        if depth == 0:
            results.append(
                PositionNeed(
                    position=position,
                    priority="Critical Need",
                    need_score=100.0,
                    current_depth=0,
                    starter_quality=None,
                    future_need="Critical Need",
                    reasons=["No active player on the roster at this position."],
                )
            )
            continue

        valuations = [
            (player, contract_by_id.get(player.id), valuation_by_id[player.id]) for player in roster
        ]

        valuations.sort(key=lambda pv: pv[2].valuation, reverse=True)
        starter, starter_contract, starter_val = valuations[0]
        backup_val = valuations[1][2].valuation if depth > 1 else None

        need_score = max(0.0, 60.0 - starter_val.valuation * 0.6)
        if starter_val.valuation < 45:
            reasons.append(f"Current starter ({starter.name}) grades below league-average value.")

        if depth == 1:
            need_score += 15
            reasons.append("No backup depth at this position.")
        elif backup_val is not None and backup_val < 35:
            need_score += 8
            reasons.append("Backup depth is below replacement-level value.")

        expiring_soon = starter_contract is not None and starter_contract.years_remaining <= 1
        if expiring_soon and starter_val.valuation >= 55:
            need_score += 12
            reasons.append(f"{starter.name}'s contract expires soon, creating near-term uncertainty.")

        # Age/succession risk: a strong older starter with no young
        # replacement behind him is a *future* need even if not urgent now.
        aging_starter = starter.age >= 30
        young_backup_exists = any(
            v[0].age <= 25 and v[2].valuation >= 45 for v in valuations[1:]
        )
        if aging_starter and not young_backup_exists:
            need_score += 10
            reasons.append(f"Starter is {starter.age} with no clear young succession plan in place.")
        elif aging_starter and young_backup_exists:
            reasons.append("Aging starter, but a promising younger option is already on the roster.")

        need_score = max(0.0, min(100.0, need_score))
        priority = _priority_label(need_score)

        if aging_starter or expiring_soon:
            future_need = "Major Need" if need_score < 55 else priority
        else:
            future_need = priority

        if not reasons:
            reasons.append(f"{starter.name} is a solid, cost-effective option at this position.")

        results.append(
            PositionNeed(
                position=position,
                priority=priority,
                need_score=round(need_score, 1),
                current_depth=depth,
                starter_quality=round(starter_val.valuation, 1),
                future_need=future_need,
                reasons=reasons,
            )
        )

    results.sort(key=lambda r: r.need_score, reverse=True)
    return results
