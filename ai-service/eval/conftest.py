import pytest

from eval.helpers import trigger, wait_for_trace, ask


@pytest.fixture(scope="session")
def slow_trace():
    r = trigger("slow")
    assert r["trace_id"], f"trigger failed: {r}"
    assert wait_for_trace(r["trace_id"]), f"trace {r['trace_id']} not found in Jaeger"
    return r


@pytest.fixture(scope="session")
def fail_trace():
    r = trigger("fail")
    assert r["trace_id"], f"trigger failed: {r}"
    assert wait_for_trace(r["trace_id"]), f"trace {r['trace_id']} not found in Jaeger"
    return r


@pytest.fixture(scope="session")
def fast_trace():
    r = trigger("fast")
    assert r["trace_id"], f"trigger failed: {r}"
    assert wait_for_trace(r["trace_id"]), f"trace {r['trace_id']} not found in Jaeger"
    return r


# Collect every done event for budget check
collected_done_events: list[dict] = []
