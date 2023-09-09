from main import Game


class Paragraphs:
    def __init__(self):
        self.game = Game()
        self.text = ""
        self.goto = []

    @staticmethod
    def par01(self):
        self.text = self.game.show_paragraph("1")
        self.goto = self.game.get_new_paths("1")

    def par02(self):
        self.text = self.game.show_paragraph("2")
        self.goto = self.game.get_new_paths("2")
