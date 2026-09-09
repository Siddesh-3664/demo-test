import re

from eval.helpers import ask, ground_truth
from eval.conftest import collected_done_events


def test_why_slow(slow_trace):
    answer, done = ask("eval-slow", f"why was {slow_trace['trace_id']} slow?")
    collected_done_events.append(done)
    assert "processing-service" in answer.lower(), f"answer: {answer}"
    assert any(w in answer.lower() for w in ["enrich", "thirdparty", "third-party"]), f"answer: {answer}"
    assert done["intent"] == "WHY_SLOW", f"intent: {done['intent']}"
    assert done["tokens_in"] < 3000, f"tokens_in: {done['tokens_in']}"
    assert done["unverified_numbers"] == [], f"unverified: {done['unverified_numbers']}"
    # every <n> ms in answer must be in ground_truth
    gt = ground_truth(slow_trace["trace_id"])
    gt_nums = set(re.findall(r"\d+(?:\.\d+)?", re.sub(r"[^0-9.]", " ", str(gt))))
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s?ms", answer):
        if m.group(1) not in gt_nums:
            pytest.fail(f"number {m.group(1)}ms not in ground truth")


def test_slowest(slow_trace):
    answer, done = ask("eval-slowest", "which request was slowest in the last hour?")
    collected_done_events.append(done)
    gt = ground_truth(slow_trace["trace_id"])
    assert slow_trace["trace_id"][:8] in answer or str(gt.get("total_ms", "")) in answer, f"answer: {answer}"
    assert done["tokens_in"] < 3000


def test_unknown():
    answer, done = ask("eval-unknown", "hello")
    collected_done_events.append(done)
    assert done["intent"] == "UNKNOWN"
    assert done["tokens_in"] == 0
    assert "slow or failed" in answer.lower() or "trends" in answer.lower()


def test_tokens_budget(slow_trace, fail_trace):
    for label, trace in [("slow", slow_trace), ("fail", fail_trace)]:
        _, done = ask(f"eval-budget-{label}", f"why was {trace['trace_id']} slow?")
        collected_done_events.append(done)
        assert done["tokens_in"] < 3000, f"{label} tokens_in: {done['tokens_in']}"
