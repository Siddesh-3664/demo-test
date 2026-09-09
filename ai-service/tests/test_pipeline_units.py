from app.verify import unverified_numbers
from app.prompt import build, SYSTEM, HINTS, USER
from app.session import get, update_trace, Session
from app.schemas import SpanRow, TraceSummary


def test_unverified_numbers_empty():
    data = {"trace": {"total_ms": 3200, "top_spans": [{"self_ms": 2800}]}}
    answer = "The request took 3200ms. The slowest span was 2800ms."
    assert unverified_numbers(answer, data) == []


def test_unverified_numbers_finds_fake():
    data = {"trace": {"total_ms": 3200, "top_spans": [{"self_ms": 2800}]}}
    answer = "The request took 9999ms."
    assert any("9999" in n for n in unverified_numbers(answer, data))


def test_unverified_numbers_pct():
    data = {"trace": {"total_ms": 3200, "top_spans": [{"pct": 87}]}}
    answer = "The span took 87% of the time."
    assert unverified_numbers(answer, data) == []


def test_prompt_build():
    data = {"trace": {"total_ms": 100}}
    msgs = build("why was it slow?", "WHY_SLOW", "discussing trace abc (100ms, ok)", data)
    assert len(msgs) == 2
    assert msgs[0]["role"] == "system"
    assert msgs[0]["content"] == SYSTEM
    assert msgs[1]["role"] == "user"
    assert "why was it slow?" in msgs[1]["content"]
    assert "WHY_SLOW" not in msgs[1]["content"] or HINTS["WHY_SLOW"] in msgs[1]["content"]
    assert "100" in msgs[1]["content"]


def test_session_get_creates():
    s = get("test-session-1")
    assert isinstance(s, Session)
    assert s.current_trace_id is None
    assert s.context_line == "none"


def test_session_update_trace():
    summary = TraceSummary(
        trace_id="a" * 32,
        total_ms=3200,
        status="ok",
        services=["order-service"],
        top_spans=[SpanRow(svc="order-service", op="POST /orders", self_ms=100, pct=100, error=False)],
    )
    update_trace("test-session-2", summary)
    s = get("test-session-2")
    assert s.current_trace_id == "a" * 32
    assert "3200ms" in s.context_line
    assert "ok" in s.context_line
