def test_save_and_get_scenario(client, make_team, make_player):
    team_a = make_team()
    team_b = make_team()
    player_a = make_player(team_a, position="WR", age=26)
    player_b = make_player(team_b, position="CB", age=27)

    resp = client.post(
        "/api/trades/scenarios",
        json={
            "name": "Test Scenario",
            "team_a": {"team_id": team_a.id, "player_ids": [player_a.id], "draft_pick_ids": []},
            "team_b": {"team_id": team_b.id, "player_ids": [player_b.id], "draft_pick_ids": []},
        },
    )
    assert resp.status_code == 200
    summary = resp.json()
    assert summary["name"] == "Test Scenario"
    scenario_id = summary["id"]

    detail = client.get(f"/api/trades/scenarios/{scenario_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["id"] == scenario_id
    assert body["team_a"]["team_id"] == team_a.id


def test_list_scenarios(client, make_team, make_player):
    team_a = make_team()
    team_b = make_team()
    player_a = make_player(team_a, position="WR", age=26)
    player_b = make_player(team_b, position="CB", age=27)
    client.post(
        "/api/trades/scenarios",
        json={
            "name": "S1",
            "team_a": {"team_id": team_a.id, "player_ids": [player_a.id], "draft_pick_ids": []},
            "team_b": {"team_id": team_b.id, "player_ids": [player_b.id], "draft_pick_ids": []},
        },
    )
    resp = client.get("/api/trades/scenarios")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_delete_scenario(client, make_team, make_player):
    team_a = make_team()
    team_b = make_team()
    player_a = make_player(team_a, position="WR", age=26)
    player_b = make_player(team_b, position="CB", age=27)
    created = client.post(
        "/api/trades/scenarios",
        json={
            "name": "ToDelete",
            "team_a": {"team_id": team_a.id, "player_ids": [player_a.id], "draft_pick_ids": []},
            "team_b": {"team_id": team_b.id, "player_ids": [player_b.id], "draft_pick_ids": []},
        },
    ).json()

    resp = client.delete(f"/api/trades/scenarios/{created['id']}")
    assert resp.status_code == 200

    resp2 = client.get(f"/api/trades/scenarios/{created['id']}")
    assert resp2.status_code == 404


def test_get_scenario_404(client):
    resp = client.get("/api/trades/scenarios/999999")
    assert resp.status_code == 404


def test_compare_scenarios(client, make_team, make_player):
    team = make_team()
    other_a = make_team()
    other_b = make_team()
    candidate_a = make_player(other_a, position="WR", age=25)
    candidate_b = make_player(other_b, position="WR", age=28)
    give_1 = make_player(team, position="LB", age=27)
    give_2 = make_player(team, position="LB", age=28)

    s1 = client.post(
        "/api/trades/scenarios",
        json={
            "name": "Acquire A",
            "team_a": {"team_id": team.id, "player_ids": [give_1.id], "draft_pick_ids": []},
            "team_b": {"team_id": other_a.id, "player_ids": [candidate_a.id], "draft_pick_ids": []},
        },
    ).json()
    s2 = client.post(
        "/api/trades/scenarios",
        json={
            "name": "Acquire B",
            "team_a": {"team_id": team.id, "player_ids": [give_2.id], "draft_pick_ids": []},
            "team_b": {"team_id": other_b.id, "player_ids": [candidate_b.id], "draft_pick_ids": []},
        },
    ).json()

    resp = client.post(
        "/api/trades/scenarios/compare",
        json={"scenario_ids": [s1["id"], s2["id"]], "perspective_team_id": team.id},
    )
    assert resp.status_code == 200
    rows = resp.json()
    assert len(rows) == 2
    assert all(r["applicable"] for r in rows)


def test_compare_requires_at_least_two(client, make_team, make_player):
    team_a = make_team()
    team_b = make_team()
    player_a = make_player(team_a, position="WR", age=26)
    player_b = make_player(team_b, position="CB", age=27)
    s1 = client.post(
        "/api/trades/scenarios",
        json={
            "name": "S1",
            "team_a": {"team_id": team_a.id, "player_ids": [player_a.id], "draft_pick_ids": []},
            "team_b": {"team_id": team_b.id, "player_ids": [player_b.id], "draft_pick_ids": []},
        },
    ).json()
    resp = client.post(
        "/api/trades/scenarios/compare",
        json={"scenario_ids": [s1["id"]], "perspective_team_id": team_a.id},
    )
    assert resp.status_code == 400


def test_compare_not_applicable_for_unrelated_team(client, make_team, make_player):
    team_a = make_team()
    team_b = make_team()
    team_c = make_team()
    player_a = make_player(team_a, position="WR", age=26)
    player_b = make_player(team_b, position="CB", age=27)
    other_player = make_player(team_b, position="S", age=26)
    other_player2 = make_player(team_c, position="S", age=27)

    s1 = client.post(
        "/api/trades/scenarios",
        json={
            "name": "S1",
            "team_a": {"team_id": team_a.id, "player_ids": [player_a.id], "draft_pick_ids": []},
            "team_b": {"team_id": team_b.id, "player_ids": [player_b.id], "draft_pick_ids": []},
        },
    ).json()
    s2 = client.post(
        "/api/trades/scenarios",
        json={
            "name": "S2",
            "team_a": {"team_id": team_b.id, "player_ids": [other_player.id], "draft_pick_ids": []},
            "team_b": {"team_id": team_c.id, "player_ids": [other_player2.id], "draft_pick_ids": []},
        },
    ).json()

    resp = client.post(
        "/api/trades/scenarios/compare",
        json={"scenario_ids": [s1["id"], s2["id"]], "perspective_team_id": team_a.id},
    )
    rows = resp.json()
    applicable_flags = {r["scenario_id"]: r["applicable"] for r in rows}
    assert applicable_flags[s1["id"]] is True
    assert applicable_flags[s2["id"]] is False
