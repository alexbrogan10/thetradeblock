"""Explainable Player Trade Value model (Section 9-11).

Produces a 0-100 "estimated organizational asset value" score built from
eight transparent, independently-inspectable components. Nothing here is
a black box: every score returned includes the raw component values and a
list of the drivers that pushed the number up or down (Section 41 -
Explainability).

This is intentionally a statistical/heuristic model, not machine
learning -- ML player-value and projection models are a Phase 5 roadmap
item (see docs/limitations.md). Using a transparent formula here keeps
Phase 1 auditable end-to-end.
"""
from dataclasses import dataclass, field
from statistics import mean

from sqlalchemy.orm import Session

from app.analytics.position_tables import (
    AGE_CURVE,
    POSITION_GROUP,
    POSITION_VALUE,
    POSITIONAL_SCARCITY,
    PRODUCTION_WEIGHTS,
)
from app.config import settings
from app.models.contract import Contract
from app.models.player import Player
from app.models.player_statistic import PlayerStatistic

MODEL_VERSION = settings.player_valuation_model_version


@dataclass
class ValuationResult:
    valuation: float
    performance_score: float
    projection_score: float
    age_score: float
    position_score: float
    contract_score: float
    availability_score: float
    scarcity_score: float
    trajectory_score: float
    confidence: float
    positive_drivers: list[str] = field(default_factory=list)
    negative_drivers: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def _clip(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))


def _age_score(position: str, age: int) -> float:
    group = POSITION_GROUP.get(position, "WR")
    peak, sigma = AGE_CURVE.get(group, (27, 4.5))
    import math

    score = 100 * math.exp(-((age - peak) ** 2) / (2 * sigma**2))
    return _clip(score, 15, 100)


def _production_score(position: str, stats: dict) -> tuple[float, bool]:
    """Returns (score, had_any_signal)."""
    weights = PRODUCTION_WEIGHTS.get(position, {})
    if not weights or not stats:
        return 50.0, False

    total_weight = 0.0
    weighted_sum = 0.0
    had_signal = False
    for key, (threshold, weight) in weights.items():
        if key == "interceptions_inv":
            raw = stats.get("interceptions")
            if raw is None:
                continue
            had_signal = True
            component = _clip(100 * (1 - min(raw / threshold, 1.5)))
        elif key == "games_started_ratio":
            games = stats.get("games") or 0
            started = stats.get("games_started") or 0
            if games <= 0:
                continue
            had_signal = True
            component = _clip(100 * (started / games))
        else:
            raw = stats.get(key)
            if raw is None:
                continue
            had_signal = True
            component = _clip(100 * min(raw / threshold, 1.25))
        weighted_sum += component * weight
        total_weight += weight

    if total_weight == 0:
        return 50.0, False
    return weighted_sum / total_weight, had_signal


def _availability_score(seasons: list[PlayerStatistic]) -> tuple[float, bool]:
    if not seasons:
        return 50.0, False
    ratios = [min(s.games / 17.0, 1.0) for s in seasons if s.games is not None]
    if not ratios:
        return 50.0, False
    return _clip(100 * mean(ratios)), True


def _trajectory_score(position: str, seasons: list[PlayerStatistic]) -> tuple[float, bool]:
    if len(seasons) < 2:
        return 50.0, False
    ordered = sorted(seasons, key=lambda s: s.season)
    recent, prior = ordered[-1], ordered[-2]
    recent_score, _ = _production_score(position, recent.stats or {})
    prior_score, _ = _production_score(position, prior.stats or {})
    trend = recent_score - prior_score
    return _clip(50 + trend * 1.5), True


def _contract_score(
    position: str, contract: Contract | None, performance_value: float, league_avg_aav: dict
) -> tuple[float, bool]:
    if contract is None or contract.annual_value <= 0:
        return 50.0, False
    avg_aav = league_avg_aav.get(position, 8.0)
    # Expected pay scales with performance relative to a league-average
    # (50) performer at the position.
    expected_aav = avg_aav * max(performance_value, 10) / 50.0
    efficiency_ratio = expected_aav / max(contract.annual_value, 0.5)
    return _clip(50 * efficiency_ratio), True


def compute_position_average_aav(db: Session) -> dict[str, float]:
    rows = (
        db.query(Player.position, Contract.annual_value)
        .join(Contract, Contract.player_id == Player.id)
        .filter(Contract.annual_value > 0)
        .all()
    )
    by_position: dict[str, list[float]] = {}
    for position, aav in rows:
        by_position.setdefault(position, []).append(aav)
    return {pos: mean(values) for pos, values in by_position.items()}


def evaluate_player(
    player: Player,
    seasons: list[PlayerStatistic],
    contract: Contract | None,
    league_avg_aav: dict[str, float],
    performance_multiplier: float = 1.0,
) -> ValuationResult:
    """performance_multiplier scales the performance/projection components
    before they flow into the rest of the score. It exists solely to
    support Sensitivity Analysis (Section 28) -- e.g. "if this player
    performs at 110% of projection" -- and defaults to 1.0 (no effect) for
    every ordinary valuation."""
    position = player.position
    group = POSITION_GROUP.get(position, "WR")

    latest_season = max(seasons, key=lambda s: s.season) if seasons else None
    performance_score, has_performance_signal = _production_score(
        position, (latest_season.stats if latest_season else {}) or {}
    )
    performance_score = _clip(performance_score * performance_multiplier)

    age_score = _age_score(position, player.age)
    next_year_age_score = _age_score(position, player.age + 1)
    projection_score = _clip(
        performance_score + (next_year_age_score - age_score) * 0.6
    )

    position_score = POSITION_VALUE.get(position, 55)
    scarcity_score = POSITIONAL_SCARCITY.get(position, 45)

    availability_score, has_availability_signal = _availability_score(seasons)
    trajectory_score, has_trajectory_signal = _trajectory_score(position, seasons)

    performance_value_proxy = performance_score * 0.5 + projection_score * 0.5
    contract_score, has_contract_signal = _contract_score(
        position, contract, performance_value_proxy, league_avg_aav
    )

    valuation = (
        settings.weight_recent_performance * performance_score
        + settings.weight_projected_performance * projection_score
        + settings.weight_age * age_score
        + settings.weight_position_value * position_score
        + settings.weight_contract_efficiency * contract_score
        + settings.weight_availability * availability_score
        + settings.weight_positional_scarcity * scarcity_score
        + settings.weight_trajectory * trajectory_score
    )
    valuation = _clip(valuation)

    # --- Confidence & explanation -------------------------------------
    confidence = 30.0
    notes: list[str] = []
    if has_performance_signal:
        confidence += 25
    else:
        notes.append(f"No recent statistical data available for position {position}.")
    if len(seasons) >= 2:
        confidence += 15
    else:
        notes.append("Limited season history (fewer than 2 seasons on file).")
    if has_contract_signal:
        confidence += 20
    else:
        notes.append("Contract data unavailable; contract score defaulted to neutral (50).")
    if has_availability_signal:
        confidence += 10
    confidence = _clip(confidence, 15, 95)

    positive_drivers: list[str] = []
    negative_drivers: list[str] = []

    def _tag(label: str, score: float, high_msg: str, low_msg: str, threshold=(60, 40)):
        if score >= threshold[0]:
            positive_drivers.append(high_msg)
        elif score <= threshold[1]:
            negative_drivers.append(low_msg)

    _tag("performance", performance_score, "Strong recent on-field production",
         "Below-average recent production")
    _tag("projection", projection_score, "Favorable performance projection",
         "Projection trending downward")
    _tag("age", age_score, "Age aligns well with position peak window",
         "Age works against typical position peak window")
    _tag("position", position_score, "Plays a premium position", "Plays a lower-premium position")
    _tag("contract", contract_score, "Contract is team/value-friendly relative to production",
         "Contract cost is high relative to production")
    _tag("availability", availability_score, "Strong recent availability",
         "Availability/durability concerns in recent seasons")
    _tag("scarcity", scarcity_score, "Position is scarce league-wide",
         "Position is relatively replaceable league-wide")
    _tag("trajectory", trajectory_score, "Performance trending upward",
         "Performance trending downward year-over-year")

    return ValuationResult(
        valuation=round(valuation, 1),
        performance_score=round(performance_score, 1),
        projection_score=round(projection_score, 1),
        age_score=round(age_score, 1),
        position_score=round(float(position_score), 1),
        contract_score=round(contract_score, 1),
        availability_score=round(availability_score, 1),
        scarcity_score=round(float(scarcity_score), 1),
        trajectory_score=round(trajectory_score, 1),
        confidence=round(confidence, 1),
        positive_drivers=positive_drivers,
        negative_drivers=negative_drivers,
        notes=notes,
    )
