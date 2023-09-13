import json
import pathlib
import random
from itertools import combinations

from character import Monster


def roll_d6():
    """
        Simulate the roll of a 6-sided die (D6).

        Returns:
            int: A random integer between 1 and 6 (inclusive).
        """
    return random.randint(1, 6)


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


def combat(game_instance):
    game_instance.monsters_kiled = 0
    game_instance.bout = 1
    monsters = get_monsters(game_instance.last_valid_chapter)
    if monsters:

        while game_instance.monsters_kiled < len(monsters):
            game_instance.monsters_in_line = len(monsters)
            if game_instance.hero.is_dead():
                print(f"{game_instance.hero.name} zginął!")
                game_instance.game_over()
            elif monsters[game_instance.monsters_kiled].is_dead():
                print(f"{monsters[game_instance.monsters_kiled].name} został pokonany!")
                print(f"Zostało ci W: {game_instance.hero.stamina}")
                game_instance.bout = 1
                game_instance.monsters_kiled += 1
            else:
                print(f"Runda {game_instance.bout}")
                fight(game_instance.hero, monsters[game_instance.monsters_kiled])
                game_instance.bout += 1
        game_instance.main_menu(game_instance.last_valid_chapter)
    else:
        print("Nie ma z kim walczyć w tym paragrafie.")


def resolve_fight(hero, monster):
    monster_result = roll_2d6()
    print(monster_result)

    hero_result = roll_2d6()
    print(hero_result)


def fight(hero, monster):
    monster_atack = monster.attack_strenght()
    hero_atack = hero.attack_strenght()

    if hero_atack > monster_atack:
        monster.stamina -= 2
    elif hero_atack < monster_atack:
        hero.stamina -= 2
    else:
        ...


def can_escape(game_instance):
    """
    Checks if hero can escape from fight.

    x można uciec
    x po 1 rundzie
    x po 2 rundzie
    x po każdej rundzie
    x po każdej walce

    Returns:
        bool: True, when he/she can.
    """
    run = False
    escape = {
        '2': '11110',
        '32': '00000',
        '69': '00000',
        '92': '10001',
        '98': '00000',
        '107': '00000',
        '109': '00000',
        '116': '00000',
        '157': '11000',
        '169': '11000',
        '184': '11100',
        '213': '00000',
        '216': '00000',
        '238': '10001',
        '255': '00000',
        '277': '10001',
        '288': '00000',
        '307': '00000',
        '309': '11000',
        '312': '10001',
        '317': '00000',
        '332': '00000',
        '341': '00000',
        '344': '00000',
        '355': '00000',
        '361': '00000',
        '367': '00000'
    }
    bout = game_instance.bout
    par = game_instance.last_valid_chapter
    monsters_kiled = game_instance.monsters_kiled

    if par in escape.keys() and escape[par][0] != "0":
        if bout == 1 and escape[par][1] != "0":
            print(1)
            run = True
        elif 0 < bout < 3 and escape[par][2] != "0":
            print(2)
            run = True
        elif bout < 0 and escape[par][3] != "0":
            print(3)
            run = True
        elif monsters_kiled > 0 and escape[par][4] != "0":
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
