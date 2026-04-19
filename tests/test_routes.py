from __future__ import annotations


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json["ok"] is True
    assert res.json["data"]["status"] == "ok"


def test_suggest_happy_path(client, monkeypatch):
    def fake_get_pokemon(identifier):
        return {"id": 25, "name": str(identifier), "types": ["electric"], "base_experience": 100, "abilities": ["static"]}

    def fake_suggest_member_team(team, target_size=4):
        return {"current_team": [{"name": "pikachu", "types": ["electric"], "ability": "static", "strengths": "...", "weaknesses": "..."}], "suggestions": []}

    monkeypatch.setattr("services.pokeapi.get_pokemon", fake_get_pokemon)
    monkeypatch.setattr("services.gemini.suggest_member_team", fake_suggest_member_team)

    res = client.post("/suggest", json={"team": ["pikachu"]})
    assert res.status_code == 200
    assert res.json["ok"] is True
    assert "current_team" in res.json["data"]


def test_analyze_happy_path(client, monkeypatch):
    def fake_get_pokemon(identifier):
        return {"id": 1, "name": str(identifier), "types": ["grass"], "base_experience": 100, "abilities": ["overgrow"]}

    def fake_analyze_team(team):
        return "Analise ok"

    monkeypatch.setattr("services.pokeapi.get_pokemon", fake_get_pokemon)
    monkeypatch.setattr("services.gemini.analyze_team", fake_analyze_team)

    res = client.post("/analyze", json={"team": ["bulbasaur"]})
    assert res.status_code == 200
    assert res.json["ok"] is True
    assert res.json["data"]["analysis"] == "Analise ok"

