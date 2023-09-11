import unittest
import random
from _player import Dice


class TestDice(unittest.TestCase):
    def setUp(self):
        self.dice = Dice()

    def test_d1(self):
        random.seed(42)  # Set a seed for reproducibility
        result = self.dice.d1()
        self.assertIn(result, range(1, 7))

    def test_d1_is_different(self):
        random.seed(42)  # Set a seed for reproducibility
        results = set()

        for _ in range(100):  # Perform 100 rolls
            result = self.dice.d1()
            results.add(result)
        self.assertEqual(len(results), 6)  # There should be 6 unique results (1 through 6)

    def test_d2(self):
        random.seed(42)  # Set a seed for reproducibility
        result = self.dice.d2()
        self.assertIn(result, range(2, 13))


if __name__ == '__main__':
    unittest.main()
