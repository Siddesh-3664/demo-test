from eval.helpers import ask
from eval.conftest import collected_done_events


def test_eval_known(fail_trace):
    answer, done = ask("eval-known", "is this a known issue?")
    collected_done_events.append(done)
    assert done["intent"] == "KNOWN", f"intent: {done['intent']}"
    assert any(w in answer.lower() for w in ["third-party", "thirdparty", "upstream"]), f"answer: {answer}"
    assert done["tokens_in"] < 3000, f"tokens_in: {done['tokens_in']}"
    assert done["unverified_numbers"] == [], f"unverified: {done['unverified_numbers']}"
