from dataclasses import dataclass, field

from app.schemas import TraceSummary

_sessions: dict[str, "Session"] = {}


@dataclass
class Session:
    current_trace_id: str | None = None
    context_line: str = "none"


def get(session_id: str) -> Session:
    if session_id not in _sessions:
        _sessions[session_id] = Session()
    return _sessions[session_id]


def update_trace(session_id: str, summary: TraceSummary) -> None:
    s = get(session_id)
    s.current_trace_id = summary.trace_id
    s.context_line = f"discussing trace {summary.trace_id} ({summary.total_ms}ms, {summary.status})"
