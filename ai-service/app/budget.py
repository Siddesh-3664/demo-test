import json
import math
import copy

LIMIT = 1800


def estimate_tokens(obj) -> int:
    return math.ceil(len(json.dumps(obj, separators=(",", ":"), default=str)) / 3.5)


def _drop_runbooks(data: dict) -> dict:
    if "runbooks" in data:
        del data["runbooks"]
    return data


def _drop_logs_samples(data: dict) -> dict:
    if "logs" in data and "samples" in data["logs"]:
        del data["logs"]["samples"]
    return data


def _drop_trace_top_spans_tail(data: dict) -> dict:
    if "trace" in data and "top_spans" in data["trace"]:
        spans = data["trace"]["top_spans"]
        if len(spans) > 3:
            data["trace"]["top_spans"] = spans[:3]
    return data


def _drop_metrics_samples(data: dict) -> dict:
    if "metrics" in data and "samples" in data["metrics"]:
        del data["metrics"]["samples"]
    if "p95" in data and "samples" in data["p95"]:
        del data["p95"]["samples"]
    if "errors" in data and "samples" in data["errors"]:
        del data["errors"]["samples"]
    return data


_DROP_ORDER = [
    _drop_runbooks,
    _drop_logs_samples,
    _drop_trace_top_spans_tail,
    _drop_metrics_samples,
]


def trim(data: dict, limit: int = LIMIT) -> dict:
    """Apply Contracts §7.2 drop order until estimate_tokens(data) <= limit. Mutates a copy."""
    result = copy.deepcopy(data)
    if estimate_tokens(result) <= limit:
        return result
    for fn in _DROP_ORDER:
        result = fn(result)
        if estimate_tokens(result) <= limit:
            return result
    return result
