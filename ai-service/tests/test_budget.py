from app.schemas import SpanRow, TraceSummary, LogLine, LogsSummary, RunbookHit, RunbookHits
from app.budget import trim, estimate_tokens, LIMIT


def _make_trace_summary(n_spans: int = 5) -> dict:
    spans = [
        SpanRow(svc="processing-service", op=f"POST /thirdparty/enrich {i}", self_ms=100 * (n_spans - i), pct=20, error=False)
        for i in range(n_spans)
    ]
    return TraceSummary(
        trace_id="a" * 32,
        total_ms=5000,
        status="ok",
        services=["order-service", "processing-service", "persistence-service"],
        top_spans=spans,
    ).model_dump()


def _make_logs_summary(n_samples: int = 3, sample_len: int = 160) -> dict:
    samples = [
        LogLine(svc="processing-service", level="ERROR", msg="x" * sample_len).model_dump()
        for _ in range(n_samples)
    ]
    return LogsSummary(
        trace_id="a" * 32,
        error_count=1,
        warn_count=0,
        first_error=LogLine(svc="processing-service", level="ERROR", msg="boom"),
        exception_class="RuntimeException",
        samples=samples,
    ).model_dump()


def _make_runbooks_hits() -> dict:
    return RunbookHits(
        hits=[
            RunbookHit(title="Runbook A", snippet="y" * 300, score=0.9),
            RunbookHit(title="Runbook B", snippet="z" * 300, score=0.8),
        ]
    ).model_dump()


def test_trim_under_limit_returns_copy():
    data = {"trace": _make_trace_summary(5)}
    result = trim(data)
    assert estimate_tokens(result) <= LIMIT


def test_trim_drops_runbooks_first():
    data = {
        "runbooks": _make_runbooks_hits(),
        "logs": _make_logs_summary(3, 160),
        "trace": _make_trace_summary(5),
    }
    result = trim(data, limit=400)
    assert "runbooks" not in result
    assert estimate_tokens(result) <= 400


def test_trim_drops_logs_samples_second():
    data = {
        "logs": _make_logs_summary(10, 160),
        "trace": _make_trace_summary(5),
    }
    result = trim(data, limit=300)
    if "logs" in result:
        assert "samples" not in result["logs"]
    assert estimate_tokens(result) <= 300


def test_trim_top_spans_never_shorter_than_3():
    data = {"trace": _make_trace_summary(5)}
    result = trim(data, limit=100)
    assert len(result["trace"]["top_spans"]) >= 3


def test_trim_does_not_mutate_original():
    data = {"trace": _make_trace_summary(5), "runbooks": _make_runbooks_hits()}
    original_spans = len(data["trace"]["top_spans"])
    _ = trim(data, limit=800)
    assert len(data["trace"]["top_spans"]) == original_spans
    assert "runbooks" in data
