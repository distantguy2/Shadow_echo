# src/core/entities/game_phase.py

from enum import Enum

class GamePhase(Enum):
    PREPARATION = "Preparation"
    DAY = "Day"
    NIGHT = "Night"
    SKILL_SELECT = "SkillSelect"
    END = "End"
