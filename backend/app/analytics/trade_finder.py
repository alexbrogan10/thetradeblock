"""Trade Finder (Section 23).

Surfaces *analytical matches* for a stated need -- never a prediction
that a specific trade will actually happen (Rule 56 #13).
"""
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.analytics.acquisition_cost import estimate_acquisition_range
from app.analytics.competitive_window import classify_team_timeline
from app.analytics.player_valuation import compute_position_average_aav, evaluate_player
from app.analytics.risk import assess_players_risk
from app.analytics.team_fit import compute_team_fit
from app.analytics.team_needs import evaluate_team_needs
from app.models.contract import Contract
from app.models.player import Player
from app.models.player_statistic import PlayerStatistic
from app.models.team import Team

RISK_ORDER = {"Low": 0, "Moderate": 1, "High": 2}
AGE_BUCKETS = {
    "young": lambda age: age <= 25,
    "prime": lambda age: 26 <= age <= 29,
    "veteran": lambda age: age >= 30,
}


@dataclass
class TradeTarget:
    player_id: int
    name: str
    position: str
    team: str | None
    age: int
    fit_score: float
    fit_explanation: str
    analytical_value: float
    estimated_cost_low: str
    estimated_cost_high: str
    cost_confidence: str
    contract_fit_note: str
    risk_level: str


def find_trade_targets(
    db: Session,
    team_id: int,
    position: str,
    max_acquisition_cost: float | None = None,
    age_preference: str | None = None,
    risk_tolerance: str | None = None,
    limit: int = 10,
) -> list[TradeTarget]:
    team = db.get(Team, team_id)
    if team is None:
        raise ValueError(f"Team {team_id} does not exist.")

    team_needs = evaluate_team_needs(db, team_id)
    position_need = next((n for n in team_needs if n.position == position.upper()), None)
    timeline = classify_team_timeline(db, team)
    league_avg_aav = compute_position_average_aav(db)

    candidates = (
        db.query(Player)
        .filter(
            Player.position == position.upper(),
            Player.status == "active",
            Player.team_id != team_id,
        )
        .all()
    )

    age_filter = AGE_BUCKETS.get(age_preference) if age_preference else None
    max_risk_rank = RISK_ORDER.get(risk_tolerance) if risk_tolerance else None

    results: list[TradeTarget] = []
    for candidate in candidates:
        if age_filter and not age_filter(candidate.age):
            continue

        seasons = db.query(PlayerStatistic).filter(PlayerStatistic.player_id == candidate.id).all()
        contract = db.query(Contract).filter(Contract.player_id == candidate.id).first()
        valuation = evaluate_player(candidate, seasons, contract, league_avg_aav)

        if max_acquisition_cost is not None and valuation.valuation > max_acquisition_cost:
            continue

        risk_level, _, _ = assess_players_risk([(candidate, valuation)])
        if max_risk_rank is not None and RISK_ORDER[risk_level] > max_risk_rank:
            continue

        fit = compute_team_fit(candidate, contract, position_need, timeline)
        acquisition = estimate_acquisition_range(valuation.valuation, valuation.confidence)

        if contract is None:
            contract_note = "No contract data on file."
        elif contract.years_remaining <= 1:
            contract_note = "Expiring contract -- likely available at lower acquisition cost, but limited long-term control."
        elif contract.years_remaining >= 4:
            contract_note = "Long-term contract -- higher control, but likely higher acquisition cost."
        else:
            contract_note = "Moderate contract term."

        results.append(
            TradeTarget(
                player_id=candidate.id,
                name=candidate.name,
                position=candidate.position,
                team=candidate.team.abbreviation if candidate.team else None,
                age=candidate.age,
                fit_score=fit.score,
                fit_explanation=fit.explanation,
                analytical_value=valuation.valuation,
                estimated_cost_low=acquisition.low_label,
                estimated_cost_high=acquisition.high_label,
                cost_confidence=acquisition.confidence,
                contract_fit_note=contract_note,
                risk_level=risk_level,
            )
        )

    results.sort(key=lambda r: r.fit_score, reverse=True)
    return results[:limit]
