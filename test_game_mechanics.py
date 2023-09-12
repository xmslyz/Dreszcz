import random
import unittest
from unittest import TestCase

import game_mechanics
import character


class TestDice(unittest.TestCase):

    def test_rolling_d6(self):
        random.seed(42)  # Set a seed for reproducibility
        result = game_mechanics.roll_d6()
        self.assertIn(result, range(1, 7))

    def test_if_each_rolling_of_d6_is_different(self):
        random.seed(42)  # Set a seed for reproducibility
        results = set()

        for _ in range(100):  # Perform 100 rolls
            result = game_mechanics.roll_d6()
            results.add(result)
        # There should be 6 unique results (1 through 6)
        self.assertEqual(len(results), 6)

    def test_rolling_2d6(self):
        random.seed(42)  # Set a seed for reproducibility
        result = game_mechanics.roll_2d6()
        self.assertIn(result, range(2, 13), result)

    def test_rolls_distribution(self):
        num_rolls = 10000  # Adjust the number of rolls as needed
        rolls = [game_mechanics.roll_d6() for _ in range(num_rolls)]

        # Calculate the mean and standard deviation
        mean = sum(rolls) / num_rolls
        std_deviation = (sum((x - mean) ** 2 for x in rolls) / num_rolls) ** 0.5

        # Assert that the mean is close to the expected mean (3.5)
        self.assertAlmostEqual(mean, 3.5, delta=0.1)

        # Assert that the standard deviation is close to the expected value
        # for a fair 6-sided die (about 1.71)
        self.assertAlmostEqual(std_deviation, 1.71, delta=0.1)


class TestMonsters(unittest.TestCase):
    def test_get_single_monster_attributes(self):
        monsters = game_mechanics.get_monster_attributes("2")
        expected_monster = character.Monster(
            "GARAZAN", 10, 10
        )

        # Check if there is at least one monster in the list
        self.assertGreaterEqual(len(monsters), 1)

        # Check if the first monster in the list
        # matches the expected monster's attributes
        if monsters:
            first_monster = monsters[0]
            self.assertEqual(first_monster.name, expected_monster.name)
            self.assertEqual(first_monster.agility, expected_monster.agility)
            self.assertEqual(first_monster.stamina, expected_monster.stamina)

    def test_get_multiply_monsters_atributes(self):
        monsters = game_mechanics.get_monster_attributes("312")
        expected_monsters = [
            ['LUDOJAD', 7, 5],
            ['ZOMBI', 6, 5],
            ['SZKIELET', 5, 4]
        ]

        # Check if there is three monsters in the list
        self.assertEqual(len(monsters), 3)

        # Check if the sample monsters from the list
        # match the expected monsters attributes
        if monsters:
            for i, monster in enumerate(monsters):
                name, agility, stamina = expected_monsters[i]
                sample_monster = character.Monster(name,
                                                   agility,
                                                   stamina)
                self.assertEqual(monster.name, sample_monster.name)
                self.assertEqual(monster.agility, sample_monster.agility)
                self.assertEqual(monster.stamina, sample_monster.stamina)

    def test_no_monster(self):
        no_monster = game_mechanics.get_monster_attributes("37")
        assertion = []
        self.assertEqual(no_monster, assertion)

    def test_similar_semantic(self):
        # "Jaką tarczę wybieras[z:] "
        no_monster = game_mechanics.get_monster_attributes("37")
        assertion = []
        self.assertEqual(no_monster, assertion)

    def test_all_monsters(self):
        all_monsters = {
            "GARAZAN": {"2": [10, 10]},
            "WILKOLUDY": {"32": [8, 7]},
            "UPIÓR": {"69": [5, 3]},
            "STRZYGA": {"69": [5, 4]},
            "MINOTAUR": {"92": [10, 10]},
            "GROBOK": {"98": [9, 8]},
            "BLACKTHORN": {"107": [10, 14],
                           "255": [10, 16],
                           "344": [10, 16],
                           "361": [8, 12]},
            "KROMAA": {"109": [7, 8]},
            "ORK": {"116": [6, 4],
                    "277": [7, 7]},
            "WILKOŁAK": {"157": [9, 6],
                         "216": [7, 6],
                         "309": [9, 6]},
            "DEMON": {"169": [8, 5],
                      "184": [7, 6]},
            "ROBALE": {"213": [7, 8]},
            "GREMLIN": {"238": [5, 3]},
            "LICHA": {"238": [6, 5]},
            "BRONGO": {"238": [8, 4]},
            "ORKONIK": {"238": [6, 4]},
            "SAMASKÓRA": {"238": [6, 5]},
            "WAMPIR": {"277": [9, 7]},
            "NIETOPERZ": {"288": [7, 6]},
            "JASZCZURY": {"307": [7, 6],
                          "341": [7, 6]},
            "LUDOJAD": {"312": [7, 5]},
            "ZOMBI": {"312": [6, 5]},
            "SZKIELET": {"312": [5, 4]},
            "OGRE": {"317": [8, 10]},
            "TROLL": {"332": [8, 8]},
            "GIGANT": {"355": [10, 12]},
            "ZŁY": {"367": [6, 6]}
        }

        new_monsters = {}
        for monster, attributes in all_monsters.items():
            for key, values in attributes.items():
                if key not in new_monsters:
                    new_monsters[key] = []
                new_monsters[key].append([monster] + values)

        for paragraph in new_monsters.keys():
            # extract monsters from paraghaph
            monsters = game_mechanics.get_monster_attributes(paragraph)

            # for each monster
            for i, monster in enumerate(monsters):
                # creates sample monster
                name, agility, stamina = new_monsters[paragraph][i]
                sample_monster = character.Monster(name,
                                                   agility,
                                                   stamina)

                if monster.name == sample_monster.name:
                    self.assertEqual(monster.agility, sample_monster.agility)
                    self.assertEqual(monster.stamina, sample_monster.stamina)


class TestKeysChecker(TestCase):
    def test_good_combination(self):
        key_a, key_b, key_c = 12, 122, 70
        self.assertTrue(game_mechanics.check_keys(key_a, key_b, key_c))

    def test_bad_combination(self):
        bad_combinations = [
            [12, 45, 93],
            [12, 45, 122],
            [12, 45, 70],
            [12, 93, 122],
            [12, 93, 70],
            [45, 93, 122],
            [45, 93, 70],
            [93, 122, 70]
        ]
        for combination in bad_combinations:
            a, b, c = combination
            self.assertFalse(game_mechanics.check_keys(a, b, c))


if __name__ == '__main__':
    unittest.main()
