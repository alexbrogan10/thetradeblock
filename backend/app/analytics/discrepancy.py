"""Trade Value Discrepancy Finder (Section 16).

Compares analytical player value against an expected-cost proxy derived
from the player's own contract relative to league-average pay at the
position. This is intentionally framed as "the model identifies a
potential value discrepancy," never "Player X is objectively
undervalued" (Rule 56 #13).
"""
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.analytics.player_valuation import bulk_evaluate_players, compute_position_average_aav
from app.models.contract import Contract
from app.models.player import Player


@dataclass
class Discrepancy:
    player_id: int
    name: str
    position: str
    team: str | None
    analytical_value: float
    expected_value_for_cost: float
    potential_discrepancy: float
    drivers: list[str]


def find_value_discrepancies(
    db: Session,
    min_abs_discrepancy: float = 12.0,
    position: str | None = None,
    limit: int = 25,
) -> list[Discrepancy]:
    query = db.query(Player).filter(Player.status == "active")
    if position:
        query = query.filter(Player.position == position.upper())
    players = query.all()

    league_avg_aav = compute_position_average_aav(db)
    contract_by_id = {
        c.player_id: c for c in db.query(Contract).filter(Contract.player_id.in_([p.id for p in players])).all()
    }
    valuation_by_id = bulk_evaluate_players(db, players, league_avg_aav)
    results: list[Discrepancy] = []

    for player in players:
        contract = contract_by_id.get(player.id)
        if not contract or contract.annual_value <= 0:
            continue

        valuation = valuation_by_id[player.id]

        expected_score_for_pay = min(
            100.0, (contract.annual_value / max(league_avg_aav.get(player.position, 8.0), 0.1)) * 50
        )
        discrepancy = valuation.valuation - expected_score_for_pay
        if abs(discrepancy) < min_abs_discrepancy:
            continue

        drivers = []
        if discrepancy > 0:
            drivers.append("Analytical value exceeds what the current contract cost would imply.")
            drivers.extend(valuation.positive_drivers[:2])
        else:
            drivers.append("Contract cost exceeds what analytical value would imply.")
            drivers.extend(valuation.negative_drivers[:2])

        results.append(
            Discrepancy(
                player_id=player.id,
                name=player.name,
                position=player.position,
                team=player.team.abbreviation if player.team else None,
                analytical_value=valuation.valuation,
                expected_value_for_cost=round(expected_score_for_pay, 1),
                potential_discrepancy=round(discrepancy, 1),
                drivers=drivers,
            )
        )

    results.sort(key=lambda d: abs(d.potential_discrepancy), reverse=True)
    return results[:limit]
