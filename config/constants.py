from enum import Enum

class PlayerRole(Enum):
    UNKNOWN = "?"
    PROTECTOR = "♕"
    TRAITOR = "♛"
    CHAOS = "☢"

class GamePhase(Enum):
    PREPARATION = "preparation"
    DAY = "day"
    NIGHT = "night"
    SKILL_SELECT = "skill_select"
    END = "end"
