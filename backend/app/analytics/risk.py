"""Shared player-risk scoring (Section 22), factored out so both the
Trade Engine and the Trade Finder use the same definition of risk for a
player rather than two independently-drifting heuristics.

Never labels a player a "bust" (Rule 56) -- risk is about uncertainty in
the trade, not a verdict on a career.
"""
from dataclasses import dataclass


@dataclass
class PlayerRiskComponents:
    age_risk: float
    contract_risk: float
    availability_risk: float
    confidence_risk: float

    @property
    def overall(self) -> float:
        return (self.age_risk + self.contract_risk + self.availability_risk + self.confidence_risk) / 4


def player_risk_components(valuation) -> PlayerRiskComponents:
    return PlayerRiskComponents(
        age_risk=100 - valuation.age_score,
        contract_risk=100 - valuation.contract_score,
        availability_risk=100 - valuation.availability_score,
        confidence_risk=100 - valuation.confidence,
    )


def risk_level_for_score(score: float) -> str:
    if score < 35:
        return "Low"
    if score < 65:
        return "Moderate"
    return "High"


def assess_players_risk(players_and_valuations: list[tuple[object, object]]):
    """players_and_valuations: list of (player, ValuationResult) tuples."""
    if not players_and_valuations:
        return "Low", ["No players in this evaluation."], ["No on-field player risk to mitigate."]

    components_list = [player_risk_components(v) for _, v in players_and_valuations]

    def _avg(attr: str) -> float:
        return sum(getattr(c, attr) for c in components_list) / len(components_list)

    named = {
        "Age curve": _avg("age_risk"),
        "Contract commitment": _avg("contract_risk"),
        "Availability history": _avg("availability_risk"),
        "Valuation uncertainty": _avg("confidence_risk"),
    }
    overall = sum(named.values()) / len(named)
    ranked = sorted(named.items(), key=lambda kv: kv[1], reverse=True)

    drivers = [name for name, score in ranked if score >= 55][:3]
    mitigators = [f"{name} is favorable" for name, score in ranked if score < 40][:3]
    if not drivers:
        drivers = ["No single risk factor stands out; overall risk is diffuse."]
    if not mitigators:
        mitigators = ["Limited mitigating factors identified from available data."]

    return risk_level_for_score(overall), drivers, mitigators
