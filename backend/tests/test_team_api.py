def test_team_needs_endpoint(client, make_team, make_player):
    team = make_team()
    make_player(team, position="QB", age=27)
    resp = client.get(f"/api/team/{team.id}/needs")
    assert resp.status_code == 200
    body = resp.json()
    assert body["team"]["id"] == team.id
    assert len(body["needs"]) > 0


def test_team_needs_404(client):
    resp = client.get("/api/team/999999/needs")
    assert resp.status_code == 404


def test_team_timeline_endpoint(client, make_team, make_player):
    team = make_team()
    make_player(team, position="QB", age=27)
    resp = client.get(f"/api/team/{team.id}/timeline")
    assert resp.status_code == 200
    body = resp.json()
    assert body["classification"] in {"Rebuilding", "Developing", "Competitive", "Contender", "Win Now"}


def test_draft_capital_dashboard_endpoint(client, make_team, make_pick):
    team = make_team()
    make_pick(2026, 1, current_team=team, overall_pick=5)
    make_pick(2027, 2, current_team=team)
    resp = client.get(f"/api/team/{team.id}/draft-capital")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_picks"] == 2
    assert len(body["by_year"]) == 2


def test_roster_impact_endpoint(client, make_team, make_player):
    team = make_team()
    player = make_player(team, position="WR", age=27)
    resp = client.get(f"/api/team/{team.id}/roster-impact?players_out={player.id}")
    assert resp.status_code == 200
    body = resp.json()
    wr = next(r for r in body["impact"] if r["position"] == "WR")
    assert wr["after"] == 0.0


def test_trade_analyze_includes_phase2_fields(client, make_team, make_player):
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
    assert "contract_impact" in body["team_a"]
    assert "roster_impact" in body["team_a"]
    assert body["team_a"]["competitive_window"] in {"Rebuilding", "Developing", "Competitive", "Contender", "Win Now"}
