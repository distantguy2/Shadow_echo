# src/game/state.py

from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

@dataclass
class PlayerState:
    id: str
    name: str
    hp: int = 100
    role: Optional[str] = None
    position: Tuple[int, int] = (0, 0)
    cards: List[str] = field(default_factory=list)
    alive: bool = True

@dataclass
class MonsterState:
    symbol: str
    hp: int
    damage: int
    position: Tuple[int, int]
    speed: float

@dataclass
class GameState:
    phase: str = "preparation"  # Options: preparation, day, night, end
    day_count: int = 0
    time_left: int = 60
    players: Dict[str, PlayerState] = field(default_factory=dict)
    monsters: List[MonsterState] = field(default_factory=list)
    npcs: List[dict] = field(default_factory=list)
    results: List[str] = field(default_factory=list)

    def reset(self):
        self.phase = "preparation"
        self.day_count = 0
        self.time_left = 60
        self.players.clear()
        self.monsters.clear()
        self.npcs.clear()
        self.results.clear()
