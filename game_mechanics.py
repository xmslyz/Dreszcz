import json
import random


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


def get_monster_atributes(paragraph):
    with open("dreszcz.json") as f:
        book = json.load(f)
    prickle = book[paragraph].split(" ")

    index_nums = []
    for i, word in enumerate(prickle):
        if str(word).isupper():
            index_nums.append(i)

    monsters = []

    consecutive_lists = []
    for i in range(len(index_nums) - 2):
        if index_nums[i] + 1 == index_nums[i + 1] and index_nums[i + 1] + 1 == index_nums[i + 2]:
            consecutive_lists.append(index_nums[i: i + 3])

    for i in consecutive_lists:
        if prickle[i[1]].startswith("Z:") and prickle[
            i[2]
        ].startswith("W:"):
            monsters.append([paragraph, prickle[i[0]]])

    return monsters
