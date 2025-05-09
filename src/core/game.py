# src/core/game.py - COMPLETE IMPLEMENTATION

import pygame
import sys
import random
import math
from pathlib import Path
from typing import Dict, Any, Optional, List


# Set up path to find project modules
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

# Import config settings
from config.settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    MAX_DAYS
)

# Import font utilities
from src.utils.font_utils import get_font, render_text

# Import from core modules with updated paths
from src.core.entities import Player, PlayerRole
from src.core.entities.game_phase import GamePhase
from src.core.phase_manager import PhaseManager
from src.core.ui import SkillSelectUI
from src.core.skills import SKILL_LIBRARY
from src.core.skill_system import get_skill_registry, SkillSystem
from src.core.swarm_mode import get_swarm_manager

# Import systems
from src.systems.auto_combat_system import AutoCombatSystem
from src.systems.card_system import CardSystem
from src.systems.monsters import MonsterSystem
if Path(project_root / "src" / "systems" / "npcs.py").exists():
    from src.systems.npcs import NPCSystem
else:
    NPCSystem = None

# Import utilities
from src.utils.logger import setup_logger
from src.utils.ui_bridge import UIBridge

# Import card generator
from src.systems.card_generator import CardGenerator

class Game:
    """Main game controller class"""
    
    def __init__(self, game_mode="standard"):
        # Initialize essential attributes
        self.screen = None
        self.clock = None
        self.font = None
        self.small_font = None
        self.game_running = True
        self.debug_mode = False
        self.paused = False
        self.auto_combat_active = True
        
        # Game mode
        self.game_mode = game_mode  # "standard" or "swarm"
        
        # Game dimensions
        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT
        
        # Initialize logger
        self.logger = setup_logger("Game")
        
        # Setup pygame
        self._setup_pygame()
        
        # Game state
        self.players = []
        self.monsters = []
        self.current_player = 0
        self.typing_mode = False
        self.command_input = ""
        self.mouse_pos = (0, 0)
        
        # Initialize game systems
        self._init_game_systems()

        # Game initialization state
        if self.game_mode == "swarm":
            # Start in character selection for Swarm mode
            self.phase_manager.set_phase(GamePhase.CHARACTER_SELECT)
        else:
            # Standard mode: Add default players and start first day
            self._add_players()
            self.phase_manager.start_day()

        # Initialize skill system (needed for both modes)
        self.skill_system = SkillSystem(self)
        
    def _setup_pygame(self):
        """Initialize pygame and display settings"""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Shadow Echo RPG")
        self.clock = pygame.time.Clock()

        # Initialize fonts with Vietnamese support
        self.font = get_font(32)
        self.small_font = get_font(24)
        self.debug_font = get_font(14)
        
    def _init_game_systems(self):
        """Initialize all game systems"""
        # Core systems
        self.phase_manager = PhaseManager(self)
        self.ui_bridge = UIBridge(self)
        
        # Player manager wrapper
        self.player_manager = type('obj', (object,), {
            'players': self.players,
            'get_current_player': lambda self: self.get_current_player()
        })
    
        # Initialize systems based on game mode
        if self.game_mode == "standard":
            # Standard game systems
            self.auto_combat = AutoCombatSystem(self)
            self.monster_system = MonsterSystem(self)
            if NPCSystem:
                self.npc_system = NPCSystem(self)
            self.card_system = CardSystem(self)
            self.card_generator = CardGenerator(self)
        else:
            # Swarm mode systems
            self.skill_registry = get_skill_registry()
            self.swarm_manager = get_swarm_manager()
            self.card_system = CardSystem(self, "config/cards.json")
    
    def _add_players(self):
        """Initialize players for standard mode"""
        names = ["Alice", "Bob", "Charlie"]
        roles = [PlayerRole.PROTECTOR, PlayerRole.TRAITOR, PlayerRole.CHAOS]
        random.shuffle(roles)
        
        for i, name in enumerate(names):
            player = Player(id=i, name=name, role=roles[i])
            player.position = (100 + i * 100, 400)
            player.level = 1
            player.exp = 0
            player.is_controlled = (i == 0)
            player.hp = 100
            self.players.append(player)
            
            # Give initial cards
            player.cards = []
            for _ in range(2):
                card_options = self.card_generator.generate_card_options(1, 1)
                if card_options:
                    player.cards.append(card_options[0]['id'])
    
    def select_character(self, character_id: str, player_name: str = "Player") -> bool:
        """Select a character for the player in Swarm mode"""
        if self.game_mode != "swarm":
            return False
            
        # Create player
        player = Player(id=0, name=player_name)
        player.is_controlled = True
        player.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        # Initialize player with character and role
        if self.swarm_manager.initialize_player(player, character_id):
            self.players.append(player)
            self.swarm_manager.add_player(player)
            
            # Start the Swarm mode game
            self.phase_manager.set_phase(GamePhase.SWARM_PREPARATION)
            self.phase_manager.start_day()
            return True
            
        return False
            
    def update(self, dt):
        """Update all game systems"""
        if self.paused:
            return

        # Update mouse position
        self.mouse_pos = pygame.mouse.get_pos()

        # Character selection phase
        if self.phase_manager.current_phase == GamePhase.CHARACTER_SELECT:
            # This is handled by event processing
            return

        # Update based on game mode
        if self.game_mode == "swarm":
            self._update_swarm_mode(dt)
        else:
            self._update_standard_mode(dt)

        # Update player movement for controlled player if applicable
        self._update_player_movement(dt)

    def _update_player_skills(self, dt):
        """Update player skills and cooldowns"""
        # Update skill system (handles cooldowns)
        if hasattr(self, 'skill_system'):
            self.skill_system.update(dt)

        # Also update individual player passive skills
        for player in self.players:
            if player.is_alive:
                if hasattr(player, 'update'):
                    player.update(dt)

                # Ensure passive skill is updated
                if hasattr(player, 'passive_skill') and player.passive_skill:
                    if hasattr(player.passive_skill, 'update'):
                        player.passive_skill.update(dt)

                # Ensure skills are updated
                if hasattr(player, 'skills'):
                    for skill in player.skills:
                        if hasattr(skill, 'update'):
                            skill.update(dt)

                # Ensure weapons are updated
                if hasattr(player, 'active_weapons'):
                    for weapon in player.active_weapons:
                        if hasattr(weapon, 'update'):
                            weapon.update(dt)
            
    def _update_standard_mode(self, dt):
        """Update standard game mode systems"""
        # Update phase manager
        self.phase_manager.update(dt)

        # Update auto-combat system
        self.auto_combat.update(dt)

        # Update monsters
        self.monster_system.update(dt)

        # Update NPCs if available
        if hasattr(self, 'npc_system'):
            self.npc_system.update(dt)

        # Update player skills and cooldowns
        self._update_player_skills(dt)

        # Update UI
        self.ui_bridge.update(dt)
    
    def _update_swarm_mode(self, dt):
        """Update swarm mode systems"""
        # Update phase manager
        self.phase_manager.update(dt)

        # Update swarm manager
        self.swarm_manager.update(dt)

        # Update player skills and cooldowns
        self._update_player_skills(dt)

        # Check victory conditions
        victory_status = self.swarm_manager.check_victory_conditions()
        if victory_status.get("game_over", False):
            self.phase_manager.set_phase(GamePhase.GAME_OVER)
            self.victory_status = victory_status

        # Update UI
        self.ui_bridge.update(dt)
            
    def _update_player_movement(self, dt):
        """Handle player movement controls"""
        if self.typing_mode:
            return
            
        if not self.players or self.current_player >= len(self.players):
            return
            
        player = self.players[self.current_player]
        if not player.is_controlled or not player.is_alive:
            return
            
        keys = pygame.key.get_pressed()
        dx = dy = 0
        speed = 200 * dt
        
        if keys[pygame.K_w]: dy = -speed
        if keys[pygame.K_s]: dy = speed
        if keys[pygame.K_a]: dx = -speed
        if keys[pygame.K_d]: dx = speed
        
        new_x = player.position[0] + dx
        new_y = player.position[1] + dy
        
        # Keep within bounds
        if 20 <= new_x <= self.SCREEN_WIDTH - 20:
            player.position = (new_x, player.position[1])
        if 20 <= new_y <= self.SCREEN_HEIGHT - 70:
            player.position = (player.position[0], new_y)
            
    def draw(self):
        """Render all game elements"""
        # Clear screen
        self.screen.fill((20, 20, 30))
        
        # Character selection screen
        if self.phase_manager.current_phase == GamePhase.CHARACTER_SELECT:
            self._draw_character_select()
            pygame.display.flip()
            return
            
        # Game over screen
        if self.phase_manager.current_phase == GamePhase.GAME_OVER:
            self._draw_game_over()
            pygame.display.flip()
            return
            
        # Draw based on game mode
        if self.game_mode == "swarm":
            self._draw_swarm_mode()
        else:
            self._draw_standard_mode()
        
        # Draw UI elements common to both modes
        self._draw_ui()
        
        # Debug info
        if self.debug_mode:
            self._draw_debug_overlay()
            
        pygame.display.flip()
    
    def _draw_standard_mode(self):
        """Draw standard game mode elements"""
        # Draw monsters
        self.monster_system.draw(self.screen)

        # Draw auto-combat indicators
        if hasattr(self, 'auto_combat'):
            self.auto_combat.draw(self.screen)
        
        # Draw NPCs if available
        if hasattr(self, 'npc_system'):
            self.npc_system.draw(self.screen)
        
        # Draw players
        self._draw_players()
        
        # Draw phase-specific UI
        self.phase_manager.draw()
    
    def _draw_swarm_mode(self):
        """Draw swarm mode elements"""
        # Draw clues
        self._draw_clues()
        
        # Draw players
        self._draw_players(show_roles=False)  # Don't show roles in Swarm mode unless discovered
        
        # Draw phase-specific UI
        self.phase_manager.draw()
    
    def _draw_character_select(self):
        """Draw character selection screen"""
        # Draw title
        title_text = self.font.render("Select Your Character", True, (255, 255, 255))
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))
        
        # Get available characters
        characters = []
        if hasattr(self, 'skill_registry'):
            characters = list(self.skill_registry.characters.values())
        
        # Draw character options
        card_width, card_height = 200, 300
        spacing = 30
        total_width = min(len(characters), 4) * (card_width + spacing) - spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        for i, character in enumerate(characters[:4]):  # Show up to 4 characters
            x = start_x + i * (card_width + spacing)
            y = SCREEN_HEIGHT // 2 - card_height // 2
            
            # Draw card background
            pygame.draw.rect(self.screen, (60, 60, 80), (x, y, card_width, card_height))
            pygame.draw.rect(self.screen, (80, 80, 100), (x, y, card_width, card_height), 2)
            
            # Draw character name
            name_text = self.font.render(character["name"], True, (255, 255, 255))
            self.screen.blit(name_text, (x + card_width // 2 - name_text.get_width() // 2, y + 20))
            
            # Draw character description
            desc_lines = self._wrap_text(character["description"], self.small_font, card_width - 20)
            for j, line in enumerate(desc_lines):
                desc_text = self.small_font.render(line, True, (200, 200, 200))
                self.screen.blit(desc_text, (x + 10, y + 70 + j * 25))
            
            # Draw passive skill info
            if "passive_skill" in character:
                skill = character["passive_skill"]
                skill_text = self.small_font.render(skill["name"], True, (255, 255, 0))
                self.screen.blit(skill_text, (x + 10, y + 180))
                
                skill_desc_lines = self._wrap_text(skill["description"], self.small_font, card_width - 20)
                for j, line in enumerate(skill_desc_lines):
                    desc_text = self.small_font.render(line, True, (180, 180, 100))
                    self.screen.blit(desc_text, (x + 10, y + 210 + j * 25))
            
            # Draw selection number
            select_text = self.font.render(str(i+1), True, (255, 255, 0))
            self.screen.blit(select_text, (x + 10, y + 10))
    
    def _draw_game_over(self):
        """Draw game over screen"""
        # Draw background overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Draw game over title
        title_text = self.font.render("Game Over", True, (255, 255, 255))
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 3))
        
        # Draw winner info if available
        if hasattr(self, 'victory_status'):
            winner = self.victory_status.get("winner", "")
            message = self.victory_status.get("message", "")
            
            if winner:
                winner_text = self.font.render(f"Winner: {winner}", True, (255, 255, 0))
                self.screen.blit(winner_text, (SCREEN_WIDTH // 2 - winner_text.get_width() // 2, SCREEN_HEIGHT // 2))
            
            if message:
                message_lines = self._wrap_text(message, self.small_font, SCREEN_WIDTH - 200)
                for i, line in enumerate(message_lines):
                    line_text = self.small_font.render(line, True, (200, 200, 200))
                    self.screen.blit(line_text, (SCREEN_WIDTH // 2 - line_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60 + i * 30))
        
        # Draw restart instructions
        restart_text = self.small_font.render("Press ENTER to restart or ESC to quit", True, (150, 150, 150))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT * 3 // 4))
    
    def _draw_clues(self):
        """Draw clues in the game world"""
        if not hasattr(self, 'swarm_manager'):
            return
            
        for i, clue in enumerate(self.swarm_manager.clues):
            if clue.get("collected", False):
                continue
                
            pos = clue.get("position", (0, 0))
            clue_type = clue.get("type", "document")
            
            # Draw different symbols based on clue type
            color = (255, 255, 255)
            symbol = "?"
            
            if clue_type == "document":
                color = (255, 255, 150)
                symbol = "📄"
            elif clue_type == "item":
                color = (150, 255, 150)
                symbol = "🔍"
            elif clue_type == "environment":
                color = (150, 150, 255)
                symbol = "🔮"
            
            # Draw clue
            clue_text = self.font.render(symbol, True, color)
            self.screen.blit(clue_text, (pos[0] - clue_text.get_width() // 2, pos[1] - clue_text.get_height() // 2))
            
            # If player is nearby, show hint
            player = self.get_current_player()
            if player:
                distance = ((player.position[0] - pos[0]) ** 2 + (player.position[1] - pos[1]) ** 2) ** 0.5
                if distance < 100:
                    hint_text = self.small_font.render("Press E to examine", True, (200, 200, 200))
                    self.screen.blit(hint_text, (pos[0] - hint_text.get_width() // 2, pos[1] + 20))
        
    def _draw_players(self, show_roles=True):
        """Draw all players"""
        for player in self.players:
            if player.is_alive:
                # Determine color based on role
                color = (100, 100, 255)  # Default blue
                
                if player.is_controlled:
                    color = (0, 255, 255)  # Cyan for controlled player
                elif show_roles:
                    # In standard mode, or if role is known in swarm mode
                    if player.role == PlayerRole.PROTECTOR:
                        color = (0, 200, 0)    # Green for protector
                    elif player.role == PlayerRole.TRAITOR:
                        color = (200, 0, 0)    # Red for traitor
                    elif player.role == PlayerRole.CHAOS:
                        color = (200, 0, 200)  # Purple for chaos
                elif player.known_role:
                    # Player knows their own role in swarm mode
                    if player.role == PlayerRole.PROTECTOR:
                        color = (0, 200, 0)
                    elif player.role == PlayerRole.TRAITOR:
                        color = (200, 0, 0)
                    elif player.role == PlayerRole.CHAOS:
                        color = (200, 0, 200)
                
                # Draw player (as a rectangle for now)
                pygame.draw.rect(self.screen, color, 
                               (int(player.position[0])-10, int(player.position[1])-10, 20, 20))
                
                # Draw name and level
                name_text = self.small_font.render(
                    f"{player.name} Lv.{player.level}", True, (255, 255, 255)
                )
                self.screen.blit(name_text, (int(player.position[0])-30, int(player.position[1])+15))
                
                # Draw role symbol if known (or in standard mode)
                role_display = "?"
                if show_roles or player.known_role:
                    role_display = player.role.value
                
                if player.is_controlled:
                    role_text = self.small_font.render(role_display, True, (255, 255, 255))
                    self.screen.blit(role_text, (int(player.position[0])-30, int(player.position[1])-30))
                
                # Draw health bar
                bar_width = 40
                bar_height = 6
                x = int(player.position[0]) - bar_width // 2
                y = int(player.position[1]) - 25
                health_pct = player.hp / player.max_hp
                
                pygame.draw.rect(self.screen, (100, 0, 0), (x, y, bar_width, bar_height))
                pygame.draw.rect(self.screen, (0, 200, 0), (x, y, int(bar_width * health_pct), bar_height))
                pygame.draw.rect(self.screen, (255, 255, 255), (x, y, bar_width, bar_height), 1)
    
    def _draw_ui(self):
        """Draw UI elements"""
        # Draw phase info
        phase_name = self.phase_manager.current_phase.value
        phase_color = (255, 255, 0)
        
        # Different colors for different phases
        if self.phase_manager.current_phase in [GamePhase.NIGHT, GamePhase.SWARM_NIGHT]:
            phase_color = (100, 100, 255)
        elif self.phase_manager.current_phase in [GamePhase.SWARM_DAY, GamePhase.SWARM_PREPARATION]:
            phase_color = (255, 200, 0)
            
        phase_text = self.font.render(phase_name, True, phase_color)
        self.screen.blit(phase_text, (20, 20))
        
        # Draw day count
        day_text = self.font.render(f"Day {self.phase_manager.day_count}/{MAX_DAYS}", True, (255, 255, 255))
        self.screen.blit(day_text, (20, 60))
        
        # Draw bottom UI panel
        pygame.draw.rect(self.screen, (40, 40, 60), (0, self.SCREEN_HEIGHT - 100, self.SCREEN_WIDTH, 100))
        
        # Draw player info if player exists
        if self.players and self.current_player < len(self.players):
            player = self.players[self.current_player]
            role_display = player.role.value if player.known_role else "?"
            player_info = self.small_font.render(
                f"{player.name} ({role_display}) - HP: {int(player.hp)}/{int(player.max_hp)} - Level: {player.level} - EXP: {player.exp}/{player.level * 100}",
                True, (255, 255, 255)
            )
            self.screen.blit(player_info, (20, self.SCREEN_HEIGHT - 90))
            
            # Draw cards or weapons
            self._draw_cards()
            
            # Draw role ability description if role is known in swarm mode
            if self.game_mode == "swarm" and player.known_role and hasattr(player, 'role_ability'):
                role_ability = player.role_ability
                ability_text = self.small_font.render(
                    f"Role Ability: {role_ability.name} - {role_ability.description[:40]}...",
                    True, (200, 200, 100)
                )
                self.screen.blit(ability_text, (20, self.SCREEN_HEIGHT - 50))
        
        # Draw command prompt if in typing mode
        if self.typing_mode:
            prompt_text = self.small_font.render(f"Command: {self.command_input}_", True, (255, 255, 255))
            self.screen.blit(prompt_text, (20, self.SCREEN_HEIGHT - 30))
        elif self.game_mode == "standard":
            help_text = self.small_font.render("Press T to enter commands", True, (200, 200, 200))
            self.screen.blit(help_text, (20, self.SCREEN_HEIGHT - 30))
            
    def _draw_cards(self):
        """Draw player's cards or weapons"""
        if not self.players or self.current_player >= len(self.players):
            return
            
        player = self.players[self.current_player]
        
        # Swarm mode: Draw weapons
        if self.game_mode == "swarm" and hasattr(player, 'active_weapons'):
            weapon_x = self.SCREEN_WIDTH - 350
            for i, weapon in enumerate(player.active_weapons[:4]):  # Show max 4 weapons
                # Draw weapon slot
                pygame.draw.rect(self.screen, (60, 60, 80), (weapon_x + i * 80, self.SCREEN_HEIGHT - 90, 70, 60))
                
                # Draw weapon name
                if hasattr(weapon, 'name'):
                    name_parts = weapon.name.split(' ')
                    short_name = name_parts[0][:3] + "." if len(name_parts[0]) > 3 else name_parts[0]
                    name_text = self.small_font.render(short_name, True, (255, 255, 255))
                    self.screen.blit(name_text, (weapon_x + i * 80 + 5, self.SCREEN_HEIGHT - 75))
                
                # Draw weapon level
                if hasattr(weapon, 'level'):
                    level_text = self.small_font.render(f"Lv{weapon.level}", True, (255, 255, 0))
                    self.screen.blit(level_text, (weapon_x + i * 80 + 5, self.SCREEN_HEIGHT - 55))
                
                # Draw number key
                key_text = self.small_font.render(str(i+1), True, (255, 255, 0))
                self.screen.blit(key_text, (weapon_x + i * 80 + 5, self.SCREEN_HEIGHT - 90))
        
        # Standard mode: Draw cards
        elif player.cards:
            card_x = self.SCREEN_WIDTH - 350
            for i, card_id in enumerate(player.cards[:4]):  # Show max 4 cards
                card_info = self.card_system.get_card_info(card_id)
                if card_info:
                    # Draw card background
                    pygame.draw.rect(self.screen, (60, 60, 80), (card_x + i * 80, self.SCREEN_HEIGHT - 90, 70, 60))
                    
                    # Draw card symbol
                    symbol_text = self.font.render(card_info.get("symbol", "?"), True, (255, 255, 255))
                    self.screen.blit(symbol_text, (card_x + i * 80 + 25, self.SCREEN_HEIGHT - 75))
                    
                    # Draw number key
                    key_text = self.small_font.render(str(i+1), True, (255, 255, 0))
                    self.screen.blit(key_text, (card_x + i * 80 + 5, self.SCREEN_HEIGHT - 85))
    
    def _draw_debug_overlay(self):
        """Draw debug information"""
        debug_info = [
            f"FPS: {int(self.clock.get_fps())}",
            f"Game Mode: {self.game_mode}",
            f"Day: {self.phase_manager.day_count}",
            f"Phase: {self.phase_manager.current_phase.name}",
            f"Time left: {self.phase_manager.time_left:.1f}s",
            f"Players: {len(self.players)}"
        ]

        # Add auto-cast information if enabled
        if hasattr(self, 'skill_system') and self.skill_system.auto_cast_enabled:
            auto_cast_skills = len(self.skill_system.auto_cast_skills)
            debug_info.append(f"Auto-cast: {auto_cast_skills} skill(s)")

            # Show details for each auto-cast skill
            for skill_id, interval in self.skill_system.auto_cast_skills.items():
                timer = self.skill_system.auto_cast_timers.get(skill_id, 0)
                debug_info.append(f"  {skill_id}: {timer:.1f}/{interval:.1f}s")
        
        # Add mode-specific debug info
        if self.game_mode == "standard":
            debug_info.append(f"Monsters: {len(self.monsters) if hasattr(self, 'monsters') else 0}")
        elif self.game_mode == "swarm":
            debug_info.append(f"Clues: {len(self.swarm_manager.clues) if hasattr(self, 'swarm_manager') else 0}")
            
            # Add role information
            roles = {
                "PROTECTOR": sum(1 for p in self.players if p.true_role == PlayerRole.PROTECTOR),
                "TRAITOR": sum(1 for p in self.players if p.true_role == PlayerRole.TRAITOR),
                "CHAOS": sum(1 for p in self.players if p.true_role == PlayerRole.CHAOS)
            }
            debug_info.append(f"Roles: P:{roles['PROTECTOR']} T:{roles['TRAITOR']} C:{roles['CHAOS']}")
        
        y = 10
        for info in debug_info:
            text = self.debug_font.render(info, True, (255, 255, 0))
            self.screen.blit(text, (self.SCREEN_WIDTH - 200, y))
            y += 20
    
    def handle_event(self, event):
        """Process game events"""
        # Handle character selection events
        if self.phase_manager.current_phase == GamePhase.CHARACTER_SELECT:
            if event.type == pygame.KEYDOWN:
                # Select character with number keys
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                    character_index = event.key - pygame.K_1
                    self._select_character_by_index(character_index)
            return
            
        # Handle game over events
        if self.phase_manager.current_phase == GamePhase.GAME_OVER:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self._restart_game()
                elif event.key == pygame.K_ESCAPE:
                    self.game_running = False
            return
            
        # Handle card selection events if active
        if self.phase_manager.handle_card_selection_event(event):
            return
            
        # Handle key events
        if event.type == pygame.KEYDOWN:
            self._handle_key_event(event)
        
        # Handle mouse events
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_event(event)
    
    def _select_character_by_index(self, index):
        """Select character by index in the selection screen"""
        if not hasattr(self, 'skill_registry'):
            return False
            
        characters = list(self.skill_registry.characters.keys())
        if 0 <= index < len(characters):
            character_id = characters[index]
            return self.select_character(character_id)
            
        return False
    
    def _restart_game(self):
        """Restart the game with the same mode"""
        # Reset game state
        self.players = []
        if hasattr(self, 'swarm_manager'):
            self.swarm_manager.players = []
            self.swarm_manager.clues = []
            self.swarm_manager.day = 1
        
        if self.game_mode == "swarm":
            self.phase_manager.set_phase(GamePhase.CHARACTER_SELECT)
        else:
            self._add_players()
            self.phase_manager.day_count = 0
            self.phase_manager.start_day()
    
    def _handle_key_event(self, event):
        """Handle keyboard input"""
        # Global controls
        if event.key == pygame.K_ESCAPE:
            self.paused = not self.paused
        elif event.key == pygame.K_F3:
            self.debug_mode = not self.debug_mode
        elif event.key == pygame.K_x:
            self.game_running = False

        # Auto-cast controls
        elif event.key == pygame.K_F2 and hasattr(self, 'skill_system'):
            # Toggle auto-cast system
            enabled = self.skill_system.toggle_auto_cast()
            status = "ON" if enabled else "OFF"
            self.ui_bridge.show_notification(f"Auto-cast: {status}", "info")
            
        # Swarm mode specific controls
        if self.game_mode == "swarm":
            if event.key == pygame.K_e:
                self._examine_nearby_clue()
            
        # Standard mode specific controls
        else:
            # Toggle auto-combat with A key
            if event.key == pygame.K_a and not self.typing_mode:
                self.auto_combat_active = not self.auto_combat_active
                status = "ON" if self.auto_combat_active else "OFF"
                self.ui_bridge.show_notification(f"Auto-combat: {status}", "info")
            
        # Command mode
        if event.key == pygame.K_t and not self.typing_mode:
            self.typing_mode = True
            self.command_input = ""
        elif self.typing_mode:
            if event.key == pygame.K_RETURN:
                self._process_command()
                self.typing_mode = False
            elif event.key == pygame.K_ESCAPE:
                self.typing_mode = False
            elif event.key == pygame.K_BACKSPACE:
                self.command_input = self.command_input[:-1]
            else:
                if event.unicode.isprintable():
                    self.command_input += event.unicode
                    
        # Skill auto-cast configuration with ALT+number keys
        elif pygame.key.get_mods() & pygame.KMOD_ALT and event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
            if hasattr(self, 'skill_system'):
                index = event.key - pygame.K_1
                player = self.get_current_player()

                if player and index < len(player.skills):
                    skill = player.skills[index]

                    # Toggle auto-cast for this skill
                    if skill.skill_id in self.skill_system.auto_cast_skills:
                        # Disable auto-cast
                        result = self.skill_system.set_auto_cast_skill(skill.skill_id, enabled=False)
                    else:
                        # Enable auto-cast with default interval
                        result = self.skill_system.set_auto_cast_skill(skill.skill_id)

                    self.ui_bridge.show_notification(result, "info")

        # Card/weapon usage with number keys
        elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
            index = event.key - pygame.K_1
            if self.game_mode == "swarm":
                self._use_weapon(index)
            else:
                self._use_card(index)
    
    def _handle_mouse_event(self, event):
        """Handle mouse input"""
        if event.button == 1:  # Left click
            # Attack if in day phase
            if self.phase_manager.current_phase in [GamePhase.DAY, GamePhase.SWARM_DAY]:
                self._attack_at_cursor()
    
    def _examine_nearby_clue(self):
        """Examine nearby clue in Swarm mode"""
        if not self.game_mode == "swarm" or not hasattr(self, 'swarm_manager'):
            return
            
        player = self.get_current_player()
        if not player:
            return
            
        # Find nearest clue
        nearest_clue_index = -1
        nearest_distance = float('inf')
        
        for i, clue in enumerate(self.swarm_manager.clues):
            if clue.get("collected", False):
                continue
                
            pos = clue.get("position", (0, 0))
            distance = ((player.position[0] - pos[0]) ** 2 + (player.position[1] - pos[1]) ** 2) ** 0.5
            
            if distance < 100 and distance < nearest_distance:
                nearest_distance = distance
                nearest_clue_index = i
        
        # Process the clue if one was found
        if nearest_clue_index >= 0:
            result = self.swarm_manager.process_clue_collection(player, nearest_clue_index)
            if result.get("success", False):
                self.ui_bridge.show_notification(result.get("message", "Found a clue!"), "success")
                
                # If role was revealed, show special notification
                if result.get("role_revealed", False):
                    role_message = f"You discovered your true role: {result.get('role')}!"
                    self.ui_bridge.show_notification(role_message, "warning")
    
    def _process_command(self):
        """Process command input"""
        if not self.command_input.strip():
            return
            
        cmd = self.command_input.strip().lower()
        parts = cmd.split()
        
        # Handle basic commands
        if cmd in ["help", "h"]:
            self.ui_bridge.show_notification("Available commands: help, restart, quit", "info")
        elif cmd in ["quit", "exit", "q"]:
            self.game_running = False
        elif cmd in ["restart", "reset"]:
            self._restart_game()
            self.ui_bridge.show_notification("Game restarted!", "info")
        elif cmd == "debug":
            self.debug_mode = not self.debug_mode
            status = "ON" if self.debug_mode else "OFF"
            self.ui_bridge.show_notification(f"Debug mode: {status}", "info")
        elif cmd == "reveal":
            # Debug command to reveal roles
            if self.game_mode == "swarm" and self.debug_mode:
                player = self.get_current_player()
                if player and not player.known_role:
                    player.discover_role()
                    self.ui_bridge.show_notification(f"Your role is: {player.role.name}", "warning")
        else:
            # Unknown command
            self.ui_bridge.show_notification(f"Unknown command: {cmd}", "error")
            
        self.command_input = ""
    
    def _use_card(self, card_index):
        """Use a card from player's hand (standard mode)"""
        player = self.get_current_player()
        if not player:
            return
            
        if 0 <= card_index < len(player.cards):
            card_id = player.cards[card_index]
            card_info = self.card_system.get_card_info(card_id)
            
            if card_info:
                # Use card
                result = self.card_system.use_card(player, card_id, self.phase_manager.current_phase)
                if result.get("success", False):
                    self.ui_bridge.show_notification(result.get("message", "Card used!"), "success")
                    player.cards.pop(card_index)
                else:
                    self.ui_bridge.show_notification(result.get("message", "Failed to use card."), "error")
    
    def _use_weapon(self, weapon_index):
        """Use a weapon from player's arsenal (swarm mode)"""
        player = self.get_current_player()
        if not player or not hasattr(player, 'active_weapons'):
            return
            
        if 0 <= weapon_index < len(player.active_weapons):
            weapon = player.active_weapons[weapon_index]
            
            if hasattr(weapon, 'is_ready') and weapon.is_ready():
                result = player.use_weapon(weapon_index, self.mouse_pos)
                if result:
                    self.ui_bridge.show_notification(f"Used {weapon.name}!", "success")
                    
                    # Record suspicious action if using weapon against another player
                    if self.game_mode == "swarm" and player.true_role == PlayerRole.TRAITOR:
                        # Check if any player is near target position
                        for other_player in self.players:
                            if other_player.id != player.id and other_player.is_alive:
                                distance = ((other_player.position[0] - self.mouse_pos[0]) ** 2 + 
                                          (other_player.position[1] - self.mouse_pos[1]) ** 2) ** 0.5
                                if distance < 50:
                                    # This is suspicious - attacking another player
                                    self.swarm_manager.record_suspicious_action(
                                        player, 
                                        "attack", 
                                        f"Attacked {other_player.name}"
                                    )
            else:
                self.ui_bridge.show_notification(f"{weapon.name} is on cooldown!", "warning")
    
    def _attack_at_cursor(self):
        """Attack at the cursor position"""
        player = self.get_current_player()
        if not player:
            return
            
        # Calculate attack direction
        direction = (self.mouse_pos[0] - player.position[0], self.mouse_pos[1] - player.position[1])
        
        # Check if targeting another player (for role-based effects)
        is_player_target = False
        target_player = None
        
        # For swarm mode, check if we're targeting another player
        if self.game_mode == "swarm":
            for other_player in self.players:
                if other_player.id != player.id and other_player.is_alive:
                    # Check if mouse position is near this player
                    dist_sq = ((other_player.position[0] - self.mouse_pos[0]) ** 2 + 
                              (other_player.position[1] - self.mouse_pos[1]) ** 2)
                    
                    if dist_sq < 900:  # 30 pixel radius for targeting
                        is_player_target = True
                        target_player = other_player
                        break
        
        # Use the player's passive skill if available, passing player targeting info
        if hasattr(player, 'passive_skill') and player.passive_skill:
            result = player.attack(self.mouse_pos, is_player_target)
            
            if result:
                # Handle swarm mode role-based attack notifications
                if self.game_mode == "swarm" and is_player_target:
                    # Record a suspicious action if a traitor attacks another player
                    if player.true_role == PlayerRole.TRAITOR:
                        self.swarm_manager.record_suspicious_action(
                            player, 
                            "attack", 
                            f"Attacked {target_player.name}"
                        )
                    
                    # Different notification based on player role
                    if player.true_role == PlayerRole.PROTECTOR and player.known_role:
                        self.ui_bridge.show_notification(
                            f"{result.get('description', 'Attack!')} (Reduced damage as Protector)",
                            "info"
                        )
                    elif player.true_role == PlayerRole.TRAITOR and player.known_role:
                        # Check if alone with target
                        is_alone = self.swarm_manager.check_player_alone(player)
                        if is_alone:
                            self.ui_bridge.show_notification(
                                f"{result.get('description', 'Attack!')} (Bonus damage when alone)",
                                "warning"
                            )
                        else:
                            self.ui_bridge.show_notification(result.get("description", "Attack!"), "info")
                    else:
                        self.ui_bridge.show_notification(result.get("description", "Attack!"), "info")
                else:
                    # Standard notification
                    self.ui_bridge.show_notification(result.get("description", "Attack!"), "info")
        else:
            # Generic attack message if no passive skill
            self.ui_bridge.show_notification("Attack!", "info")
    
    def get_current_player(self):
        """Get currently controlled player"""
        if not self.players or self.current_player >= len(self.players):
            return None
        return self.players[self.current_player]
    
    def _wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            # Test with current line + new word
            test_line = ' '.join(current_line + [word])
            width, _ = font.size(test_line)
            
            if width <= max_width:
                current_line.append(word)
            else:
                # Line is full, start new line
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Single word is too long
                    lines.append(word)
                    current_line = []
        
        # Don't forget the last line
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
    
    def run(self):
        """Main game loop"""
        try:
            while self.game_running:
                dt = self.clock.tick(FPS) / 1000.0
                
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.game_running = False
                    else:
                        self.handle_event(event)
                
                # Update and draw
                self.update(dt)
                self.draw()
                
        except Exception as e:
            self.logger.error(f"Game crashed: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            pygame.quit()
            sys.exit()