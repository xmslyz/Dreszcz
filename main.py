import json
import re
from itertools import combinations
import menu
import os
from colorama import Fore, Style

from player import Player, Actions


class Game:
    def __init__(self):
        with open("dreszcz.json") as f:
            self.book = json.load(f)
        self.saved_paragraph = None
        self.is_test = False
        self.numbers = []
        self.last_valid_input = "1"

        # create hero
        self.hero = Player()
        self.hero.set_level()

        # print 1st paragraph
        self.show_paragraph("1")

    def get_new_paths(self, number):
        for key, value in self.book.items():
            if key == number:
                self.numbers = re.findall(r"(?<!:)\b\d+\b", value)
        return self.numbers

    def show_paragraph(self, number):
        print(Fore.YELLOW + self.book[number] + Style.RESET_ALL)
        print(self.get_new_paths(number))

    def users_move(self):
        # Get the next paragraph number or action
        # list_of_paths = self.get_new_paths(self.last_valid_input)
        next_move = input('*** Wpisz numer [lub wywołaj menu "m"]: ').lower()

        if next_move == "m":
            self.action_menu()

        elif next_move.isdigit():
            # if next_move in list_of_paths and 1 <= int(next_move) <= 387:
            if 1 <= int(next_move) <= 387:
                self.last_valid_input = next_move
                return next_move

            else:
                print(
                    Fore.RED
                    + "Możesz tylko wpisywać numery podane w paragrafie, "
                      "lub znaki menu."
                    + Style.RESET_ALL
                )
                return self.last_valid_input

        else:
            print(
                Fore.RED
                + "Możesz tylko wpisywać numery podane w paragrafie, "
                  "lub znaki menu."
                + Style.RESET_ALL
            )
            return self.last_valid_input

    def action_menu(self):
        while True:
            print("Menu Akcji:")
            print("[f] walka")
            print("[r] ucieczka")
            print("[e] prowiant")
            print("[r] zasady gry")
            print("[h] hełm")
            print("[g] złoto")
            print("[x] wyjdź z menu")
            print("[q] koniec gry")
            menu_input = input("Wybierz: ")
            if menu_input == "f":
                monsters = self.extract_monster(self.last_valid_input)
                for monster in monsters:
                    Actions().fight_round_result(self.hero, monster)
            elif menu_input == "r":
                # noinspection SpellCheckingInspection
                if "Ucieczk" in self.book[self.last_valid_input]:
                    self.hero.run()
                else:
                    print("Nie możesz się teraz ratować ucieczką!")
            elif menu_input == "e":
                if "prowiant" in self.book[self.last_valid_input]:
                    self.hero.eat()
                else:
                    print("Nie możesz teraz zjeść Prowiantu!")
                self.hero.eat()
            elif menu_input == "r":
                menu.rules()
            elif menu_input == "h":
                self.hero.use_object("stamina", False, 4)
            elif menu_input == "g":
                self.hero.use_gold(False, 2)
            elif menu_input == "o":
                self.hero.use_bag("kościany kordelas")
            elif menu_input == "k":
                self.hero.play_cards(True)
            elif menu_input == "x":
                break
            elif menu_input == "q":
                exit()
            else:
                print(Fore.RED + "Zły znak" + Style.RESET_ALL)
                self.action_menu()

    def extract_monster(self, number):
        prickle = self.book[number]
        splitted_prickle = prickle.split(" ")

        index_nums = []
        for i, word in enumerate(splitted_prickle):
            if str(word).isupper():
                index_nums.append(i)

        monsters = []
        for i in extract_consecutive_lists(index_nums):
            if splitted_prickle[i[1]].startswith("Z:") and splitted_prickle[
                i[2]
            ].startswith("W:"):
                monsters.append([number, splitted_prickle[i[0]]])

        return monsters

    def save_current_paragraph(self, number):
        self.saved_paragraph = number


def play_game():
    game = Game()

    while True:
        try:
            user_input = game.users_move()

            # get paragraph content
            game.show_paragraph(user_input)
            os.system("cls")

        except KeyError:
            game.show_paragraph(game.last_valid_input)


def extract_consecutive_lists(lst):
    consecutive_lists = []
    for i in range(len(lst) - 2):
        if lst[i] + 1 == lst[i + 1] and lst[i + 1] + 1 == lst[i + 2]:
            consecutive_lists.append(lst[i: i + 3])
    return consecutive_lists


def check_keys(key_a, key_b, key_c):
    target_sum = 204
    found_combination = None

    for combination in combinations([key_a, key_b, key_c], 3):
        if sum(combination) == target_sum:
            found_combination = combination
            break

    return True if found_combination else False


if __name__ == "__main__":
    play_game()
