import unittest
from unittest.mock import MagicMock

class MockParagraph:
    def __init__(self, text="Treść paragrafu", edges=None):
        self.text = text
        self.edges = edges or []

class MockShiver:
    def __init__(self):
        self.last_valid_chapter = "1"
        self.book_chapters = {"1": MockParagraph()}
        self.paragraph_shown = False
        self.commands_run = []

    def open_chapter(self, chapter):
        self.paragraph_shown = chapter == self.last_valid_chapter

    def handle_main_menu_command(self, cmd):
        self.commands_run.append(cmd)
        return cmd == "exit"

    def main_menu(self, replay_last_paragraph=False, input_func=input):
        if replay_last_paragraph:
            print("cd. ", end='')
            self.open_chapter(self.last_valid_chapter)

        while True:
            command = input_func(">>> ").strip()
            should_break = self.handle_main_menu_command(command)
            if should_break:
                break

# Test case
class TestMainMenuReplay(unittest.TestCase):
    def test_main_menu_replays_last_paragraph(self):
        # Arrange
        game = MockShiver()
        input_mock = MagicMock(side_effect=["exit"])  # simulate one input that causes exit

        # Act
        game.main_menu(replay_last_paragraph=True, input_func=input_mock)

        # Assert
        self.assertTrue(game.paragraph_shown)
        self.assertIn("exit", game.commands_run)

unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(TestMainMenuReplay))
