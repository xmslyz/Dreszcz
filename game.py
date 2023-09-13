import json
import os
import re

import game_mechanics
import character


class Shiver:
    def __init__(self):
        self.test = True
        self.last_valid_chapter: str = "1"
        self.visited_chapters: dict = {}
        self.hero = character.Hero("Stefan")
        self.hero.set_attribute_levels()
        self.bout = 0
        self.monsters_kiled = 0
        self.book_chapters = game_mechanics.open_book()

    def start_game(self):
        try:
            # open last saved or first
            while True:
                user_input = input(
                    "[1] Nowa gra\n"
                    "[2] Wczytaj ostatni zapis\n"
                    "\n"
                    "[0] Zakończ [w dowolnym momencie gry]\n"
                    ">>> "
                )

                if user_input == "1":
                    # self.visited_chapters["1"] = True
                    self.open_chapter("1")
                    break
                elif user_input == "2":
                    self.load_last_saved_game()
                    self.open_chapter(self.last_valid_chapter)
                    break
                elif user_input == "0":
                    self.quit_game()

                else:
                    print("Spróbuj jeszcze raz.")

            self.main_menu()

        except FileNotFoundError:
            print("Nie znaleziono pliku gry.")

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
                "I tak oto kończy się twoja przygoda Śmiałku! Zginąłeś!\n\n"
                "[1] Chcesz zagrać raz jeszcze?\n"
                "[2] Wczytać zapis gry?\n\n"
                "[0] Zakończyć grę?\n"
                ">>> ")

            if game_over == "1":
                self.start_game()
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
            elif chapter == "v":
                print(sorted([int(x) for x in self.visited_chapters.keys()]))
            elif chapter == "f":
                game_mechanics.combat(self)
            elif chapter == "r":
                if game_mechanics.can_escape(self):
                    print("run")
                else:
                    print("cant run")
            elif (self.check_move(chapter)
                  and chapter.isdigit()
                  and chapter in self.book_chapters):
                self.open_chapter(chapter)
            else:
                print("Nieprawidłowy numer paragrafu. Spróbuj ponownie.")

    @staticmethod
    def show_action_menu():
        print("--- Opcje\n"
              "-- [v] Pokaż odwiedzone paragrafy\n"
              "-- [f] Walka"
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
                print("Nieprawidłowy znak. Spróbuj ponownie.")

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
        if not self.test:
            for key, value in self.book_chapters.items():
                if key == self.last_valid_chapter:
                    if chapter in re.findall(r"(?<!:)\b\d+\b", value):
                        return True
        else:
            return True


if __name__ == "__main__":
    game = Shiver()
    game.start_game()
