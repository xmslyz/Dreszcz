import json
import pathlib
import random
from itertools import combinations

import colorama
from colorama import Fore, Style, Back

from character import Monster


def roll_d6():
    """
        Simulate the roll of a 6-sided die (D6).

        Returns:
            int: A random integer between 1 and 6 (inclusive).
        """
    result = random.randint(1, 6)
    d6(random.randint(1, 6), random.randint(1, 6))
    return result


def roll_2d6():
    """
        Simulate the roll of two 6-sided dice (2D6) and calculate their sum.

        Returns:
            int: The sum of two random integers between 1 and 6 (inclusive).
        """
    return roll_d6() + roll_d6()


def play_cards(hero, with_luck: bool):
    rolling = roll_2d6()
    # if with_luck:
    #     if self.am_i_lucky():
    #         self.inventory.gold += k2
    #     else:
    #         for i in range(k2):
    #             if self.inventory.gold == 0:
    #                 print("Nie masz więcej pieniędzy")
    #                 break
    #             else:
    #                 self.inventory.gold -= 1
    # else:
    #     if k2 % 2 == 0:
    #         for i in range(k2):
    #             if self.inventory.gold == 0:
    #                 print("Nie masz więcej pieniędzy")
    #                 break
    #             else:
    #                 self.inventory.gold -= 1
    #     else:
    #         self.inventory.gold += k2
    #
    # print(self.inventory.gold)


def get_monsters(chapter):
    """
    Extracts monster attributes from a JSON book file.

    Args:
        chapter (str): The paragraph key to look up in the JSON book file.

    Returns:
        list: A list of monster attributes in the format [paragraph,
        monster_name].
    """

    book = open_book()

    # Initialize an empty list to store monster attributes
    monsters = []

    # Identify consecutive index positions indicating monster name & attributes
    consecutive_lists = []

    # Split the paragraph into words
    prickle = book[chapter].split(" ")

    # Find the index positions of uppercase words
    # (potential monster name and monster stamina and agility)
    index_nums = []
    for i, word in enumerate(prickle):
        if str(word).isupper():
            index_nums.append(i)

    for i in range(len(index_nums) - 2):
        if (index_nums[i] + 1 == index_nums[i + 1]
                and index_nums[i + 1] + 1 == index_nums[i + 2]):
            consecutive_lists.append(index_nums[i: i + 3])

    # Extract monster attributes that start with "Z:" and "W:"
    for i in consecutive_lists:
        if prickle[i[1]].startswith("Z:") and prickle[i[2]].startswith("W:"):
            # extract monster data
            name = prickle[i[0]]
            agility = int(prickle[i[1]].strip("Z:"))
            stamina = int(prickle[i[2]].strip("W:"))

            # create instance of monster
            monster = Monster(name, agility, stamina)

            # add monster object to monsters list
            monsters.append(monster)

    # Return the list of monster objects
    return monsters


def wanna_check_sss(hero):
    question = input(
        f"Chcesz sprawdzić swoje szczęście? [T]/[N]\n"
        f"Obecny poziom SZCZĘŚCIA wynosi {hero.luck}.\n"
        f">>> "
    ).lower()
    match question:
        case "t":
            return True
        case "n":
            return False
        case _:
            print(" * * * Zły znak * * * ")
            wanna_check_sss(hero)


def check_keys(key_a, key_b, key_c):
    target_sum = 204
    found_combination = False

    for combination in combinations([key_a, key_b, key_c], 3):
        if sum(combination) == target_sum:
            found_combination = True
            break

    return found_combination


def combat(story):
    story.monsters_kiled_counter = 0
    story.bout = 1
    monsters = get_monsters(story.last_valid_chapter)
    if monsters:
        while story.monsters_kiled_counter < len(monsters):
            story.monsters_in_line = len(monsters)
            if story.hero.is_dead():
                print(f"{story.hero.name} zginął!")
                story.game_over()
            elif monsters[story.monsters_kiled_counter].is_dead():
                print(
                    f"{monsters[story.monsters_kiled_counter].name} "
                    f"został pokonany!"
                )
                print(f"Zostało ci W: {story.hero.stamina}")
                story.bout = 1
                story.monsters_kiled_counter += 1
            else:
                print(Back.RED +
                      f"   {monsters[story.monsters_kiled_counter].name}"
                      f": runda {story.bout}   " + Style.RESET_ALL)
                combat_menu = input("[1] Starcie - rzut koścmi\n"
                                    "[2] Ucieczka\n"
                                    "[3] Zmiana broni\n"
                                    "[4] ...\n"
                                    "[0] Koniec gry\n"
                                    ">>> ")
                if combat_menu == "1":
                    fight(story.hero, monsters[story.monsters_kiled_counter])
                    story.bout += 1
                elif combat_menu == "2":
                    if can_escape(story):
                        break
                    else:
                        print("Nie możesz teraz uciec Śmiałku!")
                elif combat_menu == "3":
                    print("Zmieniasz broń")
                elif combat_menu == "0":
                    story.quit_game()
                else:
                    print("Nie ma takiej opcji")

        story.main_menu(story.last_valid_chapter)
    else:
        print("Nie ma z kim walczyć w tym paragrafie.")


def fight(hero, monster):
    monster_atack = monster.attack_strenght()
    hero_atack = hero.attack_strenght()

    if hero_atack > monster_atack:
        monster.stamina -= 2
        show_stamina(hero, monster)
    elif hero_atack < monster_atack:
        hero.stamina -= 2
        show_stamina(hero, monster)
    else:
        print(Fore.YELLOW + "Remis" + Style.RESET_ALL)


def show_stamina(hero, monster):
    staminas = (
        f"{monster.name} W:{monster.stamina} vs. "
        f"{hero.name} W:{hero.stamina}")
    print(Fore.GREEN + staminas + Style.RESET_ALL)


def can_escape(game_instance):
    """
    Checks if hero can escape from fight.

    x można uciec
    x po x rundzie (jeśli 0 to po każdej rundzie)
    x po każdej walce

    Returns:
        bool: True, when he/she can.
    """
    run = False
    escape = {
        '2': '1990',
        '32': '0000',
        '69': '0000',
        '92': '1990',
        '98': '0000',
        '107': '0000',
        '109': '0000',
        '116': '0000',
        '157': '1010',
        '169': '1010',
        '184': '1020',
        '213': '0000',
        '216': '0000',
        '238': '1001',
        '255': '0000',
        '277': '1001',
        '288': '0000',
        '307': '0000',
        '309': '1010',
        '312': '1001',
        '317': '0000',
        '332': '0000',
        '341': '0000',
        '344': '0000',
        '355': '0000',
        '361': '0000',
        '367': '0000'
    }
    bout = game_instance.bout
    par = game_instance.last_valid_chapter
    monsters_kiled = game_instance.monsters_kiled_counter

    if par in escape.keys() and escape[par][0] != "0":
        if 0 < bout <= int(escape[par][1:3]):
            run = True
        elif monsters_kiled > 0 and escape[par][3] != "0":
            print(4)
            run = True

    return run


def open_book():
    # Define the path to the JSON book file
    book_path = pathlib.Path.cwd() / "dreszcz.json"

    # Open and load the JSON book file
    with open(book_path) as f:
        return json.load(f)


special = {
    '109': 'po !wygranej! 1 rundzie patrz 77 **po przegranej 163',
    '355': 'po pierwszej wygranej rundzie pytanie',
    '344': 'fireball',
    '309': 'zmiana broni po 1 rundzie',
    '238': 'dalej albo 316 albo 103',
}


def d6(left, right):
    top = "_______"
    line = "|       |"
    line_o_ = "|   ●   |"
    lineo__ = "| ●     |"
    line__o = "|     ● |"
    lineo_o = "| ●   ● |"
    bottom = "‾‾‾‾‾‾‾"

    def get_lines(value):
        if value == 1:
            return line, line_o_, line
        elif value == 2:
            return lineo__, line, line__o
        elif value == 3:
            return lineo__, line_o_, line__o
        elif value == 4:
            return lineo_o, line, lineo_o
        elif value == 5:
            return lineo_o, line_o_, lineo_o
        elif value == 6:
            return lineo_o, lineo_o, lineo_o
        return line, line, line

    left_lines = get_lines(left)
    right_lines = get_lines(right)

    print("", top, "  ", top)
    for left_line, right_line in zip(left_lines, right_lines):
        print(left_line, "", right_line)
    print("", bottom, "  ", bottom)
