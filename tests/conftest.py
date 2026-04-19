from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from main import create_app  # noqa: E402


@pytest.fixture()
def app():
    app = create_app()
    app.config.update({"TESTING": True, "RATE_LIMIT_PER_MINUTE": 10_000})
    return app


@pytest.fixture()
def client(app):
    return app.test_client()
