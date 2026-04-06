class Pokemon:
    def __init__(self, data):
        self.ID = data['id']
        self.name = data['name']
        self.types = data['types']
        self.base_experience = data['base_experience']

    # def __init__(self, dict_pokemon):
    #     for k, v in dict_pokemon.items():
    #         setattr(self, k, v)

    def __str__(self):
        return f"ID: {self.ID}, Name: {self.name}, Types: {self.types}, Base Experience: {self.base_experience}"