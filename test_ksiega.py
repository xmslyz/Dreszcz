import unittest

from sprawdz_ksiege import check_book, load_book


class TestKsiega(unittest.TestCase):
    def setUp(self):
        self.problems = check_book(load_book())

    def test_kazdy_paragraf_ma_przejscia(self):
        self.assertNotIn("bez_przejsc", self.problems)

    def test_wszystkie_cele_istnieja(self):
        self.assertNotIn("brakujace_cele", self.problems)


if __name__ == "__main__":
    unittest.main()
