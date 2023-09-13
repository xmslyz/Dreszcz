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
    monster_index = 0
    monsters = get_monsters(game_instance.last_valid_chapter)
    if monsters:
        while monster_index < len(monsters):
            if game_instance.hero.is_dead():
                print(f"{game_instance.hero.name} zginął!")
                game_instance.game_over()
            elif monsters[monster_index].is_dead():
                print(f"{monsters[monster_index].name} został pokonany!")
                print(f"Zostało ci W: {game_instance.hero.stamina}")
                monster_index += 1
            else:
                fight(game_instance.hero, monsters[monster_index])
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


def can_escape(chapter):
    """
    Checks if hero can escape from fight.

    Args:
        chapter (str):

    Returns:
        bool: True, when can escape.
    """
    book = open_book()

    # Initialize an empty list to store a monster with attributes
    paragraphs = []

    # Split the paragraph into words
    prickle = book[chapter].split(" ")

    # Find the index positions of uppercase words
    index_nums = []
    for i, word in enumerate(prickle):
        if str(word).isupper():
            index_nums.append(i)

    # Identify if chapter has any monster
    for i in range(len(index_nums) - 2):
        if (index_nums[i] + 1 == index_nums[i + 1]
                and index_nums[i + 1] + 1 == index_nums[i + 2]):
            if chapter not in paragraphs:
                paragraphs.append(chapter)

    return chapter in paragraphs


# [1] nie
# [2] po każdej rundzie
# [3] po 1 rundzie
# [4] po pokonaniu potwora
# [5] przejdź do innego punktu
# [6] inne

def open_book():
    # Define the path to the JSON book file
    book_path = pathlib.Path.cwd() / "dreszcz.json"

    # Open and load the JSON book file
    with open(book_path) as f:
        return json.load(f)


""" nie
    nie, ale po wygranej 1 rundzie patrz
    tylko po 1 rundzie
    po 1 i 2 rundzie
    po każdej rundzie
    po każdej rundzie i po każdej walce
    po każdej walce  
    * fireball
"""

escape = {
    '2': 'po każdej rundzie',
    '32': 'no',
    '69': 'no',
    '92': 'po wygranej walce',
    '98': 'no',
    '107': 'no',
    '109': 'no, *po wygranej! 1 rundzie patrz 77 **po przegranej 163',
    '116': 'no',
    '157': 'tylko po pierwszej rundzie',
    '169': 'tylko po pierwszej rundzie',
    '184': 'po 1 rundzie lub po drugiej rundzie',
    '213': 'no',
    '216': 'no',
    '238': 'po każdej walce * dalej albo 316 albo 103',
    '255': 'no',
    '277': 'po każdej walce',
    '288': 'no',
    '307': 'no',
    '309': 'po 1 rundzie * zmiana broni po 1 rundzie',
    '312': 'po każdym',
    '317': 'no',
    '332': 'no',
    '341': 'no',
    '344': 'special - fireball',
    '355': 'no, ale po pierwszej wygranej rundzie pytanie',
    '361': 'no',
    '367': 'no'
}
