# src/game/events.py

import random
from enum import Enum, auto

# Xác định các loại sự kiện game có thể xảy ra
class GameEventType(Enum):
    MONSTER_ATTACK = auto()
    NPC_INTERACTION = auto()
    RESOURCE_FOUND = auto()
    CARD_DISCOVERED = auto()

# Định nghĩa class GameEvent để biểu diễn một sự kiện
class GameEvent:
    def __init__(self, event_type, description, payload=None):
        self.type = event_type
        self.description = description
        self.payload = payload or {}

    def to_dict(self):
        return {
            "type": self.type.name,
            "description": self.description,
            "payload": self.payload
        }

# Generator sinh sự kiện dựa trên phase hiện tại
class EventGenerator:
    def __init__(self, game_state):
        self.game_state = game_state

    def generate_event(self, phase):
        if phase == "DAY":
            return self._generate_day_event()
        elif phase == "NIGHT":
            return self._generate_night_event()
        return None

    def _generate_day_event(self):
        event_type = random.choice([
            GameEventType.RESOURCE_FOUND,
            GameEventType.CARD_DISCOVERED
        ])
        if event_type == GameEventType.RESOURCE_FOUND:
            return GameEvent(
                event_type,
                "You found a hidden resource!",
                {"resource": "wood", "amount": 1}
            )
        elif event_type == GameEventType.CARD_DISCOVERED:
            return GameEvent(
                event_type,
                "You discovered a mysterious card!",
                {"card_symbol": random.choice(["⎈", "✚", "🗺"])}
            )

    def _generate_night_event(self):
        event_type = random.choice([
            GameEventType.MONSTER_ATTACK,
            GameEventType.NPC_INTERACTION
        ])
        if event_type == GameEventType.MONSTER_ATTACK:
            return GameEvent(
                event_type,
                "A monster ambushes the area!",
                {"damage": random.randint(5, 15)}
            )
        elif event_type == GameEventType.NPC_INTERACTION:
            return GameEvent(
                event_type,
                "A suspicious NPC approaches you.",
                {"npc_id": random.randint(100, 999)}
            )
