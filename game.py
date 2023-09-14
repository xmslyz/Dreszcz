import json
import os
import re

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

    def start_game(self):
        try:
            # open last saved or first
            while True:
                start_game = input(
                    Fore.MAGENTA + "[1] " + Fore.GREEN + "Nowa gra\n" +
                    Fore.MAGENTA + "[2] " + Fore.GREEN + "Wczytaj ostatni "
                                                        "zapis\n" + "\n" +
                    Fore.MAGENTA + "[0] " + Fore.GREEN + "Zakończ [w dowolnym "
                                                        "momencie gry]\n" +
                    Fore.MAGENTA + ">>> " + Style.RESET_ALL
                )

                if start_game == "1":
                    self.create_new_hero()
                    self.open_chapter("1")
                    break
                elif start_game == "2":
                    self.load_last_saved_game()
                    self.load_hero()
                    self.open_chapter(self.last_valid_chapter)
                    break
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
        with open("save.txt", "w", encoding="utf-8") as s:
            s.write(self.last_valid_chapter)
        with open("visited.json", "w") as v:
            json.dump(self.visited_chapters, v, indent=4)
        exit()

    def load_last_saved_game(self):
        if os.path.exists("save.txt"):
            with open("save.txt") as f:
                self.last_valid_chapter = f.read().strip()
                if os.path.exists("visited.json"):
                    with open("visited.json") as v:
                        self.visited_chapters = json.load(v)
        else:
            print("Nie ma zapisanej gry w bibliotece.")
            self.start_game()

    def game_over(self):
        while True:
            game_over = input(
                Fore.GREEN +
                "I tak oto kończy się twoja przygoda Śmiałku! Zginąłeś!\n\n" +
                Fore.MAGENTA + "[1]" + Fore.GREEN + "Chcesz zagrać raz jeszcze?\n" +
                Fore.MAGENTA + "[2]" + Fore.GREEN + "Wczytać zapis gry?\n\n" +
                Fore.MAGENTA + "[0]" + Fore.GREEN + "Zakończyć grę?\n" +
                Fore.MAGENTA + ">>> " + Style.RESET_ALL)

            if game_over == "1":
                self.start_game()
                # tu potrzebna replikacja martwego bohatera
                break
            elif game_over == "2":
                break
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
            elif chapter == "h":
                print(self.hero)
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
                if chapter == "89":
                    self.hero.change_atribute_level("luck", False, 2)
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

    def load_hero(self):
        pass


if __name__ == "__main__":
    game = Shiver()
    game.start_game()
