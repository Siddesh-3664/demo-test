from app.tools.prometheus import summarize, _trend


def test_summarize_up():
    values = [(1, 0.1), (2, 0.12), (3, 0.2), (4, 0.4), (5, 0.5)]
    m = summarize("processing-service", "p95_latency_ms", "1h", values)
    assert m.now == 500.0
    assert m.start == 100.0
    assert m.trend == "up"
    assert len(m.samples) == 5
    assert m.service == "processing-service"
    assert m.metric == "p95_latency_ms"


def test_summarize_flat():
    values = [(1, 100.0), (2, 101.0), (3, 99.0), (4, 100.0), (5, 100.0)]
    m = summarize("order-service", "error_rate_pct", "15m", values)
    assert m.trend == "flat"
    assert abs(m.delta_pct) < 10


def test_summarize_down():
    values = [(1, 500.0), (2, 400.0), (3, 300.0), (4, 200.0), (5, 100.0)]
    m = summarize("persistence-service", "p95_latency_ms", "6h", values)
    assert m.trend == "down"
    assert m.delta_pct < 0


def test_summarize_pads_to_5():
    values = [(1, 100.0), (2, 200.0)]
    m = summarize("order-service", "p95_latency_ms", "1h", values)
    assert len(m.samples) == 5
    assert m.samples[2] == 0.0
    assert m.samples[4] == 0.0


def test_trend_threshold():
    assert _trend(9) == "flat"
    assert _trend(-9) == "flat"
    assert _trend(10) == "up"
    assert _trend(-10) == "down"
    assert _trend(50) == "up"
    assert _trend(-50) == "down"
