# src/ai/enhanced_ai.py
import random

class EnhancedAI:
    def __init__(self, name="AI_NPC"):
        self.name = name
        self.personality = random.choice(["cautious", "aggressive", "neutral"])
        self.trust_level = 5  # Scale 0-10
        self.suspicion_meter = {}  # Track suspicion for each player

    def decide_action(self, game_state):
        if game_state.get("phase") == "night":
            return self.night_strategy(game_state)
        else:
            return self.day_strategy(game_state)

    def night_strategy(self, game_state):
        if self.personality == "cautious":
            return "hide inside"
        elif self.personality == "aggressive":
            return "patrol area"
        else:
            return random.choice(["observe", "check defenses"])

    def day_strategy(self, game_state):
        suspicious_player = self.get_most_suspicious()
        if self.personality == "aggressive" and suspicious_player:
            return f"accuse {suspicious_player}"
        elif self.personality == "cautious":
            return "stay near crowd"
        return random.choice(["talk", "gather info", "idle"])

    def update_suspicion(self, player_id: str, amount: int):
        self.suspicion_meter[player_id] = self.suspicion_meter.get(player_id, 0) + amount

    def get_most_suspicious(self):
        if not self.suspicion_meter:
            return None
        return max(self.suspicion_meter.items(), key=lambda x: x[1])[0]
