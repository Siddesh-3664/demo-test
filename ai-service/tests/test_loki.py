import json
from pathlib import Path

from app.tools.loki import summarize, EXC_RE


def _load_fixture() -> dict:
    fixture_path = Path(__file__).parent / "fixtures" / "loki_fail.json"
    with open(fixture_path) as f:
        return json.load(f)


def test_summarize_error_count():
    result = _load_fixture()
    summary = summarize("abcdef1234567890abcdef1234567890", result)
    assert summary.error_count >= 1


def test_summarize_first_error_svc():
    result = _load_fixture()
    summary = summarize("abcdef1234567890abcdef1234567890", result)
    assert summary.first_error is not None
    assert summary.first_error.svc == "processing-service"


def test_summarize_first_error_msg():
    result = _load_fixture()
    summary = summarize("abcdef1234567890abcdef1234567890", result)
    assert summary.first_error is not None
    assert "Third-party enrich failed" in summary.first_error.msg


def test_summarize_samples_le_3():
    result = _load_fixture()
    summary = summarize("abcdef1234567890abcdef1234567890", result)
    assert len(summary.samples) <= 3


def test_summarize_exception_class():
    result = _load_fixture()
    summary = summarize("abcdef1234567890abcdef1234567890", result)
    assert summary.exception_class is not None
    assert "Exception" in summary.exception_class


def test_exc_re():
    assert EXC_RE.search("HttpServerErrorException: 500")
    assert EXC_RE.search("raised RuntimeException")
    assert not EXC_RE.search("no exception here")
