from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=openai_api_key)

def analyze_team(team):
    prompt = "Analyze this team of Pokémon and point out their weaknesses: \n" + "\n".join(f"{p.name} ({', '.join(p.types)})" for p in team.pokemons)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=1.0,
        max_tokens=100
    )

    return response.choices[0].message.content