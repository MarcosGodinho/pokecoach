from __future__ import annotations

from dataclasses import dataclass, field

from models.pokemon import Pokemon


@dataclass(slots=True)
class Team:
    max_length: int = 6
    pokemons: list[Pokemon] = field(default_factory=list)

    def add_pokemon(self, pokemon: Pokemon) -> None:
        if len(self.pokemons) >= self.max_length:
            raise ValueError(f"Team already with {self.max_length} members.")
        self.pokemons.append(pokemon)

    def add_from_api(self, pokemon_data: dict) -> None:
        self.add_pokemon(Pokemon.from_api(pokemon_data))

    def remove_pokemon(self, pokemon: Pokemon) -> None:
        if pokemon not in self.pokemons:
            raise ValueError("Pokemon not in the team.")
        self.pokemons.remove(pokemon)

    def __len__(self) -> int:
        return len(self.pokemons)

    def to_prompt_lines(self) -> list[str]:
        return [p.to_prompt_line() for p in self.pokemons]

    def __str__(self) -> str:
        return "\n".join(self.to_prompt_lines())
