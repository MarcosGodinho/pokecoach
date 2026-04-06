MAX_LENGHT = 6

class Team:

    def __init__(self):
        self.pokemons = []

    def add_pokemon(self, pokemon):
        if len(self.pokemons) < MAX_LENGHT:
            self.pokemons.append(pokemon)
            return
        else:
            raise ValueError("Team already with 6 members.")


    def remove_pokemon(self, pokemon):
        if pokemon in self.pokemons:
            self.pokemons.remove(pokemon)
        else:
            raise ValueError("Pokemons not in the team.")

    def __len__(self):
        return len(self.pokemons)

    def __str__(self):
        return "\n".join(str(p) for p in self.pokemons)