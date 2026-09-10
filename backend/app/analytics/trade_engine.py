"""Trade analysis engine (Sections 3, 7, 8, 14-23).

Turns a hypothetical trade into a structured, explainable, per-team
assessment. This module never states that a trade is objectively correct
-- it only ever produces qualitative labels such as "Potentially
Favorable" alongside a confidence percentage and an explicit list of
what could change the conclusion (Sections 3, 29, 42).
"""
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.analytics.competitive_window import classify_team_timeline
from app.analytics.draft_pick_valuation import (
    PICK_POINTS_TO_ASSET_SCALE,
    evaluate_draft_pick,
)
from app.analytics.player_valuation import (
    compute_position_average_aav,
    evaluate_player,
)
from app.analytics.team_fit import compute_team_fit
from app.analytics.team_needs import evaluate_team_needs
from app.analytics.roster_impact import compute_roster_impact
from app.config import settings
from app.models.contract import Contract
from app.models.draft_pick import DraftPick
from app.models.player import Player
from app.models.player_statistic import PlayerStatistic
from app.models.team import Team


class TradeValidationError(ValueError):
    pass


@dataclass
class _AssetBundle:
    team: Team
    players: list[Player]
    picks: list[DraftPick]
    player_values: dict[int, object]  # player_id -> ValuationResult
    pick_values: dict[int, object]  # pick_id -> DraftPickValuation


def _load_side(db: Session, team_id: int, player_ids: list[int], pick_ids: list[int]):
    team = db.get(Team, team_id)
    if team is None:
        raise TradeValidationError(f"Team {team_id} does not exist.")

    players = db.query(Player).filter(Player.id.in_(player_ids)).all() if player_ids else []
    if len(players) != len(set(player_ids)):
        found = {p.id for p in players}
        missing = set(player_ids) - found
        raise TradeValidationError(f"Player id(s) not found: {sorted(missing)}")

    picks = db.query(DraftPick).filter(DraftPick.id.in_(pick_ids)).all() if pick_ids else []
    if len(picks) != len(set(pick_ids)):
        found = {p.id for p in picks}
        missing = set(pick_ids) - found
        raise TradeValidationError(f"Draft pick id(s) not found: {sorted(missing)}")

    return team, players, picks


def _valuate_players(db: Session, players: list[Player], league_avg_aav: dict):
    values = {}
    for player in players:
        seasons = (
            db.query(PlayerStatistic).filter(PlayerStatistic.player_id == player.id).all()
        )
        contract = db.query(Contract).filter(Contract.player_id == player.id).first()
        values[player.id] = evaluate_player(player, seasons, contract, league_avg_aav)
    return values


def _valuate_picks(picks: list[DraftPick]):
    return {
        pick.id: evaluate_draft_pick(pick.year, pick.round, pick.overall_pick)
        for pick in picks
    }


def _roster_fit(
    team: Team,
    received_players: list[Player],
    team_needs: list,
    timeline,
) -> tuple[float, list[str]]:
    """Full Team Fit Engine (Section 17): need score + timeline/age +
    contract-length fit, replacing the Phase 1 depth-count heuristic."""
    if not received_players:
        return 50.0, ["No players received in this trade; roster fit is not directly applicable."]

    needs_by_position = {n.position: n for n in team_needs}
    notes = []
    fit_scores = []
    for player in received_players:
        position_need = needs_by_position.get(player.position)
        fit_result = compute_team_fit(player, player.contract, position_need, timeline)
        fit_scores.append(fit_result.score)
        notes.append(f"{player.name}: {fit_result.explanation}")
    return sum(fit_scores) / len(fit_scores), notes


def _risk_assessment(received_players: list[Player], player_values: dict, contracts_by_player: dict):
    if not received_players:
        return "Low", ["No players received in this trade."], ["Draft-pick-only trades carry no on-field player risk."]

    age_risks, contract_risks, availability_risks, confidence_risks = [], [], [], []
    for player in received_players:
        val = player_values[player.id]
        age_risks.append(100 - val.age_score)
        contract_risks.append(100 - val.contract_score)
        availability_risks.append(100 - val.availability_score)
        confidence_risks.append(100 - val.confidence)

    def _avg(xs):
        return sum(xs) / len(xs)

    components = {
        "Age curve": _avg(age_risks),
        "Contract commitment": _avg(contract_risks),
        "Availability history": _avg(availability_risks),
        "Valuation uncertainty": _avg(confidence_risks),
    }
    risk_score = sum(components.values()) / len(components)

    ranked = sorted(components.items(), key=lambda kv: kv[1], reverse=True)
    drivers = [f"{name}" for name, score in ranked if score >= 55][:3]
    mitigators = [f"{name.replace('risk', 'profile')} is favorable" for name, score in ranked if score < 40][:3]

    if risk_score < 35:
        level = "Low"
    elif risk_score < 65:
        level = "Moderate"
    else:
        level = "High"

    if not drivers:
        drivers = ["No single risk factor stands out; overall risk is diffuse."]
    if not mitigators:
        mitigators = ["Limited mitigating factors identified from available data."]

    return level, drivers, mitigators


def _timeline_alignment(
    team: Team, received_players: list[Player], received_picks: list[DraftPick], timeline
) -> tuple[float, list[str]]:
    """Full Competitive Window classifier (Section 20), replacing the
    Phase 1 average-age proxy."""
    classification = timeline.classification
    notes = [
        f"{team.abbreviation} is classified '{classification}' "
        f"(timeline score {timeline.timeline_score:.0f}/100)."
    ] + timeline.reasons

    if not received_players and not received_picks:
        return 50.0, notes

    score = 50.0
    prefers_picks = classification in ("Rebuilding", "Developing")
    prefers_proven = classification in ("Win Now", "Contender")

    for player in received_players:
        target_age = 24 if prefers_picks else 28 if prefers_proven else 27
        distance = abs(player.age - target_age)
        contribution = max(-15.0, 15.0 - distance * 2.5)
        score += contribution
        if contribution > 3:
            notes.append(f"{player.name} (age {player.age}) fits a {classification.lower()} timeline.")
        elif contribution < -3:
            notes.append(f"{player.name} (age {player.age}) is a mismatch for a {classification.lower()} timeline.")

    if received_picks and prefers_picks:
        score += 8
        notes.append("Additional draft capital aligns well with a timeline built around future assets.")
    elif received_picks and prefers_proven:
        score -= 3
        notes.append("Draft picks add less immediate value for a team prioritizing near-term contention.")

    return max(0.0, min(100.0, score)), notes


def _contract_impact(given_players: list[Player], received_players: list[Player]) -> dict:
    """Section 12 - Contract Analysis, applied to a hypothetical trade.

    Distinguishes this-year cap impact from an approximate multi-year
    (3-year) outlook. All figures are derived from the contract data on
    file -- demo/estimated unless a licensed data source is connected
    (Section 12: distinguish observed data from model estimates).
    """
    cap_added = sum((p.contract.cap_hit if p.contract else 0.0) for p in received_players)
    cap_freed = sum((p.contract.cap_hit if p.contract else 0.0) for p in given_players)

    dead_cap = 0.0
    for p in given_players:
        if p.contract and p.contract.guaranteed_money:
            factor = 0.4 if p.contract.years_remaining > 1 else 0.15
            dead_cap += p.contract.guaranteed_money * factor

    def _multi_year(players: list[Player]) -> float:
        total = 0.0
        for p in players:
            if p.contract and p.contract.annual_value:
                years = max(1, min(3, p.contract.years_remaining or 1))
                total += p.contract.annual_value * years
        return total

    future_added = _multi_year(received_players)
    future_freed = _multi_year(given_players)

    net_this_year = cap_freed - cap_added - dead_cap
    net_multi_year = future_freed - future_added - dead_cap

    if net_this_year > 1 and net_multi_year > 1:
        note = "Frees cap space both this year and over the following seasons."
    elif net_this_year < -1 and net_multi_year < -1:
        note = "Adds cap commitment both this year and over the following seasons."
    elif net_this_year > 1 >= net_multi_year:
        note = "Frees cap space immediately, but the multi-year outlook is closer to neutral or negative."
    else:
        note = "Cap impact is roughly neutral relative to the assets already on the books."

    return {
        "cap_added_this_year": round(cap_added, 2),
        "cap_freed_this_year": round(cap_freed, 2),
        "dead_cap_incurred": round(dead_cap, 2),
        "net_cap_impact_this_year": round(net_this_year, 2),
        "future_cap_added_3yr": round(future_added, 2),
        "future_cap_freed_3yr": round(future_freed, 2),
        "net_multi_year_impact": round(net_multi_year, 2),
        "note": note,
    }


def _assessment_label(combined: float) -> str:
    if combined >= 25:
        return "Strongly Favorable"
    if combined >= 12:
        return "Favorable"
    if combined >= 4:
        return "Potentially Favorable"
    if combined > -4:
        return "Balanced"
    if combined >= -12:
        return "Potentially Unfavorable"
    if combined >= -25:
        return "Unfavorable"
    return "Strongly Unfavorable"


def _confidence_label(agreement: str) -> float:
    return {"High": 90.0, "Moderate": 65.0, "Low": 40.0}.get(agreement, 50.0)


def analyze_trade(db: Session, team_a_input, team_b_input) -> dict:
    if not any(
        [
            team_a_input.player_ids,
            team_a_input.draft_pick_ids,
            team_b_input.player_ids,
            team_b_input.draft_pick_ids,
        ]
    ):
        raise TradeValidationError("A trade must include at least one asset.")

    dup_players = set(team_a_input.player_ids) & set(team_b_input.player_ids)
    dup_picks = set(team_a_input.draft_pick_ids) & set(team_b_input.draft_pick_ids)
    if dup_players or dup_picks:
        raise TradeValidationError("The same asset cannot appear on both sides of a trade.")

    team_a, players_a, picks_a = _load_side(
        db, team_a_input.team_id, team_a_input.player_ids, team_a_input.draft_pick_ids
    )
    team_b, players_b, picks_b = _load_side(
        db, team_b_input.team_id, team_b_input.player_ids, team_b_input.draft_pick_ids
    )
    if team_a.id == team_b.id:
        raise TradeValidationError("Team A and Team B must be different teams.")

    league_avg_aav = compute_position_average_aav(db)
    all_players = players_a + players_b
    player_values = _valuate_players(db, all_players, league_avg_aav)
    pick_values = _valuate_picks(picks_a + picks_b)

    team_needs_by_team = {
        team_a.id: evaluate_team_needs(db, team_a.id),
        team_b.id: evaluate_team_needs(db, team_b.id),
    }
    timeline_by_team = {
        team_a.id: classify_team_timeline(db, team_a),
        team_b.id: classify_team_timeline(db, team_b),
    }

    def build_side(
        team: Team,
        given_players: list[Player],
        given_picks: list[DraftPick],
        received_players: list[Player],
        received_picks: list[DraftPick],
    ):
        team_needs = team_needs_by_team[team.id]
        timeline = timeline_by_team[team.id]
        gives = [
            {"asset_type": "player", "asset_id": p.id, "label": f"{p.name} ({p.position})",
             "value": player_values[p.id].valuation}
            for p in given_players
        ] + [
            {"asset_type": "draft_pick", "asset_id": pk.id, "label": pick_values[pk.id].pick_label,
             "value": pick_values[pk.id].average_value}
            for pk in given_picks
        ]
        receives = [
            {"asset_type": "player", "asset_id": p.id, "label": f"{p.name} ({p.position})",
             "value": player_values[p.id].valuation}
            for p in received_players
        ] + [
            {"asset_type": "draft_pick", "asset_id": pk.id, "label": pick_values[pk.id].pick_label,
             "value": pick_values[pk.id].average_value}
            for pk in received_picks
        ]

        player_value_given = sum(player_values[p.id].valuation for p in given_players)
        player_value_received = sum(player_values[p.id].valuation for p in received_players)
        draft_capital_given = sum(pick_values[pk.id].average_value for pk in given_picks)
        draft_capital_received = sum(pick_values[pk.id].average_value for pk in received_picks)

        asset_value_delta = (
            (player_value_received + draft_capital_received / PICK_POINTS_TO_ASSET_SCALE)
            - (player_value_given + draft_capital_given / PICK_POINTS_TO_ASSET_SCALE)
        )

        contract_impact = _contract_impact(given_players, received_players)
        cap_given = contract_impact["cap_freed_this_year"]
        cap_received = contract_impact["cap_added_this_year"]
        dead_cap = contract_impact["dead_cap_incurred"]
        financial_impact = contract_impact["net_cap_impact_this_year"]

        roster_fit_score, fit_notes = _roster_fit(team, received_players, team_needs, timeline)
        risk_level, risk_drivers, risk_mitigators = _risk_assessment(
            received_players, player_values, {}
        )
        timeline_alignment, timeline_notes = _timeline_alignment(
            team, received_players, received_picks, timeline
        )
        roster_impact = compute_roster_impact(
            db, team.id, [p.id for p in given_players], received_players, league_avg_aav
        )
        roster_impact_out = [
            {"position": r.position, "before": r.before, "after": r.after, "change": r.change}
            for r in roster_impact
            if r.change != 0
        ]

        opportunity_cost_notes = [
            f"Giving up {pick_values[pk.id].pick_label} forgoes the option to retain in-house "
            "talent, draft a rookie prospect, or package the pick in a future trade."
            for pk in given_picks
        ]
        if given_players:
            opportunity_cost_notes.append(
                "Trading established players also forgoes their potential value if kept and "
                "developed, or traded later under different market conditions."
            )

        combined = (
            0.40 * max(-60.0, min(60.0, asset_value_delta))
            + 0.30 * (roster_fit_score - 50)
            + 0.15 * max(-20.0, min(20.0, financial_impact))
            + 0.15 * (50 - {"Low": 20, "Moderate": 50, "High": 80}[risk_level])
        )
        assessment = _assessment_label(combined)

        positive_drivers, negative_drivers = [], []
        if asset_value_delta > 2:
            positive_drivers.append("Receives more analytical asset value than it gives up.")
        elif asset_value_delta < -2:
            negative_drivers.append("Gives up more analytical asset value than it receives.")
        if roster_fit_score >= 65:
            positive_drivers.append("Strong roster fit for incoming player(s).")
        elif roster_fit_score <= 40:
            negative_drivers.append("Weak roster fit given existing positional depth.")
        if financial_impact > 1:
            positive_drivers.append("Net positive cap impact (frees more than it commits).")
        elif financial_impact < -1:
            negative_drivers.append("Net negative cap impact (commits more than it frees).")
        if risk_level == "Low":
            positive_drivers.append("Overall trade risk is low.")
        elif risk_level == "High":
            negative_drivers.append("Overall trade risk is elevated.")
        for p in received_players:
            positive_drivers.extend(f"{p.name}: {d}" for d in player_values[p.id].positive_drivers[:2])
            negative_drivers.extend(f"{p.name}: {d}" for d in player_values[p.id].negative_drivers[:2])

        what_could_change_this = [
            "If a received player's on-field performance materially declines relative to projection.",
            "If the team's positional need at this spot changes before the player develops.",
            "If contract renegotiation or injury changes the modeled financial impact.",
        ]
        if given_picks:
            what_could_change_this.append(
                "If the draft class in the relevant future year is perceived as unusually deep or shallow at a position of need."
            )
        what_could_change_this.extend(fit_notes[:1])
        what_could_change_this.extend(timeline_notes[:1])

        return {
            "team_id": team.id,
            "team_name": team.name,
            "gives": gives,
            "receives": receives,
            "player_value_given": round(player_value_given, 1),
            "player_value_received": round(player_value_received, 1),
            "draft_capital_given": round(draft_capital_given, 1),
            "draft_capital_received": round(draft_capital_received, 1),
            "asset_value_delta": round(asset_value_delta, 1),
            "roster_fit_score": round(roster_fit_score, 1),
            "draft_capital_delta": round(draft_capital_received - draft_capital_given, 1),
            "financial_impact": round(financial_impact, 2),
            "cap_given": round(cap_given, 2),
            "cap_received": round(cap_received, 2),
            "dead_cap_incurred": round(dead_cap, 2),
            "risk_level": risk_level,
            "risk_drivers": risk_drivers,
            "risk_mitigators": risk_mitigators,
            "timeline_alignment": round(timeline_alignment, 1),
            "competitive_window": timeline.classification,
            "opportunity_cost_notes": opportunity_cost_notes,
            "contract_impact": contract_impact,
            "roster_impact": roster_impact_out,
            "team_fit_explanations": fit_notes,
            "assessment": assessment,
            "positive_drivers": positive_drivers or ["No strong positive drivers identified."],
            "negative_drivers": negative_drivers or ["No strong negative drivers identified."],
            "what_could_change_this": what_could_change_this,
        }

    team_a_result = build_side(team_a, players_a, picks_a, players_b, picks_b)
    team_b_result = build_side(team_b, players_b, picks_b, players_a, picks_a)

    all_confidences = [player_values[p.id].confidence for p in all_players]
    pick_confidences = [_confidence_label(v.model_agreement) for v in pick_values.values()]
    combined_confidences = all_confidences + pick_confidences
    overall_confidence = (
        sum(combined_confidences) / len(combined_confidences) if combined_confidences else 50.0
    )

    confidence_limitations = [
        "Player valuations rely on a transparent statistical model, not proprietary scouting data.",
        "Draft-pick values are approximations; three independent methodologies are shown to surface disagreement.",
        "Contract and cap figures are demo/estimated data unless a licensed data source is connected.",
    ]
    if any(p.contract is None for p in all_players):
        confidence_limitations.append("One or more players are missing contract data; contract score defaulted to neutral.")

    return {
        "team_a": team_a_result,
        "team_b": team_b_result,
        "confidence": round(overall_confidence, 1),
        "confidence_limitations": confidence_limitations,
        "player_valuation_model_version": settings.player_valuation_model_version,
        "draft_pick_model_version": settings.draft_pick_model_version,
    }
