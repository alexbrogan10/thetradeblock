def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_list_teams_empty(client):
    resp = client.get("/api/teams")
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_and_get_team(client, make_team):
    team = make_team(name="Test City Testers")
    resp = client.get("/api/teams")
    assert resp.status_code == 200
    assert any(t["id"] == team.id for t in resp.json())

    resp = client.get(f"/api/teams/{team.id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Test City Testers"


def test_get_team_404(client):
    resp = client.get("/api/teams/999999")
    assert resp.status_code == 404


def test_list_players_filter_by_team(client, make_team, make_player):
    team_a = make_team()
    team_b = make_team()
    make_player(team_a, position="QB")
    make_player(team_b, position="RB")

    resp = client.get(f"/api/players?team_id={team_a.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["position"] == "QB"


def test_get_player_detail_includes_valuation(client, make_team, make_player):
    team = make_team()
    player = make_player(team, position="WR", age=26)
    resp = client.get(f"/api/players/{player.id}")
    assert resp.status_code == 200
    body = resp.json()
    assert "valuation" in body
    assert 0 <= body["valuation"]["valuation"] <= 100


def test_get_player_404(client):
    resp = client.get("/api/players/999999")
    assert resp.status_code == 404


def test_draft_picks_endpoint(client, make_team, make_pick):
    team = make_team()
    make_pick(2027, 1, current_team=team)
    resp = client.get(f"/api/draft-picks?team_id={team.id}")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_analyze_trade_endpoint_happy_path(client, make_team, make_player):
    team_a = make_team()
    team_b = make_team()
    player_a = make_player(team_a, position="CB", age=25)
    player_b = make_player(team_b, position="S", age=26)

    resp = client.post(
        "/api/trades/analyze",
        json={
            "team_a": {"team_id": team_a.id, "player_ids": [player_a.id], "draft_pick_ids": []},
            "team_b": {"team_id": team_b.id, "player_ids": [player_b.id], "draft_pick_ids": []},
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "team_a" in body and "team_b" in body
    assert "disclaimer" in body


def test_analyze_trade_endpoint_validation_error(client, make_team):
    team_a = make_team()
    team_b = make_team()
    resp = client.post(
        "/api/trades/analyze",
        json={
            "team_a": {"team_id": team_a.id, "player_ids": [], "draft_pick_ids": []},
            "team_b": {"team_id": team_b.id, "player_ids": [], "draft_pick_ids": []},
        },
    )
    assert resp.status_code == 400


def test_dashboard_endpoint_runs_with_no_data(client):
    resp = client.get("/api/analytics/dashboard")
    assert resp.status_code == 200
    body = resp.json()
    assert "trade_market" in body
    assert "model_alerts" in body


def test_dashboard_endpoint_with_data(client, make_team, make_player, make_stats, make_contract):
    team = make_team()
    player = make_player(team, position="WR", age=25)
    make_stats(player, stats={"receptions": 90, "targets": 130, "rec_yards": 1250, "rec_td": 9, "yards_per_reception": 13.9})
    make_contract(player, annual_value=6, years_remaining=1)

    resp = client.get("/api/analytics/dashboard")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["trade_market"]["highest_value_players"]) >= 1
