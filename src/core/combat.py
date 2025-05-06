# src/core/combat.py - IMPROVED VERSION

import math
import random
from typing import List, Tuple, Optional
from ..core.entities import Player, Monster
from .skills import SKILL_LIBRARY
from ..utils.logger import setup_logger

logger = setup_logger("Combat")

class AutoCombatSystem:
    """Improved auto combat system with EXP sharing"""
    
    def __init__(self, game):
        self.game = game
        self.attack_timer = 0.0
        self.attack_interval = 1.5  # Attack every 1.5 seconds
        self.attack_range = 80.0
        self.attack_damage = 30
        self.last_attack_targets = {}  # Track last targets for each player
        
    def update(self, dt: float):
        """Update auto combat system"""
        self.attack_timer += dt
        
        if self.attack_timer >= self.attack_interval:
            self.attack_timer = 0.0
            self.perform_auto_attacks()
    
    def perform_auto_attacks(self):
        """Perform auto attacks for all players"""
        for player in self.game.players:
            if player.is_alive:
                # Get mouse direction for controlled player
                target_pos = self.get_attack_direction(player)
                
                # Find monster in direction
                target_monster = self.find_monster_in_range(player, target_pos)
                
                if target_monster:
                    self.execute_attack(player, target_monster)
                    self.last_attack_targets[player.id] = target_monster
                else:
                    # Fall back to nearest monster
                    nearest_monster = self.find_nearest_monster(player)
                    if nearest_monster and self.in_attack_range(player, nearest_monster):
                        self.execute_attack(player, nearest_monster)
                        self.last_attack_targets[player.id] = nearest_monster
    
    def get_attack_direction(self, player: Player) -> Tuple[float, float]:
        """Get attack direction based on player control"""
        if player.is_controlled:
            # Use mouse position for controlled player
            return self.game.mouse_pos if hasattr(self.game, 'mouse_pos') else (400, 300)
        else:
            # AI attacks in movement direction
            return (player.position[0] + 50, player.position[1])
    
    def find_monster_in_range(self, player: Player, target_pos: Tuple[float, float]) -> Optional[Monster]:
        """Find monster in attack direction cone"""
        px, py = player.position
        tx, ty = target_pos
        
        # Calculate attack direction vector
        dx = tx - px
        dy = ty - py
        length = math.sqrt(dx**2 + dy**2)
        
        if length == 0:
            return None
        
        # Normalize direction vector
        dx /= length
        dy /= length
        
        best_monster = None
        min_angle_diff = float('inf')
        
        for monster in self.game.monsters:
            if not monster.hp > 0:
                continue
            
            # Vector to monster
            mx, my = monster.position
            mdx = mx - px
            mdy = my - py
            mdist = math.sqrt(mdx**2 + mdy**2)
            
            if mdist > self.attack_range:
                continue
            
            # Normalize
            if mdist > 0:
                mdx /= mdist
                mdy /= mdist
            
            # Calculate angle between vectors
            dot_product = dx * mdx + dy * mdy
            angle_diff = math.acos(max(-1, min(1, dot_product)))
            
            # Check if monster is within 45-degree cone
            if angle_diff < math.pi/4 and angle_diff < min_angle_diff:
                min_angle_diff = angle_diff
                best_monster = monster
        
        return best_monster
    
    def execute_attack(self, player: Player, target) -> bool:
        """Execute attack and handle EXP sharing
        Returns True if attack was successful, False otherwise"""
        
        # Prevent attacking other players when auto-combat is active
        if isinstance(target, Player) or (hasattr(target, 'is_controlled') and self.game.auto_combat_active):
            logger.debug(f"Auto-combat blocked attack on player {target.name}")
            return False
        
        # Calculate attack angle for visuals
        angle = math.atan2(
            target.position[1] - player.position[1],
            target.position[0] - player.position[0]
        )
        
        # Create attack effect
        if hasattr(self.game, 'gameplay_enhancements'):
            self.game.gameplay_enhancements.create_attack_effect(
                player.position, angle, self.attack_range
            )
        
        # Calculate damage
        damage = self.attack_damage
        
        # Apply passive skill effects
        for skill in player.skills:
            if skill.skill_id == "blood_lust":
                # Blood Lust increases damage
                damage += damage * 0.2  # +20% damage
        
        # Deal damage
        target.hp -= damage
        
        # Create impact effect
        if hasattr(self.game, 'gameplay_enhancements'):
            self.game.gameplay_enhancements.create_impact_effect(target.position)
        
        # Handle monster death
        if target.hp <= 0:
            if isinstance(target, Monster):
                self.game.monsters.remove(target)
                
                # Trigger kill effects
                self.trigger_kill_effects(player)
                
                # Share EXP with nearby players
                exp_gained = 50  # Base EXP amount
                if hasattr(self.game, 'share_exp_with_nearby_players'):
                    self.game.share_exp_with_nearby_players(player, exp_gained)
                
                logger.info(f"Player {player.name} killed monster {target.symbol}")
            else:
                logger.warning(f"Player {player.name} attacked non-monster target")
                return False
        
        return True
    
    def trigger_kill_effects(self, player: Player):
        """Trigger on-kill skill effects"""
        for skill in player.skills:
            if skill.skill_id == "blood_lust":
                # Heal on kill
                skill_data = SKILL_LIBRARY.get("blood_lust")
                if skill_data:
                    heal_amount = skill_data.effect["heal_per_kill"][skill.level - 1]
                    player.hp = min(player.hp + heal_amount, player.max_hp)
                    self.game.ui_bridge.show_notification(
                        f"Blood Lust: {player.name} healed {heal_amount} HP", "success"
                    )
    
    # Utility methods
    def find_nearest_monster(self, player: Player) -> Optional[Monster]:
        """Find nearest monster to player"""
        nearest = None
        min_distance = float('inf')
        
        for monster in self.game.monsters:
            if not monster.hp > 0:
                continue
            
            distance = self.distance(player.position, monster.position)
            if distance < min_distance:
                min_distance = distance
                nearest = monster
        
        return nearest
    
    def in_attack_range(self, player: Player, monster: Monster) -> bool:
        """Check if monster is in attack range"""
        distance = self.distance(player.position, monster.position)
        return distance <= self.attack_range
    
    def distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """Calculate distance between two positions"""
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        return math.sqrt(dx**2 + dy**2)
