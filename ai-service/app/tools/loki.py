import re

import httpx

from app.config import settings
from app.schemas import LogsSummary, LogLine

EXC_RE = re.compile(r"\b[A-Za-z_][\w.]*Exception\b")

_client: httpx.AsyncClient | None = None


def _client_get() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(base_url=settings.loki_url, timeout=10)
    return _client


def summarize(trace_id: str, result: dict) -> LogsSummary:
    """Pure function: convert a Loki query_range response into LogsSummary."""
    error_count = 0
    warn_count = 0
    first_error: LogLine | None = None
    exception_class: str | None = None
    samples: list[LogLine] = []

    for stream_entry in result.get("data", {}).get("result", []):
        stream = stream_entry.get("stream", {})
        svc = stream.get("service_name", "unknown")
        for ts, line in stream_entry.get("values", []):
            level = stream.get("severity_text") or stream.get("detected_level") or "INFO"
            level_upper = level.upper()
            msg = line[:160]

            # Search for exception class in the raw line
            if exception_class is None:
                exc_match = EXC_RE.search(line)
                if exc_match:
                    exception_class = exc_match.group()

            if level_upper == "ERROR":
                error_count += 1
                if first_error is None:
                    first_error = LogLine(svc=svc, level="ERROR", msg=msg)
                if len(samples) < 3:
                    samples.append(LogLine(svc=svc, level="ERROR", msg=msg))
            elif level_upper == "WARN":
                warn_count += 1
                if len(samples) < 3:
                    samples.append(LogLine(svc=svc, level="WARN", msg=msg))

    return LogsSummary(
        trace_id=trace_id,
        error_count=error_count,
        warn_count=warn_count,
        first_error=first_error,
        exception_class=exception_class,
        samples=samples,
    )


async def logs_for_trace(trace_id: str, since: str = "24h") -> LogsSummary:
    """Query Loki for logs matching a trace_id."""
    client = _client_get()
    query = f'{{service_name=~".+"}} | trace_id="{trace_id}" | severity_text=~"WARN|ERROR"'
    params = {
        "query": query,
        "limit": "20",
        "since": since,
        "direction": "forward",
    }
    resp = await client.get("/loki/api/v1/query_range", params=params)
    resp.raise_for_status()
    return summarize(trace_id, resp.json())
