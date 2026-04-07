import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=gemini_api_key)

def analyze_team(team):
    prompt = "Analyze this team of Pokémon and point out their weaknesses in Portuguese: \n" + "\n".join(f"{p.name} ({', '.join(p.types)})" for p in team.pokemons)

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )

    return response.text

def suggest_member_team(team):
    prompt = (
                 "Analyze this Pokémon team and suggest new members to complete a 4-Pokémon team. "
                 "Do not remove current members or repeat Pokémon. "
                 "Your output MUST be formatted for a terminal display using ASCII art elements (borders, boxes, and tables). "
                 "Do not use Markdown (no asterisks, no hashes). Use plain text and characters like '=', '|', '-', and '+'. "
                 "\nStructure the response exactly like this:\n"
                 "1. A header box with the title 'TIME ATUAL'.\n"
                 "2. A plain text table for current Pokémon (Name | Types | Ability).\n"
                 "3. A section for 'ANALISE' using '+' for strengths and '-' for weaknesses.\n"
                 "4. A 'RECOMENDACAO' box containing the suggested Pokémon's details and a brief 'Why' section.\n"
                 "Use simple Unicode symbols like 🛡️ for defense and ⚔️ for attack and others that you think are appropriate.\n"
                 "\nAll text must be in Portuguese. Current team: \n"
             ) + "\n".join(f"{p.name} ({', '.join(p.types)})" for p in team.pokemons)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )

    return response.text