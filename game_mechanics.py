import json
import pathlib
import random
from itertools import combinations

from character import Monster
from paragraph import Paragraph


def consume(hero, extra: bool = False) -> tuple[int, int]:
    """
    Heals the hero by consuming one food unit.

    Each unit of food restores 4 (or 5 if `extra=True`) stamina points,
    but not beyond the hero's max stamina.

    Args:
        hero: The Hero instance.
        extra (bool): If True, restores 5 points instead of 4.

    Returns:
        tuple[int, int]: (amount healed, remaining food units)

    TODO:
        In GUI version, use return values to show a visual effect or message.
    """
    value = 5 if extra else 4
    healed = 0

    if hero.inventory.food > 0:
        healed = min(value, hero.max_stamina - hero.stamina)
        hero.stamina += healed
        hero.inventory.food -= 1

    return healed, hero.inventory.food


def get_monsters(paragraph: Paragraph) -> list[Monster]:
    """
    Extracts monster data from a paragraph in the JSON book file.

    Looks for patterns like: NAME Z:6 W:4

    Args:
        paragraph (Paragraph): The paragraph object.

    Returns:
        list[Monster]: List of Monster objects found in the paragraph.

    TODO:
        Consider extending pattern to include additional attributes, e.g. type or effects.
    """
    words = paragraph.text.split(" ")
    monsters: list[Monster] = []
    # Find sequences like: NAME Z:x W:y
    index_nums = [i for i, word in enumerate(words) if word.isupper()]

    for i in range(len(index_nums) - 2):
        a, b, c = index_nums[i:i + 3]
        if a + 1 == b and b + 1 == c:
            name = words[a]
            if words[b].startswith("Z:") and words[c].startswith("W:"):
                try:
                    agility = int(words[b][2:])
                    stamina = int(words[c][2:])
                    monsters.append(Monster(name, agility, stamina))
                except ValueError:
                    pass  # silently skip malformed entries

    return monsters


def wanna_check_sss_input(value: str) -> bool | None:
    """
    Interprets user input for checking luck (SSS).

    Args:
        value (str): User input (e.g., "t", "n").

    Returns:
        bool | None: True if yes, False if no, None if invalid.

    This function is suitable for GUI use or unit testing.
    """
    value = value.strip().lower()
    if value == "t":
        return True
    elif value == "n":
        return False
    return None


def wanna_check_sss_cli(hero) -> bool:
    """
    CLI-only version of SSS prompt. Asks user interactively
    if they want to check their luck.

    Returns:
        bool: True or False based on user choice.
    """
    while True:
        print(f"Obecny poziom SZCZĘŚCIA wynosi {hero.luck}.")
        user_input = input("Chcesz sprawdzić swoje szczęście? [T]/[N]\n>>> ")
        result = wanna_check_sss_input(user_input)
        if result is not None:
            return result
        print(" * * * Zły znak * * * ")


def sss(hero) -> tuple[bool, int, int]:
    """
    Performs a Luck Test (Sprawdzian Swojego Szczęścia).

    Reduces hero's current luck by 1, rolls 2D6 and compares.

    Returns:
        tuple[bool, int, int]:
            - success (bool): Whether the test was successful.
            - rolled (int): The result of the 2D6 roll.
            - remaining_luck (int): Hero's updated luck value.

    TODO:
        In GUI, use returned values to show results visually.
    """
    hero.luck = max(0, hero.luck - 1)
    rolled = roll_2d6_cli()
    success = rolled <= hero.luck
    return success, rolled, hero.luck


def check_keys(key_a: int, key_b: int, key_c: int, target: int = 204) -> bool:
    """
    Checks if the given 3 keys add up to the target sum.

    Args:
        key_a (int): Value of key A.
        key_b (int): Value of key B.
        key_c (int): Value of key C.
        target (int): Required sum of the keys. Default is 204.

    Returns:
        bool: True if keys add up to target sum, False otherwise.

    TODO:
        Extend to allow more than 3 keys (optional).
    """
    return any(sum(combo) == target for combo in combinations([key_a, key_b, key_c], 3))


def resolve_combat_round(hero, monster, use_sss: bool = False) -> dict:
    """
    Resolves a single round of combat with optional luck check.

    Args:
        hero: The hero object.
        monster: The monster object.
        use_sss (bool): Whether hero wants to use luck to modify outcome.

    Returns:
        dict: {
            "result": "hero_win" | "monster_win" | "tie",
            "hero_roll": int,
            "monster_roll": int,
            "hero_attack": int,
            "monster_attack": int,
            "hero_stamina": int,
            "monster_stamina": int,
            "narrative": str,
            "sss_used": bool,
            "sss_success": bool | None,
            "sss_roll": int | None,
            "damage": int
        }
    """
    monster_roll = roll_2d6_cli()
    monster_attack = monster.attack_strength(monster_roll)

    hero_roll = roll_2d6_cli()
    hero_attack = hero.attack_strength(hero_roll)

    sss_used = False
    sss_success = None
    sss_roll = None
    damage = 0

    if hero_attack > monster_attack:
        result = "hero_win"
        if use_sss:
            sss_used = True
            sss_success, sss_roll, _ = sss(hero)
            if sss_success:
                damage = 4
            else:
                damage = 1
        else:
            damage = 2
        monster.take_damage(damage)
        narrative_text = get_narrative("hero")

    elif monster_attack > hero_attack:
        result = "monster_win"
        if use_sss:
            sss_used = True
            sss_success, sss_roll, _ = sss(hero)
            if sss_success:
                damage = 1
            else:
                damage = 3
        else:
            damage = 2
        hero.take_damage(damage)
        narrative_text = get_narrative("monster")

    else:
        result = "tie"
        narrative_text = get_narrative("tie")

    return {
        "monster_name": monster.name,
        "result": result,
        "hero_roll": hero_roll,
        "monster_roll": monster_roll,
        "hero_attack": hero_attack,
        "monster_attack": monster_attack,
        "hero_stamina": hero.stamina,
        "monster_stamina": monster.stamina,
        "narrative": narrative_text,
        "sss_used": sss_used,
        "sss_success": sss_success,
        "sss_roll": sss_roll,
        "damage": damage
    }


def combat_cli(story, cheat=False):
    story.monsters_killed_counter = 0
    story.bout = 1
    paragraph = story.book_raw[story.last_valid_chapter]
    monsters = get_monsters(paragraph)

    if not monsters:
        print("Nie ma z kim walczyć w tym paragrafie.")
        return

    while story.monsters_killed_counter < len(monsters):
        monster = monsters[story.monsters_killed_counter]

        # Jeśli potwór już pokonany w tym paragrafie
        if monster.name in story.hero.kills and \
                story.hero.kills[monster.name] == story.last_valid_chapter:
            print(f"{monster.name} już nieżyje!")
            story.monsters_killed_counter += 1
            continue

        if cheat:
            monster.stamina = 0
            story.hero.kills[monster.name] = story.last_valid_chapter
            story.monsters_killed_counter += 1
            continue

        # Główna pętla walki z jednym potworem
        while not story.hero.is_dead() and not monster.is_dead():
            print(f"\n{monster.name} — Runda {story.bout}")
            choice = input("[1] Atakuj  [2] Ucieczka  [3] Zmień broń  [0] Zakończ\n>>> ")

            if choice == "1":
                round_result = resolve_combat_round(story.hero, monster)
                print(round_result["narrative"])
                show_stamina(story.hero, monster)
                story.bout += 1
            elif choice == "2":
                paragraph = story.book_raw[story.last_valid_chapter]
                if can_escape(paragraph, story.bout, story.monsters_killed_counter):
                    use_luck = sss_check_cli(story.hero)
                    escape_result = process_escape(story.hero, True, use_luck)
                    print(escape_result["narrative"])
                    if escape_result["escaped"]:
                        return
                else:
                    print("Nie możesz teraz uciec!")
            elif choice == "3":
                print("Zmieniasz broń (jeszcze nie zaimplementowano)")
            elif choice == "0":
                story.quit_game()
            else:
                print("Nieprawidłowy wybór.")

        # Po walce
        if monster.is_dead():
            print(f"{monster.name} został pokonany!")
            story.hero.kills[monster.name] = story.last_valid_chapter
            story.monsters_killed_counter += 1
            story.bout = 1

        if story.hero.is_dead():
            story.game_over()
            return

    # Po wszystkich walkach
    story.main_menu(story.last_valid_chapter)


def process_escape(hero, can_escape: bool, use_sss: bool) -> dict:
    """
    Processes hero's attempt to escape from combat.

    Args:
        hero: Hero instance
        can_escape (bool): Whether escape is allowed in this round.
        use_sss (bool): Whether the player chose to use Luck check.

    Returns:
        dict: {
            "escaped": bool,
            "damage": int,
            "success": bool | None,
            "narrative": str
        }

    TODO:
        GUI can use the result to display summary and adjust HP bar.
    """
    if not can_escape:
        return {
            "escaped": False,
            "damage": 0,
            "success": None,
            "narrative": "Nie możesz teraz uciec, Śmiałku!"
        }

    # Używa SSS (szczęścia)
    if use_sss:
        success, rolled, remaining = sss(hero)
        if success:
            hero.take_damage(1)
            return {
                "escaped": True,
                "damage": 1,
                "success": True,
                "narrative": "Miałeś szczęście – uciekasz, tracąc tylko 1 punkt W."
            }
        else:
            hero.take_damage(3)
            return {
                "escaped": True,
                "damage": 3,
                "success": False,
                "narrative": "Masz pecha – uciekasz, ale z ciężką raną (-3 W)."
            }
    else:
        # Nie używa szczęścia
        hero.take_damage(2)
        return {
            "escaped": True,
            "damage": 2,
            "success": None,
            "narrative": "Uciekasz, ale potwór rani cię w plecy (-2 W)."
        }


# Cache narracji po załadowaniu
_NARRATIVES_CACHE = None


def get_narrative(character_type: str) -> str:
    """
    Returns a random narrative string for the given character type.

    Args:
        character_type (str): One of "hero", "monster", or "tie".

    Returns:
        str: Randomly selected narrative string.

    Raises:
        ValueError: If character_type is invalid or file missing.
    """
    global _NARRATIVES_CACHE

    if _NARRATIVES_CACHE is None:
        try:
            with open("narratives.json", encoding="utf-8") as f:
                _NARRATIVES_CACHE = json.load(f)
        except FileNotFoundError:
            raise ValueError("Nie znaleziono pliku narratives.json")

    if character_type not in _NARRATIVES_CACHE:
        raise ValueError(f"Nieznany typ narracji: {character_type}")

    return random.choice(_NARRATIVES_CACHE[character_type])


def narrative(character_type: str):
    """
    CLI wrapper for narrative printing.
    """
    print(get_narrative(character_type))


def sss_check_input(user_input: str) -> bool:
    """
    Interprets player's response to the SSS prompt.

    Args:
        user_input (str): User's input (e.g., 't', 'T', 'n').

    Returns:
        bool: True if user said yes, False otherwise.
    """
    return user_input.strip().lower() == "t"


def sss_check_cli(hero) -> bool:
    """
    CLI interface asking if the player wants to use SSS (Luck check).

    Returns:
        bool: True if player agrees, False otherwise.
    """
    while True:
        question = input(
            f"Twój aktualny poziom SZCZĘŚCIA wynosi {hero.luck}.\n"
            f"Czy chcesz Sprawdzić Swoje Szczęście? >>> [t/n]: "
        )
        if question.lower() in ("t", "n"):
            return sss_check_input(question)
        print("Nieprawidłowy wybór.")


def show_stamina(hero, monster) -> None:
    print(format_stamina(hero, monster))


def format_stamina(hero, monster) -> str:
    """
    Returns a formatted string showing current stamina values of hero and monster.

    Args:
        hero: Hero instance.
        monster: Monster instance.

    Returns:
        str: Formatted stamina summary.
    """
    return (
        f"{monster.name} W:{monster.stamina} vs. "
        f"{hero.name} W:{hero.stamina}"
    )


def can_escape(paragraph: Paragraph, bout: int, monsters_killed: int) -> bool:
    """
    Determines whether escape is allowed in the current context.

    Args:
        paragraph (Paragraph): The current paragraph.
        bout (int): Current round number.
        monsters_killed (int): Number of monsters already defeated in this combat.

    Returns:
        bool: True if escape is allowed, False otherwise.
    """
    rule = paragraph.escape_rule
    if rule:
        if not rule.get("enabled", False):
            return False

        max_round = rule.get("max_round")
        after_kill = rule.get("after_kill", False)

        # Ucieczka możliwa bez limitu rund
        if max_round is None:
            return True

        # Ucieczka możliwa do określonej rundy
        if bout <= max_round:
            return True

        # Ucieczka możliwa po pokonaniu przynajmniej jednego potwora
        if monsters_killed > 0 and after_kill:
            return True

        return False

    # fallback: analiza treści paragrafu
    return paragraph.can_escape


def open_book() -> dict[str, Paragraph]:
    path = pathlib.Path.cwd() / "shiver.json"
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    return {k: Paragraph(k, v) for k, v in raw.items()}

ESCAPE_RULES = {
    "2": {"enabled": True, "max_round": None, "after_kill": False},
    "32": {"enabled": False, "max_round": 0, "after_kill": False},
    "69": {"enabled": False, "max_round": 0, "after_kill": False},
    "92": {"enabled": True, "max_round": None, "after_kill": False},
    "98": {"enabled": False, "max_round": 0, "after_kill": False},
    "107": {"enabled": False, "max_round": 0, "after_kill": False},
    "109": {"enabled": False, "max_round": 0, "after_kill": False},
    "116": {"enabled": False, "max_round": 0, "after_kill": False},
    "157": {"enabled": True, "max_round": 1, "after_kill": False},
    "169": {"enabled": True, "max_round": 1, "after_kill": False},
    "184": {"enabled": True, "max_round": 2, "after_kill": False},
    "213": {"enabled": False, "max_round": 0, "after_kill": False},
    "216": {"enabled": False, "max_round": 0, "after_kill": False},
    "238": {"enabled": True, "max_round": 0, "after_kill": True},
    "255": {"enabled": False, "max_round": 0, "after_kill": False},
    "277": {"enabled": True, "max_round": 0, "after_kill": True},
    "288": {"enabled": False, "max_round": 0, "after_kill": False},
    "307": {"enabled": False, "max_round": 0, "after_kill": False},
    "309": {"enabled": True, "max_round": 1, "after_kill": False},
    "312": {"enabled": True, "max_round": 0, "after_kill": True},
    "317": {"enabled": False, "max_round": 0, "after_kill": False},
    "332": {"enabled": False, "max_round": 0, "after_kill": False},
    "341": {"enabled": False, "max_round": 0, "after_kill": False},
    "344": {"enabled": False, "max_round": 0, "after_kill": False},
    "355": {"enabled": False, "max_round": 0, "after_kill": False},
    "361": {"enabled": False, "max_round": 0, "after_kill": False},
    "367": {"enabled": False, "max_round": 0, "after_kill": False}
}


class BookAdapter:
    """
    Adapter umożliwiający używanie dict[str, Paragraph]
    jakby to był dict[str, str] – zwraca paragraph.text.

    Dodatkowo pozwala sięgnąć po cały obiekt Paragraph,
    jeśli zajdzie taka potrzeba.
    """

    def __init__(self, data: dict[str, 'Paragraph']):
        self._data = data

    def __getitem__(self, key: str) -> str:
        return self._data[key].text

    def get(self, key: str, default=None) -> str:
        para = self._data.get(key)
        return para.text if para else default

    def get_paragraph(self, key: str) -> 'Paragraph':
        """Zwraca oryginalny obiekt Paragraph."""
        return self._data[key]

    def __contains__(self, key: str) -> bool:
        return key in self._data

    def keys(self):
        return self._data.keys()

    def values(self):
        return (para.text for para in self._data.values())

    def items(self):
        return ((k, para.text) for k, para in self._data.items())


special = {
    '109': 'po !wygranej! 1 rundzie patrz 77 **po przegranej 163',
    '355': 'po pierwszej wygranej rundzie pytanie',
    '344': 'fireball',
    '309': 'zmiana broni po 1 rundzie',
    '238': 'dalej albo 316 albo 103',
}
