import json
import os
import pathlib
from typing import Callable
import sys

from colorama import Fore, Style, init
import game_mechanics
import character
import menu
from paragraph import Paragraph

init(autoreset=True)


class Shiver:
    def __init__(self):
        self.book_raw: dict[str, dict] = {}
        self.book_chapters: dict[str, Paragraph] = {}
        self.dev_mode: bool = False
        self.test = False
        self.last_valid_chapter: str = "1"
        self.book_chapters: dict[str, Paragraph] = {}
        self.visited_chapters: dict = {}
        self.hero = None
        self.bout = 0
        self.monsters_killed_counter = 0
        self.killed_monsters_dict = {}

        self.COMMANDS: dict[str, Callable[[], bool]] = {
            "0": self.quit_game,
            "q": self.quit_game,
            "s": lambda: self.save_game(quicksave=True) or False,
            "h": lambda: print(self.hero) or False,
            "f": lambda: game_mechanics.combat_cli(self) or False,
            "v": lambda: print(sorted([int(x) for x in self.visited_chapters.keys()])) or False,
            "e": self._eat_provision,
            "i": lambda: print(self.hero.inventory) or False,
            "?": self._show_command_list,
            "help": self._show_command_list,
            "dev": lambda: self._toggle_dev_mode()
        }

        self.DEV_COMMANDS: dict[str, Callable[[], bool]] = {
            "t": self._toggle_test_mode,
            "k": lambda: game_mechanics.combat_cli(self, True) or False,
            "killself": self._hero_suicide,
            "sal": lambda: self.hero.change_attribute_level("stamina", 10) or False,
        }

    def _toggle_dev_mode(self) -> bool:
        self.dev_mode = not self.dev_mode
        print(Fore.MAGENTA + f"Tryb deweloperski: {self.dev_mode}")
        return False

    def _next_input_or_prompt(self, prompt: str) -> str:
        if hasattr(self, "_menu_sequence") and self._menu_sequence:
            return self._menu_sequence.pop(0)

        return input(prompt)

    def start_game(self):
        # Wczytanie i przygotowanie danych książki
        path = pathlib.Path.cwd() / "shiver.json"
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)

        self.book_raw = raw
        self.book_chapters = {k: Paragraph(k, v) for k, v in raw.items()}

        # Otwarcie pierwszego rozdziału
        self.open_chapter(self.last_valid_chapter)

        # Uruchomienie głównego menu gry
        self.main_menu(self.last_valid_chapter)
        # try:
        #     # open last saved or first
        #     while True:
        #         start_game = self._next_input_or_prompt(
        #             Fore.MAGENTA + "[1] " + Fore.GREEN + "Nowa gra\n" +
        #             Fore.MAGENTA + "[2] " + Fore.GREEN + "Wczytaj ostatni "
        #                                                  "zapis\n" +
        #             Fore.MAGENTA + "[3] " + Fore.GREEN + "Usuń zapis\n" + "\n" +
        #             Fore.MAGENTA + "[0] " + Fore.GREEN + "Zakończ [w dowolnym "
        #                                                  "momencie gry]\n" +
        #             Fore.MAGENTA + ">>> " + Style.RESET_ALL
        #         )
        #
        #         if start_game == "1":
        #             self.create_new_hero()
        #             self.save_game()
        #             self.open_chapter("1")
        #             break
        #         elif start_game == "2":
        #             self.load_last_saved_game()
        #             self.open_chapter(self.last_valid_chapter)
        #             break
        #         elif start_game == "3":
        #             self.delete_game()
        #         elif start_game == "0":
        #             self.quit_game()
        #         else:
        #             print("Spróbuj jeszcze raz.")
        #     self.main_menu()
        # except FileNotFoundError:
        #     print("Nie znaleziono pliku gry.")

    def create_new_hero(self):
        self.hero = character.Hero()
        self.hero.interactive_character_creation()
        self.hero.choose_potion_cli()  # TODO: W wersji GUI zastąpić interaktywnym modułem wyboru mikstury
        print(Fore.RED + "\n *** ZACZYNAMY !!! *** " +
              Style.RESET_ALL)
        print(menu.intro(self.hero))

    def quit_game(self):
        print("Do zobaczenia wkrótce Śmiałku!")
        self.save_game()
        exit()

    def load_last_saved_game(self, default: int=None):
        directory_path, files = self.get_saved_files()
        if files:
            txt = ("Wybierz zapis. "
                   "[* aby wrócić do poprzedniego menu]\n"
                   ">>> ")
            # add each file in the directory to input list
            for i, file in enumerate(files):
                txt += f"[{i + 1}] {file.strip('.json')}\n"

            while True:
                try:
                    file_index = input(txt)
                    if file_index == "*":
                        self.start_game()
                    selected_file = files[int(file_index) - 1]
                    if os.path.exists(directory_path / selected_file):
                        with open(directory_path / selected_file) as f:
                            load_data = json.load(f)
                            self.load_hero(load_data)
                            break
                    else:
                        print("Nie ma zapisanej gry w bibliotece.")
                        self.start_game()
                except IndexError:
                    self.load_last_saved_game()
        else:
            print("Nie ma żadnych zapisanych plików")
            self.start_game()

    @staticmethod
    def get_saved_files():
        directory_path = pathlib.Path.cwd() / "SAVE"
        files = []

        try:
            # Get a list of files (excluding directories) in the directory
            files = [f for f in os.listdir(directory_path) if
                     os.path.isfile(os.path.join(directory_path, f))]
            return directory_path, files
        except WindowsError:
            ...
        except Exception as e:
            print(e)

        return pathlib.Path.cwd(), files

    def game_over(self):
        while True:
            game_over = input(
                Fore.GREEN +
                "I tak oto kończy się twoja przygoda Śmiałku! Zginąłeś!\n\n" +
                Fore.MAGENTA + "[1]" + Fore.GREEN +
                "Chcesz zagrać raz jeszcze?\n" +
                Fore.MAGENTA + "[2]" + Fore.GREEN + "Wczytać zapis gry?\n\n" +
                Fore.MAGENTA + "[0]" + Fore.GREEN + "Zakończyć grę?\n" +
                Fore.MAGENTA + ">>> " + Style.RESET_ALL)

            if game_over == "1":
                self.start_game()
                # tu potrzebna replikacja martwego bohatera
                break
            elif game_over == "2":
                self.load_last_saved_game()
            elif game_over == "0":
                self.quit_game()

    def _toggle_test_mode(self):
        self.test = not self.test
        print(f"TEST: {self.test}")
        return False

    def _hero_suicide(self):
        self.hero.stamina = 0
        print(f"{self.hero.name} zginął!")
        self.game_over()
        return True

    def _eat_provision(self):
        if "Prowiant" in self.book_chapters[self.last_valid_chapter]:
            healed, _ = game_mechanics.consume(self.hero)
            if healed > 0:
                print(f"Spożyłeś prowiant. W: +{healed}")
            else:
                print("Nie masz już Prowiantu albo jesteś najedzony.")
        else:
            print("Nie możesz w tej chwili zjeść Prowiantu")
        return False

    def handle_main_menu_command(self, cmd: str) -> bool:
        paragraph = self.book_chapters.get(self.last_valid_chapter)

        if cmd in self.COMMANDS:
            return self.COMMANDS[cmd]()
        elif self.dev_mode and cmd in self.DEV_COMMANDS:
            return self.DEV_COMMANDS[cmd]()
        elif (self.check_move(cmd)
              and cmd.isdigit()
              and cmd in self.book_chapters):
            self.open_chapter(cmd)
            return False
        else:
            if paragraph:
                posible_moves = [int(x) for x in paragraph.edges]
                print(posible_moves)
                print(Fore.YELLOW + f"Nieprawidłowy wybór. Możliwe ruchy: {posible_moves}")
            else:
                print(Fore.YELLOW + "Nieprawidłowy wybór i brak dostępu do aktualnego paragrafu.")
            return False

    def check_move(self, cmd):
        return True

    def main_menu(self, relecture=None):
        if relecture:
            print("cd. ", end='')
            # self.open_chapter(None, relecture)

        while True:
            chapter = input(">>> ")
            should_break = self.handle_main_menu_command(chapter)
            if should_break:
                break

    def _show_command_list(self) -> bool:
        """
        Displays a grouped list of available command keys for the player.
        """
        print(Fore.CYAN + "\nDostępne komendy:" + Style.RESET_ALL)

        command_groups = {
            "🧱 System": [],
            "🧙‍♂️ Bohater": [],
            "⚔️ Walka": [],
            "🧪 Debug / Dev": []
        }

        label_map = {
            "0": "Zakończ grę",
            "q": "Zakończ grę",
            "s": "Zapisz grę",
            "dev": "Tryb developerski",
            "?": "Lista komend",
            "help": "Lista komend",

            "h": "Parametry bohatera",
            "i": "Plecak",
            "e": "Zjedz Prowiant",

            "f": "Walka",
            "k": "Walka testowa (1hp)",
            "v": "Odwiedzone paragrafy",

            "t": "Tryb testowy",
            "killself": "Zabij się",
            "sal": "Ulecz się"
        }

        group_map = {
            "0": "🧱 System",
            "q": "🧱 System",
            "s": "🧱 System",
            "dev": "🧱 System",
            "?": "🧱 System",
            "help": "🧱 System",

            "h": "🧙‍♂️ Bohater",
            "i": "🧙‍♂️ Bohater",
            "e": "🧙‍♂️ Bohater",

            "f": "⚔️ Walka",
            "k": "🧪 Debug / Dev",
            "v": "⚔️ Walka",

            "t": "🧪 Debug / Dev",
            "killself": "🧪 Debug / Dev",
            "sal": "🧪 Debug / Dev"
        }

        dev_items = []
        if self.dev_mode:
            dev_items = [
                ("test", "Tryb testowy"),
                ("k","Walka testowa z 1hp"),
                ("killself", "Zabij się"),
                ("sal", "Ulecz się"),
            ]

        printed = set()

        for key, func in self.COMMANDS.items():
            if func in printed:
                continue
            printed.add(func)

            group = group_map.get(key, "🧱 System")
            label = label_map.get(key, "<nieznana akcja>")
            command_groups[group].append((key, label))

        for group, items in command_groups.items():
            if items:
                print(Fore.BLUE + f"\n{group}" + Style.RESET_ALL)
                for key, label in sorted(items):
                    print(Fore.MAGENTA + f"[{key}]" + Fore.GREEN + f" {label}")

        if self.dev_mode:
            print(Fore.BLUE + "\n🧪 Debug / Dev" + Style.RESET_ALL)
            for key, label in sorted(dev_items):
                print(Fore.MAGENTA + f"[{key}]" + Fore.GREEN + f" {label}")
        return False

    @staticmethod
    def open_book() -> dict[str, Paragraph]:
        path = pathlib.Path.cwd() / "shiver.json"
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
        print({k: Paragraph(k, v) for k, v in raw.items()})
        return {k: Paragraph(k, v) for k, v in raw.items()}

    def open_chapter(self, chapter: str):
        self.last_valid_chapter = chapter
        paragraph = self.book_chapters.get(chapter)

        if not paragraph:
            print(Fore.RED + f"Nie znaleziono paragrafu {chapter}.")
            return

        # Wyświetl tekst paragrafu
        print(Fore.CYAN + f"\n[{chapter}]\n" + Style.RESET_ALL + paragraph.text)

        # Dodaj do odwiedzonych
        self.visited_chapters[chapter] = True

        # Wyświetl możliwe przejścia
        if paragraph.edges:
            if "END" in paragraph.edges:
                print(Fore.RED + "\n🔚 To może być koniec twojej przygody...\n")
            else:
                print(Fore.GREEN + "\nMożliwe przejścia: " + " / ".join(str(x) for x in paragraph.edges))
        else:
            print(Fore.YELLOW + "\nBrak oczywistych dróg dalszych.\n")

    def possible_moves(self) -> str:
        paragraph = self.book_raw[self.last_valid_chapter]
        moves = paragraph.get_choices()

        if not moves:
            return "Brak widocznych opcji przejścia."

        return " / ".join(moves)

    def load_hero(self, hero_data):
        self.hero = character.Hero()
        self.test = hero_data["TEST"]
        self.hero.name = hero_data["NAME"]
        self.hero.max_agility = hero_data["MAX_AGILITY"]
        self.hero.max_stamina = hero_data["MAX_STAMINA"]
        self.hero.max_luck = hero_data["MAX_LUCK"]
        self.hero.agility = hero_data["AGILITY"]
        self.hero.stamina = hero_data["STAMINA"]
        self.hero.luck = hero_data["LUCK"]
        self.hero.inventory.sword = hero_data["INVENTORY"]["SWORD"]
        self.hero.inventory.shield = hero_data["INVENTORY"]["SHIELD"]
        self.hero.inventory.lantern = hero_data["INVENTORY"]["LANTERN"]
        self.hero.inventory.agility_potion = hero_data["INVENTORY"]["A_POTION"]
        self.hero.inventory.stamina_potion = hero_data["INVENTORY"]["S_POTION"]
        self.hero.inventory.luck_potion = hero_data["INVENTORY"]["L_POTION"]
        self.hero.inventory.food = hero_data["INVENTORY"]["FOOD"]
        self.hero.inventory.gold = hero_data["INVENTORY"]["GOLD"]
        self.hero.inventory.bag = hero_data["INVENTORY"]["BAG"]
        self.hero.kills = hero_data["KILLS"]
        self.last_valid_chapter = hero_data["LAST_CHAPTER"]
        self.visited_chapters = hero_data["VISITED"]
        self.dev_mode = hero_data["DEV"]

    def save_game(self, quicksave: bool = False):
        if self.hero is not None:
            save_payload = {
                "NAME": f"{self.hero.name}",
                "TEST": self.test,
                "MAX_AGILITY": self.hero.max_agility,
                "MAX_STAMINA": self.hero.max_stamina,
                "MAX_LUCK": self.hero.max_luck,
                "AGILITY": self.hero.agility,
                "STAMINA": self.hero.stamina,
                "LUCK": self.hero.luck,
                "INVENTORY": {
                    "SWORD": f"{self.hero.inventory.sword}",
                    "SHIELD": f"{self.hero.inventory.shield}",
                    "LANTERN": f"{self.hero.inventory.lantern}",
                    "A_POTION": self.hero.inventory.agility_potion,
                    "S_POTION": self.hero.inventory.stamina_potion,
                    "L_POTION": self.hero.inventory.luck_potion,
                    "FOOD": self.hero.inventory.food,
                    "GOLD": self.hero.inventory.gold,
                    "BAG": {

                    },
                },
                "VISITED": self.visited_chapters,
                "LAST_CHAPTER": self.last_valid_chapter,
                "KILLS": self.hero.kills,
                "DEV": self.dev_mode
            }

            dir_path = pathlib.Path.cwd() / "SAVE"
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)

            save_path = dir_path / self.hero.name
            with open(save_path.with_suffix(".json"), "w", encoding="utf-8") as f:
                json.dump(save_payload, f, indent=4)
            print(f"Zapisano plik: {self.hero.name}")
        else:
            if quicksave:
                print("Nie można było zapisać pliku.")

    def delete_game(self):
        while True:
            directory_path, files = self.get_saved_files()
            if files:
                txt = ("Wybierz zapis który chcesz usunąć. "
                       "[* aby wrócić do poprzedniego menu]\n"
                       ">>> ")

                # add each file in the directory to input list
                for i, file in enumerate(files):
                    txt += f"[{i + 1}] {file.strip('.json')}\n"

                try:
                    file_index = input(txt)
                    if file_index == "*":
                        break
                    selected_file = files[int(file_index) - 1]
                    if os.path.exists(directory_path / selected_file):
                        os.remove(directory_path / selected_file)
                except IndexError:
                    self.delete_game()
            else:
                print("Nie ma plików do usunięcia")
                break


if __name__ == "__main__":
    args = sys.argv[1:]
    game = Shiver()
    game.start_game()