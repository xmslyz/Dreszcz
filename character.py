import game_mechanics as mech


class Character:
    def __int__(self, name):
        self.name = name
        self.agility = 0
        self.stamina = 0
        self.luck = 0


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


class Hero(Character):
    def __init__(self, name):
        super().__init__(name)
        self.agility, self.stamina, self.luck = 0, 0, 0
        self.max_luck, self.max_stamina, self.max_agility = 0, 0, 0

        # self.max_luck_potion_usage = 2
        # self.max_agility_potion_usage = 2
        # self.max_stamina_potion_usage = 2
        # self.inventory = Inventory()

    def __str__(self):
        return (
            f"{self.name}:\n"
            f"ZRĘCZNOŚĆ: {self.agility}\n"
            f"WYTRZYMAŁOŚĆ: {self.stamina}\n"
            f"SZCZĘŚCIE: {self.luck}"
        )

    def set_max_attribute_levels(self):
        self.max_agility = mech.roll_d6() + 6
        self.max_stamina = mech.roll_2d6() + 12
        self.max_luck = mech.roll_d6() + 6

        self.agility = self.max_agility
        self.stamina = self.max_stamina
        self.luck = self.max_luck
