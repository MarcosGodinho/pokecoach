from __future__ import annotations

import threading
import time
from dataclasses import dataclass

import requests

from utils.errors import APIError


def normalize_identifier(identifier: str | int) -> str:
    s = str(identifier).strip().lower()
    # Common normalization for names like "Mr Mime" -> "mr-mime".
    s = s.replace(" ", "-")
    return s


@dataclass(slots=True)
class _CacheEntry:
    value: dict
    expires_at: float


class PokeAPIClient:
    def __init__(self, base_url: str = "https://pokeapi.co/api/v2/", timeout_s: float = 10.0, cache_ttl_s: float = 300.0):
        self._base_url = base_url.rstrip("/") + "/"
        self._timeout_s = timeout_s
        self._cache_ttl_s = cache_ttl_s
        self._session = requests.Session()
        self._cache: dict[str, _CacheEntry] = {}
        self._lock = threading.Lock()

    def get_pokemon(self, identifier: str | int) -> dict:
        normalized = normalize_identifier(identifier)

        now = time.time()
        with self._lock:
            entry = self._cache.get(normalized)
            if entry and entry.expires_at > now:
                return entry.value

        url = f"{self._base_url}pokemon/{normalized}"
        try:
            response = self._session.get(url, timeout=self._timeout_s)
        except requests.exceptions.RequestException as exc:
            raise APIError("pokeapi_unavailable", "Failed to reach PokeAPI", status_code=502, details={"identifier": normalized}) from exc

        if response.status_code == 404:
            raise APIError("pokemon_not_found", "Pokemon not found", status_code=404, details={"identifier": normalized})
        if response.status_code != 200:
            raise APIError(
                "pokeapi_error",
                "Unexpected PokeAPI response",
                status_code=502,
                details={"identifier": normalized, "status_code": response.status_code},
            )

        data = response.json()
        types = [x["type"]["name"] for x in data.get("types", [])]
        abilities = [x["ability"]["name"] for x in data.get("abilities", [])]

        normalized_data = {
            "id": data.get("id"),
            "name": data.get("name"),
            "base_experience": data.get("base_experience"),
            "types": types,
            "abilities": abilities,
        }

        with self._lock:
            self._cache[normalized] = _CacheEntry(value=normalized_data, expires_at=now + self._cache_ttl_s)

        return normalized_data


_default_client = PokeAPIClient()


def get_pokemon(identifier: str | int) -> dict:
    return _default_client.get_pokemon(identifier)
