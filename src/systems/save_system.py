# src/systems/save_system.py
import json
import os
from datetime import datetime
from dataclasses import asdict

class SaveSystem:
    def __init__(self, save_dir="data/saves"):
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

    def save_game(self, game_state, slot=1):
        save_data = {
            "timestamp": datetime.now().isoformat(),
            "day": game_state.day_count,
            "phase": game_state.phase,
            "players": [asdict(p) for p in game_state.players.values()],
            "monsters": [asdict(m) for m in game_state.monsters],
            "npcs": game_state.npcs,
            "results": game_state.results
        }

        save_file = os.path.join(self.save_dir, f"save_{slot}.json")
        with open(save_file, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)

    def load_game(self, slot=1):
        save_file = os.path.join(self.save_dir, f"save_{slot}.json")
        if not os.path.exists(save_file):
            return None

        with open(save_file, "r", encoding="utf-8") as f:
            save_data = json.load(f)

        return save_data
