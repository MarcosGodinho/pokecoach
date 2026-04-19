from __future__ import annotations

import pytest

from utils.errors import APIError
from utils.validation import parse_team_payload


def test_parse_team_payload_happy_path():
    assert parse_team_payload({"team": ["Pikachu", "Mr Mime"]}) == ["pikachu", "mr-mime"]


@pytest.mark.parametrize(
    "payload,code",
    [
        (None, "invalid_json"),
        ({}, "missing_team"),
        ({"team": "pikachu"}, "invalid_team"),
        ({"team": []}, "empty_team"),
        ({"team": ["pikachu", "pikachu"]}, "duplicate_team_member"),
    ],
)
def test_parse_team_payload_errors(payload, code):
    with pytest.raises(APIError) as exc:
        parse_team_payload(payload)
    assert exc.value.code == code

