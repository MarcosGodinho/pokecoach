from __future__ import annotations

import json
from typing import Any

from utils.errors import APIError


def extract_json_object(text: str) -> dict[str, Any]:
    """
    Best-effort extraction of a JSON object from model output.
    Accepts raw JSON, code-fenced JSON, or text with a JSON object embedded.
    """
    cleaned = text.strip()
    if not cleaned:
        raise APIError("empty_model_output", "Model returned empty output", status_code=502)

    # Remove common fenced markers while keeping content.
    cleaned = cleaned.replace("```json", "").replace("```JSON", "").replace("```", "").strip()

    # Fast path: direct parse.
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    # Heuristic: find the first balanced JSON object.
    start = cleaned.find("{")
    if start == -1:
        raise APIError("no_json_found", "No JSON object found in model output", status_code=502)

    depth = 0
    end = -1
    for i in range(start, len(cleaned)):
        ch = cleaned[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break

    if end == -1:
        raise APIError("bad_json", "Unterminated JSON object in model output", status_code=502)

    snippet = cleaned[start:end]
    try:
        parsed = json.loads(snippet)
    except json.JSONDecodeError as exc:
        raise APIError("bad_json", "Failed to parse JSON object in model output", status_code=502) from exc

    if not isinstance(parsed, dict):
        raise APIError("bad_json", "Expected a JSON object", status_code=502)
    return parsed

