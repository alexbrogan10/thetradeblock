"""Shared feature extraction for the Player Performance Projection model.

Used by BOTH the training script (scripts/train_performance_projection.py)
and the runtime inference module (app/ml/performance_projection.py) so
there is exactly one definition of what a "feature" means -- the classic
way train/serve skew creeps in is two slightly-different implementations
of the same feature.

Leakage rule (Section 38, Rule 56 #8): every feature here is something
that would have been known *before* the target season started. The
target is the following season's performance score. Contract fields use
the player's *current* contract as a proxy for "their contract situation
at prediction time" -- this dataset has no historical contract table, so
it is not a look-ahead in the demo data (documented as a limitation).
"""
from dataclasses import dataclass

from app.analytics.player_valuation import _production_score

FEATURE_COLUMNS = [
    "age",
    "position",
    "prior_performance",
    "prior_availability",
    "annual_value",
    "years_remaining",
]


@dataclass
class FeatureRow:
    age: int
    position: str
    prior_performance: float
    prior_availability: float
    annual_value: float
    years_remaining: float

    def as_dict(self) -> dict:
        return {
            "age": self.age,
            "position": self.position,
            "prior_performance": self.prior_performance,
            "prior_availability": self.prior_availability,
            "annual_value": self.annual_value,
            "years_remaining": self.years_remaining,
        }


def performance_score_for_season(position: str, stats: dict) -> float:
    score, _ = _production_score(position, stats or {})
    return score


def availability_score_for_season(games: int | None) -> float:
    if not games:
        return 50.0
    return max(0.0, min(100.0, 100 * games / 17.0))


def build_feature_row(player, prior_season, contract) -> FeatureRow:
    """prior_season: a PlayerStatistic row to derive 'as of prediction
    time' signal from (the most recent season actually on file)."""
    prior_performance = performance_score_for_season(player.position, prior_season.stats if prior_season else {})
    prior_availability = availability_score_for_season(prior_season.games if prior_season else None)
    return FeatureRow(
        age=player.age,
        position=player.position,
        prior_performance=prior_performance,
        prior_availability=prior_availability,
        annual_value=contract.annual_value if contract else 0.0,
        years_remaining=contract.years_remaining if contract else 0.0,
    )
