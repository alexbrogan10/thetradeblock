"""Competitive Window classifier (Section 20).

Classifies a team's timeline as Rebuilding / Developing / Competitive /
Contender / Win Now using only signals already available in the app:
roster age distribution, an on-the-fly "team strength" proxy (average
valuation of the best player at each position the team fields), and
future draft capital relative to the rest of the league. This is a
transparent heuristic, not a claim of insider knowledge about a team's
actual plans (Rule 56 #18-19).
"""
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.analytics.draft_pick_valuation import evaluate_draft_pick
from app.analytics.player_valuation import bulk_evaluate_players, compute_position_average_aav
from app.models.draft_pick import DraftPick
from app.models.player import Player
from app.models.team import Team

CLASSIFICATIONS_HIGH_TO_LOW = ["Win Now", "Contender", "Competitive", "Developing", "Rebuilding"]


@dataclass
class TimelineResult:
    classification: str
    timeline_score: float
    team_strength: float
    average_age: float
    veteran_pct: float
    young_pct: float
    draft_capital_percentile: float
    reasons: list[str] = field(default_factory=list)


def _team_strength(db: Session, players: list[Player], league_avg_aav: dict) -> float:
    if not players:
        return 50.0
    by_position: dict[str, list[Player]] = {}
    for p in players:
        by_position.setdefault(p.position, []).append(p)

    valuation_by_id = bulk_evaluate_players(db, players, league_avg_aav)
    starter_scores = []
    for position, roster in by_position.items():
        best = max(valuation_by_id[p.id].valuation for p in roster)
        starter_scores.append(best)
    return sum(starter_scores) / len(starter_scores) if starter_scores else 50.0


def _draft_capital_totals(db: Session) -> dict[int, float]:
    totals: dict[int, float] = {}
    picks = db.query(DraftPick).all()
    for pick in picks:
        value = evaluate_draft_pick(pick.year, pick.round, pick.overall_pick).average_value
        totals[pick.current_team_id] = totals.get(pick.current_team_id, 0.0) + value
    return totals


def classify_team_timeline(db: Session, team: Team) -> TimelineResult:
    players = db.query(Player).filter(Player.team_id == team.id, Player.status == "active").all()
    league_avg_aav = compute_position_average_aav(db)

    avg_age = sum(p.age for p in players) / len(players) if players else 27.0
    veteran_pct = (sum(1 for p in players if p.age >= 29) / len(players)) if players else 0.0
    young_pct = (sum(1 for p in players if p.age <= 24) / len(players)) if players else 0.0

    team_strength = _team_strength(db, players, league_avg_aav)

    totals = _draft_capital_totals(db)
    all_teams = db.query(Team.id).all()
    for (tid,) in all_teams:
        totals.setdefault(tid, 0.0)
    ranked = sorted(totals.values())
    team_total = totals.get(team.id, 0.0)
    rank_index = sum(1 for v in ranked if v <= team_total)
    draft_capital_percentile = 100.0 * rank_index / len(ranked) if ranked else 50.0

    veteran_lean_scaled = max(0.0, min(100.0, 50 + (veteran_pct - young_pct) * 100))

    timeline_score = (
        0.5 * team_strength
        + 0.3 * veteran_lean_scaled
        + 0.2 * (100 - draft_capital_percentile)
    )
    timeline_score = max(0.0, min(100.0, timeline_score))

    if timeline_score >= 75:
        classification = "Win Now"
    elif timeline_score >= 58:
        classification = "Contender"
    elif timeline_score >= 42:
        classification = "Competitive"
    elif timeline_score >= 25:
        classification = "Developing"
    else:
        classification = "Rebuilding"

    reasons = [
        f"Estimated team strength (avg. valuation of the best player at each position): {team_strength:.0f}/100.",
        f"Roster average age is {avg_age:.1f} ({veteran_pct*100:.0f}% age 29+, {young_pct*100:.0f}% age 24-or-younger).",
        f"Future draft capital ranks in the {draft_capital_percentile:.0f}th percentile league-wide.",
    ]

    return TimelineResult(
        classification=classification,
        timeline_score=round(timeline_score, 1),
        team_strength=round(team_strength, 1),
        average_age=round(avg_age, 1),
        veteran_pct=round(veteran_pct * 100, 1),
        young_pct=round(young_pct * 100, 1),
        draft_capital_percentile=round(draft_capital_percentile, 1),
        reasons=reasons,
    )
