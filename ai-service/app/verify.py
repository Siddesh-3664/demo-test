import json
import re

_NUM_RE = re.compile(r"\b\d+(?:\.\d+)?\s?(?:ms|%)\b", re.IGNORECASE)


def unverified_numbers(answer: str, data: dict) -> list[str]:
    """Return numbers in the answer (with ms/%) that don't appear anywhere in data."""
    # Collect all numbers from data as strings
    data_str = json.dumps(data, default=str)
    data_numbers = set()
    for m in re.finditer(r"\d+(?:\.\d+)?", data_str):
        val = m.group()
        data_numbers.add(val)
        # Also add with .0 stripped
        if val.endswith(".0"):
            data_numbers.add(val[:-2])
        # And with .0 added
        if "." not in val:
            data_numbers.add(val + ".0")

    # Find numbers in answer
    answer_nums = _NUM_RE.findall(answer)
    result = []
    for num_str in answer_nums:
        # Extract the numeric part
        num_part = re.match(r"(\d+(?:\.\d+)?)", num_str)
        if num_part:
            n = num_part.group(1)
            if n not in data_numbers and n.rstrip("0").rstrip(".") not in data_numbers:
                result.append(num_str)
    return result
