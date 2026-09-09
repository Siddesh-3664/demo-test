import json
from pathlib import Path

from app.tools.jaeger import summarize, is_error
from app.schemas import TraceSummary


def _load_fixture() -> dict:
    fixture_path = Path(__file__).parent / "fixtures" / "trace_slow.json"
    with open(fixture_path) as f:
        data = json.load(f)
    return data["data"][0]


def test_summarize_total_ms():
    trace = _load_fixture()
    result = summarize(trace)
    assert result.total_ms >= 2000


def test_summarize_top_span_is_processing_service():
    trace = _load_fixture()
    result = summarize(trace)
    assert result.top_spans[0].svc == "processing-service"


def test_summarize_top_span_pct_ge_60():
    trace = _load_fixture()
    result = summarize(trace)
    assert result.top_spans[0].pct >= 60


def test_summarize_top_span_op_mentions_wiremock_or_enrich():
    trace = _load_fixture()
    result = summarize(trace)
    op = result.top_spans[0].op.lower()
    assert "wiremock" in op or "enrich" in op or "post" in op


def test_summarize_pct_sum_le_105():
    trace = _load_fixture()
    result = summarize(trace)
    assert sum(r.pct for r in result.top_spans) <= 105


def test_summarize_top_spans_le_5():
    trace = _load_fixture()
    result = summarize(trace)
    assert len(result.top_spans) <= 5


def test_summarize_status_ok():
    trace = _load_fixture()
    result = summarize(trace)
    assert result.status == "ok"


def test_summarize_services_sorted_unique():
    trace = _load_fixture()
    result = summarize(trace)
    assert result.services == sorted(set(result.services))
    assert "order-service" in result.services
    assert "processing-service" in result.services


def test_is_error_no_tags():
    assert is_error({"tags": []}) is False


def test_is_error_true_tag():
    assert is_error({"tags": [{"key": "error", "value": True}]}) is True


def test_is_error_otel_status():
    assert is_error({"tags": [{"key": "otel.status_code", "value": "ERROR"}]}) is True


def test_is_error_500_status():
    assert is_error({"tags": [{"key": "http.response.status_code", "value": 500}]}) is True


def test_is_error_200_status():
    assert is_error({"tags": [{"key": "http.response.status_code", "value": 200}]}) is False
