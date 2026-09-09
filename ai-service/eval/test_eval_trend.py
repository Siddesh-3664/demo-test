from eval.helpers import ask
from eval.conftest import collected_done_events


def test_eval_trend(slow_trace):
    answer, done = ask("eval-trend", "is processing-service getting slower over time?")
    collected_done_events.append(done)
    assert done["intent"] == "TREND", f"intent: {done['intent']}"
    assert done["unverified_numbers"] == [], f"unverified: {done['unverified_numbers']}"
    assert "processing-service" in answer.lower(), f"answer: {answer}"
    assert any(w in answer.lower() for w in ["up", "flat", "down"]), f"answer: {answer}"
