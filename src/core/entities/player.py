# src/core/entities/player.py

from enum import Enum
from typing import List, Tuple, Optional


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
        self.true_role = role  # Thêm true_role để phù hợp với logic game
        self.hp = hp
        self.max_hp = hp
        self.cards: List[str] = []
        self.skills: List = []  # Thêm skills để phù hợp với skill system
        self.position = (100.0, 400.0)  # Dùng float để di chuyển mềm mại
        self.ready = False
        self.is_alive = True
        self.is_controlled = False  # Thêm để phân biệt player do người dùng điều khiển
        self.level = 1  # Thêm level cho hệ thống level up
        self.exp = 0
        self.clues = []  # Thêm để lưu trữ clues

    def take_damage(self, amount: int):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False

    def heal(self, amount: int):
        if self.is_alive:
            self.hp += amount
            if self.hp > self.max_hp:
                self.hp = self.max_hp

    def use_card(self, card_symbol: str):
        if card_symbol in self.cards:
            self.cards.remove(card_symbol)
            return True
        return False

    def add_card(self, card_symbol: str):
        self.cards.append(card_symbol)
        
    def add_exp(self, amount: int):
        """Thêm exp và level up nếu đủ điều kiện"""
        self.exp += amount
        if self.exp >= self.level * 100:
            self.exp = 0
            self.level += 1
            return True
        return False
        
    def add_clue(self, clue):
        """Thêm clue vào danh sách clues của player"""
        self.clues.append(clue)

    def __repr__(self):
        return f"<Player {self.name} ({self.role.value}) HP: {self.hp}/{self.max_hp} Lvl: {self.level}>"
