import json

SYSTEM = """You are an SRE assistant explaining request latency and failures.
Rules: Answer in at most 6 sentences. Use ONLY numbers present in DATA and quote them exactly (ms, %).
Always name the responsible service and operation. If DATA does not contain enough to answer, say
"The data does not show that" - do not guess. No preamble."""

HINTS = {
    "SLOWEST":  "Name the slowest trace, its total_ms, and the span with the highest pct.",
    "WHY_SLOW": "Identify the span with the highest pct and explain it.",
    "WHY_FAIL": "State which service and operation failed and quote the error message.",
    "TREND":    "State the trend, the start and now values, and delta_pct.",
    "KNOWN":    "Summarise the most relevant runbook hit and its mitigation.",
}

USER = """QUESTION: {question}
HINT: {hint}
CONTEXT: {context_line}
DATA:
{data_json}"""


def build(question: str, intent: str, context_line: str, data: dict) -> list[dict]:
    hint = HINTS.get(intent, "")
    data_json = json.dumps(data, separators=(",", ":"), default=str)
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": USER.format(
            question=question,
            hint=hint,
            context_line=context_line,
            data_json=data_json,
        )},
    ]
