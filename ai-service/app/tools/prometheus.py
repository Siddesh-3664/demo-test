import math
from datetime import datetime, timezone

import httpx

from app.config import settings
from app.schemas import MetricsSummary

WINDOWS = {"15m": 900, "1h": 3600, "6h": 21600, "24h": 86400}

_client: httpx.AsyncClient | None = None


def _client_get() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(base_url=settings.prom_url, timeout=10)
    return _client


def _trend(delta_pct: int) -> str:
    if abs(delta_pct) < 10:
        return "flat"
    return "up" if delta_pct > 0 else "down"


def summarize(service: str, metric: str, window: str, values: list[tuple[float, float]]) -> MetricsSummary:
    """Pure function: convert (timestamp, value) pairs into MetricsSummary."""
    w = WINDOWS.get(window, 3600)
    # p95 values come from Prometheus in seconds; convert to ms
    if metric == "p95_latency_ms":
        values = [(ts, v * 1000) for ts, v in values]
    samples = [round(v, 1) for _, v in values]
    # Pad to 5
    while len(samples) < 5:
        samples.append(0.0)
    samples = samples[:5]

    start = samples[0] if samples else 0.0
    now = samples[-1] if samples else 0.0
    delta_pct = round(100 * (now - start) / start) if start else 0
    trend = _trend(delta_pct)

    return MetricsSummary(
        service=service,
        metric=metric,
        window=window,
        now=now,
        start=start,
        delta_pct=delta_pct,
        trend=trend,
        samples=samples,
    )


async def _query_range(promql: str, window: str) -> list[tuple[float, float]]:
    w = WINDOWS.get(window, 3600)
    now_ts = datetime.now(timezone.utc).timestamp()
    start_ts = now_ts - w
    step = max(1, w // 4)
    client = _client_get()
    params = {
        "query": promql,
        "start": str(start_ts),
        "end": str(now_ts),
        "step": str(step),
    }
    resp = await client.get("/api/v1/query_range", params=params)
    resp.raise_for_status()
    data = resp.json()
    if data.get("status") != "success":
        return []
    result = data.get("data", {}).get("result", [])
    if not result:
        return []
    values = result[0].get("values", [])
    return [(float(ts), float(val)) for ts, val in values]


async def p95(service: str, window: str = "1h") -> MetricsSummary:
    promql = (
        f'histogram_quantile(0.95, sum by (le) '
        f'(rate(http_server_request_duration_seconds_bucket{{service_name="{service}"}}[5m])))'
    )
    values = await _query_range(promql, window)
    return summarize(service, "p95_latency_ms", window, values)


async def error_rate(service: str, window: str = "1h") -> MetricsSummary:
    promql = (
        f'100 * sum(rate(http_server_request_duration_seconds_count'
        f'{{service_name="{service}",http_response_status_code=~"5.."}}[5m])) '
        f'/ sum(rate(http_server_request_duration_seconds_count{{service_name="{service}"}}[5m]))'
    )
    values = await _query_range(promql, window)
    values_clean = [(ts, v if not math.isnan(v) else 0.0) for ts, v in values]
    return summarize(service, "error_rate_pct", window, values_clean)
