import pytest

from app.analytics.trade_engine import TradeValidationError, analyze_trade
from app.schemas.trade import TradeSideInput


def test_simple_player_for_player_trade(db_session, make_team, make_player, make_contract):
    team_a = make_team(abbreviation="AAA")
    team_b = make_team(abbreviation="BBB")
    player_a = make_player(team_a, position="WR", age=26)
    player_b = make_player(team_b, position="CB", age=27)
    make_contract(player_a, annual_value=8)
    make_contract(player_b, annual_value=8)

    result = analyze_trade(
        db_session,
        TradeSideInput(team_id=team_a.id, player_ids=[player_a.id], draft_pick_ids=[]),
        TradeSideInput(team_id=team_b.id, player_ids=[player_b.id], draft_pick_ids=[]),
    )

    assert result["team_a"]["team_id"] == team_a.id
    assert result["team_b"]["team_id"] == team_b.id
    assert result["team_a"]["player_value_given"] > 0
    assert result["team_a"]["player_value_received"] > 0
    assert 0 <= result["confidence"] <= 100
    assert result["team_a"]["assessment"] in {
        "Strongly Favorable", "Favorable", "Potentially Favorable",
        "Balanced", "Potentially Unfavorable", "Unfavorable", "Strongly Unfavorable",
    }


def test_player_for_pick_trade(db_session, make_team, make_player, make_pick):
    team_a = make_team(abbreviation="AAA")
    team_b = make_team(abbreviation="BBB")
    player_a = make_player(team_a, position="EDGE", age=25)
    pick_b = make_pick(2027, 1, current_team=team_b)

    result = analyze_trade(
        db_session,
        TradeSideInput(team_id=team_a.id, player_ids=[player_a.id], draft_pick_ids=[]),
        TradeSideInput(team_id=team_b.id, player_ids=[], draft_pick_ids=[pick_b.id]),
    )
    assert result["team_a"]["draft_capital_received"] > 0
    assert result["team_b"]["player_value_received"] > 0


def test_multi_asset_trade(db_session, make_team, make_player, make_pick):
    team_a = make_team(abbreviation="AAA")
    team_b = make_team(abbreviation="BBB")
    p1 = make_player(team_a, position="WR", age=26)
    p2 = make_player(team_a, position="LB", age=28)
    pick_a = make_pick(2027, 3, current_team=team_a)
    p3 = make_player(team_b, position="OT", age=29)
    pick_b1 = make_pick(2027, 1, current_team=team_b)
    pick_b2 = make_pick(2028, 2, current_team=team_b)

    result = analyze_trade(
        db_session,
        TradeSideInput(team_id=team_a.id, player_ids=[p1.id, p2.id], draft_pick_ids=[pick_a.id]),
        TradeSideInput(team_id=team_b.id, player_ids=[p3.id], draft_pick_ids=[pick_b1.id, pick_b2.id]),
    )
    assert len(result["team_a"]["gives"]) == 3
    assert len(result["team_b"]["gives"]) == 3


def test_rejects_empty_trade(db_session, make_team):
    team_a = make_team()
    team_b = make_team()
    with pytest.raises(TradeValidationError):
        analyze_trade(
            db_session,
            TradeSideInput(team_id=team_a.id, player_ids=[], draft_pick_ids=[]),
            TradeSideInput(team_id=team_b.id, player_ids=[], draft_pick_ids=[]),
        )


def test_rejects_same_team_both_sides(db_session, make_team, make_player):
    team = make_team()
    p1 = make_player(team)
    p2 = make_player(team)
    with pytest.raises(TradeValidationError):
        analyze_trade(
            db_session,
            TradeSideInput(team_id=team.id, player_ids=[p1.id], draft_pick_ids=[]),
            TradeSideInput(team_id=team.id, player_ids=[p2.id], draft_pick_ids=[]),
        )


def test_rejects_duplicate_asset_on_both_sides(db_session, make_team, make_player):
    team_a = make_team()
    team_b = make_team()
    shared_player = make_player(team_a)
    with pytest.raises(TradeValidationError):
        analyze_trade(
            db_session,
            TradeSideInput(team_id=team_a.id, player_ids=[shared_player.id], draft_pick_ids=[]),
            TradeSideInput(team_id=team_b.id, player_ids=[shared_player.id], draft_pick_ids=[]),
        )


def test_rejects_invalid_player_id(db_session, make_team, make_player):
    team_a = make_team()
    team_b = make_team()
    player = make_player(team_a)
    with pytest.raises(TradeValidationError):
        analyze_trade(
            db_session,
            TradeSideInput(team_id=team_a.id, player_ids=[player.id], draft_pick_ids=[]),
            TradeSideInput(team_id=team_b.id, player_ids=[999999], draft_pick_ids=[]),
        )


def test_rejects_invalid_team_id(db_session, make_team, make_player):
    team_a = make_team()
    player = make_player(team_a)
    with pytest.raises(TradeValidationError):
        analyze_trade(
            db_session,
            TradeSideInput(team_id=team_a.id, player_ids=[player.id], draft_pick_ids=[]),
            TradeSideInput(team_id=999999, player_ids=[], draft_pick_ids=[]),
        )


def test_trade_with_missing_contract_data_does_not_crash(db_session, make_team, make_player):
    team_a = make_team()
    team_b = make_team()
    player_a = make_player(team_a, position="TE", age=27)  # no contract
    player_b = make_player(team_b, position="S", age=27)  # no contract

    result = analyze_trade(
        db_session,
        TradeSideInput(team_id=team_a.id, player_ids=[player_a.id], draft_pick_ids=[]),
        TradeSideInput(team_id=team_b.id, player_ids=[player_b.id], draft_pick_ids=[]),
    )
    assert result["team_a"]["cap_given"] == 0
    assert "contract data" in " ".join(result["confidence_limitations"]).lower()


def test_future_draft_pick_without_slot_still_values(db_session, make_team, make_pick):
    team_a = make_team()
    team_b = make_team()
    future_pick = make_pick(2028, 4, current_team=team_a, overall_pick=None)
    current_pick = make_pick(2026, 4, current_team=team_b, overall_pick=110)

    result = analyze_trade(
        db_session,
        TradeSideInput(team_id=team_a.id, player_ids=[], draft_pick_ids=[future_pick.id]),
        TradeSideInput(team_id=team_b.id, player_ids=[], draft_pick_ids=[current_pick.id]),
    )
    assert result["team_a"]["draft_capital_given"] > 0
    assert result["team_b"]["draft_capital_given"] > 0
