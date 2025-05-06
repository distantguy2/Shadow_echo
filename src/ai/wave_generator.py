# src/ai/wave_generator.py

import random
from typing import List, Dict

class WaveGenerator:
    def __init__(self):
        self.wave_number = 0
        self.base_hp = 30
        self.base_damage = 5
        self.monster_symbols = ["§", "¥", "※"]

    def generate_wave(self, player_count: int) -> List[Dict]:
        """
        Tạo một đợt quái vật dựa trên số người chơi và số đợt hiện tại.
        """
        self.wave_number += 1
        num_monsters = player_count + self.wave_number
        monsters = []

        for i in range(num_monsters):
            symbol = random.choice(self.monster_symbols)
            hp = self.base_hp + self.wave_number * 10 + random.randint(0, 10)
            damage = self.base_damage + self.wave_number + random.randint(0, 5)
            position = [random.randint(100, 800), random.randint(300, 500)]
            speed = random.uniform(0.5, 1.5)

            monster = {
                "symbol": symbol,
                "hp": hp,
                "damage": damage,
                "position": position,
                "speed": speed
            }
            monsters.append(monster)

        return monsters

    def reset(self):
        self.wave_number = 0
