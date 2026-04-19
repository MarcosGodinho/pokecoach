from __future__ import annotations

import time
from dataclasses import dataclass

from utils.errors import APIError


@dataclass(slots=True)
class _Window:
    start: float
    count: int


class InMemoryRateLimiter:
    """
    Simple fixed-window limiter: N requests per minute per key (e.g. IP).
    Good enough to prevent accidental cost spikes in local/prototype deployments.
    """

    def __init__(self, limit_per_minute: int = 60):
        self._limit = int(limit_per_minute)
        self._windows: dict[str, _Window] = {}

    def check(self, key: str) -> None:
        now = time.time()
        window = self._windows.get(key)
        if window is None or (now - window.start) >= 60:
            self._windows[key] = _Window(start=now, count=1)
            return

        if window.count >= self._limit:
            raise APIError("rate_limited", "Too many requests", status_code=429, details={"limit_per_minute": self._limit})

        window.count += 1

