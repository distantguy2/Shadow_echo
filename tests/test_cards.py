import unittest
import json
from src.systems.cards import CardManager

class TestCards(unittest.TestCase):
    def setUp(self):
        # Mock card data
        self.mock_data = {
            "universal_cards": {
                "⎈": {
                    "name": "Iron Axe",
                    "type": "weapon",
                    "day_effect": {"action": "damage_boost", "value": 20},
                    "night_effect": {"action": "break_barricade", "value": 1},
                    "rarity": "common"
                }
            },
            "role_cards": {},
            "boss_cards": {}
        }
        self.card_manager = CardManager(card_data=self.mock_data)

    def test_get_universal_card(self):
        card = self.card_manager.get_card("⎈")
        self.assertIsNotNone(card)
        self.assertEqual(card["name"], "Iron Axe")

    def test_card_effect_day(self):
        effect = self.card_manager.get_effect("⎈", time_of_day="day")
        self.assertEqual(effect["action"], "damage_boost")
        self.assertEqual(effect["value"], 20)

    def test_card_effect_night(self):
        effect = self.card_manager.get_effect("⎈", time_of_day="night")
        self.assertEqual(effect["action"], "break_barricade")
        self.assertEqual(effect["value"], 1)

if __name__ == '__main__':
    unittest.main()
