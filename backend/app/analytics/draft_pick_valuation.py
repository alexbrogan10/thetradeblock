"""Configurable draft-pick valuation (Section 13).

Three independent curves are computed for every pick so the UI can show
*model disagreement* rather than pretending a single chart is correct
(Section 3, Section 13). None of these reproduce any specific
copyrighted/proprietary team's draft chart -- they are original,
documented approximations of the well-known shape of public draft value
curves (steep early falloff, long flat tail), intended for relative
comparison rather than exact historical accuracy.

- Traditional Model: steep early falloff, mirrors classic pick-trade
  charts where top-10 picks are valued very highly relative to Day 3.
- Historical Model: flatter falloff, consistent with published research
  showing surplus value is more evenly distributed than trade charts
  suggest.
- Expected Value Model: intermediate curve, meant to approximate expected
  future on-field contribution.

For future picks with no assigned slot yet, the pick is valued at the
midpoint of its round (assumption clearly noted) since we cannot know a
team's future draft position.
"""
import math
from dataclasses import dataclass

ROUND_MIDPOINT_SLOT = {1: 16, 2: 48, 3: 80, 4: 112, 5: 144, 6: 176, 7: 208}


@dataclass
class DraftPickValuation:
    pick_label: str
    traditional_value: float
    historical_value: float
    expected_value: float
    average_value: float
    model_agreement: str


def _effective_pick_number(round_: int, overall_pick: int | None) -> int:
    if overall_pick:
        return overall_pick
    return ROUND_MIDPOINT_SLOT.get(round_, (round_ - 1) * 32 + 16)


TRADITIONAL_BASE = 3000.0
TRADITIONAL_DECAY = 0.075


def _traditional(pick: int) -> float:
    return TRADITIONAL_BASE / (1 + TRADITIONAL_DECAY * (pick - 1))


def _historical(pick: int) -> float:
    return 2400 * pick ** -0.45


def _expected(pick: int) -> float:
    return 2000 * pick ** -0.55


def _agreement_label(values: list[float]) -> str:
    m = sum(values) / len(values)
    if m == 0:
        return "Low"
    variance = sum((v - m) ** 2 for v in values) / len(values)
    cv = math.sqrt(variance) / m
    if cv < 0.15:
        return "High"
    if cv < 0.35:
        return "Moderate"
    return "Low"


def evaluate_draft_pick(
    year: int, round_: int, overall_pick: int | None
) -> DraftPickValuation:
    pick = _effective_pick_number(round_, overall_pick)
    traditional = _traditional(pick)
    historical = _historical(pick)
    expected = _expected(pick)
    values = [traditional, historical, expected]

    label = f"{year} Round {round_}"
    label += f", Pick {overall_pick}" if overall_pick else " (future - round midpoint assumed)"

    return DraftPickValuation(
        pick_label=label,
        traditional_value=round(traditional, 1),
        historical_value=round(historical, 1),
        expected_value=round(expected, 1),
        average_value=round(sum(values) / len(values), 1),
        model_agreement=_agreement_label(values),
    )


# Calibration constant used by the trade engine to convert draft-pick
# chart points into the same comparable "asset points" scale as the 0-100
# player valuation score (an elite #1 overall pick ~= an elite player).
PICK_POINTS_TO_ASSET_SCALE = 33.0
