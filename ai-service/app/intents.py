import re
from dataclasses import dataclass

TRACE_ID_RE = re.compile(r"\b[0-9a-f]{32}\b")
SERVICES = ["order-service", "processing-service", "persistence-service"]

# Order of evaluation per Contracts §7.3
_INTENTS = [
    ("SLOWEST",  re.compile(r"slowest|most time|longest|took the most|worst", re.IGNORECASE)),
    ("WHY_FAIL", re.compile(r"fail|error|500|broke|exception|crash", re.IGNORECASE)),
    ("TREND",    re.compile(r"getting slower|over time|trend|degrad|compared to|usual", re.IGNORECASE)),
    ("KNOWN",    re.compile(r"known issue|runbook|seen before|how do i fix|mitigat", re.IGNORECASE)),
    ("WHY_SLOW", re.compile(r"(why|what).*(slow|long|latency|took)|breakdown|where.*time", re.IGNORECASE)),
]

_UNKNOWN_REPLY = "I can answer questions about slow or failed requests, trends, and known issues."


@dataclass
class Route:
    intent: str            # SLOWEST | WHY_FAIL | WHY_SLOW | TREND | KNOWN | UNKNOWN
    trace_id: str | None   # from question only; pipeline resolves session/newest
    service: str | None    # TREND only


def classify(question: str) -> Route:
    trace_id = None
    m = TRACE_ID_RE.search(question)
    if m:
        trace_id = m.group()

    for intent, pattern in _INTENTS:
        if pattern.search(question):
            service = None
            if intent == "TREND":
                for svc in SERVICES:
                    if svc in question.lower():
                        service = svc
                        break
                if service is None:
                    service = "processing-service"
            return Route(intent=intent, trace_id=trace_id, service=service)

    return Route(intent="UNKNOWN", trace_id=trace_id, service=None)


def unknown_reply() -> str:
    return _UNKNOWN_REPLY
