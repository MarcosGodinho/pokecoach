from __future__ import annotations

import logging
import os
import time
import uuid
from typing import Any

from flask import Flask, jsonify, g, request

from models.team import Team
from services import gemini, pokeapi
from utils.errors import APIError
from utils.rate_limit import InMemoryRateLimiter
from utils.responses import ok, fail
from utils.validation import parse_team_payload


def create_app() -> Flask:
    app = Flask(__name__)

    # Config via env vars for local/prod parity.
    app.config["MAX_TEAM_SIZE"] = int(os.getenv("MAX_TEAM_SIZE", "6"))
    app.config["TARGET_TEAM_SIZE"] = int(os.getenv("TARGET_TEAM_SIZE", "4"))
    app.config["RATE_LIMIT_PER_MINUTE"] = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    limiter = InMemoryRateLimiter(limit_per_minute=app.config["RATE_LIMIT_PER_MINUTE"])

    @app.before_request
    def _before_request() -> None:
        g.request_id = uuid.uuid4().hex
        g.start_time = time.time()
        limiter.check(request.remote_addr or "unknown")

    @app.after_request
    def _after_request(response):  # type: ignore[no-untyped-def]
        response.headers["X-Request-Id"] = getattr(g, "request_id", "")
        try:
            elapsed_ms = int((time.time() - getattr(g, "start_time", time.time())) * 1000)
            logging.info(
                "request_id=%s method=%s path=%s status=%s elapsed_ms=%s",
                getattr(g, "request_id", ""),
                request.method,
                request.path,
                response.status_code,
                elapsed_ms,
            )
        except Exception:
            # Never fail the request due to logging.
            pass
        return response

    @app.errorhandler(APIError)
    def _handle_api_error(err: APIError):  # type: ignore[no-untyped-def]
        payload, status = fail(err.code, err.message, status=err.status_code, details=err.details)
        return jsonify(payload), status

    @app.errorhandler(Exception)
    def _handle_unexpected_error(err: Exception):  # type: ignore[no-untyped-def]
        logging.exception("Unhandled error request_id=%s", getattr(g, "request_id", ""))
        payload, status = fail("internal_error", "Unexpected server error", status=500)
        return jsonify(payload), status

    @app.errorhandler(404)
    def _handle_404(_err):  # type: ignore[no-untyped-def]
        payload, status = fail("not_found", "Route not found", status=404)
        return jsonify(payload), status

    @app.errorhandler(405)
    def _handle_405(_err):  # type: ignore[no-untyped-def]
        payload, status = fail("method_not_allowed", "Method not allowed", status=405)
        return jsonify(payload), status

    def build_team(team_identifiers: list[str]) -> Team:
        team = Team(max_length=app.config["MAX_TEAM_SIZE"])
        for identifier in team_identifiers:
            pokemon_data = pokeapi.get_pokemon(identifier)
            team.add_from_api(pokemon_data)
        return team

    @app.get("/health")
    def health():  # type: ignore[no-untyped-def]
        return jsonify(ok({"status": "ok"}))

    @app.get("/pokemon/<identifier>")
    def get_pokemon(identifier: str):  # type: ignore[no-untyped-def]
        pokemon_data = pokeapi.get_pokemon(identifier)
        return jsonify(ok(pokemon_data))

    @app.post("/analyze")
    def analyze_team():  # type: ignore[no-untyped-def]
        team_identifiers = parse_team_payload(request.get_json(silent=True), max_size=app.config["MAX_TEAM_SIZE"])
        team = build_team(team_identifiers)
        analysis_text = gemini.analyze_team(team)
        return jsonify(ok({"analysis": analysis_text}))

    @app.post("/suggest")
    def suggest_pokemon():  # type: ignore[no-untyped-def]
        team_identifiers = parse_team_payload(request.get_json(silent=True), max_size=app.config["MAX_TEAM_SIZE"])
        team = build_team(team_identifiers)
        suggestions = gemini.suggest_member_team(team, target_size=app.config["TARGET_TEAM_SIZE"])
        return jsonify(ok(suggestions))

    return app


app = create_app()


if __name__ == "__main__":
    # Don't force debug=True; prefer FLASK_DEBUG=1 or env-based config in prod.
    debug = os.getenv("FLASK_DEBUG", "").strip().lower() in {"1", "true", "yes", "y", "on"}
    app.run(host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")), debug=debug)
