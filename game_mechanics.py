import json
import pathlib
import random
import re
from itertools import combinations

from colorama import Fore, Style

from character import Monster


def consume(hero, extra: bool = False):
    """
    Consume supplies. Each supply gives S: +4.

    Args:
        hero: instance of hero
        extra: when chapter [162] S: +5

    Returns:
        Actual value of food.

    """
    value = 5 if extra else 4
    food = hero.inventory.food
    j = 0
    if food > 0:
        while not hero.stamina >= hero.max_stamina:
            for _ in range(value):
                hero.stamina += 1
                j += 1
                if hero.stamina <= hero.max_stamina:
                    break
        hero.inventory.food -= 1
        print(f"Spożyłeś prowiant. W: +{j}")
    else:
        print("Nie masz już Prowiantu")

    return hero.inventory.food


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

    # Initialize an empty list to store monster objects
    monsters = []

    # Initialize an empty list to store posible monsters occurences
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


def sss(hero):
    """ Sprawdzian Swojego Szczęścia """
    hero.luck -= 1
    return True if roll_2d6() <= hero.luck else False


def check_keys(key_a, key_b, key_c):
    target_sum = 204
    found_combination = False

    for combination in combinations([key_a, key_b, key_c], 3):
        if sum(combination) == target_sum:
            found_combination = True
            break

    return found_combination


def combat(story, cheat=False):
    # create conter of dueled monsters
    story.monsters_kiled_counter = 0

    # create counter for rounds
    story.bout = 1

    # get all monster to fight with form chapter
    monsters = get_monsters(story.last_valid_chapter)

    if monsters:
        while story.monsters_kiled_counter < len(monsters):
            monster_name = monsters[story.monsters_kiled_counter].name
            # if the monster was allready killed
            if monster_name in story.hero.kills.keys():
                if story.last_valid_chapter == story.hero.kills[monster_name]:
                    print(f"{monster_name} już nieżyje!")
                    story.monsters_kiled_counter += 1  # get the next one
            else:
                # for tests only!
                if cheat:
                    print(monster_name, "SUCKERPUNCH", sep=": ")
                    monsters[story.monsters_kiled_counter].stamina = 0
                    story.hero.kills[monster_name] = story.last_valid_chapter
                    story.monsters_kiled_counter += 1
                else:
                    # hero dies
                    if story.hero.is_dead():
                        print(f"{story.hero.name} zginął!")
                        story.game_over()
                    # monster dies
                    elif monsters[story.monsters_kiled_counter].is_dead():
                        story.hero.kills[monster_name] = (
                            story.last_valid_chapter)
                        print(f"{monster_name} został pokonany!")
                        print(f"Zostało ci W: {story.hero.stamina}")
                        story.bout = 1
                        story.monsters_kiled_counter += 1
                    # tie
                    else:
                        print(f"\n   {monster_name}"
                              f": runda {story.bout}   ")
                        combat_menu = input("[1] Starcie - rzut koścmi\n"
                                            "[2] Ucieczka\n"
                                            "[3] Zmiana broni\n"
                                            "[4] Modyfikacja parametrów\n"
                                            "[0] Koniec gry\n"
                                            ">>> ")
                        if combat_menu == "1":
                            fight(story.hero,
                                  monsters[story.monsters_kiled_counter])
                            story.bout += 1
                        elif combat_menu == "2":
                            if can_escape(story):
                                if sss_check(story.hero):
                                    if sss(story.hero):
                                        print(
                                            "Miałeś szczęście, potwór ledwo "
                                            "drasnął twoje plecy. "
                                            "Wytrzymałość -1"
                                        )
                                        story.hero.stamina -= 1
                                    else:
                                        print(
                                            "Masz pecha.  Kiedy zacząłeś "
                                            "uciekać potwór zdążył w "
                                            "ostatniej chwili zadać ci głęboką "
                                            "ranę. Wytrzymałość -3"
                                        )
                                        story.hero.stamina -= 3
                                else:
                                    print(
                                        "Kiedy odwróciłeś się aby uciec, "
                                        "potwór zdążył uderzyć po raz "
                                        "ostatni, zadając ci bolesną ranę. "
                                        "Wytrzymałość -2"
                                    )
                                    story.hero.stamina -= 2
                                break
                            else:
                                print("Nie możesz teraz uciec Śmiałku!")
                        elif combat_menu == "3":
                            print("Zmieniasz broń")
                        elif combat_menu == "4":
                            print(f"Podaj modyfikator:")
                            modificator = input("+/- number Z/S/W (np.: +1Z, -2S\n"
                                                ">>> ")
                            modify_atributes(story, modificator)
                        elif combat_menu == "0":
                            story.quit_game()
                        else:
                            print("Nie ma takiej opcji")

        story.main_menu(story.last_valid_chapter)
    else:
        print("Nie ma z kim walczyć w tym paragrafie.")


def fight(hero, monster):
    print(monster.stamina)
    while True:
        input("Rzuć kośćmi dla potwora.")
        monster_roll = roll_2d6()
        monster_atack = monster.attack_strenght(monster_roll)
        input("Rzuć kośćmi za siebie")
        hero_roll = roll_2d6()
        hero_atack = hero.attack_strenght(hero_roll)
        break

    if hero_atack > monster_atack:
        narrative("hero")
        if sss_check(hero):
            if sss(hero):
                print("Masz szczęście!")
                monster.stamina -= 4
            else:
                print("Zabrakło ci szczęścia!")
                monster.stamina -= 1
        else:
            monster.stamina -= 2
        show_stamina(hero, monster)
    elif hero_atack < monster_atack:
        narrative("monster")
        if sss_check(hero):
            if sss(hero):
                print("Masz szczęście!")
                hero.stamina -= 1
            else:
                print("Zabrakło ci szczęścia!")
                hero.stamina -= 3
        else:
            hero.stamina -= 2
        show_stamina(hero, monster)
    else:
        print("Remis")
        narrative("tie")


def sss_check(hero):
    question = input(f"Twój aktualny poziom SZCZĘŚCIA wynosi {hero.luck}.\n"
                     f"Jeśli chcesz Sprawdzić Swoje Szczęście (SSS) >>> ["
                     f"t]: ").upper()
    if question == "T":
        return True


def narrative(character):
    """
    Epic narrative of combat

    Args:
        character: hero, monster, tie

    Returns:
        random element of the list
    """
    with open("narratives.json", encoding="utf=8") as f:
        narratives = json.load(f)
    print(random.choice(narratives[character]))


def show_stamina(hero, monster):
    staminas = (
        f"{monster.name} W:{monster.stamina} vs. "
        f"{hero.name} W:{hero.stamina}")
    print(staminas)


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


def modify_atributes(story, modificator: str):
    check_input = re.findall(r'(([+|-])([0-9])([WSZ]))', modificator)
    if check_input:
        inplus, value, atribute = modificator
        inplus = True if inplus == "+" else False
        if atribute == "S":
            atribute = "luck"
        elif atribute == "W":
            atribute = "stamina"
        else:
            atribute = "agility"
        story.hero.change_atribute_level(atribute, inplus, int(value))
    else:
        print("zły format")


def open_book():
    # Define the path to the JSON book file
    book_path = pathlib.Path.cwd() / "dreszcz.json"

    # Open and load the JSON book file
    with open(book_path) as f:
        return json.load(f)


def roll_d6():
    """
    Simulate the roll of a 6-sided die (D6).

    Returns:
        int: A random integer between 1 and 6 (inclusive).
    """

    roll = random.randint(1, 6)
    top = "_______"
    line = "|       |"
    line_o_ = "|   " + Fore.BLACK + "●" + Style.RESET_ALL + "   |"
    lineo__ = "| " + Fore.BLACK + "●" + Style.RESET_ALL + "     |"
    line__o = "|     " + Fore.BLACK + "●" + Style.RESET_ALL + " |"
    lineo_o = "| " + Fore.BLACK + "●   ●" + Style.RESET_ALL + " |"
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

    lines = get_lines(roll)

    print("", top)
    for line in lines:
        print(line)
    print("", bottom)

    return roll


def roll_2d6():
    """
    Simulate the roll of two 6-sided dice (2D6) and calculate their sum.

    Returns:
        int: The sum of two random integers between 1 and 6 (inclusive).
    """

    left = random.randint(1, 6)
    right = random.randint(1, 6)
    top = "_______"
    line = "|       |"
    line_o_ = "|   " + Fore.BLACK + "●" + Style.RESET_ALL + "   |"
    lineo__ = "| " + Fore.BLACK + "●" + Style.RESET_ALL + "     |"
    line__o = "|     " + Fore.BLACK + "●" + Style.RESET_ALL + " |"
    lineo_o = "| " + Fore.BLACK + "●   ●" + Style.RESET_ALL + " |"
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

    return left + right


special = {
    '109': 'po !wygranej! 1 rundzie patrz 77 **po przegranej 163',
    '355': 'po pierwszej wygranej rundzie pytanie',
    '344': 'fireball',
    '309': 'zmiana broni po 1 rundzie',
    '238': 'dalej albo 316 albo 103',
}
