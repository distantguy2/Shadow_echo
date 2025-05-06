import unittest
from src.entities.player import Player
from src.systems.commands import CommandProcessor

class TestCommands(unittest.TestCase):
    def setUp(self):
        self.player = Player(id=1, name="Tester", hp=100, role="♛")
        self.processor = CommandProcessor()

    def test_valid_build_command(self):
        result = self.processor.process(self.player, "build barricade --pos=gate")
        self.assertIn("built", result)

    def test_valid_use_command(self):
        self.player.cards.append("✚")
        result = self.processor.process(self.player, "use ✚ --target=self")
        self.assertIn("used", result)

    def test_invalid_command(self):
        result = self.processor.process(self.player, "fly to moon")
        self.assertIn("Unknown command", result)

    def test_scan_command(self):
        result = self.processor.process(self.player, "scan area")
        self.assertIn("scanning", result)

if __name__ == '__main__':
    unittest.main()
