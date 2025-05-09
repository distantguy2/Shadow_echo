# src/core/entities.py

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List


class PlayerRole(Enum):
    UNKNOWN = auto()
    PROTECTOR = auto()
    TRAITOR = auto()
    CHAOS = auto()


class SkillType(Enum):
    PASSIVE = "passive"
    ACTIVE = "active"
    SUPPORT = "support"


@dataclass
class Player:
    id: int
    name: str
    position: List[float] = field(default_factory=lambda: [0.0, 0.0])
    is_alive: bool = True
    is_controlled: bool = False
    level: int = 1
    exp: int = 0
    role: PlayerRole = PlayerRole.UNKNOWN
    true_role: PlayerRole = PlayerRole.UNKNOWN
    alignment: "AlignmentSystem" = None
    clues: List[str] = field(default_factory=list)
    cards: List[str] = field(default_factory=list)
    card_options: List[dict] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)

    def add_exp(self, amount: int):
        self.exp += amount
        level_up_threshold = self.level * 100
        while self.exp >= level_up_threshold:
            self.exp -= level_up_threshold
            self.level += 1
            level_up_threshold = self.level * 100


@dataclass
class Card:
    id: str
    name: str
    type: str
    description: str
    effect: dict = field(default_factory=dict)
    icon: str = "?"
    is_new: bool = False
    symbol: str = "?"
    
    # Additional fields for character cards
    character_id: str = None
    passive_skill: dict = field(default_factory=dict)
    potential_roles: List[str] = field(default_factory=list)
    
    # Additional fields for role cards
    role_id: str = None
    special_ability: dict = field(default_factory=dict)
    victory_condition: str = ""


@dataclass
class SkillCard:
    skill_id: str  # <- sửa lại tên trường này từ `id` thành `skill_id`
    name: str
    description: str
    icon: str
    type: SkillType
    cooldown: float = 0
    level: int = 1
    max_level: int = 5
    effect: dict = field(default_factory=dict)


class AlignmentSystem:
    """Tracks hidden alignment and suspicion for a player."""

    def __init__(self):
        self.trust = 0.5  # Neutral at start
        self.suspicion = 0.0
        self.loyalty = 0.5
        self.chaos = 0.0

    def adjust(self, trust_delta=0.0, suspicion_delta=0.0, loyalty_delta=0.0, chaos_delta=0.0):
        self.trust = min(max(self.trust + trust_delta, 0.0), 1.0)
        self.suspicion = min(max(self.suspicion + suspicion_delta, 0.0), 1.0)
        self.loyalty = min(max(self.loyalty + loyalty_delta, 0.0), 1.0)
        self.chaos = min(max(self.chaos + chaos_delta, 0.0), 1.0)
