# src/core/skill_system.py - SKILL MANAGEMENT

from .entities import PlayerSkill
from .skills import SKILL_LIBRARY
import json
import os
import random
from src.core.entities.skills import EchoStrike, VoidResonance, SkillType, Skill
from src.core.entities.weapons import AniMines, JinxTriNamite

class SkillSystem:
    """Manages skill usage and cooldowns"""

    def __init__(self, game):
        self.game = game

        # Auto-cast system
        self.auto_cast_enabled = False  # Toàn bộ hệ thống tự động
        self.auto_cast_skills = {}      # Dict lưu trữ các kỹ năng được cài đặt tự động {skill_id: interval}
        self.auto_cast_timers = {}      # Theo dõi thời gian cho mỗi kỹ năng {skill_id: elapsed_time}
        self.default_auto_cast_interval = 5.0  # Thời gian mặc định giữa các lần tự động thi triển (giây)
    
    def update(self, dt):
        """Update skill cooldowns and handle auto-casting"""
        for player in self.game.player_manager.players:
            if hasattr(player, 'skills'):
                for skill in player.skills:
                    if hasattr(skill, 'cooldown') and skill.cooldown > 0:
                        skill.cooldown = max(0, skill.cooldown - dt)

        # Xử lý tự động thi triển kỹ năng nếu được bật
        if self.auto_cast_enabled:
            self._update_auto_cast(dt)
    
    def use_skill(self, skill_index):
        """Use player skill"""
        player = self.game.player_manager.get_current_player()

        if not player or not hasattr(player, 'skills'):
            self.game.ui_bridge.show_notification("Player has no skills!", "error")
            return

        # Filter active skills
        active_skills = []
        for player_skill in player.skills:
            if not hasattr(player_skill, 'skill_id'):
                continue

            skill_data = SKILL_LIBRARY.get(player_skill.skill_id)
            if skill_data and hasattr(skill_data, 'type') and skill_data.type.value == "active":
                active_skills.append((player_skill, skill_data))

        # Check if skill exists and available
        if skill_index < len(active_skills):
            player_skill, skill_data = active_skills[skill_index]

            if not hasattr(player_skill, 'cooldown') or player_skill.cooldown <= 0:
                # Use skill
                self._execute_skill(player, player_skill, skill_data)

                # Set cooldown
                if hasattr(skill_data, 'cooldown'):
                    player_skill.cooldown = skill_data.cooldown

                self.game.ui_bridge.show_notification(
                    f"Used {skill_data.name}!", "success"
                )
            else:
                self.game.ui_bridge.show_notification(
                    f"{skill_data.name} is on cooldown!", "warning"
                )
    
    def _execute_skill(self, player, player_skill, skill_data):
        """Execute skill effect"""
        # Get target position (usually mouse position in game)
        target_pos = self.game.mouse_pos if hasattr(self.game, 'mouse_pos') else player.position

        effect_result = None
        skill_type = skill_data.type.value if hasattr(skill_data, 'type') else "active"

        # Execute skill based on type
        if skill_type == "active":
            # Handle active skill (direct damage, projectile, etc)
            effect_result = self._execute_active_skill(player, player_skill, skill_data, target_pos)
        elif skill_type == "support":
            # Handle support skill (healing, buffs, etc)
            effect_result = self._execute_support_skill(player, player_skill, skill_data, target_pos)
        elif skill_type == "passive":
            # Passive skills usually don't need manual execution
            # They're handled in update loops, but we can trigger them here if needed
            self.game.ui_bridge.show_notification(
                f"{skill_data.name} is a passive skill", "info"
            )
            return

        # Apply skill effects to game state
        if effect_result:
            # Apply damage if it's a damage skill
            if "damage" in effect_result:
                self._apply_damage_effect(effect_result)

            # Apply healing if it's a healing skill
            if "heal" in effect_result:
                self._apply_healing_effect(effect_result)

            # Create visual effects based on skill type and effect
            if hasattr(self.game, 'gameplay_enhancements'):
                effect_type = effect_result.get("effect_type", skill_data.id if hasattr(skill_data, 'id') else skill_data.name)
                skill_name = skill_data.name if hasattr(skill_data, 'name') else None

                # Determine appropriate visual effect for each skill type
                if skill_type == "active":
                    if "aoe" in effect_result or "area" in effect_result.get("type", ""):
                        # Area of effect skill
                        self.game.gameplay_enhancements.create_skill_effect(
                            player.position,
                            effect_result.get("position", target_pos),
                            "aoe", skill_name
                        )
                    elif "projectile" in effect_result or effect_result.get("type", "") in ["projectile", "ranged"]:
                        # Projectile skill
                        self.game.gameplay_enhancements.create_skill_effect(
                            player.position,
                            effect_result.get("position", target_pos),
                            "projectile", skill_name
                        )
                    elif "beam" in effect_result or effect_result.get("type", "") == "beam":
                        # Beam attack
                        self.game.gameplay_enhancements.create_skill_effect(
                            player.position,
                            effect_result.get("position", target_pos),
                            "beam", skill_name
                        )
                    else:
                        # Default active effect
                        self.game.gameplay_enhancements.create_skill_effect(
                            player.position,
                            effect_result.get("position", target_pos),
                            effect_type, skill_name
                        )

                elif skill_type == "support":
                    if "heal" in effect_result:
                        # Healing effect
                        self.game.gameplay_enhancements.create_skill_effect(
                            player.position,
                            player.position if "self_heal" in effect_result.get("type", "") else target_pos,
                            "heal_wave", skill_name
                        )
                    elif "shield" in effect_result or "protection" in effect_result:
                        # Shield effect
                        self.game.gameplay_enhancements.create_skill_effect(
                            player.position,
                            player.position,
                            "divine_shield", skill_name
                        )
                    else:
                        # Default support effect
                        self.game.gameplay_enhancements.create_skill_effect(
                            player.position,
                            target_pos,
                            effect_type, skill_name
                        )

            # Show notification with detailed information about the skill effect
            description = effect_result.get("description", f"Used {skill_data.name}!")
            if "damage" in effect_result:
                damage_amount = effect_result["damage"]
                if "is_critical" in effect_result and effect_result["is_critical"]:
                    description = f"{description} ({damage_amount:.0f} damage - CRITICAL!)"
                else:
                    description = f"{description} ({damage_amount:.0f} damage)"
            elif "heal" in effect_result:
                heal_amount = effect_result["heal"]
                description = f"{description} ({heal_amount:.0f} healing)"

            self.game.ui_bridge.show_notification(description, "success")

            return True

        return False

    def _execute_active_skill(self, player, player_skill, skill_data, target_pos):
        """Execute active skill effect"""
        # Basic implementation for active skills
        base_damage = 50  # Default damage

        if "damage" in skill_data.effect:
            base_damage = skill_data.effect["damage"]

        # Apply player stats
        damage = base_damage * (1 + player.stats.get("damage", 0) / 100)

        # Apply critical chance
        crit_chance = player.stats.get("crit_rate", 0.05)
        is_critical = random.random() < crit_chance
        if is_critical:
            damage *= 2

        # Calculate effect area
        area_radius = skill_data.effect.get("aoe_radius", 0)
        if area_radius > 0:
            # This is an AoE skill
            affected_entities = self._get_entities_in_radius(target_pos, area_radius)

            return {
                "type": "aoe_damage",
                "damage": damage,
                "position": target_pos,
                "radius": area_radius,
                "is_critical": is_critical,
                "affected_entities": affected_entities,
                "description": f"Used {skill_data.name} for {damage:.0f} damage in area!"
            }
        else:
            # This is a single target skill
            target = self._get_closest_entity_to_position(target_pos)

            if target:
                return {
                    "type": "single_target_damage",
                    "damage": damage,
                    "position": target_pos,
                    "target": target,
                    "is_critical": is_critical,
                    "description": f"Used {skill_data.name} for {damage:.0f} damage!"
                }

        return None

    def _execute_support_skill(self, player, player_skill, skill_data, target_pos):
        """Execute support skill effect"""
        # Basic implementation for support skills (healing, buffs)
        if "heal" in skill_data.effect:
            heal_amount = skill_data.effect["heal"]

            # Apply player stats
            heal_amount *= (1 + player.stats.get("effect_duration", 0) / 100)

            # Get healing targets (self and allies in radius)
            heal_radius = skill_data.effect.get("radius", 0)
            if heal_radius > 0:
                # This is an AoE heal
                affected_players = self._get_players_in_radius(player.position, heal_radius)

                # Apply healing to all affected players
                for affected_player in affected_players:
                    affected_player.heal(heal_amount)

                return {
                    "type": "aoe_heal",
                    "heal": heal_amount,
                    "position": player.position,
                    "radius": heal_radius,
                    "affected_players": affected_players,
                    "description": f"Used {skill_data.name} to heal {len(affected_players)} players for {heal_amount:.0f} HP!"
                }
            else:
                # This is a single target heal (self)
                player.heal(heal_amount)

                return {
                    "type": "self_heal",
                    "heal": heal_amount,
                    "position": player.position,
                    "description": f"Used {skill_data.name} to heal for {heal_amount:.0f} HP!"
                }

        # Handle shield/damage negation
        if "negate_damage" in skill_data.effect:
            duration = skill_data.effect.get("duration", 5)

            # Apply shield effect to player
            if not hasattr(player, "shield_active"):
                player.shield_active = True
                player.shield_duration = duration

                return {
                    "type": "shield",
                    "duration": duration,
                    "position": player.position,
                    "description": f"Used {skill_data.name} to block damage for {duration} seconds!"
                }

        return None

    def _apply_damage_effect(self, effect_result):
        """Apply damage effects to targets"""
        if effect_result["type"] == "aoe_damage":
            # Apply AoE damage
            for entity in effect_result.get("affected_entities", []):
                if hasattr(entity, "take_damage"):
                    entity.take_damage(effect_result["damage"])
        elif effect_result["type"] == "single_target_damage":
            # Apply single target damage
            target = effect_result.get("target")
            if target and hasattr(target, "take_damage"):
                target.take_damage(effect_result["damage"])

    def _apply_healing_effect(self, effect_result):
        """Apply healing effects to targets"""
        # Healing is already applied in _execute_support_skill
        # This is just a placeholder for additional effects
        pass

    def _get_entities_in_radius(self, position, radius):
        """Get all entities within a radius of the position"""
        entities = []

        # Add monsters in radius
        for monster in self.game.monsters:
            if self._distance(position, monster.position) <= radius:
                entities.append(monster)

        return entities

    def _get_players_in_radius(self, position, radius):
        """Get all players within a radius of the position"""
        players = []

        # Add players in radius
        for player in self.game.player_manager.players:
            if player.is_alive and self._distance(position, player.position) <= radius:
                players.append(player)

        return players

    def _get_closest_entity_to_position(self, position):
        """Get the closest entity to a position"""
        closest_entity = None
        min_distance = float('inf')

        # Check monsters
        for monster in self.game.monsters:
            if monster.is_alive if hasattr(monster, 'is_alive') else True:
                distance = self._distance(position, monster.position)
                if distance < min_distance:
                    min_distance = distance
                    closest_entity = monster

        return closest_entity

    def _distance(self, pos1, pos2):
        """Calculate distance between two positions"""
        import math
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        return math.sqrt(dx**2 + dy**2)
    
    def process_skill_selection(self, player, skill_card):
        """Process skill selection from skill selection phase"""
        # Check existing skill
        existing_skill = None
        for player_skill in player.skills:
            if player_skill.skill_id == skill_card.id:
                existing_skill = player_skill
                break
        
        if existing_skill and existing_skill.level < skill_card.max_level:
            # Upgrade skill
            existing_skill.level += 1
            self.game.ui_bridge.show_notification(
                f"Upgraded {skill_card.name} to level {existing_skill.level}!", "success"
            )
        elif not existing_skill:
            # Add new skill
            player.skills.append(PlayerSkill(skill_id=skill_card.id, level=1))
            self.game.ui_bridge.show_notification(
                f"Learned {skill_card.name}!", "success"
            )

# Updated SkillRegistry for the new character/role system
class RoleAbility(Skill):
    """Role-specific special ability implementation"""
    def __init__(self, ability_id, name, level=1):
        super().__init__(level)
        self.id = ability_id
        self.name = name
        self.type = SkillType.PASSIVE  # Role abilities are usually passive
        self.owner = None
        
        # Set default values based on ability ID
        if ability_id == 'protection_aura':
            self.description = "Tạo aura bảo vệ cho đồng đội xung quanh, giảm sát thương nhận vào"
            self.protection_value = 5 + (level * 2)
            self.aura_radius = 100 + (level * 20)
        elif ability_id == 'betrayal':
            self.description = "Tăng sát thương đối với người chơi khác khi không có ai khác quan sát"
            self.damage_bonus = 20 + (level * 5)
        elif ability_id == 'chaotic_energy':
            self.description = "Có cơ hội gây hiệu ứng hỗn loạn khi tấn công, ảnh hưởng ngẫu nhiên đến mục tiêu"
            self.chaos_chance = 0.15 + (level * 0.05)
    
    def activate(self, target_position):
        """Role abilities are usually passive and don't need normal activation"""
        return None
    
    def apply_effect(self, target):
        """Apply role ability effect to a target"""
        if self.id == 'protection_aura':
            return {
                "effect": "protection",
                "value": self.protection_value,
                "source": self.owner,
                "description": f"Protected by {self.owner.name}'s aura"
            }
        elif self.id == 'betrayal':
            # Check if no other players are nearby
            is_alone = True  # This would be determined by the game's logic
            
            if is_alone:
                return {
                    "effect": "damage_bonus",
                    "value": self.damage_bonus,
                    "source": self.owner,
                    "description": f"{self.owner.name} attacks from the shadows"
                }
        elif self.id == 'chaotic_energy':
            # Random chance to apply chaos effect
            if random.random() < self.chaos_chance:
                effects = ["slow", "stun", "burn", "heal", "silence"]
                chosen_effect = random.choice(effects)
                
                return {
                    "effect": chosen_effect,
                    "value": 1.0,  # Effect potency
                    "duration": 2.0,  # Effect duration in seconds
                    "source": self.owner,
                    "description": f"{target.name} is affected by chaotic energy"
                }
        
        return None


class SkillRegistry:
    """Registry for all skills, weapons, characters and roles"""
    def __init__(self):
        self.skills = {}
        self.weapons = {}
        self.characters = {}
        self.roles = {}
        self._load_data()
        
    def _load_data(self):
        """Load skill, weapon, character, and role data from config"""
        config_path = os.path.join('config', 'cards.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Register weapons
            for category, weapons in data.get('weapon_cards', {}).items():
                for weapon_data in weapons:
                    self.register_weapon(weapon_data['id'], weapon_data, category)
            
            # Register character passive skills
            for character in data.get('character_cards', []):
                self.register_character(character['id'], character)
                if 'passive_skill' in character:
                    self.register_skill(character['passive_skill']['id'], character['passive_skill'], 'passive')
                    if 'upgrade' in character['passive_skill']:
                        self.register_skill(
                            character['passive_skill']['upgrade']['id'], 
                            character['passive_skill']['upgrade'],
                            'passive',
                            is_upgrade=True,
                            base_skill_id=character['passive_skill']['id']
                        )
            
            # Register role abilities
            for role in data.get('role_cards', []):
                self.register_role(role['id'], role)
                if 'special_ability' in role:
                    self.register_skill(
                        role['special_ability']['id'], 
                        role['special_ability'], 
                        'role_ability'
                    )
                    
        except Exception as e:
            print(f"Error loading skill data: {e}")
    
    def register_skill(self, skill_id, skill_data, skill_category='unknown', is_upgrade=False, base_skill_id=None):
        """Register a skill with the registry"""
        self.skills[skill_id] = {
            'data': skill_data,
            'category': skill_category,
            'is_upgrade': is_upgrade,
            'base_skill_id': base_skill_id
        }
    
    def register_weapon(self, weapon_id, weapon_data, category='unknown'):
        """Register a weapon with the registry"""
        self.weapons[weapon_id] = {
            'data': weapon_data,
            'category': category
        }
    
    def register_character(self, character_id, character_data):
        """Register a character with the registry"""
        self.characters[character_id] = character_data
    
    def register_role(self, role_id, role_data):
        """Register a role with the registry"""
        self.roles[role_id] = role_data
    
    def create_skill(self, skill_id, player=None, level=1):
        """Create a skill instance by id"""
        if skill_id not in self.skills:
            return None
            
        # Map skill IDs to their class implementations
        # This would be expanded with all skill implementations
        skill_classes = {
            'echo_strike': EchoStrike,
            'void_resonance': VoidResonance,
            # Add other skill implementations here as they're created
            'protection_aura': lambda lvl: RoleAbility('protection_aura', 'Protection Aura', lvl),
            'betrayal': lambda lvl: RoleAbility('betrayal', 'Betrayal', lvl),
            'chaotic_energy': lambda lvl: RoleAbility('chaotic_energy', 'Chaotic Energy', lvl)
        }
        
        if skill_id in skill_classes:
            skill = skill_classes[skill_id](level)
            if player:
                skill.owner = player
            return skill
        
        # If no specific implementation, create a generic skill
        skill_data = self.skills[skill_id]
        return GenericSkill(skill_id, skill_data['data'], level)
    
    def create_weapon(self, weapon_id, player=None, level=1):
        """Create a weapon instance by id"""
        if weapon_id not in self.weapons:
            return None
            
        # Map weapon IDs to their class implementations
        # This would be expanded with all weapon implementations
        weapon_classes = {
            'ani_mines': AniMines,
            'jinx_tri_namite': JinxTriNamite,
            # Add other weapon implementations here
        }
        
        if weapon_id in weapon_classes:
            weapon = weapon_classes[weapon_id](level)
            if player:
                weapon.owner = player
            return weapon
        
        # If no specific implementation, create a generic weapon
        weapon_data = self.weapons[weapon_id]
        return GenericWeapon(weapon_id, weapon_data['data'], level)
    
    def can_upgrade_skill(self, skill_id, player_stats):
        """Check if a skill can be upgraded based on player stats"""
        if skill_id not in self.skills:
            return False
            
        skill_data = self.skills[skill_id]
        if not skill_data.get('is_upgrade', False) and 'upgrade' not in skill_data.get('data', {}):
            return False
            
        # Get upgrade condition
        condition = None
        if 'upgrade' in skill_data.get('data', {}):
            condition = skill_data['data']['upgrade'].get('condition')
        
        if not condition:
            return False
            
        # Map condition to player stat
        condition_map = {
            'Số lượng đạn': 'projectile_count',
            'Sát thương': 'damage',
            'Tốc độ hồi chiêu': 'cooldown_reduction',
            'Kích thước vùng': 'area_size',
            'Tỉ lệ chí mạng': 'crit_rate',
            'Máu tối đa': 'max_health',
            'Tốc độ di chuyển': 'movement_speed',
            'Giáp': 'armor',
            'Thời gian hiệu lực': 'effect_duration',
            'Bán kính nhắt vật phẩm': 'pickup_radius',
            'Hồi phục máu': 'health_regen',
            'Kinh nghiệm (EXP)': 'exp'
        }
        
        if condition not in condition_map:
            return False
            
        stat_name = condition_map[condition]
        
        # Different threshold levels based on the stat
        threshold_map = {
            'projectile_count': 3,
            'damage': 25,
            'cooldown_reduction': 0.3,
            'area_size': 2.0,
            'crit_rate': 0.15,
            'max_health': 150,
            'movement_speed': 7,
            'armor': 15,
            'effect_duration': 2.0,
            'pickup_radius': 3.0,
            'health_regen': 2.0,
            'exp': 300
        }
        
        required_value = threshold_map.get(stat_name, 5)  # Default if not in map
        
        return player_stats.get(stat_name, 0) >= required_value
    
    def get_potential_roles_for_character(self, character_id):
        """Get list of potential roles for a character"""
        if character_id not in self.characters:
            return ['protector', 'traitor', 'chaos']  # Default roles
            
        character = self.characters[character_id]
        return character.get('potential_roles', ['protector', 'traitor', 'chaos'])
    
    def get_ability_for_role(self, role_id):
        """Get the special ability for a role"""
        if role_id not in self.roles:
            return None
            
        role = self.roles[role_id]
        if 'special_ability' not in role:
            return None
            
        ability_id = role['special_ability']['id']
        return self.create_skill(ability_id)


# Generic classes for skills and weapons when specific implementations are not available

class GenericSkill(Skill):
    """Generic skill implementation when a specific class is not available"""
    def __init__(self, skill_id, skill_data, level=1):
        super().__init__(level)
        self.id = skill_id
        self.name = skill_data.get('name', 'Unknown Skill')
        self.description = skill_data.get('description', '')
        self.type = SkillType.BASIC
        
        # Set base stats scaled by level
        self.base_damage = (skill_data.get('damage', 20) + (level * 5))
        self.cooldown = max(1, skill_data.get('cooldown', 5) - (level * 0.3))
        self.current_cooldown = 0
        self.owner = None
        
        # Extra properties if defined
        self.extra_properties = skill_data.get('stats', [])
    
    def activate(self, target_position):
        """Generic skill activation"""
        if not self.is_ready():
            return None
            
        self.current_cooldown = self.cooldown
        
        # Create a generic effect based on skill type
        return {
            "type": self.id,
            "source": self.owner,
            "damage": self.base_damage,
            "position": target_position,
            "description": self.description
        }
    
    def get_description(self):
        """Get generic skill description"""
        return f"{self.name} (Level {self.level}): {self.description}"


class GenericWeapon:
    """Generic weapon implementation when a specific class is not available"""
    def __init__(self, weapon_id, weapon_data, level=1):
        self.id = weapon_id
        self.name = weapon_data.get('name', 'Unknown Weapon')
        self.description = weapon_data.get('description', '')
        self.level = level
        self.cooldown = 5 - (level * 0.3)
        self.current_cooldown = 0
        self.owner = None
        
        # Base stats
        self.base_damage = weapon_data.get('damage', 15) + (level * 5)
    
    def activate(self, target_position):
        """Generic weapon activation"""
        if self.current_cooldown > 0:
            return None
            
        self.current_cooldown = self.cooldown
        
        return {
            "type": self.id,
            "source": self.owner,
            "damage": self.base_damage,
            "position": target_position,
            "description": f"Used {self.name}"
        }
    
    def update(self, dt):
        """Update weapon cooldown"""
        if self.current_cooldown > 0:
            self.current_cooldown -= dt
    
    def is_ready(self):
        """Check if weapon is ready to use"""
        return self.current_cooldown <= 0


# Create a global instance
skill_registry = SkillRegistry()

def get_skill_registry():
    """Get the global skill registry"""
    return skill_registry


# Auto-Cast System Implementation for SkillSystem
def _update_auto_cast(self, dt):
    """Cập nhật và thi triển kỹ năng tự động sau mỗi khoảng thời gian"""
    player = self.game.player_manager.get_current_player()
    if not player or not player.is_alive:
        return

    # Cập nhật bộ đếm thời gian cho mỗi kỹ năng tự động
    for skill_id, interval in self.auto_cast_skills.items():
        # Tăng thời gian đã trôi qua
        if skill_id not in self.auto_cast_timers:
            self.auto_cast_timers[skill_id] = 0.0

        self.auto_cast_timers[skill_id] += dt

        # Kiểm tra xem đã đến lúc thi triển kỹ năng chưa
        if self.auto_cast_timers[skill_id] >= interval:
            # Đặt lại bộ đếm thời gian
            self.auto_cast_timers[skill_id] = 0.0

            # Tìm và thi triển kỹ năng
            self._auto_cast_skill(player, skill_id)

def _auto_cast_skill(self, player, skill_id):
    """Tìm và thi triển kỹ năng theo ID"""
    if not hasattr(player, 'skills'):
        return False

    # Lấy danh sách kỹ năng của người chơi
    active_skills = []
    for index, player_skill in enumerate(player.skills):
        if not hasattr(player_skill, 'skill_id'):
            continue

        skill_data = SKILL_LIBRARY.get(player_skill.skill_id)
        if skill_data and (
            (hasattr(skill_data, 'id') and skill_data.id == skill_id) or
            (player_skill.skill_id == skill_id)
        ):
            if not hasattr(player_skill, 'cooldown') or player_skill.cooldown <= 0:
                # Thi triển kỹ năng
                self._execute_skill(player, player_skill, skill_data)
                return True

    # Không tìm thấy kỹ năng hoặc kỹ năng đang hồi chiêu
    return False

def toggle_auto_cast(self, enabled=None):
    """Bật/tắt toàn bộ hệ thống tự động thi triển kỹ năng"""
    if enabled is None:
        # Đảo trạng thái nếu không cung cấp giá trị cụ thể
        self.auto_cast_enabled = not self.auto_cast_enabled
    else:
        self.auto_cast_enabled = enabled

    return self.auto_cast_enabled

def set_auto_cast_skill(self, skill_id, interval=None, enabled=True):
    """Thiết lập kỹ năng tự động thi triển

    Parameters:
    - skill_id: ID của kỹ năng cần thiết lập
    - interval: Khoảng thời gian giữa các lần thi triển (giây)
    - enabled: True để bật, False để tắt kỹ năng cụ thể
    """
    if enabled:
        # Thêm hoặc cập nhật kỹ năng vào danh sách tự động
        self.auto_cast_skills[skill_id] = interval or self.default_auto_cast_interval
        self.auto_cast_timers[skill_id] = 0.0  # Đặt lại bộ đếm thời gian

        # Đảm bảo hệ thống tự động được bật
        if not self.auto_cast_enabled:
            self.auto_cast_enabled = True

        return f"Enabled auto-cast for {skill_id} every {self.auto_cast_skills[skill_id]} seconds"
    else:
        # Xóa kỹ năng khỏi danh sách tự động
        if skill_id in self.auto_cast_skills:
            del self.auto_cast_skills[skill_id]

        if skill_id in self.auto_cast_timers:
            del self.auto_cast_timers[skill_id]

        return f"Disabled auto-cast for {skill_id}"

def get_auto_cast_status(self):
    """Lấy thông tin trạng thái hiện tại của hệ thống tự động"""
    return {
        "enabled": self.auto_cast_enabled,
        "skills": self.auto_cast_skills,
        "timers": self.auto_cast_timers,
        "default_interval": self.default_auto_cast_interval
    }

# Attach methods to SkillSystem class
SkillSystem._update_auto_cast = _update_auto_cast
SkillSystem._auto_cast_skill = _auto_cast_skill
SkillSystem.toggle_auto_cast = toggle_auto_cast
SkillSystem.set_auto_cast_skill = set_auto_cast_skill
SkillSystem.get_auto_cast_status = get_auto_cast_status