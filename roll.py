import random

from colorama import Fore, Style

def roll_d6_raw() -> int:
    """Returns a random int from 1 to 6 without any output."""
    return random.randint(1, 6)


def roll_2d6_raw() -> tuple[int, int]:
    """Returns two random ints (1–6 each), representing 2D6."""
    return random.randint(1, 6), random.randint(1, 6)


def roll_d6_cli() -> int:
    roll = roll_d6_raw()
    _print_d6_graphic(roll)
    return roll


def roll_2d6_cli() -> int:
    left, right = roll_2d6_raw()
    _print_d6_double_graphic(left, right)
    return left + right


def _print_d6_graphic(value: int) -> None:
    """
    Prints an ASCII graphic of a single D6 die.

    Args:
        value (int): Rolled value from 1 to 6.
    """
    top = "_______"
    line = "|       |"
    line_o_ = "|   " + Fore.BLACK + "●" + Style.RESET_ALL + "   |"
    lineo__ = "| " + Fore.BLACK + "●" + Style.RESET_ALL + "     |"
    line__o = "|     " + Fore.BLACK + "●" + Style.RESET_ALL + " |"
    lineo_o = "| " + Fore.BLACK + "●   ●" + Style.RESET_ALL + " |"
    bottom = "‾‾‾‾‾‾‾"

    def get_lines(v):
        match v:
            case 1:
                return [line, line_o_, line]
            case 2:
                return [lineo__, line, line__o]
            case 3:
                return [lineo__, line_o_, line__o]
            case 4:
                return [lineo_o, line, lineo_o]
            case 5:
                return [lineo_o, line_o_, lineo_o]
            case 6:
                return [lineo_o, lineo_o, lineo_o]
            case _:
                return [line, line, line]

    print("", top)
    for ln in get_lines(value):
        print(ln)
    print("", bottom)


def _print_d6_double_graphic(left: int, right: int) -> None:
    """
    Prints two D6 dice side by side using ASCII graphics.

    Args:
        left (int): First die roll.
        right (int): Second die roll.
    """
    top = "_______"
    line = "|       |"
    line_o_ = "|   " + Fore.BLACK + "●" + Style.RESET_ALL + "   |"
    lineo__ = "| " + Fore.BLACK + "●" + Style.RESET_ALL + "     |"
    line__o = "|     " + Fore.BLACK + "●" + Style.RESET_ALL + " |"
    lineo_o = "| " + Fore.BLACK + "●   ●" + Style.RESET_ALL + " |"
    bottom = "‾‾‾‾‾‾‾"

    def get_lines(v):
        match v:
            case 1:
                return [line, line_o_, line]
            case 2:
                return [lineo__, line, line__o]
            case 3:
                return [lineo__, line_o_, line__o]
            case 4:
                return [lineo_o, line, lineo_o]
            case 5:
                return [lineo_o, line_o_, lineo_o]
            case 6:
                return [lineo_o, lineo_o, lineo_o]
            case _:
                return [line, line, line]

    left_lines = get_lines(left)
    right_lines = get_lines(right)

    print("", top, "  ", top)
    for l, r in zip(left_lines, right_lines):
        print(l, "", r)
    print("", bottom, "  ", bottom)