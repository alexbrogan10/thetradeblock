from app.analytics.player_valuation import evaluate_player


def test_strong_qb_outvalues_weak_qb(make_team, make_player, make_stats, make_contract):
    team = make_team()
    strong = make_player(team, position="QB", age=27)
    weak = make_player(team, position="QB", age=27)

    strong_stat = make_stats(strong, stats={
        "games": 17, "pass_yards": 4900, "pass_td": 38, "interceptions": 8,
        "completion_pct": 69, "rush_yards": 300, "epa_per_play": 0.22,
    })
    weak_stat = make_stats(weak, stats={
        "games": 17, "pass_yards": 2800, "pass_td": 14, "interceptions": 15,
        "completion_pct": 58, "rush_yards": 20, "epa_per_play": -0.02,
    })
    make_contract(strong, annual_value=40, years_remaining=3)
    make_contract(weak, annual_value=40, years_remaining=3)

    result_strong = evaluate_player(strong, [strong_stat], None, {})
    result_weak = evaluate_player(weak, [weak_stat], None, {})

    assert result_strong.performance_score > result_weak.performance_score
    assert result_strong.valuation > result_weak.valuation


def test_age_score_peaks_near_position_prime(make_team, make_player):
    team = make_team()
    prime_qb = make_player(team, position="QB", age=29)
    old_qb = make_player(team, position="QB", age=41)

    prime_result = evaluate_player(prime_qb, [], None, {})
    old_result = evaluate_player(old_qb, [], None, {})

    assert prime_result.age_score > old_result.age_score


def test_missing_contract_defaults_to_neutral_and_lowers_confidence(make_team, make_player):
    team = make_team()
    player = make_player(team, position="WR", age=26)

    with_contract_result = evaluate_player(player, [], _FakeContract(annual_value=12, years_remaining=2, guaranteed_money=10), {"WR": 10.0})
    without_contract_result = evaluate_player(player, [], None, {"WR": 10.0})

    assert without_contract_result.contract_score == 50.0
    assert without_contract_result.confidence < with_contract_result.confidence
    assert "Contract data unavailable" in " ".join(without_contract_result.notes)


def test_missing_statistics_defaults_to_neutral_performance(make_team, make_player):
    team = make_team()
    player = make_player(team, position="RB", age=24)

    result = evaluate_player(player, [], None, {})
    assert result.performance_score == 50.0
    assert result.confidence < 60


def test_extreme_production_is_clipped_to_100(make_team, make_player, make_stats):
    team = make_team()
    player = make_player(team, position="WR", age=27)
    stat = make_stats(player, stats={
        "receptions": 400, "targets": 500, "rec_yards": 9000, "rec_td": 60,
        "yards_per_reception": 40,
    })

    result = evaluate_player(player, [stat], None, {})
    assert result.performance_score <= 100
    assert result.valuation <= 100


def test_valuation_never_below_zero_or_above_hundred(make_team, make_player, make_stats):
    team = make_team()
    player = make_player(team, position="K", age=45)
    stat = make_stats(player, stats={"fg_pct": 0.0, "long": 0, "fg_made": 0})

    result = evaluate_player(player, [stat], None, {})
    assert 0 <= result.valuation <= 100


class _FakeContract:
    def __init__(self, annual_value, years_remaining, guaranteed_money):
        self.annual_value = annual_value
        self.years_remaining = years_remaining
        self.guaranteed_money = guaranteed_money
