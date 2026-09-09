from eval.conftest import collected_done_events


def test_zz_budget():
    """Runs last (name starts with zz). Asserts every collected done event is within budget."""
    assert len(collected_done_events) > 0, "no done events collected"
    for i, done in enumerate(collected_done_events):
        assert done["tokens_in"] < 3000, f"event {i}: tokens_in {done['tokens_in']} >= 3000"
        assert done["unverified_numbers"] == [], f"event {i}: unverified_numbers {done['unverified_numbers']}"
