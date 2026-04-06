import requests

url = 'https://pokeapi.co/api/v2/'

def get_pokemon(pokemon_name):
    url_pokemon = url + 'pokemon/' + pokemon_name
    response = requests.get(url_pokemon)

    if response.status_code == 200:
        data = response.json()
        types = [x['type']['name'] for x in data['types']]

        return{
            'id': data['id'],
            'name': data['name'],
            'base_experience': data['base_experience'],
            'types': types
        }

    else:
        return None