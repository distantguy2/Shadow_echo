# src/core/skill_system.py - SKILL MANAGEMENT

from .entities import PlayerSkill
from .skills import SKILL_LIBRARY

class SkillSystem:
    """Manages skill usage and cooldowns"""
    
    def __init__(self, game):
        self.game = game
    
    def update(self, dt):
        """Update skill cooldowns"""
        for player in self.game.player_manager.players:
            for skill in player.skills:
                if skill.cooldown > 0:
                    skill.cooldown = max(0, skill.cooldown - dt)
    
    def use_skill(self, skill_index):
        """Use player skill"""
        player = self.game.player_manager.get_current_player()
        
        # Filter active skills
        active_skills = []
        for player_skill in player.skills:
            skill_data = SKILL_LIBRARY.get(player_skill.skill_id)
            if skill_data and skill_data.type.value == "active":
                active_skills.append((player_skill, skill_data))
        
        # Check if skill exists and available
        if skill_index < len(active_skills):
            player_skill, skill_data = active_skills[skill_index]
            
            if player_skill.cooldown <= 0:
                # Use skill
                self._execute_skill(player, player_skill, skill_data)
                
                # Set cooldown
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
        # Implementation of skill effects
        # This would be expanded based on skill types
        pass
    
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
