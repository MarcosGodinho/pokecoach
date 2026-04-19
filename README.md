# PokeCoach

Small Flask API that:
1) Fetches Pokemon data from PokeAPI
2) Uses Gemini to analyze a team and suggest new members

## Setup

1. Create a `.env` (see `.env.example`) and set `GEMINI_API_KEY`.
2. Install dependencies (example):
   - `pip install -r requirements.txt`

## Run

- `python main.py`
- Server defaults to `http://127.0.0.1:5000`

## Django UI (demo page)

This repo also includes a minimal Django dark-mode page with a Pokemon picker (images) you can use to demo the project.

- Install deps: `pip install -r requirements.txt -r requirements-dev.txt`
- Run: `python manage.py runserver`
- Open: `http://127.0.0.1:8000/`

## Endpoints

- `GET /health`
- `GET /pokemon/<name_or_id>`
- `POST /analyze`
- `POST /suggest`

### Example request

`POST /suggest`

```json
{
  "team": ["pikachu", "charizard"]
}
```

PowerShell example:

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:5000/suggest `
  -ContentType application/json `
  -Body '{"team":["pikachu","charizard"]}'
```

## Notes

- Responses are wrapped as `{ "ok": true, "data": ... }` or `{ "ok": false, "error": ... }`.
- PokeAPI calls are cached in-memory for a few minutes to reduce repeated requests.
- Rate limiting is in-memory per IP (configurable via `RATE_LIMIT_PER_MINUTE`).
