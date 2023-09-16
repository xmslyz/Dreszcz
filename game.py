import json
import os
import pathlib
import re
import arrow
from colorama import Fore, Style, init
import game_mechanics
import character
import menu

init(autoreset=True)


class Shiver:
    def __init__(self):
        self.test = False
        self.last_valid_chapter: str = "1"
        self.visited_chapters: dict = {}
        self.hero = None
        self.bout = 0
        self.monsters_kiled_counter = 0
        self.killed_monsters_dict = {}
        self.book_chapters = game_mechanics.open_book()
        self.TEMP = {}

    def start_game(self):
        try:
            # open last saved or first
            while True:
                start_game = input(
                    Fore.MAGENTA + "[1] " + Fore.GREEN + "Nowa gra\n" +
                    Fore.MAGENTA + "[2] " + Fore.GREEN + "Wczytaj ostatni "
                                                         "zapis\n" +
                    Fore.MAGENTA + "[3] " + Fore.GREEN + "Usuń zapis\n" + "\n" +
                    Fore.MAGENTA + "[0] " + Fore.GREEN + "Zakończ [w dowolnym "
                                                         "momencie gry]\n" +
                    Fore.MAGENTA + ">>> " + Style.RESET_ALL
                )

                if start_game == "1":
                    self.create_new_hero()
                    self.save_game()
                    self.open_chapter("1")
                    break
                elif start_game == "2":
                    self.load_last_saved_game()
                    self.open_chapter(self.last_valid_chapter)
                    break
                elif start_game == "3":
                    self.delete_game()
                elif start_game == "0":
                    self.quit_game()

                else:
                    print("Spróbuj jeszcze raz.")

            self.main_menu()

        except FileNotFoundError:
            print("Nie znaleziono pliku gry.")

    def create_new_hero(self):
        self.hero = character.Hero()
        self.hero.set_attribute_levels()
        self.hero.choose_potion()
        print(Fore.RED + "\n *** ZACZYNAMY !!! *** " +
              Style.RESET_ALL)
        print(menu.intro(self.hero))

    def quit_game(self):
        print("Do zobaczenia wkrótce Śmiałku!")
        self.save_game()
        exit()

    def load_last_saved_game(self):
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
        except WindowsError as e:
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

    def main_menu(self, relecture=None):
        if relecture:
            print("cd. ", end='')
            self.open_chapter(relecture)

        while True:
            chapter = input(">>> ")
            if chapter == "0":
                self.quit_game()
            elif chapter == "o":
                self.show_action_menu()
            elif chapter == "s":
                self.save_game(quicksave=True)
            elif chapter == "h":
                print(self.hero)
            elif chapter == "killself":
                self.hero.stamina = 0
                print(f"{self.hero.name} zginął!")
                self.game_over()
            elif chapter == "k":
                game_mechanics.combat(self, True)
            elif chapter == "v":
                print(sorted([int(x) for x in self.visited_chapters.keys()]))
            elif chapter == "f":
                game_mechanics.combat(self)
            elif chapter == "e":
                if "Prowiant" in self.book_chapters[self.last_valid_chapter]:
                    game_mechanics.consume(self.hero)
                else:
                    print("Nie możesz w tej chwili zjeść Prowiantu")
            elif chapter == "i":
                print(self.hero.inventory)
            elif chapter == "test":
                self.test = not self.test
                print(f"TEST: {self.test}")
            elif (self.check_move(chapter)
                  and chapter.isdigit()
                  and chapter in self.book_chapters):
                # if chapter == "89":
                #     self.hero.change_atribute_level("luck", False, 2)
                self.open_chapter(chapter)
            else:
                print(f"Nieprawidłowy znak. Masz do wyboru: "
                      f"{self.possible_moves()}")

    @staticmethod
    def show_action_menu():
        print("--- Opcje\n"
              "-- [v] Pokaż odwiedzone paragrafy\n"
              "-- [h] Parametry Śmiałka\n"
              "-- [f] Walka\n"
              "-- [e] Zjedz Prowiant\n"
              "-- [i] Plecak\n"
              )

    def action_menu(self):
        """Main action menu"""
        while True:
            menu_input = input("Menu:\n"
                               "[1] Pokaż odwiedzone paragrafy\n"
                               "[2] Walka\n"
                               "\n"
                               ">>> ")
            if menu_input == "1":
                break
            if menu_input == "2":
                game_mechanics.combat(self)
                break
            if menu_input == "q":
                self.quit_game()
            else:
                print(f"Nieprawidłowy znak. Spróbuj ponownie.")

    def open_chapter(self, chapter: str):
        self.last_valid_chapter = chapter
        text = self.book_chapters[chapter]

        if chapter not in self.visited_chapters:
            # show actual paragraph
            print(f"[{chapter}] {text}")
            # add paragraph to visited places
            self.visited_chapters[chapter] = True
        else:
            print(f"[{chapter}*] {text}")

    def check_move(self, chapter):
        """checks if introduced number is valid next move"""
        pass_from_238 = ["316", "103"]
        if not self.test:
            for key, value in self.book_chapters.items():
                if key == self.last_valid_chapter:
                    if chapter in re.findall(r"(?<!:)\b\d+\b", value):
                        return True
                    elif (self.last_valid_chapter == "238" and chapter in
                          pass_from_238):
                        return True
        else:
            return True

    def possible_moves(self):
        book = self.book_chapters
        moves = re.findall(r"(?<!:)\b\d+\b", book[self.last_valid_chapter])
        txt = ""
        for move in moves:
            txt += f"{move} / "

        return f"{txt}"

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

    def save_game(self, quicksave: bool = False):
        if self.hero is not None:
            self.TEMP = {
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
                "KILLS": self.hero.kills
            }

            save_time = arrow.Arrow.now().format(
                f"[{self.hero.name}] YYYY-MM-DD HH-mm-ss")

            save_hero = self.hero.name

            dir_path = pathlib.Path.cwd() / "SAVE"
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)

            save_path = dir_path / save_hero
            with open(save_path.with_suffix(".json"), "w",
                      encoding="utf-8") as f:
                json.dump(self.TEMP, f, indent=4)
            print(f"Zapisano plik: {save_hero}")
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
    game = Shiver()
    game.start_game()
