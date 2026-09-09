from app.intents import classify, unknown_reply, TRACE_ID_RE


def test_slowest():
    for q in [
        "which request was slowest today",
        "what took the most time",
        "show me the longest trace",
        "which request was worst",
    ]:
        r = classify(q)
        assert r.intent == "SLOWEST", f"{q!r} -> {r.intent}"


def test_why_fail():
    for q in [
        "why did this request fail",
        "there was an error",
        "I got a 500",
        "something broke",
        "an exception was thrown",
        "did it crash",
    ]:
        r = classify(q)
        assert r.intent == "WHY_FAIL", f"{q!r} -> {r.intent}"


def test_why_fail_with_trace_id():
    r = classify("why did 0123456789abcdef0123456789abcdef fail")
    assert r.intent == "WHY_FAIL"
    assert r.trace_id == "0123456789abcdef0123456789abcdef"


def test_trend():
    for q in [
        "is processing-service getting slower",
        "are we degrading over time",
        "what's the trend",
        "compared to usual",
    ]:
        r = classify(q)
        assert r.intent == "TREND", f"{q!r} -> {r.intent}"


def test_trend_service_extraction():
    r = classify("is processing-service getting slower")
    assert r.intent == "TREND"
    assert r.service == "processing-service"

    r2 = classify("is order-service degrading over time")
    assert r2.intent == "TREND"
    assert r2.service == "order-service"

    r3 = classify("what's the trend")
    assert r3.intent == "TREND"
    assert r3.service == "processing-service"  # default


def test_known():
    for q in [
        "is this a known issue",
        "do we have a runbook for this",
        "have we seen before",
        "how do i fix this",
        "is there a mitigation",
    ]:
        r = classify(q)
        assert r.intent == "KNOWN", f"{q!r} -> {r.intent}"


def test_why_slow():
    for q in [
        "why was this request slow",
        "where did the time go in this request",
        "what is causing the latency",
        "breakdown the request time",
        "why did it take so long",
    ]:
        r = classify(q)
        assert r.intent == "WHY_SLOW", f"{q!r} -> {r.intent}"


def test_unknown():
    for q in [
        "hello",
        "what is the weather",
        "tell me a joke",
    ]:
        r = classify(q)
        assert r.intent == "UNKNOWN", f"{q!r} -> {r.intent}"


def test_unknown_reply():
    assert "slow or failed" in unknown_reply()
    assert "trends" in unknown_reply()
    assert "known issues" in unknown_reply()


def test_trace_id_extraction():
    r = classify("why was abcdef1234567890abcdef1234567890 slow")
    assert r.trace_id == "abcdef1234567890abcdef1234567890"


def test_no_trace_id():
    r = classify("which request was slowest")
    assert r.trace_id is None


import pytest


@pytest.mark.live
@pytest.mark.asyncio
async def test_paraphrase_why_slow():
    from app.intents import classify_async
    r = await classify_async("what dragged this request down")
    assert r.intent == "WHY_SLOW", f"got {r.intent}"


@pytest.mark.live
@pytest.mark.asyncio
async def test_paraphrase_known():
    from app.intents import classify_async
    r = await classify_async("anything documented about this")
    assert r.intent == "KNOWN", f"got {r.intent}"


@pytest.mark.live
@pytest.mark.asyncio
async def test_paraphrase_slowest():
    from app.intents import classify_async
    r = await classify_async("show me the worst performing request")
    assert r.intent == "SLOWEST", f"got {r.intent}"


@pytest.mark.live
@pytest.mark.asyncio
async def test_paraphrase_why_fail():
    from app.intents import classify_async
    r = await classify_async("this request blew up")
    assert r.intent == "WHY_FAIL", f"got {r.intent}"


@pytest.mark.live
@pytest.mark.asyncio
async def test_paraphrase_trend():
    from app.intents import classify_async
    r = await classify_async("are we getting worse over the day")
    assert r.intent == "TREND", f"got {r.intent}"
