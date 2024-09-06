import json
import random

from colorama import Fore, Style, Back

import game_mechanics as mech
from inventory import Inventory


class Character(object):
    def __init__(self):
        self.name = None
        self.agility = 0
        self.stamina = 0
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
        print(f"{txt}" f"{' ' * spacer}")
        return attack

    def take_damage(self, damage):
        self.stamina -= damage

    def is_dead(self):
        return self.stamina <= 0


class Hero(Character):
    def __init__(self):
        super().__init__()
        self.name = None
        self.agility, self.stamina, self.luck = 0, 0, 0
        self.max_luck, self.max_stamina, self.max_agility = 0, 0, 0
        self.kills = {}
        # self.max_luck_potion_usage = 2
        # self.max_agility_potion_usage = 2
        # self.max_stamina_potion_usage = 2
        self.inventory = Inventory()

    def __str__(self):
        return (
            f"{self.name}:\n"
            f"ZRĘCZNOŚĆ     [max. {self.max_agility}] : {self.agility}\n"
            f"WYTRZYMAŁOŚĆ  [max. {self.max_stamina}] : {self.stamina}\n"
            f"SZCZĘŚCIE     [max. {self.max_luck}]  : {self.luck} "
        )

    def set_name(self):
        with open("hero_names.json") as f:
            names = json.load(f)
        self.name = random.choice(names["hero"])

    def clone_hero(self):
        ...

    def set_attribute_levels(self):
        print(Fore.RED + " *** Tworzenie postaci bohatera *** " +
              Style.RESET_ALL)

        input(Fore.YELLOW + "Wylosuj imię " +
              Back.CYAN + Fore.BLACK + "[ ENTER ]" +
              Style.RESET_ALL + "\n")
        self.set_name()

        input(Fore.YELLOW + "Rzuć 1k6 dla określenia [Z]ręczności " +
              Back.CYAN + Fore.BLACK + "[ ENTER ]" +
              Style.RESET_ALL + "")
        self.max_agility = mech.roll_d6() + 6
        print("Twoja ZRĘCZNOŚĆ [Z] wynosi", self.max_agility, sep=":")

        input(Fore.YELLOW + "Rzuć 2k6 dla określenia [W]ytrzymałości " +
              Back.CYAN + Fore.BLACK + "[ ENTER ]" +
              Style.RESET_ALL + "")
        self.max_stamina = mech.roll_2d6() + 12
        print("Twoja WYTRZYMAŁOŚĆ [W] wynosi", self.max_stamina, sep=":")

        input(Fore.YELLOW + "Rzuć kostką 1k6 dla określenia [S]zczęścia " +
              Back.CYAN + Fore.BLACK + "[ ENTER ]" +
              Style.RESET_ALL + "")
        self.max_luck = mech.roll_d6() + 6
        print("Twoje SZCZĘŚCIE [S] wynosi", self.max_luck, sep=":")

        self.agility = self.max_agility
        self.stamina = self.max_stamina
        self.luck = self.max_luck

    def choose_potion(self):
        while True:
            querry = input(
                Fore.GREEN + "Jaki eliksir wybierasz:\n" +
                Fore.MAGENTA + "[1] " + Fore.GREEN + "Zręczności\n" +
                Fore.MAGENTA + "[2] " + Fore.GREEN + "Wytrzymałości\n" +
                Fore.MAGENTA + "[3] " + Fore.GREEN + "Szczęścia\n" +
                Fore.MAGENTA + ">>> "
            )
            if querry == "1":
                self.inventory.agility_potion = 2
                break
            elif querry == "2":
                self.inventory.stamina_potion = 2
                break
            elif querry == "3":
                self.inventory.luck_potion = 2
                break
            else:
                print(f"Nieprawidłowy znak")
            # inventory.potion.update({"luck": 1})

    def change_atribute_level(self, attribute: str,
                              in_plus: bool, value: int):
        """

        Args:
            attribute: "stamina", "agility", "luck
            in_plus: value * -1 if False
            value: value

        Returns:

        """

        if not in_plus:
            value = value * -1

        attr = getattr(self, attribute)
        max_attr = getattr(self, f"max_{attribute}")
        for i in range(abs(value)):
            # Check if the attribute is within the allowed range
            if in_plus:
                if attr < max_attr:
                    attr += 1
                    setattr(self, attribute, attr)
                else:
                    print("Osiągnięto maksymalny poziom atrybutu")
                    break
            else:
                if attr > 0:
                    attr -= 1
                    setattr(self, attribute, attr)
                else:
                    break

    def change_atribute_level_(self, attribute: str, new_value: int):
        """

        Args:
            attribute: "stamina", "agility", "luck
            new_value: int

        """

        max_attr = getattr(self, f"max_{attribute}")
        if new_value <= max_attr:
            setattr(self, attribute, new_value)
        else:
            print("Osiągnięto maksymalny poziom atrybutu")


class Monster(Character):
    def __init__(self, name, agility, stamina):
        super().__init__()
        self.name = name
        self.agility = agility
        self.stamina = stamina

    def __str__(self):
        return f"{self.name} Z:{self.agility}, W:{self.stamina}"
