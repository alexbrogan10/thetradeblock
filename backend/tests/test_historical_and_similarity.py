import pytest

from app.analytics.historical_trades import find_comparable_trades
from app.analytics.player_similarity import find_similar_players
from app.models.historical_trade import HistoricalTrade, TradeAsset


def _make_historical_trade(db_session, team_a, team_b, player, age_at_trade):
    trade = HistoricalTrade(date="2023-05-01", team_a_id=team_a.id, team_b_id=team_b.id, notes="Test outcome note.")
    db_session.add(trade)
    db_session.commit()
    db_session.refresh(trade)

    asset = TradeAsset(
        trade_id=trade.id,
        team_from_id=team_a.id,
        team_to_id=team_b.id,
        asset_type="player",
        asset_id=player.id,
        label=f"{player.name} ({player.position})",
        player_age_at_trade=age_at_trade,
        player_position_at_trade=player.position,
        value_at_trade=0.0,
    )
    db_session.add(asset)
    db_session.commit()
    return trade


def test_find_comparable_trades_by_position_and_age(db_session, make_team, make_player):
    team_a = make_team()
    team_b = make_team()
    player = make_player(team_a, position="WR", age=30)
    _make_historical_trade(db_session, team_a, team_b, player, age_at_trade=26)

    results = find_comparable_trades(db_session, position="WR", age_min=24, age_max=28)
    assert len(results) == 1
    assert results[0].matching_position == "WR"
    assert results[0].outcome_note == "Test outcome note."


def test_find_comparable_trades_filters_out_non_matching_position(db_session, make_team, make_player):
    team_a = make_team()
    team_b = make_team()
    player = make_player(team_a, position="RB", age=27)
    _make_historical_trade(db_session, team_a, team_b, player, age_at_trade=25)

    results = find_comparable_trades(db_session, position="WR")
    assert results == []


def test_historical_trade_detail_endpoint(client, db_session, make_team, make_player):
    team_a = make_team()
    team_b = make_team()
    player = make_player(team_a, position="S", age=29)
    trade = _make_historical_trade(db_session, team_a, team_b, player, age_at_trade=26)

    resp = client.get(f"/api/historical-trades/{trade.id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == trade.id
    assert len(body["assets"]) == 1


def test_historical_trade_404(client):
    resp = client.get("/api/historical-trades/999999")
    assert resp.status_code == 404


def test_comparable_trades_endpoint_returns_results(client, db_session, make_team, make_player):
    team_a = make_team()
    team_b = make_team()
    player = make_player(team_a, position="TE", age=27)
    _make_historical_trade(db_session, team_a, team_b, player, age_at_trade=25)

    resp = client.get("/api/historical-trades/comparable?position=TE&age_min=23&age_max=27")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_similar_players_same_position_only(db_session, make_team, make_player, make_stats, make_contract):
    team = make_team()
    target = make_player(team, position="WR", age=26)
    make_stats(target, stats={"receptions": 80, "targets": 120, "rec_yards": 1100, "rec_td": 7, "yards_per_reception": 13.7})
    make_contract(target, annual_value=12, years_remaining=3)

    similar_wr = make_player(team, position="WR", age=27)
    make_stats(similar_wr, stats={"receptions": 78, "targets": 118, "rec_yards": 1080, "rec_td": 7, "yards_per_reception": 13.8})
    make_contract(similar_wr, annual_value=11, years_remaining=3)

    different_position = make_player(team, position="RB", age=26)

    results = find_similar_players(db_session, target.id, top_n=5)
    assert all(r.position == "WR" for r in results)
    assert all(r.player_id != target.id for r in results)
    assert any(r.player_id == similar_wr.id for r in results)


def test_similar_players_too_few_candidates_returns_empty(db_session, make_team, make_player):
    team = make_team()
    lonely = make_player(team, position="K", age=30)
    results = find_similar_players(db_session, lonely.id, top_n=5)
    assert results == []


def test_similar_players_invalid_player(db_session):
    with pytest.raises(ValueError):
        find_similar_players(db_session, 999999)


def test_similar_players_endpoint(client, make_team, make_player, make_stats):
    team = make_team()
    p1 = make_player(team, position="WR", age=26)
    make_stats(p1, stats={"receptions": 80, "targets": 120, "rec_yards": 1100, "rec_td": 7, "yards_per_reception": 13.7})
    p2 = make_player(team, position="WR", age=27)
    make_stats(p2, stats={"receptions": 75, "targets": 115, "rec_yards": 1000, "rec_td": 6, "yards_per_reception": 13.3})

    resp = client.get(f"/api/players/{p1.id}/similar")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
