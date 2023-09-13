import json
import random

from colorama import Back, Style, Fore

import game_mechanics as mech


class Character:
    def __init__(self, name, agility, stamina):
        self.name = name
        self.agility = agility
        self.stamina = stamina
        self.luck = 0

    def __str__(self):
        return (
            f"{self.name}\n"
            f"ZRĘCZNOŚĆ: {self.agility}\n"
            f"WYTRZYMAŁOŚĆ: {self.stamina}"
        )

    def attack_strenght(self, dices_roll):
        attack = self.agility + dices_roll
        txt = f"{self.name}: {dices_roll} + Z:{self.agility} = {attack}"
        spacer = 40 - len(txt)
        print(Fore.RED + f"{txt}" f"{' ' * spacer}" + Style.RESET_ALL)
        return attack

    def take_damage(self, damage):
        self.stamina -= damage

    def is_dead(self):
        return self.stamina <= 0


class Hero(Character):
    def __init__(self, name):
        super().__init__(name, 0, 0)
        self.name = name
        self.agility, self.stamina, self.luck = 0, 0, 0
        self.max_luck, self.max_stamina, self.max_agility = 0, 0, 0
        self.kills = {}
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

    def clone_hero(self):
        ...

    def set_attribute_levels(self):
        self.max_agility = mech.roll_d6() + 6
        self.max_stamina = mech.roll_2d6() + 12
        self.max_luck = mech.roll_d6() + 6

        self.agility = self.max_agility
        self.stamina = self.max_stamina
        self.luck = self.max_luck

    def set_name(self):
        with open("hero_names.json") as hero:
            names = json.load(hero)

        self.name = random.choice(names)


class Monster(Character):
    def __init__(self, name, agility, stamina):
        super().__init__(name, agility, stamina)

    def __str__(self):
        return f"{self.name} Z:{self.agility}, W:{self.stamina}"
