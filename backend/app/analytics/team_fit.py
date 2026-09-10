"""Full Team Fit Engine (Section 17).

Replaces the Phase 1 "basic" roster-depth-only heuristic
(docs/team_fit_methodology.md) with a model that incorporates:

  1. The Team Needs Engine's need score at the player's position
     (Section 18) -- the dominant factor.
  2. Age alignment with the team's Competitive Window classification
     (Section 20) -- a young player fits a rebuild better than a
     32-year-old, and vice versa for a Win Now roster.
  3. Contract-length fit -- a long, cheap contract suits a team that
     isn't trying to win immediately; a short, tradeable one suits a
     team that is.

Every score returned includes a plain-language explanation of what drove
it, per Section 17's example ("Team A receives a higher fit score
because...").
"""
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.analytics.competitive_window import TimelineResult
from app.analytics.team_needs import PositionNeed
from app.models.contract import Contract
from app.models.player import Player


@dataclass
class TeamFitResult:
    score: float
    explanation: str


_TIMELINE_AGE_TARGET = {
    "Win Now": 27,
    "Contender": 28,
    "Competitive": 27,
    "Developing": 25,
    "Rebuilding": 24,
}


def _age_component(classification: str, age: int) -> float:
    target = _TIMELINE_AGE_TARGET.get(classification, 27)
    distance = abs(age - target)
    return max(10.0, 100.0 - distance * 9.0)


def _contract_component(classification: str, contract: Contract | None) -> float:
    if contract is None:
        return 50.0
    long_term_friendly = classification in ("Developing", "Rebuilding")
    if long_term_friendly:
        # Longer runway is worth more to a team not trying to win this year.
        return max(10.0, min(100.0, 40 + contract.years_remaining * 12))
    # Win Now / Contender / Competitive: length matters less than not
    # being saddled with a long, immovable commitment.
    if contract.years_remaining <= 3:
        return 80.0
    return max(20.0, 80.0 - (contract.years_remaining - 3) * 15)


def compute_team_fit(
    player: Player,
    contract: Contract | None,
    position_need: PositionNeed | None,
    timeline: TimelineResult,
) -> TeamFitResult:
    need_score = position_need.need_score if position_need else 50.0
    age_score = _age_component(timeline.classification, player.age)
    contract_score = _contract_component(timeline.classification, contract)

    score = 0.55 * need_score + 0.30 * age_score + 0.15 * contract_score
    score = max(5.0, min(100.0, score))

    reasons = []
    if position_need:
        reasons.append(
            f"{player.position} is graded a '{position_need.priority}' for this roster"
            f" (need score {position_need.need_score:.0f}/100)."
        )
    if age_score >= 80:
        reasons.append(f"Age {player.age} aligns well with a {timeline.classification.lower()} timeline.")
    elif age_score <= 40:
        reasons.append(f"Age {player.age} is a mismatch for a {timeline.classification.lower()} timeline.")
    if contract is not None:
        if contract_score >= 70:
            reasons.append("Contract length/structure fits the team's timeline well.")
        elif contract_score <= 35:
            reasons.append("Contract length/structure is a mismatch for the team's timeline.")
    else:
        reasons.append("No contract on file; assumed timeline-neutral.")

    explanation = " ".join(reasons)
    return TeamFitResult(score=round(score, 1), explanation=explanation)
