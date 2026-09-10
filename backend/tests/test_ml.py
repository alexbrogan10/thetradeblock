from app.models.model_version import ModelVersion


def test_model_versions_endpoint_empty(client):
    resp = client.get("/api/ml/model-versions")
    assert resp.status_code == 200
    assert resp.json() == []


def test_model_versions_endpoint_returns_stored_versions(client, db_session):
    db_session.add(
        ModelVersion(
            model_name="test-model",
            version="v1.0",
            features=["a", "b"],
            parameters={"x": 1},
            evaluation_metrics={"mae": 1.2},
            dataset_version="demo-v1",
            limitations=["Test limitation."],
        )
    )
    db_session.commit()

    resp = client.get("/api/ml/model-versions")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["model_name"] == "test-model"
    assert body[0]["evaluation_metrics"]["mae"] == 1.2


def test_projection_endpoint_reports_unavailable_when_untrained(client, make_team, make_player, monkeypatch):
    import app.ml.performance_projection as pp

    monkeypatch.setattr(pp, "_load_model", lambda: None)

    team = make_team()
    player = make_player(team, position="WR", age=26)
    resp = client.get(f"/api/players/{player.id}/projection")
    assert resp.status_code == 200
    body = resp.json()
    assert body["available"] is False
    assert "not been trained" in body["note"]


def test_projection_endpoint_returns_prediction_when_model_available(client, make_team, make_player, make_stats):
    import app.ml.performance_projection as pp

    if not pp.is_model_available():
        return  # model not trained in this environment; covered by the monkeypatched test above

    team = make_team()
    player = make_player(team, position="WR", age=26)
    make_stats(player, stats={"receptions": 80, "targets": 120, "rec_yards": 1100, "rec_td": 8, "yards_per_reception": 13.7})

    resp = client.get(f"/api/players/{player.id}/projection")
    assert resp.status_code == 200
    body = resp.json()
    assert body["available"] is True
    assert 0 <= body["predicted_performance_score"] <= 100
    assert len(body["top_features"]) > 0


def test_projection_endpoint_404_for_missing_player(client):
    resp = client.get("/api/players/999999/projection")
    assert resp.status_code == 404


def test_trade_matches_endpoint_structure(client, make_team, make_player):
    team = make_team()
    make_player(team, position="QB", age=27)  # everything else empty -> critical need
    other_team = make_team()
    make_player(other_team, position="RB", age=25)

    resp = client.get(f"/api/team/{team.id}/trade-matches")
    assert resp.status_code == 200
    body = resp.json()
    assert body["team"]["id"] == team.id
    assert isinstance(body["matches"], list)
    if body["matches"]:
        match = body["matches"][0]
        assert match["priority"] in ("Critical Need", "Major Need")
        assert "targets" in match


def test_trade_matches_404(client):
    resp = client.get("/api/team/999999/trade-matches")
    assert resp.status_code == 404
