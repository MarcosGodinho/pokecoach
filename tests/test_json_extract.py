from __future__ import annotations

import pytest

from utils.errors import APIError
from utils.json_extract import extract_json_object


def test_extract_json_object_direct():
    assert extract_json_object('{"a": 1}') == {"a": 1}


def test_extract_json_object_code_fence():
    assert extract_json_object("```json\n{\"a\": 1}\n```") == {"a": 1}


def test_extract_json_object_embedded():
    text = "Here you go:\n{\n  \"a\": 1\n}\nThanks"
    assert extract_json_object(text) == {"a": 1}


def test_extract_json_object_no_json():
    with pytest.raises(APIError) as exc:
        extract_json_object("nope")
    assert exc.value.code == "no_json_found"

