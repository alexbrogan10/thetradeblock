from app.analytics.competitive_window import classify_team_timeline
from app.analytics.roster_impact import compute_roster_impact
from app.analytics.team_fit import compute_team_fit
from app.analytics.team_needs import evaluate_team_needs


def test_team_fit_higher_for_critical_need_position(db_session, make_team, make_player):
    team = make_team()
    make_player(team, position="QB", age=27)  # everything else empty -> critical need

    timeline = classify_team_timeline(db_session, team)
    needs = evaluate_team_needs(db_session, team.id)
    needs_by_pos = {n.position: n for n in needs}

    rb_candidate = make_player(None, position="RB", age=26)
    result = compute_team_fit(rb_candidate, None, needs_by_pos.get("RB"), timeline)

    assert result.score > 50
    assert "Critical Need" in result.explanation or "critical need" in result.explanation.lower()


def test_team_fit_explanation_present(db_session, make_team, make_player):
    team = make_team()
    make_player(team, position="QB", age=27)
    timeline = classify_team_timeline(db_session, team)
    needs = evaluate_team_needs(db_session, team.id)
    needs_by_pos = {n.position: n for n in needs}

    player = make_player(None, position="RB", age=26)
    result = compute_team_fit(player, None, needs_by_pos.get("RB"), timeline)
    assert len(result.explanation) > 0


def test_roster_impact_increases_with_strong_addition(db_session, make_team, make_player, make_stats, make_contract):
    team = make_team()
    weak_wr = make_player(team, position="WR", age=30)
    make_stats(weak_wr, stats={"receptions": 20, "targets": 35, "rec_yards": 250, "rec_td": 1, "yards_per_reception": 12.5})

    strong_wr = make_player(None, position="WR", age=25)
    make_stats(strong_wr, stats={"receptions": 100, "targets": 145, "rec_yards": 1400, "rec_td": 11, "yards_per_reception": 14})
    make_contract(strong_wr, annual_value=14, years_remaining=3)

    league_avg_aav = {}
    impact = compute_roster_impact(db_session, team.id, [], [strong_wr], league_avg_aav)
    wr_impact = next(r for r in impact if r.position == "WR")

    assert wr_impact.after > wr_impact.before


def test_roster_impact_drops_to_zero_when_only_player_removed(db_session, make_team, make_player):
    team = make_team()
    only_te = make_player(team, position="TE", age=27)

    league_avg_aav = {}
    impact = compute_roster_impact(db_session, team.id, [only_te.id], [], league_avg_aav)
    te_impact = next(r for r in impact if r.position == "TE")

    assert te_impact.after == 0.0
    assert te_impact.before > te_impact.after
