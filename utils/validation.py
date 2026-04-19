from __future__ import annotations

from utils.errors import APIError


def normalize_pokemon_identifier(value: str) -> str:
    s = value.strip().lower()
    s = s.replace(" ", "-")
    return s


def parse_team_payload(payload: dict | None, max_size: int = 6) -> list[str]:
    if not isinstance(payload, dict):
        raise APIError("invalid_json", "Request body must be a JSON object", status_code=400)

    team = payload.get("team")
    if team is None:
        raise APIError("missing_team", "Field 'team' is required", status_code=400)
    if not isinstance(team, list):
        raise APIError("invalid_team", "Field 'team' must be a list", status_code=400)
    if len(team) == 0:
        raise APIError("empty_team", "Team is required", status_code=400)
    if len(team) > max_size:
        raise APIError("team_too_large", f"Team must have at most {max_size} members", status_code=400)

    normalized: list[str] = []
    for idx, item in enumerate(team):
        if not isinstance(item, (str, int)):
            raise APIError("invalid_team_member", "Team entries must be strings or integers", status_code=400, details={"index": idx})
        s = normalize_pokemon_identifier(str(item))
        if not s:
            raise APIError("invalid_team_member", "Team entries cannot be empty", status_code=400, details={"index": idx})
        normalized.append(s)

    # Prevent duplicates (case/spacing normalization already applied).
    if len(set(normalized)) != len(normalized):
        raise APIError("duplicate_team_member", "Team entries must be unique", status_code=400)

    return normalized

