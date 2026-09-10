from app.analytics.competitive_window import classify_team_timeline, CLASSIFICATIONS_HIGH_TO_LOW


def test_classification_is_one_of_the_five_labels(db_session, make_team, make_player):
    team = make_team()
    make_player(team, position="QB", age=27)

    result = classify_team_timeline(db_session, team)
    assert result.classification in CLASSIFICATIONS_HIGH_TO_LOW


def test_empty_roster_does_not_crash(db_session, make_team):
    team = make_team()
    result = classify_team_timeline(db_session, team)
    assert 0 <= result.timeline_score <= 100
    assert result.classification in CLASSIFICATIONS_HIGH_TO_LOW


def test_older_roster_scores_higher_timeline_than_younger_roster(db_session, make_team, make_player):
    old_team = make_team(abbreviation="OLD")
    for _ in range(5):
        make_player(old_team, position="LB", age=33)

    young_team = make_team(abbreviation="YNG")
    for _ in range(5):
        make_player(young_team, position="LB", age=22)

    old_result = classify_team_timeline(db_session, old_team)
    young_result = classify_team_timeline(db_session, young_team)

    assert old_result.timeline_score > young_result.timeline_score


def test_reasons_are_present(db_session, make_team, make_player):
    team = make_team()
    make_player(team, position="QB", age=27)
    result = classify_team_timeline(db_session, team)
    assert len(result.reasons) >= 1
