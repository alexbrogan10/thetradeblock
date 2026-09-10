"""Roster Impact (Section 19).

A trade should not be evaluated only by looking at the assets
exchanged -- this computes a before/after positional-strength view for
every position touched by a hypothetical trade.

Positional strength (0-100) is a depth-aware score: the best player at
the position contributes most, a quality second option adds some
additional strength, beyond which additional depth adds little. This
mirrors how an actual depth chart matters (a great starter with no
backup is more fragile than the raw "sum" would suggest).
"""
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.analytics.player_valuation import bulk_evaluate_players
from app.models.player import Player


@dataclass
class PositionImpact:
    position: str
    before: float
    after: float
    change: float


def _positional_strength(valuations: list[float]) -> float:
    if not valuations:
        return 0.0
    ordered = sorted(valuations, reverse=True)
    top = ordered[0]
    second = ordered[1] if len(ordered) > 1 else 0.0
    rest_bonus = min(5.0, 1.5 * (len(ordered) - 2)) if len(ordered) > 2 else 0.0
    return round(min(100.0, top * 0.7 + second * 0.25 + rest_bonus), 1)


def compute_roster_impact(
    db: Session,
    team_id: int,
    given_player_ids: list[int],
    received_players: list[Player],
    league_avg_aav: dict,
) -> list[PositionImpact]:
    roster = db.query(Player).filter(Player.team_id == team_id, Player.status == "active").all()

    all_players = list({p.id: p for p in (roster + received_players)}.values())
    valuation_by_id = bulk_evaluate_players(db, all_players, league_avg_aav)

    def valuation_of(player: Player) -> float:
        return valuation_by_id[player.id].valuation

    positions = {p.position for p in roster} | {p.position for p in received_players}

    results = []
    for position in sorted(positions):
        before_players = [p for p in roster if p.position == position]
        before_score = _positional_strength([valuation_of(p) for p in before_players])

        after_players = [p for p in before_players if p.id not in given_player_ids]
        after_players += [p for p in received_players if p.position == position]
        after_score = _positional_strength([valuation_of(p) for p in after_players])

        results.append(
            PositionImpact(
                position=position,
                before=before_score,
                after=after_score,
                change=round(after_score - before_score, 1),
            )
        )

    results.sort(key=lambda r: abs(r.change), reverse=True)
    return results
