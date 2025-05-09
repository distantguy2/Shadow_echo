# src/core/entities/player.py

from enum import Enum
import random
from typing import List, Tuple, Optional, Dict, Any


class PlayerRole(Enum):
    PROTECTOR = "♕"
    TRAITOR = "♛"
    CHAOS = "☢"
    UNKNOWN = "?"


class Player:
    def __init__(self, id: int, name: str, role: PlayerRole = PlayerRole.UNKNOWN, hp: int = 100):
        # Basic attributes
        self.id = id
        self.name = name
        self.role = role
        self.true_role = role  # Hidden true role that player doesn't know initially
        self.known_role = False  # Whether player has discovered their role
        self.hp = hp
        self.max_hp = hp
        self.is_alive = True
        self.is_controlled = False  # Whether this player is controlled by the user
        
        # Position and movement
        self.position = (100.0, 400.0)  # Use float for smooth movement
        self.ready = False
        
        # Character and skills
        self.character_id = None  # Character selected by player
        self.passive_skill = None  # Character's passive skill
        self.level = 1
        self.exp = 0
        
        # Inventory
        self.cards: List[str] = []  # Weapon/item cards
        self.active_weapons: List = []  # Equipped weapons
        self.max_weapons = 4  # Maximum weapons player can equip
        self.clues = []  # Clues discovered
        self.skills = []  # Player skills

        # Stats (modified by character, skills, and items)
        self.stats = {
            "damage": 10,
            "cooldown_reduction": 0,
            "area_size": 1.0,
            "crit_rate": 0.05,
            "projectile_count": 1,
            "max_health": 100,
            "movement_speed": 5,
            "armor": 0,
            "effect_duration": 1.0,
            "pickup_radius": 1.5,
            "health_regen": 0,
            "exp_bonus": 0
        }

    def set_character(self, character_id: str, character_data: Dict[str, Any], skill_registry=None):
        """Set character and initialize passive skill"""
        self.character_id = character_id

        # Initialize character-specific attributes
        if 'passive_skill' in character_data:
            if skill_registry:
                # Use skill registry to create the skill object
                skill_id = character_data['passive_skill']['id']
                self.passive_skill = skill_registry.create_skill(skill_id, level=1)

                # Set the owner of the skill
                if self.passive_skill:
                    self.passive_skill.owner = self

                    # Log successful skill initialization
                    print(f"Character {character_id} initialized with passive skill: {skill_id}")
                else:
                    # Fallback if skill creation failed
                    print(f"WARNING: Failed to create passive skill {skill_id} for character {character_id}")
            else:
                # Log warning if skill_registry is not provided
                print(f"WARNING: skill_registry not provided for character {character_id}, passive skill not initialized")
    
    def assign_role(self, role_id: str, role_data: Dict[str, Any], skill_registry=None):
        """Assign a role to player (but player doesn't know yet)"""
        # Validate role assignment if skill registry is provided
        if skill_registry and self.character_id:
            valid_roles = skill_registry.get_potential_roles_for_character(self.character_id)
            if role_id not in valid_roles:
                # Role not valid for this character, use a fallback valid role
                if valid_roles:
                    # Choose first valid role from potential roles
                    role_id = valid_roles[0]
                else:
                    # Default to protector if no valid roles
                    role_id = "protector"
        
        # Set the role based on validated role_id
        if role_id == "protector":
            self.true_role = PlayerRole.PROTECTOR
        elif role_id == "traitor":
            self.true_role = PlayerRole.TRAITOR
        elif role_id == "chaos":
            self.true_role = PlayerRole.CHAOS
        else:
            self.true_role = PlayerRole.UNKNOWN
            
        self.role = PlayerRole.UNKNOWN  # Player starts without knowing their role
        self.known_role = False
        
        return role_id  # Return the final role ID that was assigned
        
    def discover_role(self):
        """Player discovers their role"""
        self.role = self.true_role
        self.known_role = True
        return self.role
        
    def take_damage(self, amount: int):
        """Take damage, accounting for armor"""
        # Apply armor reduction if any
        if "armor" in self.stats:
            reduced_amount = max(1, amount - self.stats["armor"])
            self.hp -= reduced_amount
        else:
            self.hp -= amount
            
        if self.hp <= 0:
            self.hp = 0
            self.is_alive = False

    def heal(self, amount: int):
        """Heal the player"""
        if self.is_alive:
            self.hp += amount
            if self.hp > self.max_hp:
                self.hp = self.max_hp

    def add_weapon(self, weapon):
        """Add a weapon to player's arsenal"""
        if len(self.active_weapons) >= self.max_weapons:
            return False
            
        self.active_weapons.append(weapon)
        return True
        
    def remove_weapon(self, weapon_index: int):
        """Remove a weapon from player's arsenal"""
        if 0 <= weapon_index < len(self.active_weapons):
            self.active_weapons.pop(weapon_index)
            return True
        return False
    
    def use_card(self, card_symbol: str):
        """Use a card from inventory"""
        if card_symbol in self.cards:
            self.cards.remove(card_symbol)
            return True
        return False

    def add_card(self, card_symbol: str):
        """Add a card to inventory"""
        self.cards.append(card_symbol)
        
    def attack(self, target_position, is_player_target=False):
        """Basic attack using passive skill, modified by role abilities"""
        if self.passive_skill and hasattr(self.passive_skill, 'is_ready') and self.passive_skill.is_ready():
            attack_result = self.passive_skill.activate(target_position)
            
            # Apply role ability modifiers if player knows their role
            if attack_result and self.known_role and hasattr(self, 'role_ability') and self.role_ability:
                # Protector damage reduction against players
                if self.true_role == PlayerRole.PROTECTOR and is_player_target:
                    # Protectors deal less damage to other players
                    attack_result["damage"] = attack_result.get("damage", 0) * 0.7
                    attack_result["description"] += " (Reduced damage to fellow players)"
                
                # Traitor damage bonus when alone
                elif self.true_role == PlayerRole.TRAITOR and is_player_target:
                    # Check if no witnesses (would be determined by game logic)
                    is_alone = hasattr(self.role_ability, 'is_alone_with_target') and self.role_ability.is_alone_with_target
                    
                    if is_alone and hasattr(self.role_ability, 'damage_bonus'):
                        attack_result["damage"] = attack_result.get("damage", 0) + self.role_ability.damage_bonus
                        attack_result["description"] += " (Bonus damage from betrayal)"
                
                # Chaos random effects
                elif self.true_role == PlayerRole.CHAOS:
                    if hasattr(self.role_ability, 'chaos_chance') and random.random() < self.role_ability.chaos_chance:
                        # Add a random chaos effect
                        effects = ["slow", "stun", "burn", "heal", "silence"]
                        chosen_effect = random.choice(effects)
                        
                        if "extra_effects" not in attack_result:
                            attack_result["extra_effects"] = {}
                            
                        attack_result["extra_effects"]["chaos"] = {
                            "type": chosen_effect,
                            "duration": 2.0,
                            "description": f"Target affected by chaotic energy: {chosen_effect}"
                        }
                        
                        attack_result["description"] += f" (Chaotic effect: {chosen_effect})"
            
            return attack_result
            
        return None
        
    def use_weapon(self, weapon_index: int, target_position):
        """Use a weapon from arsenal"""
        if 0 <= weapon_index < len(self.active_weapons):
            weapon = self.active_weapons[weapon_index]
            if hasattr(weapon, 'activate'):
                return weapon.activate(target_position)
        return None
        
    def add_exp(self, amount: int):
        """Add experience and level up if conditions met"""
        # Apply experience bonus if any
        if "exp_bonus" in self.stats:
            bonus_amount = amount * (1 + self.stats["exp_bonus"])
            self.exp += bonus_amount
        else:
            self.exp += amount
            
        if self.exp >= self.level * 100:
            self.exp = 0
            self.level += 1
            self._on_level_up()
            return True
        return False
    
    def _on_level_up(self):
        """Handle level up effects"""
        # Increase max HP
        hp_gain = 10
        self.max_hp += hp_gain
        self.hp = self.max_hp  # Full heal on level up
        
        # Improve stats based on level
        self.stats["damage"] += 2
        self.stats["crit_rate"] += 0.01
        
    def add_clue(self, clue):
        """Add a clue to the player's clue list"""
        self.clues.append(clue)
        
        # Chance to discover role based on clue
        if not self.known_role and hasattr(clue, 'reveals_role') and clue.reveals_role:
            self.discover_role()
            return True
        return False
    
    def update(self, dt: float):
        """Update player state"""
        # Update passive skill cooldown
        if self.passive_skill and hasattr(self.passive_skill, 'update'):
            self.passive_skill.update(dt)
            
        # Update role ability if it exists and player knows their role
        if self.known_role and hasattr(self, 'role_ability') and self.role_ability:
            self.role_ability.update(dt)
            
            # Apply passive effects from role abilities
            self._apply_role_ability_effects()
            
        # Update weapons
        for weapon in self.active_weapons:
            if hasattr(weapon, 'update'):
                weapon.update(dt)
                
        # Health regeneration
        if self.is_alive and "health_regen" in self.stats and self.stats["health_regen"] > 0:
            self.hp = min(self.max_hp, self.hp + self.stats["health_regen"] * dt)
            
    def _apply_role_ability_effects(self):
        """Apply passive effects from role abilities"""
        if not self.known_role or not hasattr(self, 'role_ability') or not self.role_ability:
            return
            
        # Apply protector aura effect
        if self.true_role == PlayerRole.PROTECTOR and self.role_ability.id == 'protection_aura':
            # Stats boost for protector: increased armor and health regeneration
            if 'armor' in self.stats and not hasattr(self, '_protector_bonus_applied'):
                self.stats['armor'] += self.role_ability.protection_value / 2
                self.stats['health_regen'] += 0.5
                setattr(self, '_protector_bonus_applied', True)
                
        # Apply traitor betrayal effect when alone
        elif self.true_role == PlayerRole.TRAITOR and self.role_ability.id == 'betrayal':
            # Stats boost for traitor: increased damage when no one's watching
            # This is situational and handled during combat
            pass
            
        # Apply chaos energy effects
        elif self.true_role == PlayerRole.CHAOS and self.role_ability.id == 'chaotic_energy':
            # Stats boost for chaos: increased critical chance
            if 'crit_rate' in self.stats and not hasattr(self, '_chaos_bonus_applied'):
                self.stats['crit_rate'] += self.role_ability.chaos_chance / 2
                setattr(self, '_chaos_bonus_applied', True)

    def __repr__(self):
        role_display = self.role.value if self.known_role else "?"
        return f"<Player {self.name} ({role_display}) HP: {self.hp}/{self.max_hp} Lvl: {self.level}>"