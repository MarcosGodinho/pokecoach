from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class APIError(Exception):
    code: str
    message: str
    status_code: int = 400
    details: Any | None = None

