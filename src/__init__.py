# src/__init__.py
# Core components
from .core.game import Game
from .core.phase_manager import GamePhase  # Import từ phase_manager thay vì entities
from .core.entities import (
    Player, 
    Monster,
    SkillCard,
    PlayerSkill,
    PlayerRole,
    SkillType
)
from .core.skills import SKILL_LIBRARY
from .core.ui import SkillSelectUI
