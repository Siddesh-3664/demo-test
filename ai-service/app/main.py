import json
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from app.config import settings
from app.pipeline import run as run_pipeline

log = logging.getLogger("ai-service")

app = FastAPI(title="ai-service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    try:
        from app.tools.runbooks import index
        count = await index()
        log.info("indexed %d runbook chunks", count)
    except Exception as e:
        log.warning("runbook indexing skipped: %s", e)


@app.get("/health")
async def health():
    return {"ok": True, "model": settings.model}


class ChatRequest(BaseModel):
    session_id: str
    question: str


@app.post("/chat")
async def chat(req: ChatRequest):
    async def gen():
        async for ev in run_pipeline(req.session_id, req.question):
            if ev["type"] == "token":
                yield {"event": "token", "data": ev["text"]}
            else:
                yield {"event": "done", "data": json.dumps({
                    "intent": ev["intent"],
                    "trace_id": ev["trace_id"],
                    "tokens_in": ev["tokens_in"],
                    "unverified_numbers": ev["unverified_numbers"],
                })}

    return EventSourceResponse(gen())
