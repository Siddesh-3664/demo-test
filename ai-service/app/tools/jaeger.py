import asyncio
from datetime import datetime, timezone

import httpx

from app.config import settings
from app.schemas import SpanRow, TraceSummary, TraceRow, SlowestTraces

_client: httpx.AsyncClient | None = None


def _client_get() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(base_url=settings.jaeger_url, timeout=10)
    return _client


def is_error(span: dict) -> bool:
    """Contracts §6.5 rule: span is an error if any tag error=true, otel.status_code=ERROR, or http.response.status_code>=500."""
    for tag in span.get("tags", []):
        key = tag.get("key")
        val = tag.get("value")
        if key == "error" and val is True:
            return True
        if key == "otel.status_code" and val == "ERROR":
            return True
        if key == "http.response.status_code" and isinstance(val, (int, str)):
            try:
                if int(val) >= 500:
                    return True
            except (ValueError, TypeError):
                pass
    return False


def _get_tag(span: dict, key: str, default=None):
    for tag in span.get("tags", []):
        if tag.get("key") == key:
            return tag.get("value")
    return default


def summarize(trace: dict) -> TraceSummary:
    """Pure function: convert a Jaeger trace dict into a TraceSummary."""
    procs = trace["processes"]
    spans = trace["spans"]

    # Build child map: parent_span_id -> [child spans]
    children: dict[str, list] = {}
    for sp in spans:
        for ref in sp.get("references", []):
            if ref.get("refType") == "CHILD_OF":
                parent_id = ref["spanID"]
                children.setdefault(parent_id, []).append(sp)

    # Find root span: no CHILD_OF reference (fallback: min startTime)
    root = None
    for sp in spans:
        refs = sp.get("references", [])
        has_child_of = any(r.get("refType") == "CHILD_OF" for r in refs)
        if not has_child_of:
            root = sp
            break
    if root is None:
        root = min(spans, key=lambda s: s["startTime"])

    total_us = root["duration"]
    total_ms = total_us // 1000

    # Compute self time for each span
    rows = []
    for sp in spans:
        child_duration_sum = sum(c["duration"] for c in children.get(sp["spanID"], []))
        self_us = max(0, sp["duration"] - child_duration_sum)
        self_ms = self_us // 1000
        proc = procs.get(sp["processID"], {})
        svc = proc.get("serviceName", "unknown")

        # Build a descriptive op name
        op = sp["operationName"][:60]
        server_addr = _get_tag(sp, "server.address")
        http_method = _get_tag(sp, "http.request.method")
        url_path = _get_tag(sp, "url.path")
        if server_addr and http_method:
            path = url_path or ""
            op = f"{http_method} {server_addr}{path}"[:60]

        pct = round(100 * self_us / total_us) if total_us > 0 else 0
        rows.append(SpanRow(
            svc=svc,
            op=op,
            self_ms=self_ms,
            pct=pct,
            error=is_error(sp),
        ))

    # top_spans: 5 largest by self_ms
    top_spans = sorted(rows, key=lambda r: r.self_ms, reverse=True)[:5]

    # error_span: first error row in span start order
    error_span = None
    span_start_order = sorted(
        range(len(spans)),
        key=lambda i: spans[i]["startTime"]
    )
    for idx in span_start_order:
        if rows[idx].error:
            error_span = rows[idx]
            break

    status = "error" if any(r.error for r in rows) else "ok"
    services = sorted(set(r.svc for r in rows))

    return TraceSummary(
        trace_id=trace["traceID"],
        total_ms=total_ms,
        status=status,
        services=services,
        top_spans=top_spans,
        error_span=error_span,
    )


async def slowest(lookback: str = "24h", min_duration: str = "1s", limit: int = 100,
                  service: str = "order-service") -> SlowestTraces:
    """GET /api/traces with params, sort by root duration desc, take 5."""
    client = _client_get()
    params = {
        "service": service,
        "lookback": lookback,
        "minDuration": min_duration,
        "limit": str(limit),
    }
    resp = await client.get("/api/traces", params=params)
    resp.raise_for_status()
    data = resp.json().get("data", [])

    # Sort by root duration desc
    def root_duration(trace):
        spans = trace.get("spans", [])
        root = None
        for sp in spans:
            refs = sp.get("references", [])
            if not any(r.get("refType") == "CHILD_OF" for r in refs):
                root = sp
                break
        if root is None and spans:
            root = min(spans, key=lambda s: s["startTime"])
        return root["duration"] if root else 0

    data.sort(key=root_duration, reverse=True)
    top = data[:5]

    rows = []
    for trace in top:
        spans = trace.get("spans", [])
        root = None
        for sp in spans:
            refs = sp.get("references", [])
            if not any(r.get("refType") == "CHILD_OF" for r in refs):
                root = sp
                break
        if root is None and spans:
            root = min(spans, key=lambda s: s["startTime"])
        if root is None:
            continue
        total_ms = root["duration"] // 1000
        procs = trace.get("processes", {})
        svc = procs.get(root.get("processID", ""), {}).get("serviceName", "unknown")
        # started_at from root startTime µs → ISO seconds UTC
        started_ts = root["startTime"] / 1_000_000
        started_at = datetime.fromtimestamp(started_ts, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        # Determine status
        trace_status = "error" if any(is_error(sp) for sp in spans) else "ok"

        rows.append(TraceRow(
            trace_id=trace["traceID"],
            total_ms=total_ms,
            root_op=root["operationName"][:60],
            status=trace_status,
            started_at=started_at,
        ))

    return SlowestTraces(
        window=f"last {lookback}",
        count_found=len(data),
        rows=rows,
    )


async def detail(trace_id: str) -> TraceSummary:
    """GET /api/traces/{traceId} → TraceSummary."""
    client = _client_get()
    resp = await client.get(f"/api/traces/{trace_id}")
    resp.raise_for_status()
    data = resp.json().get("data", [])
    if not data:
        raise ValueError(f"trace {trace_id} not found")
    return summarize(data[0])
