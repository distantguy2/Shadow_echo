import unittest
from src.entities.player import Player
from src.entities.monster import Monster
from src.systems.combat import CombatSystem

class TestCombat(unittest.TestCase):
    def setUp(self):
        self.player = Player(id=1, name="Hero", hp=100, role="♕")
        self.monster = Monster(symbol="§", hp=50, damage=15, position=(100, 100), speed=1)
        self.combat = CombatSystem()

    def test_player_attack_monster(self):
        result = self.combat.attack(self.player, self.monster)
        self.assertIn("attacked", result)
        self.assertLess(self.monster.hp, 50)

    def test_monster_attack_player(self):
        result = self.combat.monster_attack(self.monster, self.player)
        self.assertIn("hit", result)
        self.assertLess(self.player.hp, 100)

    def test_monster_defeated(self):
        self.monster.hp = 5
        result = self.combat.attack(self.player, self.monster)
        self.assertIn("defeated", result)
        self.assertLessEqual(self.monster.hp, 0)

if __name__ == '__main__':
    unittest.main()
