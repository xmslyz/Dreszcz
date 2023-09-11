import random
import unittest

import game_mechanics


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


class Test(unittest.TestCase):
    def test_get_single_monster_atributes(self):
        monsters = game_mechanics.get_monster_atributes("2")
        assertion = ["2", "GARAZAN"]
        self.assertEqual(monsters[0], assertion)

    def test_get_multiply_monsters_atributes(self):
        monsters = game_mechanics.get_monster_atributes("312")
        assertion = [
            ['312', 'LUDOJAD'],
            ['312', 'ZOMBI'],
            ['312', 'SZKIELET']
        ]
        self.assertEqual(monsters, assertion)

    def test_no_monster(self):
        no_monster = game_mechanics.get_monster_atributes("37")
        assertion = []
        self.assertEqual(no_monster, assertion)

    def test_similar_semantic(self):
        # "Jaką tarczę wybieras[z:] "
        no_monster = game_mechanics.get_monster_atributes("37")
        assertion = []
        self.assertEqual(no_monster, assertion)


if __name__ == '__main__':
    unittest.main()
