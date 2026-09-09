import logging
import time
from typing import AsyncIterator

from app.budget import trim, estimate_tokens
from app.intents import classify_async, unknown_reply
from app.llm import stream_chat
from app.prompt import build
from app.session import get as get_session, update_trace
from app.tools import jaeger, prometheus, loki, runbooks
from app.verify import unverified_numbers

log = logging.getLogger("pipeline")


async def run(session_id: str, question: str) -> AsyncIterator[dict]:
    """Yields {"type":"token","text":...} then one {"type":"done", ...}."""
    route = await classify_async(question)

    # Resolve trace_id: question → session → newest trace
    trace_id = route.trace_id
    if trace_id is None:
        sess = get_session(session_id)
        trace_id = sess.current_trace_id

    data: dict = {}

    if route.intent == "UNKNOWN":
        answer = unknown_reply()
        yield {"type": "token", "text": answer}
        yield {
            "type": "done",
            "intent": "UNKNOWN",
            "trace_id": trace_id,
            "tokens_in": 0,
            "unverified_numbers": [],
        }
        return

    if route.intent == "SLOWEST":
        slowest = await jaeger.slowest(lookback="1h", min_duration="0ms", limit=1)
        if slowest.rows:
            trace_id = slowest.rows[0].trace_id
            data["slowest"] = slowest.model_dump()
            data["trace"] = (await jaeger.detail(trace_id)).model_dump()
            if data["trace"].get("status") == "error":
                data["logs"] = (await loki.logs_for_trace(trace_id)).model_dump()

    elif route.intent == "WHY_FAIL":
        if trace_id is None:
            slowest = await jaeger.slowest(lookback="1h", min_duration="0ms", limit=1)
            if slowest.rows:
                trace_id = slowest.rows[0].trace_id
        if trace_id:
            data["trace"] = (await jaeger.detail(trace_id)).model_dump()
            data["logs"] = (await loki.logs_for_trace(trace_id)).model_dump()
            # Search runbooks using the error message
            search_query = "failure"
            if data.get("logs", {}).get("first_error"):
                search_query = data["logs"]["first_error"].get("msg", "failure")
            data["runbooks"] = (await runbooks.search(search_query)).model_dump()

    elif route.intent == "WHY_SLOW":
        if trace_id is None:
            slowest = await jaeger.slowest(lookback="1h", min_duration="0ms", limit=1)
            if slowest.rows:
                trace_id = slowest.rows[0].trace_id
        if trace_id:
            data["trace"] = (await jaeger.detail(trace_id)).model_dump()
            if data["trace"].get("status") == "error":
                data["logs"] = (await loki.logs_for_trace(trace_id)).model_dump()

    elif route.intent == "TREND":
        svc = route.service or "processing-service"
        data["p95"] = (await prometheus.p95(svc)).model_dump()
        data["errors"] = (await prometheus.error_rate(svc)).model_dump()

    elif route.intent == "KNOWN":
        data["runbooks"] = (await runbooks.search(question)).model_dump()
        if trace_id:
            data["trace"] = (await jaeger.detail(trace_id)).model_dump()

    data = trim(data)
    tokens_in = estimate_tokens(data) + 300

    sess = get_session(session_id)
    context_line = sess.context_line
    if trace_id and "trace" in data:
        update_trace(session_id, __import__("app.schemas", fromlist=["TraceSummary"]).TraceSummary(**data["trace"]))

    messages = build(question, route.intent, context_line, data)

    answer_parts = []
    start = time.monotonic()
    async for token in stream_chat(messages):
        answer_parts.append(token)
        yield {"type": "token", "text": token}

    answer = "".join(answer_parts)
    elapsed_ms = int((time.monotonic() - start) * 1000)

    log.info("%s %s %d %dms", route.intent, trace_id, tokens_in, elapsed_ms)

    yield {
        "type": "done",
        "intent": route.intent,
        "trace_id": trace_id,
        "tokens_in": tokens_in,
        "unverified_numbers": unverified_numbers(answer, data),
    }
