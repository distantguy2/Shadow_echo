# File: src/core/entities/weapons.py

import random
import math
from enum import Enum

class WeaponType(Enum):
    AREA_ATTACK = "area_attack"
    RANGED_ATTACK = "ranged_attack"
    EFFECT = "effect"
    SUMMON = "summon"

class Weapon:
    """Base class for all weapons in Swarm mode"""
    def __init__(self, level=1):
        self.level = level
        self.name = "Base Weapon"
        self.type = WeaponType.RANGED_ATTACK
        self.cooldown = 0
        self.current_cooldown = 0
        self.is_upgraded = False
        self.upgrade_condition = None
        self.upgrade_threshold = 0
        
    def activate(self, user, target_position):
        """Activate the weapon"""
        raise NotImplementedError("Subclasses must implement activate()")
    
    def is_ready(self):
        """Check if weapon is ready to use"""
        return self.current_cooldown <= 0
    
    def update(self, dt):
        """Update weapon cooldown"""
        if self.current_cooldown > 0:
            self.current_cooldown -= dt
    
    def can_upgrade(self, player_stats):
        """Check if weapon can be upgraded"""
        if self.level < 5 or self.is_upgraded:
            return False
            
        if self.upgrade_condition is None:
            return False
            
        condition_value = player_stats.get(self.upgrade_condition, 0)
        return condition_value >= self.upgrade_threshold
    
    def upgrade(self):
        """Upgrade the weapon"""
        raise NotImplementedError("Subclasses must implement upgrade()")
    
    def get_description(self):
        """Get weapon description"""
        return f"{self.name} (Level {self.level})"


# Example implementation of Ani-Mines weapon
class AniMines(Weapon):
    def __init__(self, level=1):
        super().__init__(level)
        self.name = "Ani-Mines"
        self.type = WeaponType.AREA_ATTACK
        
        # Base stats
        self.base_damage = 35 + (level * 20)
        self.cooldown = 10 - (level * 0.7)
        self.area_size = 2.5 + (level * 0.3)
        self.mine_count = 1 + (level // 2)
        
        # Upgrade requirements
        self.upgrade_condition = "area_size"
        self.upgrade_threshold = 5.0
        
    def activate(self, user, target_position):
        """Place mines at target position"""
        if not self.is_ready():
            return None
            
        self.current_cooldown = self.cooldown
        
        # Calculate positions for multiple mines
        mine_positions = [target_position]
        if self.mine_count > 1:
            for i in range(1, self.mine_count):
                # Calculate offset positions
                angle = random.uniform(0, 2 * 3.14159)
                distance = random.uniform(1, 2)
                offset_x = distance * math.cos(angle)
                offset_y = distance * math.sin(angle)
                mine_positions.append((target_position[0] + offset_x, target_position[1] + offset_y))
        
        result = {
            "type": "mine_placement",
            "source": user,
            "damage": self.base_damage,
            "positions": mine_positions,
            "radius": self.area_size,
            "count": self.mine_count,
            "effect": "explosion",
            "description": "Đặt mìn gây sát thương diện rộng khi kẻ địch đi qua"
        }
        
        return result
    
    def upgrade(self):
        """Upgrade to Jinx's Tri-Namite"""
        if self.is_upgraded:
            return False
            
        return JinxTriNamite(self.level)
    
    def get_description(self):
        """Get detailed weapon description"""
        return (f"Ani-Mines (Cấp {self.level}): Đặt {self.mine_count} mìn gây "
                f"{self.base_damage} sát thương trong phạm vi {self.area_size}m. "
                f"Hồi chiêu: {self.cooldown}s.")


# Upgraded version of Ani-Mines
class JinxTriNamite(AniMines):
    def __init__(self, level=5):
        super().__init__(level)
        # Override base properties
        self.name = "Jinx's Tri-Namite"
        self.is_upgraded = True
        
        # Enhanced stats
        self.base_damage = 70 + (level * 25)
        self.cooldown = 8 - (level * 0.5)
        self.area_size = 3.5 + (level * 0.4)
        self.mine_count = 3 + (level // 2)
        
        # Special properties
        self.fragment_count = 6
        self.fragment_damage = self.base_damage * 0.3
        
    def activate(self, user, target_position):
        """Place tri-mines at target position"""
        result = super().activate(user, target_position)
        if not result:
            return None
            
        result["type"] = "tri_namite"
        result["effect"] = "tri_explosion"
        result["description"] = "Đặt mìn ba nhánh gây sát thương lớn và bắn văng mảnh vỡ"
        result["extra_effects"] = {
            "fragment_count": self.fragment_count,
            "fragment_damage": self.fragment_damage
        }
        
        return result
    
    def get_description(self):
        """Get detailed weapon description"""
        return (f"Jinx's Tri-Namite (Cấp {self.level}): Đặt {self.mine_count} mìn ba nhánh gây "
                f"{self.base_damage} sát thương trong phạm vi {self.area_size}m. "
                f"Phát nổ tạo {self.fragment_count} mảnh vỡ, mỗi mảnh gây {self.fragment_damage} sát thương. "
                f"Hồi chiêu: {self.cooldown}s.")