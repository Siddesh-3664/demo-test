import httpx

ORDER_URL = "http://localhost:8081/orders"
AI_URL = "http://localhost:8000/chat"
JAEGER_URL = "http://localhost:16686"


def trigger(scenario: str = "slow") -> dict:
    """POST an order with X-Scenario; return dict with status, json, trace_id."""
    headers = {"Content-Type": "application/json", "X-Scenario": scenario}
    body = {"item": "widget", "quantity": 2}
    try:
        resp = httpx.post(ORDER_URL, headers=headers, json=body, timeout=30)
        data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
        return {"status": resp.status_code, "json": data, "trace_id": data.get("traceId") or resp.headers.get("X-Trace-Id")}
    except Exception as e:
        return {"status": 0, "json": {}, "trace_id": None, "error": str(e)}


def wait_for_trace(trace_id: str, timeout: int = 15) -> bool:
    """Poll Jaeger until the trace is available."""
    import time
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = httpx.get(f"{JAEGER_URL}/api/traces/{trace_id}", timeout=5)
            if resp.status_code == 200 and resp.json().get("data"):
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def ask(session: str, question: str) -> tuple[str, dict]:
    """Consume the SSE stream from /chat; return (answer_text, done_event)."""
    answer_parts = []
    done = {}
    with httpx.stream("POST", AI_URL, json={"session_id": session, "question": question}, timeout=120) as resp:
        event_type = None
        data_buf = []
        for line in resp.iter_lines():
            if line.startswith("event:"):
                event_type = line[6:].strip()
            elif line.startswith("data:"):
                data_buf.append(line[5:].lstrip())
            elif line == "" and event_type:
                data = "\n".join(data_buf)
                if event_type == "token":
                    answer_parts.append(data)
                elif event_type == "done":
                    import json
                    done = json.loads(data)
                event_type = None
                data_buf = []
    return "".join(answer_parts), done


def ground_truth(trace_id: str) -> dict:
    """Get the TraceSummary for a trace via Jaeger API."""
    from app.tools.jaeger import summarize
    resp = httpx.get(f"{JAEGER_URL}/api/traces/{trace_id}", timeout=10)
    data = resp.json().get("data", [])
    if not data:
        return {}
    return summarize(data[0]).model_dump()
