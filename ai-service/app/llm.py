import json
from typing import AsyncIterator

import httpx

from app.config import settings
from app.prompt import build

OPTIONS = {"num_ctx": 8192, "num_predict": 400, "temperature": 0.1}


async def stream_chat(messages: list[dict]) -> AsyncIterator[str]:
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(
            f"{settings.ollama_url}/api/chat",
            json={
                "model": settings.model,
                "messages": messages,
                "stream": True,
                "think": False,
                "options": OPTIONS,
            },
        )
        if resp.status_code != 200:
            raise RuntimeError(f"ollama {resp.status_code}: {resp.text[:200]}")
        async for line in resp.aiter_lines():
            if not line:
                continue
            obj = json.loads(line)
            msg = obj.get("message", {})
            content = msg.get("content", "")
            if content:
                yield content
            if obj.get("done"):
                break


async def complete(messages: list[dict], fmt: dict | None = None, num_predict: int = 400) -> str:
    async with httpx.AsyncClient(timeout=120) as client:
        payload = {
            "model": settings.model,
            "messages": messages,
            "stream": False,
            "think": False,
            "options": {**OPTIONS, "num_predict": num_predict},
        }
        if fmt is not None:
            payload["format"] = fmt
        resp = await client.post(f"{settings.ollama_url}/api/chat", json=payload)
        if resp.status_code != 200:
            raise RuntimeError(f"ollama {resp.status_code}: {resp.text[:200]}")
        data = resp.json()
        return data.get("message", {}).get("content", "")


if __name__ == "__main__":
    import asyncio

    async def smoke():
        data = {
            "trace": {
                "trace_id": "abcdef1234567890abcdef1234567890",
                "total_ms": 3200,
                "status": "ok",
                "services": ["order-service", "processing-service", "persistence-service"],
                "top_spans": [
                    {"svc": "processing-service", "op": "POST wiremock:8080/thirdparty/enrich", "self_ms": 2800, "pct": 87, "error": False},
                    {"svc": "order-service", "op": "POST /orders", "self_ms": 100, "pct": 3, "error": False},
                    {"svc": "persistence-service", "op": "POST /persist", "self_ms": 50, "pct": 1, "error": False},
                ],
                "error_span": None,
            }
        }
        messages = build("why was this request slow?", "WHY_SLOW", "discussing trace abcdef12 (3200ms, ok)", data)
        async for token in stream_chat(messages):
            print(token, end="", flush=True)
        print()

    asyncio.run(smoke())
