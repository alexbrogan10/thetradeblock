"""Acquisition Cost Estimator (Section 15).

Translates a player's analytical value into an estimated draft-capital
range using the same chart used for draft-pick valuation, framed
explicitly as a *model estimate*, never a team's actual asking price
(Rule 56 #15, Section 15's "Model Estimated Acquisition Range" label).
"""
from dataclasses import dataclass

from app.analytics.draft_pick_valuation import (
    PICK_POINTS_TO_ASSET_SCALE,
    TRADITIONAL_BASE,
    TRADITIONAL_DECAY,
)

MAX_PICK = 224  # end of a 7-round draft


@dataclass
class AcquisitionRange:
    low_label: str
    high_label: str
    confidence: str


def _points_to_pick_number(points: float) -> int:
    # Inverse of the Traditional Model's _traditional(pick) formula.
    if points <= 0:
        return MAX_PICK
    pick = ((TRADITIONAL_BASE / points) - 1) / TRADITIONAL_DECAY + 1
    return max(1, min(MAX_PICK, round(pick)))


def _pick_label(pick_number: int) -> str:
    round_number = min(7, (pick_number - 1) // 32 + 1)
    slot_in_round = (pick_number - 1) % 32 + 1
    if slot_in_round <= 11:
        timing = "Early"
    elif slot_in_round <= 21:
        timing = "Mid"
    else:
        timing = "Late"
    return f"{timing} {round_number}{_ordinal_suffix(round_number)} Round"


def _ordinal_suffix(n: int) -> str:
    return {1: "st", 2: "nd", 3: "rd"}.get(n if n < 20 else n % 10, "th")


def _confidence_label(valuation_confidence: float) -> str:
    if valuation_confidence >= 75:
        return "High"
    if valuation_confidence >= 50:
        return "Moderate"
    return "Low"


def estimate_acquisition_range(valuation: float, valuation_confidence: float) -> AcquisitionRange:
    chart_points = max(1.0, valuation * PICK_POINTS_TO_ASSET_SCALE)
    high_points = chart_points * 1.2  # better (earlier-pick-equivalent) end
    low_points = chart_points * 0.8  # more modest end

    better_pick = _points_to_pick_number(high_points)
    modest_pick = _points_to_pick_number(low_points)

    return AcquisitionRange(
        low_label=_pick_label(better_pick),
        high_label=_pick_label(modest_pick),
        confidence=_confidence_label(valuation_confidence),
    )
