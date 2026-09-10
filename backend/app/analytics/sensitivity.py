"""Sensitivity Analysis (Section 28) and "What Would Change This?"
support (Section 29).

Re-runs the full trade engine under varied assumptions so a user can see
what must be true for a recommendation to hold, rather than treating the
baseline assessment as fixed. Every re-run goes through the exact same
`analyze_trade` code path as an ordinary analysis -- there is no separate,
drift-prone "sensitivity formula."
"""
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.analytics.trade_engine import analyze_trade

PERFORMANCE_SCENARIOS = [
    (0.90, "Underperforms (90% of projection)"),
    (1.00, "Performs at projection"),
    (1.10, "Outperforms (110% of projection)"),
]

PICK_MODELS = [
    ("traditional", "Traditional Model"),
    ("historical", "Historical Model"),
    ("expected", "Expected Value Model"),
]


@dataclass
class SensitivityPoint:
    label: str
    assessment: str
    asset_value_delta: float
    confidence: float


def _extract(result: dict, perspective_team_id: int) -> dict:
    side = result["team_a"] if result["team_a"]["team_id"] == perspective_team_id else result["team_b"]
    return side


def compute_sensitivity(
    db: Session, team_a_input, team_b_input, perspective_team_id: int
) -> dict:
    performance_points = []
    for multiplier, label in PERFORMANCE_SCENARIOS:
        result = analyze_trade(db, team_a_input, team_b_input, performance_multiplier=multiplier)
        side = _extract(result, perspective_team_id)
        performance_points.append(
            SensitivityPoint(
                label=label,
                assessment=side["assessment"],
                asset_value_delta=side["asset_value_delta"],
                confidence=result["confidence"],
            )
        )

    pick_model_points = []
    for model, label in PICK_MODELS:
        result = analyze_trade(db, team_a_input, team_b_input, pick_model=model)
        side = _extract(result, perspective_team_id)
        pick_model_points.append(
            SensitivityPoint(
                label=label,
                assessment=side["assessment"],
                asset_value_delta=side["asset_value_delta"],
                confidence=result["confidence"],
            )
        )

    baseline_assessment = performance_points[1].assessment
    would_change_mind = []
    if performance_points[0].assessment != baseline_assessment:
        would_change_mind.append(
            f"If performance drops to 90% of projection, the assessment shifts from "
            f"'{baseline_assessment}' to '{performance_points[0].assessment}'."
        )
    if performance_points[2].assessment != baseline_assessment:
        would_change_mind.append(
            f"If performance rises to 110% of projection, the assessment shifts from "
            f"'{baseline_assessment}' to '{performance_points[2].assessment}'."
        )
    distinct_pick_assessments = {p.assessment for p in pick_model_points}
    if len(distinct_pick_assessments) > 1:
        would_change_mind.append(
            "The assessment is sensitive to which draft-pick valuation methodology is used "
            f"({', '.join(sorted(distinct_pick_assessments))})."
        )
    if not would_change_mind:
        would_change_mind.append(
            "The assessment is stable across the performance and draft-pick-model scenarios tested."
        )

    return {
        "performance_sensitivity": [p.__dict__ for p in performance_points],
        "draft_model_sensitivity": [p.__dict__ for p in pick_model_points],
        "what_would_change_this": would_change_mind,
    }
