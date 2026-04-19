from __future__ import annotations

import os
from typing import Any

from dotenv import load_dotenv
from google import genai

from models.team import Team
from utils.errors import APIError
from utils.json_extract import extract_json_object


def _get_env(name: str) -> str | None:
    value = os.getenv(name)
    return value.strip() if value else None


_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is not None:
        return _client

    # Load from .env for local dev; in production you'd typically set env vars directly.
    load_dotenv()
    api_key = _get_env("GEMINI_API_KEY")
    if not api_key:
        raise APIError("missing_gemini_api_key", "GEMINI_API_KEY is not configured", status_code=500)

    _client = genai.Client(api_key=api_key)
    return _client


def _model_name() -> str:
    return _get_env("GEMINI_MODEL") or "gemini-2.5-flash"


def analyze_team(team: Team) -> str:
    prompt = (
        "Analyze this Pokemon team and point out their weaknesses in Portuguese.\n"
        "Be concise and practical.\n\n"
        "Team:\n"
        + "\n".join(team.to_prompt_lines())
    )
    try:
        response = _get_client().models.generate_content(model=_model_name(), contents=prompt)
    except Exception as exc:
        raise APIError("gemini_error", "Failed to generate analysis", status_code=502) from exc
    return response.text or ""


def suggest_member_team(team: Team, target_size: int = 4) -> dict[str, Any]:
    prompt = (
        "You are an assistant that suggests Pokemon to complete a team.\n"
        "Rules:\n"
        f"- Target team size is {target_size}.\n"
        "- Do not remove current members.\n"
        "- Do not repeat any Pokemon already in the current team.\n"
        "- All text must be in Portuguese.\n"
        "- Output MUST be valid JSON only (no Markdown, no code fences).\n\n"
        "Return JSON with exactly this schema:\n"
        "{\n"
        '  \"current_team\": [\n'
        '    {\"name\": \"...\", \"types\": [\"...\"], \"ability\": \"...\", \"strengths\": \"...\", \"weaknesses\": \"...\"}\n'
        "  ],\n"
        '  \"suggestions\": [\n'
        '    {\"name\": \"...\", \"types\": [\"...\"], \"ability\": \"...\", \"strengths\": \"...\", \"weaknesses\": \"...\", \"why\": \"...\"}\n'
        "  ]\n"
        "}\n\n"
        "Current team:\n"
        + "\n".join(team.to_prompt_lines())
    )

    try:
        response = _get_client().models.generate_content(model=_model_name(), contents=prompt)
    except Exception as exc:
        raise APIError("gemini_error", "Failed to generate suggestions", status_code=502) from exc

    text = (response.text or "").strip()
    try:
        return extract_json_object(text)
    except APIError:
        raise
    except Exception as exc:
        raise APIError("gemini_bad_json", "Gemini response was not valid JSON", status_code=502, details={"raw_text": text}) from exc

