from app.analytics.discrepancy import find_value_discrepancies
from app.analytics.trade_finder import find_trade_targets


def test_underpaid_star_flagged_as_positive_discrepancy(db_session, make_team, make_player, make_stats, make_contract):
    team = make_team()
    star = make_player(team, position="WR", age=25)
    make_stats(star, stats={"receptions": 100, "targets": 145, "rec_yards": 1400, "rec_td": 11, "yards_per_reception": 14})
    make_contract(star, annual_value=2.0, years_remaining=3)  # way below market for this production

    results = find_value_discrepancies(db_session, min_abs_discrepancy=5)
    match = next((r for r in results if r.player_id == star.id), None)
    assert match is not None
    assert match.potential_discrepancy > 0


def test_no_contract_players_excluded_from_discrepancy_finder(db_session, make_team, make_player):
    team = make_team()
    make_player(team, position="WR", age=25)  # no contract
    results = find_value_discrepancies(db_session, min_abs_discrepancy=0)
    assert results == []


def test_discrepancy_endpoint(client, make_team, make_player, make_stats, make_contract):
    team = make_team()
    star = make_player(team, position="WR", age=25)
    make_stats(star, stats={"receptions": 100, "targets": 145, "rec_yards": 1400, "rec_td": 11, "yards_per_reception": 14})
    make_contract(star, annual_value=2.0, years_remaining=3)

    resp = client.get("/api/analytics/value-discrepancies?min_discrepancy=5")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_trade_finder_filters_by_position_and_excludes_own_team(db_session, make_team, make_player):
    team = make_team()
    other = make_team()
    make_player(team, position="WR", age=26)  # own team, should be excluded
    target = make_player(other, position="WR", age=25)
    make_player(other, position="CB", age=25)  # wrong position

    results = find_trade_targets(db_session, team_id=team.id, position="WR")
    ids = [r.player_id for r in results]
    assert target.id in ids
    assert all(r.position == "WR" for r in results)


def test_trade_finder_respects_max_acquisition_cost(db_session, make_team, make_player, make_stats, make_contract):
    team = make_team()
    other = make_team()
    star = make_player(other, position="WR", age=25)
    make_stats(star, stats={"receptions": 100, "targets": 145, "rec_yards": 1400, "rec_td": 11, "yards_per_reception": 14})
    make_contract(star, annual_value=16, years_remaining=3)

    results = find_trade_targets(db_session, team_id=team.id, position="WR", max_acquisition_cost=10)
    assert all(r.analytical_value <= 10 for r in results)


def test_trade_finder_endpoint(client, make_team, make_player):
    team = make_team()
    other = make_team()
    make_player(other, position="WR", age=25)

    resp = client.post("/api/trades/finder", json={"team_id": team.id, "position": "WR"})
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_trade_finder_invalid_team(client):
    resp = client.post("/api/trades/finder", json={"team_id": 999999, "position": "WR"})
    assert resp.status_code == 400
