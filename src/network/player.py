# src/entities/player.py

from enum import Enum
from typing import List


class PlayerRole(Enum):
    PROTECTOR = "♕"
    TRAITOR = "♛"
    CHAOS = "☢"
    UNKNOWN = "?"

class Player:
    def __init__(self, id: int, name: str, role: PlayerRole = PlayerRole.UNKNOWN, hp: int = 100):
        self.id = id
        self.name = name
        self.role = role
        self.hp = hp
        self.cards: List[str] = []
        self.position = (100, 400)
        self.ready = False
        self.is_alive = True

    def take_damage(self, amount: int):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False

    def heal(self, amount: int):
        if self.is_alive:
            self.hp += amount
            if self.hp > 100:
                self.hp = 100

    def use_card(self, card_symbol: str):
        if card_symbol in self.cards:
            self.cards.remove(card_symbol)
            return True
        return False

    def add_card(self, card_symbol: str):
        self.cards.append(card_symbol)

    def __repr__(self):
        return f"<Player {self.name} ({self.role.value}) HP: {self.hp}>"
