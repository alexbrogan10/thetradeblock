from app.analytics.draft_pick_valuation import evaluate_draft_pick


def test_pick_value_decreases_monotonically():
    p1 = evaluate_draft_pick(2026, 1, 1)
    p32 = evaluate_draft_pick(2026, 1, 32)
    p64 = evaluate_draft_pick(2026, 2, 64)
    p224 = evaluate_draft_pick(2026, 7, 224)

    assert p1.average_value > p32.average_value > p64.average_value > p224.average_value


def test_first_overall_is_highest_traditional_value():
    p1 = evaluate_draft_pick(2026, 1, 1)
    assert p1.traditional_value == 3000.0


def test_future_pick_without_slot_uses_round_midpoint():
    known = evaluate_draft_pick(2026, 1, 16)
    future = evaluate_draft_pick(2027, 1, None)
    assert future.average_value == known.average_value
    assert "future" in future.pick_label.lower()


def test_model_agreement_label_present():
    result = evaluate_draft_pick(2026, 3, 80)
    assert result.model_agreement in {"High", "Moderate", "Low"}


def test_three_models_are_independent():
    result = evaluate_draft_pick(2026, 1, 10)
    values = {result.traditional_value, result.historical_value, result.expected_value}
    assert len(values) == 3
