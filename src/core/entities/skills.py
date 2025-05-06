# src/core/entities/skills.py

from enum import Enum

class SkillType(Enum):
    PASSIVE = "passive"
    ACTIVE = "active"
    SUPPORT = "support"

class SkillCard:
    def __init__(self, skill_id, name, description, icon, type, cooldown=0, effect=None, max_level=5):
        self.id = skill_id
        self.name = name
        self.description = description
        self.icon = icon
        self.type = type
        self.cooldown = cooldown
        self.effect = effect or {}
        self.max_level = max_level

class PlayerSkill:
    def __init__(self, skill_id, level=1, cooldown=0):
        self.skill_id = skill_id
        self.level = level
        self.cooldown = cooldown
