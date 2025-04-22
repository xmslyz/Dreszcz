import json
import random

from colorama import Fore, Style, Back

import roll
from inventory import Inventory


class Character(object):
    def __init__(self):
        self.name = None
        self.agility = 0
        self.stamina = 0
        self.luck = 0

    def __str__(self) -> str:
        """Textual representation for CLI (print)."""
        return (
            f"{self.name}\n"
            f"ZRĘCZNOŚĆ: {self.agility}\n"
            f"WYTRZYMAŁOŚĆ: {self.stamina}"
        )

    def describe(self) -> dict:
        """
        Structured representation for GUI or serialization.

        Returns:
            dict: Dictionary with character's core stats.
        """
        return {
            "name": self.name,
            "agility": self.agility,
            "stamina": self.stamina,
            "luck": self.luck
        }

    def attack_strength(self, dice_roll: int) -> tuple[int, str]:
        """
        Calculates attack strength based on dice roll and agility.

        Args:
            dice_roll (int): The result of the dice roll.

        Returns:
            tuple[int, str]: (attack value, formatted description)
        """
        attack = self.agility + dice_roll
        txt = f"{self.name}: {dice_roll} + Z:{self.agility} = {attack}"
        return attack, txt.ljust(40)

    def take_damage(self, damage: int) -> None:
        """
        Applies damage to character. Stamina cannot drop below 0.

        Args:
            damage (int): Amount of damage taken.
        """
        self.stamina = max(self.stamina - damage, 0)

    def is_dead(self) -> bool:
        """
        Checks if character is dead.

        Returns:
            bool: True if stamina is 0 or less.
        """
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

    def describe(self) -> dict:
        """
        Returns structured data describing the hero's current state.
        Useful for GUI rendering or logging.

        Returns:
            dict: Dictionary of current and max attributes.
        """
        return {
            "name": self.name,
            "agility": self.agility,
            "max_agility": self.max_agility,
            "stamina": self.stamina,
            "max_stamina": self.max_stamina,
            "luck": self.luck,
            "max_luck": self.max_luck,
            "kills": self.kills.copy()
            # "inventory": self.inventory.describe()  # zakładam, że Inventory to obsługuje
        }

    def set_name(self) -> str:
        """
        Randomly selects a name for the hero from a JSON file
        and assigns it to the hero. Also returns the selected name.

        Returns:
            str: The selected hero name.
        """
        with open("hero_names.json", encoding="utf-8") as f:
            names = json.load(f)
        self.name = random.choice(names["hero"])
        return self.name

    def clone_hero(self):
        ...

    def roll_single_attribute(self, attr: str) -> int:
        """
        Rolls a single attribute based on its type.

        Args:
            attr (str): One of "agility", "stamina", "luck".

        Returns:
            int: Rolled value.
        """
        if attr == "agility" or attr == "luck":
            return roll.roll_d6_cli() + 6
        elif attr == "stamina":
            return roll.roll_2d6_cli() + 12
        else:
            raise ValueError("Nieznany atrybut.")

    def interactive_character_creation(self) -> None:
        """
        CLI-based character creation with atmospheric pauses and prompts.
        Used only in terminal mode to build narrative tension during stat rolls.

        This method is intended for command-line interaction and will be
        replaced by a GUI dialog in future versions.

        For GUI implementation:
        - Replace input() with button clicks or stepper controls.
        - Use `roll_single_attribute(attr)` to generate values on demand.
        - Show rolled values in UI and allow confirmation or rerolling.
        """
        # TODO: Replace this method with GUI-driven attribute selection in future

        print(Fore.RED + " *** Tworzenie postaci bohatera *** " + Style.RESET_ALL)

        input(Fore.YELLOW + "Wylosuj imię " +
              Back.CYAN + Fore.BLACK + "[ ENTER ]" + Style.RESET_ALL + "\n")
        self.set_name()

        input(Fore.YELLOW + "Rzuć 1k6 dla określenia [Z]ręczności " +
              Back.CYAN + Fore.BLACK + "[ ENTER ]" + Style.RESET_ALL)
        self.max_agility = self.roll_single_attribute("agility")
        print("Twoja ZRĘCZNOŚĆ [Z] wynosi:", self.max_agility)

        input(Fore.YELLOW + "Rzuć 2k6 dla określenia [W]ytrzymałości " +
              Back.CYAN + Fore.BLACK + "[ ENTER ]" + Style.RESET_ALL)
        self.max_stamina = self.roll_single_attribute("stamina")
        print("Twoja WYTRZYMAŁOŚĆ [W] wynosi:", self.max_stamina)

        input(Fore.YELLOW + "Rzuć kostką 1k6 dla określenia [S]zczęścia " +
              Back.CYAN + Fore.BLACK + "[ ENTER ]" + Style.RESET_ALL)
        self.max_luck = self.roll_single_attribute("luck")
        print("Twoje SZCZĘŚCIE [S] wynosi:", self.max_luck)

        self.agility = self.max_agility
        self.stamina = self.max_stamina
        self.luck = self.max_luck

    def choose_potion(self, choice: int) -> str:
        """
        Selects a potion type based on user's choice.

        Args:
            choice (int): 1 for agility, 2 for stamina, 3 for luck.

        Returns:
            str: The name of the selected potion.

        Raises:
            ValueError: If an invalid choice is given.

        GUI note:
            This method is intended to be called after the user selects
            a potion via a button, dropdown, or other interface component.
        """
        if choice == 1:
            self.inventory.agility_potion = 2
            return "Zręczność"
        elif choice == 2:
            self.inventory.stamina_potion = 2
            return "Wytrzymałość"
        elif choice == 3:
            self.inventory.luck_potion = 2
            return "Szczęście"
        else:
            raise ValueError("Nieprawidłowy wybór mikstury.")

    def choose_potion_cli(self) -> None:
        """
        CLI interaction for choosing a potion with user input.
        Intended only for terminal version. Use `choose_potion()` in GUI.
        """

        # TODO: Rozważyć trzymanie mikstur jako słownik (np. {"luck": 2}) przy rozbudowie systemu mikstur (np. eliksir siły, eliksir mocy, eliksir krwi)

        while True:
            choice = input(
                Fore.GREEN + "Jaki eliksir wybierasz:\n" +
                Fore.MAGENTA + "[1] " + Fore.GREEN + "Zręczności\n" +
                Fore.MAGENTA + "[2] " + Fore.GREEN + "Wytrzymałości\n" +
                Fore.MAGENTA + "[3] " + Fore.GREEN + "Szczęścia\n" +
                Fore.MAGENTA + ">>> " + Style.RESET_ALL
            )
            if choice in ("1", "2", "3"):
                selected = self.choose_potion(int(choice))
                print(Fore.YELLOW + f"Wybrałeś miksturę: {selected}" + Style.RESET_ALL)
                break
            else:
                print("Nieprawidłowy wybór. Spróbuj ponownie.")

    def change_attribute_level(self, attribute: str, in_plus: bool, value: int) -> str | None:
        """
        Changes a hero attribute (agility, stamina, or luck) up or down
        by the specified value, respecting upper and lower bounds.

        Args:
            attribute (str): One of "agility", "stamina", or "luck".
            in_plus (bool): True to increase, False to decrease.
            value (int): Amount to adjust.

        Returns:
            str | None: Message if capped/floored, or None if change succeeded silently.

        TODO:
            In GUI, use the returned string as a user-visible status message.
        """
        if attribute not in ("agility", "stamina", "luck"):
            raise ValueError(f"Nieznany atrybut: {attribute}")

        current = getattr(self, attribute)
        max_attr = getattr(self, f"max_{attribute}")

        if in_plus:
            new_value = current + value
            if new_value > max_attr:
                setattr(self, attribute, max_attr)
                return f"{attribute.upper()} osiągnęło maksimum ({max_attr})."
            setattr(self, attribute, new_value)
        else:
            new_value = current - value
            if new_value < 0:
                setattr(self, attribute, 0)
                return f"{attribute.upper()} nie może spaść poniżej 0."
            setattr(self, attribute, new_value)

        return None


class Monster(Character):
    def __init__(self, name, agility, stamina):
        """
            Creates a Monster with given stats.

            Args:
                name (str): Monster name.
                agility (int): Agility value.
                stamina (int): Stamina (health) value.
            """
        super().__init__()
        self.name = name
        self.agility = agility
        self.stamina = stamina

    def __str__(self):
        return f"{self.name} Z:{self.agility}, W:{self.stamina}"

    def describe(self) -> dict:
        """
        Returns structured data for the monster.

        Returns:
            dict: Dictionary with monster's stats.
        """
        return {
            "name": self.name,
            "agility": self.agility,
            "stamina": self.stamina
        }
