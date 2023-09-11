import random


def roll_d6():
    return random.randint(1, 6)


def roll_2d6():
    return roll_d6() + roll_d6()
