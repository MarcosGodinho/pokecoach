from models.team import Team
from services import gemini, pokeapi
from utils.errors import APIError


team_obj = Team()
while len(team_obj) < 3:
    poke_name = input("Write the pokemon name: ").strip()
    if not poke_name:
        continue

    try:
        poke_json = pokeapi.get_pokemon(poke_name)
        team_obj.add_from_api(poke_json)
    except APIError as e:
        print(f"API error: {e.code} - {e.message}")
    except ValueError as e:
        print(e)

print(gemini.analyze_team(team_obj))
print(gemini.suggest_member_team(team_obj))
