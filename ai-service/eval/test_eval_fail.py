from eval.helpers import ask, ground_truth
from app.tools.loki import logs_for_trace
from eval.conftest import collected_done_events
import asyncio


def test_eval_fail(fail_trace):
    answer, done = ask("eval-fail", f"why did {fail_trace['trace_id']} fail?")
    collected_done_events.append(done)
    assert "processing-service" in answer.lower(), f"answer: {answer}"
    assert any(w in answer.lower() for w in ["upstream unavailable", "500", "exception"]), f"answer: {answer}"
    assert done["intent"] == "WHY_FAIL", f"intent: {done['intent']}"
    assert done["unverified_numbers"] == [], f"unverified: {done['unverified_numbers']}"
    assert done["tokens_in"] < 3000, f"tokens_in: {done['tokens_in']}"
    # Ground truth: logs exist for this trace
    logs = asyncio.run(logs_for_trace(fail_trace["trace_id"]))
    assert logs.error_count >= 1, f"no error logs found for {fail_trace['trace_id']}"
