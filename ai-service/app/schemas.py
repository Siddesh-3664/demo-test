from pydantic import BaseModel


class SpanRow(BaseModel):
    svc: str
    op: str            # ≤ 60 chars
    self_ms: int
    pct: int
    error: bool


class TraceSummary(BaseModel):
    trace_id: str
    total_ms: int
    status: str        # "ok" | "error"
    services: list[str]
    top_spans: list[SpanRow]          # ≤ 5, by self_ms desc
    error_span: SpanRow | None = None


class TraceRow(BaseModel):
    trace_id: str
    total_ms: int
    root_op: str
    status: str
    started_at: str    # ISO-8601 seconds


class SlowestTraces(BaseModel):
    window: str
    count_found: int
    rows: list[TraceRow]              # ≤ 5


class MetricsSummary(BaseModel):
    service: str
    metric: str        # "p95_latency_ms" | "error_rate_pct"
    window: str
    now: float
    start: float
    delta_pct: int
    trend: str         # "up" | "flat" | "down"   (|delta_pct| < 10 → flat)
    samples: list[float]              # exactly 5


class LogLine(BaseModel):
    svc: str
    level: str
    msg: str           # ≤ 160 chars


class LogsSummary(BaseModel):
    trace_id: str
    error_count: int
    warn_count: int
    first_error: LogLine | None
    exception_class: str | None
    samples: list[LogLine]            # ≤ 3


class RunbookHit(BaseModel):
    title: str
    snippet: str       # ≤ 300 chars
    score: float


class RunbookHits(BaseModel):
    hits: list[RunbookHit]            # ≤ 2
