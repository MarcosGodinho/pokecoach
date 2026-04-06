from services import pokeapi
from models.pokemon import Pokemon
from models.team import Team

team_obj = Team()
while len(team_obj) < 6:
    poke_name = input("Write the pokemon name: ")

    poke_json = pokeapi.get_pokemon(poke_name)

    if poke_json is None:
        print("Error fetching result")
    else:
        try:
            team_obj.add_pokemon(Pokemon(poke_json))

        except ValueError as e:
            print(e)


print(team_obj)