from __future__ import annotations

import json
from typing import Any

from django.http import HttpRequest, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from models.team import Team
from services import gemini, pokeapi
from utils.errors import APIError
from utils.validation import parse_team_payload


def _build_team(team_identifiers: list[str], max_size: int = 6) -> Team:
    team = Team(max_length=max_size)
    for identifier in team_identifiers:
        pokemon_data = pokeapi.get_pokemon(identifier)
        team.add_from_api(pokemon_data)
    return team


def index(request: HttpRequest):
    return render(request, "ui/index.html", {})


@require_POST
@csrf_exempt
def api_suggest(request: HttpRequest):
    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else None
        team_identifiers = parse_team_payload(payload, max_size=6)
        team = _build_team(team_identifiers, max_size=6)
        data = gemini.suggest_member_team(team, target_size=4)
        return JsonResponse({"ok": True, "data": data})
    except APIError as e:
        body: dict[str, Any] = {"ok": False, "error": {"code": e.code, "message": e.message}}
        if e.details is not None:
            body["error"]["details"] = e.details
        return JsonResponse(body, status=e.status_code)


@require_POST
@csrf_exempt
def api_analyze(request: HttpRequest):
    try:
        payload = json.loads(request.body.decode("utf-8")) if request.body else None
        team_identifiers = parse_team_payload(payload, max_size=6)
        team = _build_team(team_identifiers, max_size=6)
        analysis = gemini.analyze_team(team)
        return JsonResponse({"ok": True, "data": {"analysis": analysis}})
    except APIError as e:
        body: dict[str, Any] = {"ok": False, "error": {"code": e.code, "message": e.message}}
        if e.details is not None:
            body["error"]["details"] = e.details
        return JsonResponse(body, status=e.status_code)
