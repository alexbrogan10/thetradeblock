from app.analytics.sensitivity import compute_sensitivity
from app.schemas.trade import TradeSideInput


def test_sensitivity_returns_three_performance_points(db_session, make_team, make_player, make_stats):
    team_a = make_team()
    team_b = make_team()
    player_a = make_player(team_a, position="WR", age=26)
    make_stats(player_a, stats={"receptions": 80, "targets": 120, "rec_yards": 1100, "rec_td": 8, "yards_per_reception": 13.7})
    player_b = make_player(team_b, position="CB", age=27)

    result = compute_sensitivity(
        db_session,
        TradeSideInput(team_id=team_a.id, player_ids=[player_a.id], draft_pick_ids=[]),
        TradeSideInput(team_id=team_b.id, player_ids=[player_b.id], draft_pick_ids=[]),
        perspective_team_id=team_a.id,
    )
    assert len(result["performance_sensitivity"]) == 3
    assert len(result["draft_model_sensitivity"]) == 3
    assert "what_would_change_this" in result


def test_sensitivity_higher_performance_multiplier_increases_asset_value(
    db_session, make_team, make_player, make_stats
):
    team_a = make_team()
    team_b = make_team()
    player_a = make_player(team_a, position="WR", age=26)
    make_stats(player_a, stats={"receptions": 80, "targets": 120, "rec_yards": 1100, "rec_td": 8, "yards_per_reception": 13.7})
    player_b = make_player(team_b, position="CB", age=27)

    result = compute_sensitivity(
        db_session,
        TradeSideInput(team_id=team_a.id, player_ids=[], draft_pick_ids=[]),
        TradeSideInput(team_id=team_b.id, player_ids=[player_a.id], draft_pick_ids=[]),
        perspective_team_id=team_a.id,
    )
    points = result["performance_sensitivity"]
    # team_a is receiving player_a; higher performance multiplier should raise
    # team_a's asset_value_delta (it's receiving more value).
    assert points[2]["asset_value_delta"] >= points[0]["asset_value_delta"]


def test_sensitivity_endpoint(client, make_team, make_player):
    team_a = make_team()
    team_b = make_team()
    player_a = make_player(team_a, position="WR", age=26)
    player_b = make_player(team_b, position="CB", age=27)

    resp = client.post(
        "/api/trades/sensitivity",
        json={
            "team_a": {"team_id": team_a.id, "player_ids": [player_a.id], "draft_pick_ids": []},
            "team_b": {"team_id": team_b.id, "player_ids": [player_b.id], "draft_pick_ids": []},
            "perspective_team_id": team_a.id,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["performance_sensitivity"]) == 3


def test_sensitivity_endpoint_rejects_invalid_perspective(client, make_team, make_player):
    team_a = make_team()
    team_b = make_team()
    team_c = make_team()
    player_a = make_player(team_a, position="WR", age=26)
    player_b = make_player(team_b, position="CB", age=27)

    resp = client.post(
        "/api/trades/sensitivity",
        json={
            "team_a": {"team_id": team_a.id, "player_ids": [player_a.id], "draft_pick_ids": []},
            "team_b": {"team_id": team_b.id, "player_ids": [player_b.id], "draft_pick_ids": []},
            "perspective_team_id": team_c.id,
        },
    )
    assert resp.status_code == 400
