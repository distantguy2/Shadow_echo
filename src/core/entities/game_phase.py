# src/core/entities/game_phase.py

from enum import Enum

class GamePhase(Enum):
    # Menu phases
    MENU = "Menu"
    CHARACTER_SELECT = "CharacterSelect"
    
    # Standard game phases
    PREPARATION = "Preparation"
    DAY = "Day"
    NIGHT = "Night"
    SKILL_SELECT = "SkillSelect"
    
    # Swarm mode specific phases
    SWARM_PREPARATION = "SwarmPreparation"
    SWARM_DAY = "SwarmDay"
    SWARM_NIGHT = "SwarmNight"
    ROLE_REVEAL = "RoleReveal"
    
    # Special events
    SPECIAL_EVENT = "SpecialEvent"
    BOSS_ENCOUNTER = "BossEncounter"
    
    # End phases
    END = "End"
    GAME_OVER = "GameOver"