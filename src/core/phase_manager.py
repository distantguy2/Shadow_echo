# src/core/phase_manager.py - FIXED IMPORTS

import os
import sys
import pygame
import math
import random
from pathlib import Path
from enum import Enum
from typing import Optional, List

# Sửa lại đường dẫn import
from .entities.player import PlayerRole

class GamePhase(Enum):
    PREPARATION = "Preparation"
    DAY = "Day"
    NIGHT = "Night"
    SKILL_SELECT = "SkillSelect"
    END = "End"

class PhaseManager:
    """Manages game phases and transitions for the 10-day campaign"""
    
    def __init__(self, game):
        self.game = game
        self.current_phase = GamePhase.PREPARATION
        self.day_count = 0
        
        # Get timing constants from settings or use defaults
        self.PREPARATION_TIME = 20
        self.DAY_DURATION = 90
        self.NIGHT_DURATION = 60
        self.SKILL_CARD_SELECT_TIME = 20
        self.MAX_DAYS = 10
        
        try:
            # Try to import settings - if not available, use defaults
            from config.settings import (
                PREPARATION_TIME, DAY_DURATION, NIGHT_DURATION, 
                SKILL_CARD_SELECT_TIME, MAX_DAYS
            )
            self.PREPARATION_TIME = PREPARATION_TIME
            self.DAY_DURATION = DAY_DURATION
            self.NIGHT_DURATION = NIGHT_DURATION
            self.SKILL_CARD_SELECT_TIME = SKILL_CARD_SELECT_TIME
            self.MAX_DAYS = MAX_DAYS
        except ImportError:
            print("Using default timing settings")
        
        self.time_left = self.PREPARATION_TIME
        self.skill_select_ui = None
        self.card_selection_ui = None
        self.just_switched_phase = False
    
    def update(self, dt):
        """Update phase timer and handle transitions"""
        self.just_switched_phase = False
        
        # Special handling for card selection during night phase
        if self.card_selection_ui:
            self.card_selection_ui.update(dt)
            
            # Auto-select khi hết thời gian
            if self.card_selection_ui.time_left <= 0 and self.card_selection_ui.selected_card_index is None:
                # Chọn card đầu tiên nếu chưa chọn
                self.card_selection_ui.selected_card_index = 0
            
            # Hoàn tất quá trình khi đã chọn card
            if self.card_selection_ui.selected_card_index is not None:
                selected_card = self.card_selection_ui.card_options[self.card_selection_ui.selected_card_index]
                player = self.game.get_current_player()
                
                # Add the selected card to player
                if hasattr(self.game, 'card_system'):
                    self.game.card_system.add_card_to_player(player, selected_card)
                else:
                    player.cards.append(selected_card["id"])
                
                # Notify player
                if hasattr(self.game, 'ui_bridge'):
                    self.game.ui_bridge.show_notification(f"Added {selected_card['name']} to your deck!", "success")
                
                # Continue night phase normally
                self.card_selection_ui = None
            
            # Slow down time during selection
            self.time_left -= dt * 0.5
        
        # Special handling for skill selection
        elif self.current_phase == GamePhase.SKILL_SELECT and self.skill_select_ui:
            self.skill_select_ui.update(dt)
            if self.skill_select_ui.time_left <= 0:
                self.end_skill_selection()
            return
        
        # Normal phase timer update
        else:
            self.time_left -= dt
            if self.time_left <= 0:
                self.advance_phase()
                self.just_switched_phase = True
    
    def advance_phase(self):
        """Advance to next phase"""
        if self.current_phase == GamePhase.PREPARATION:
            self.start_day()
        elif self.current_phase == GamePhase.DAY:
            self.start_night()
        elif self.current_phase == GamePhase.NIGHT:
            self.start_skill_selection()
        elif self.current_phase == GamePhase.END:
            self.restart_game()
    
    def start_day(self):
        """Start day phase, or end game if reached max days"""
        self.day_count += 1
        
        # Check if we've reached the maximum number of days
        if self.day_count > self.MAX_DAYS:
            self.end_game()
            return
        
        self.current_phase = GamePhase.DAY
        self.time_left = self.DAY_DURATION
        
        # Spawn monsters if monster system exists
        if hasattr(self.game, 'monster_system'):
            self.game.monster_system.spawn_monsters()
        
            # Increase monster difficulty based on day
            difficulty_scaling = 1 + (self.day_count - 1) * 0.15  # 15% increase per day
            if hasattr(self.game.monster_system, 'apply_difficulty_scaling'):
                self.game.monster_system.apply_difficulty_scaling(difficulty_scaling)
            
            # Spawn boss on specific days (3, 6, 10)
            if self.day_count in [3, 6, 10] and hasattr(self.game.monster_system, 'spawn_boss'):
                self.game.monster_system.spawn_boss(self.day_count)
        
        # Generate daily event
        if hasattr(self.game, 'event_system'):
            self.game.event_system.generate_daily_event(self.day_count)
        
        # Notify players
        if hasattr(self.game, 'ui_bridge'):
            self.game.ui_bridge.show_notification(f"DAY {self.day_count} HAS BEGUN!", "info")
    
    def start_night(self):
        """Start night phase with card selection"""
        self.current_phase = GamePhase.NIGHT
        self.time_left = self.NIGHT_DURATION
        
        # Show card selection right at the start of night
        if hasattr(self.game, 'card_generator'):
            player = self.game.get_current_player()
            card_options = self.game.card_generator.generate_card_options(player.level)
            
            # Create and show card selection UI
            from .card_selection_ui import CardSelectionUI
            self.card_selection_ui = CardSelectionUI(self.game)
            self.card_selection_ui.set_card_options(card_options)
        
        # Start night phase for all players
        if hasattr(self.game, 'player_manager') and hasattr(self.game.player_manager, 'start_night_card_selection'):
            self.game.player_manager.start_night_card_selection()
        
        # Notify about night phase
        if hasattr(self.game, 'ui_bridge'):
            self.game.ui_bridge.show_notification("NIGHT FALLS...", "warning")
    
    def start_skill_selection(self):
        """Start skill selection phase after night"""
        from .ui import SkillSelectUI
        
        try:
            from .skills import SKILL_LIBRARY
            
            self.current_phase = GamePhase.SKILL_SELECT
            player = self.game.get_current_player()
            self.skill_select_ui = SkillSelectUI(self.game.screen)
            self.skill_select_ui.time_left = self.SKILL_CARD_SELECT_TIME
            
            # Select 3 random skills for player to choose from
            available_skills = list(SKILL_LIBRARY.values())
            self.skill_select_ui.skill_options = random.sample(available_skills, min(3, len(available_skills)))
            
            if hasattr(self.game, 'ui_bridge'):
                self.game.ui_bridge.show_notification("Choose a skill!", "info")
        except (ImportError, AttributeError):
            # If skills not available, skip to new day
            print("Skill library not available, skipping skill selection")
            self.start_day()
    
    def end_skill_selection(self):
        """End skill selection and start new day"""
        if self.skill_select_ui and self.skill_select_ui.selected_skill is not None:
            player = self.game.get_current_player()
            skill_card = self.skill_select_ui.skill_options[self.skill_select_ui.selected_skill]
            
            # Process skill selection
            if hasattr(self.game, 'skill_system'):
                self.game.skill_system.process_skill_selection(player, skill_card)
            elif hasattr(player, 'skills'):
                # Simple fallback if no skill system
                from .entities import PlayerSkill
                player.skills.append(PlayerSkill(skill_id=skill_card.id, level=1))
        
        # Reset for next day
        self.skill_select_ui = None
        
        # Start the new day
        self.start_day()
    
    def end_game(self):
        """End the game and show results"""
        self.current_phase = GamePhase.END
        self.time_left = 30  # Show results for 30 seconds
        
        # Calculate victory/defeat if possible
        survivors = [p for p in self.game.players if hasattr(p, 'is_alive') and p.is_alive]
        
        try:
            traitors = [p for p in survivors if p.true_role == PlayerRole.TRAITOR]
            protectors = [p for p in survivors if p.true_role == PlayerRole.PROTECTOR]
            
            # Determine outcome
            if not survivors:
                outcome = "DEFEAT - Everyone died!"
            elif not traitors and protectors:
                outcome = "VICTORY - Protectors won!"
            elif traitors and not protectors:
                outcome = "DEFEAT - Traitors eliminated all Protectors!"
            else:
                outcome = "STALEMATE - Both sides survived!"
        except AttributeError:
            # Simplified outcome if role data not available
            if survivors:
                outcome = f"GAME OVER - {len(survivors)} survivors!"
            else:
                outcome = "DEFEAT - No survivors!"
        
        # Show game results
        if hasattr(self.game, 'ui_bridge') and hasattr(self.game.ui_bridge, 'show_game_results'):
            self.game.ui_bridge.show_game_results(outcome, survivors)
        elif hasattr(self.game, 'ui_bridge'):
            self.game.ui_bridge.show_notification(outcome, "info")
    
    def restart_game(self):
        """Reset the game to start a new session"""
        self.current_phase = GamePhase.PREPARATION
        self.day_count = 0
        self.time_left = self.PREPARATION_TIME
        
        # Reset all game systems if available
        if hasattr(self.game, 'player_manager') and hasattr(self.game.player_manager, 'initialize_players'):
            self.game.player_manager.initialize_players()
        
        if hasattr(self.game, 'monster_system') and hasattr(self.game.monster_system, 'reset'):
            self.game.monster_system.reset()
        
        if hasattr(self.game, 'npc_system') and hasattr(self.game.npc_system, 'initialize_npcs'):
            self.game.npc_system.initialize_npcs()
        
        # Distribute initial cards if card system available
        if hasattr(self.game, 'player_manager') and hasattr(self.game.player_manager, 'distribute_initial_cards'):
            self.game.player_manager.distribute_initial_cards()
        
        # Notify about new game
        if hasattr(self.game, 'ui_bridge'):
            self.game.ui_bridge.show_notification("NEW GAME STARTED!", "info")
    
    def is_day_phase(self):
        """Check if current phase is day"""
        return self.current_phase == GamePhase.DAY
    
    def is_night_phase(self):
        """Check if current phase is night"""
        return self.current_phase == GamePhase.NIGHT
    
    def is_end_phase(self):
        """Check if game has ended"""
        return self.current_phase == GamePhase.END
    
    def is_skill_selection_phase(self):
        """Check if current phase is skill selection"""
        return self.current_phase == GamePhase.SKILL_SELECT
    
    def get_phase_display_text(self):
        """Get display text for current phase with time left"""
        phase_name = self.current_phase.name
        minutes = int(self.time_left // 60)
        seconds = int(self.time_left % 60)
        return f"{phase_name} - {minutes:02d}:{seconds:02d}"
    
    def handle_card_selection_event(self, event):
        """Handle events during card selection"""
        if self.card_selection_ui:
            result = self.card_selection_ui.handle_event(event)
            if result and result.get("action") == "select_card":
                # Process card selection
                return True
        return False
    
    def draw(self):
        """Draw phase-specific UI elements"""
        # Draw card selection UI if active
        if self.card_selection_ui:
            self.card_selection_ui.draw()
        
        # Draw skill selection UI if active
        elif self.current_phase == GamePhase.SKILL_SELECT and self.skill_select_ui and hasattr(self.skill_select_ui, 'draw'):
            player = self.game.get_current_player() if hasattr(self.game, 'get_current_player') else None
            self.skill_select_ui.draw(player)
        
        # Draw phase info
        elif self.current_phase == GamePhase.END:
            # Draw game over screen
            self._draw_game_over()
    
    def _draw_game_over(self):
        """Draw game over screen with results"""
        if not hasattr(self.game, 'screen'):
            return
            
        screen = self.game.screen
        width, height = screen.get_width(), screen.get_height()
        
        # Create overlay
        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))  # Semi-transparent black
        screen.blit(overlay, (0, 0))
        
        # Draw title
        font_large = pygame.font.SysFont("Arial", 48, bold=True)
        title_text = font_large.render("GAME OVER", True, (255, 0, 0))
        screen.blit(title_text, (width // 2 - title_text.get_width() // 2, 100))
        
        # Draw day count
        font_medium = pygame.font.SysFont("Arial", 36)
        day_text = font_medium.render(f"Survived {self.day_count} days", True, (255, 255, 255))
        screen.blit(day_text, (width // 2 - day_text.get_width() // 2, 180))
        
        # Draw restart prompt
        font_small = pygame.font.SysFont("Arial", 24)
        restart_text = font_small.render("Press SPACE to restart", True, (200, 200, 200))
        screen.blit(restart_text, (width // 2 - restart_text.get_width() // 2, height - 100))
