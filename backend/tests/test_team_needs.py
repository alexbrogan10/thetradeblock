from app.analytics.team_needs import evaluate_team_needs


def test_position_with_no_players_is_critical_need(db_session, make_team, make_player):
    team = make_team()
    make_player(team, position="QB", age=27)  # only QB filled; everything else empty

    needs = evaluate_team_needs(db_session, team.id)
    by_position = {n.position: n for n in needs}

    assert by_position["RB"].priority == "Critical Need"
    assert by_position["RB"].need_score == 100.0
    assert by_position["RB"].current_depth == 0


def test_single_starter_with_no_backup_flagged(db_session, make_team, make_player, make_stats, make_contract):
    team = make_team()
    player = make_player(team, position="WR", age=26)
    make_stats(player, stats={"receptions": 90, "targets": 130, "rec_yards": 1300, "rec_td": 10, "yards_per_reception": 14.4})
    make_contract(player, annual_value=15, years_remaining=3)

    needs = evaluate_team_needs(db_session, team.id)
    wr_need = next(n for n in needs if n.position == "WR")

    assert wr_need.current_depth == 1
    assert any("no backup depth" in r.lower() for r in wr_need.reasons)


def test_needs_sorted_highest_first(db_session, make_team, make_player):
    team = make_team()
    make_player(team, position="QB", age=27)

    needs = evaluate_team_needs(db_session, team.id)
    scores = [n.need_score for n in needs]
    assert scores == sorted(scores, reverse=True)


def test_expiring_contract_on_good_starter_increases_need(db_session, make_team, make_player, make_stats, make_contract):
    team = make_team()
    stable = make_player(team, position="TE", age=27)
    make_stats(stable, stats={"receptions": 70, "targets": 90, "rec_yards": 850, "rec_td": 7, "yards_per_reception": 12})
    make_contract(stable, annual_value=10, years_remaining=4)

    expiring = make_player(team, position="EDGE", age=27)
    make_stats(expiring, stats={"sacks": 11, "tackles_for_loss": 13, "qb_hits": 19, "forced_fumbles": 3, "tackles": 50})
    make_contract(expiring, annual_value=18, years_remaining=1)

    needs = evaluate_team_needs(db_session, team.id)
    edge_need = next(n for n in needs if n.position == "EDGE")
    assert any("contract expires soon" in r.lower() for r in edge_need.reasons)
