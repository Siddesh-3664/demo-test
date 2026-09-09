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

EXAMPLES = {
    "SLOWEST": [
        "which request took the longest today",
        "show me the worst performing request",
        "what was the most time-consuming trace",
    ],
    "WHY_FAIL": [
        "this request blew up",
        "the endpoint returned a server error",
        "something went wrong with that call",
    ],
    "WHY_SLOW": [
        "what dragged this request down",
        "where did all the time go",
        "what is making this call take so long",
    ],
    "TREND": [
        "are we getting worse over the day",
        "has the latency changed compared to before",
        "is the service degrading",
    ],
    "KNOWN": [
        "anything documented about this",
        "have we written up this problem",
        "is there a fix described somewhere",
    ],
}

_example_embeddings: dict[str, list[list[float]]] | None = None


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


def _cosine_sim(a: list[float], b: list[float]) -> float:
    import math
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


async def classify_async(question: str) -> Route:
    """Regex first; if UNKNOWN, try embedding similarity; if that fails, try LLM."""
    route = classify(question)
    if route.intent != "UNKNOWN":
        return route

    trace_id = route.trace_id

    # Try embedding similarity
    try:
        from app.tools.runbooks import embed
        global _example_embeddings

        if _example_embeddings is None:
            _example_embeddings = {}
            for intent, examples in EXAMPLES.items():
                _example_embeddings[intent] = await embed(examples)

        q_emb = (await embed([question]))[0]

        best_intent = "UNKNOWN"
        best_score = 0.0
        for intent, example_embs in _example_embeddings.items():
            for ex_emb in example_embs:
                score = _cosine_sim(q_emb, ex_emb)
                if score > best_score:
                    best_score = score
                    best_intent = intent

        if best_score >= 0.6:
            service = None
            if best_intent == "TREND":
                service = "processing-service"
            return Route(intent=best_intent, trace_id=trace_id, service=service)
    except Exception:
        pass

    # Try LLM fallback
    try:
        from app.llm import complete
        messages = [
            {"role": "system", "content": "Classify the question into exactly one label."},
            {"role": "user", "content": question},
        ]
        fmt = {"type": "string", "enum": ["SLOWEST", "WHY_FAIL", "WHY_SLOW", "TREND", "KNOWN", "UNKNOWN"]}
        result = await complete(messages, fmt=fmt, num_predict=10)
        result = result.strip().upper()
        if result in ("SLOWEST", "WHY_FAIL", "WHY_SLOW", "TREND", "KNOWN", "UNKNOWN"):
            service = None
            if result == "TREND":
                service = "processing-service"
            return Route(intent=result, trace_id=trace_id, service=service)
    except Exception:
        pass

    return Route(intent="UNKNOWN", trace_id=trace_id, service=None)
