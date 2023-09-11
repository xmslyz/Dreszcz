import game_mechanics as mech


class Character:
    def __int__(self, name):
        self.name = name
        self.agility = 0
        self.stamina = 0

    def __str__(self):
        return (
            f"{self.name}\n"
            f"ZRĘCZNOŚĆ: {self.agility}\n"
            f"WYTRZYMAŁOŚĆ: {self.stamina}"
        )

    def attack_strenght(self):
        return self.agility + mech.roll_2d6()

    def take_damage(self, damage):
        self.stamina -= damage

    def is_alive(self):
        return self.stamina > 0
