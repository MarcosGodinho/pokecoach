from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Pokemon:
    id: int
    name: str
    types: list[str]
    base_experience: int | None = None
    abilities: list[str] | None = None

    @staticmethod
    def from_api(data: dict) -> "Pokemon":
        return Pokemon(
            id=int(data["id"]),
            name=str(data["name"]),
            types=list(data.get("types", [])),
            base_experience=data.get("base_experience"),
            abilities=data.get("abilities"),
        )

    def to_prompt_line(self) -> str:
        abilities = self.abilities or []
        ability_hint = f"; abilities: {', '.join(abilities)}" if abilities else ""
        return f"{self.name} ({', '.join(self.types)}){ability_hint}"
