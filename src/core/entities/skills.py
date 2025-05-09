# src/core/entities/skills.py

import random
from enum import Enum

class SkillType(Enum):
    PASSIVE = "passive"
    ACTIVE = "active"
    SUPPORT = "support"
    BASIC = "basic"
    UPGRADED = "upgraded"

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

# Base Skill class for new system
class Skill:
    """Base class for all skills"""
    def __init__(self, level=1):
        self.level = level
        self.name = "Base Skill"
        self.type = SkillType.BASIC
        self.cooldown = 0
        self.current_cooldown = 0
    
    def activate(self, user, target_position):
        """Activate the skill"""
        raise NotImplementedError("Subclasses must implement activate()")
    
    def is_ready(self):
        """Check if skill is ready to use"""
        return self.current_cooldown <= 0
    
    def update(self, dt):
        """Update skill cooldown"""
        if self.current_cooldown > 0:
            self.current_cooldown -= dt
    
    def get_description(self):
        """Get skill description"""
        return f"{self.name} (Level {self.level})"


# Echo Strike skill implementation
class EchoStrike(Skill):
    def __init__(self, level=1):
        super().__init__(level)
        # Base stats
        self.name = "Echo Strike"
        self.base_damage = 25 + (level * 15)  # Base damage
        self.cooldown = 8 - (level * 0.5)     # Cooldown time (seconds)
        self.area_size = 2 + (level * 0.2)    # Effect area size
        self.crit_rate = 0.05 + (level * 0.03) # Critical hit rate
        self.projectile_count = 1 + (level // 2) # Number of projectiles
        
        # Skill-specific properties
        self.echo_duration = 2.0  # Duration of echo effect in seconds

    def activate(self, user, target_position):
        """Activate Echo Strike skill"""
        if not self.is_ready():
            return None
            
        self.current_cooldown = self.cooldown
        actual_damage = self.calculate_damage()
        
        return {
            "type": "echo_wave",
            "source": user,
            "damage": actual_damage,
            "position": target_position,
            "radius": self.area_size,
            "projectiles": self.projectile_count,
            "duration": self.echo_duration,
            "effect": "echo_resonance",
            "description": "Tạo ra sóng âm tại vị trí mục tiêu, gây sát thương cho kẻ địch và để lại dư chấn"
        }

    def calculate_damage(self):
        """Calculate actual damage with critical hit chance"""
        is_critical = random.random() < self.crit_rate
        damage_multiplier = 2.0 if is_critical else 1.0
        return self.base_damage * damage_multiplier

    def get_description(self):
        """Get detailed skill description"""
        return (f"Echo Strike (Cấp {self.level}): Phóng ra {self.projectile_count} sóng âm "
                f"gây {self.base_damage} sát thương trong phạm vi {self.area_size}m. "
                f"Tỉ lệ chí mạng: {(self.crit_rate * 100):.1f}%. Hồi chiêu: {self.cooldown}s.")


# Void Resonance (upgraded Echo Strike) implementation
class VoidResonance(EchoStrike):
    def __init__(self, level=5):
        super().__init__(level)
        # Override base stats
        self.name = "Void Resonance"
        self.type = SkillType.UPGRADED
        self.base_damage = 50 + (level * 25)    # Enhanced base damage
        self.cooldown = 6 - (level * 0.4)       # Reduced cooldown
        self.area_size = 3 + (level * 0.3)      # Enlarged area
        self.crit_rate = 0.15 + (level * 0.04)  # Enhanced crit rate
        self.projectile_count = 3 + (level // 2) # More projectiles
        
        # Special properties of Void Resonance
        self.echo_count = 2          # Number of echoes
        self.echo_delay = 0.8        # Delay between echoes (seconds)
        self.echo_multiplier = 0.6   # Damage multiplier for each echo
        self.echo_duration = 3.0     # Extended echo duration

    def activate(self, user, target_position):
        """Activate Void Resonance skill"""
        main_strike = super().activate(user, target_position)
        if not main_strike:
            return None
            
        main_strike["type"] = "void_resonance"
        main_strike["effect"] = "void_echo"
        main_strike["description"] = f"Tạo ra sóng hư không gây sát thương và dội lại {self.echo_count} lần"
        main_strike["extra_effects"] = {
            "echo_count": self.echo_count,
            "echo_delay": self.echo_delay,
            "echo_multiplier": self.echo_multiplier,
            "duration": self.echo_duration
        }
        
        return main_strike

    def get_description(self):
        """Get detailed skill description"""
        return (f"Void Resonance (Cấp {self.level}): Phóng ra {self.projectile_count} sóng hư không "
                f"gây {self.base_damage} sát thương trong phạm vi {self.area_size}m. "
                f"Sóng dội lại {self.echo_count} lần, mỗi lần gây {(self.echo_multiplier * 100):.0f}% sát thương. "
                f"Tỉ lệ chí mạng: {(self.crit_rate * 100):.1f}%. Hồi chiêu: {self.cooldown}s.")