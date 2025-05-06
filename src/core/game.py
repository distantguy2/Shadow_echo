# src/core/game.py - COMPLETE IMPLEMENTATION

import pygame
import sys
import random
import math
from pathlib import Path


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

# Import from core modules with updated paths
from src.core.entities import Player, PlayerRole
from src.core.phase_manager import PhaseManager, GamePhase
from src.core.ui import SkillSelectUI
from src.core.skills import SKILL_LIBRARY

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
    
    def __init__(self):
        # Initialize essential attributes
        self.screen = None
        self.clock = None
        self.font = None
        self.small_font = None
        self.game_running = True
        self.debug_mode = False
        self.paused = False
        self.auto_combat_active = True
        
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
        
        # Initialize game state
        self._add_players()
        
        # Start first day
        self.phase_manager.start_day()
        
    def _setup_pygame(self):
        """Initialize pygame and display settings"""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Shadow Echo RPG")
        self.clock = pygame.time.Clock()
        
        # Initialize fonts
        self.font = pygame.font.SysFont('Arial', 32)
        self.small_font = pygame.font.SysFont('Arial', 24)
        self.debug_font = pygame.font.SysFont('Courier', 14)
        
    def _init_game_systems(self):
        
        """Initialize all game systems"""
        # Core systems
        self.phase_manager = PhaseManager(self)
        self.ui_bridge = UIBridge(self)
        self.auto_combat = AutoCombatSystem(self)
        
        # Thêm player_manager trống để tương thích với monsters.py
        self.player_manager = type('obj', (object,), {
            'players': self.players,
            'get_current_player': lambda self: self.get_current_player()
        })
    
        # Entity systems
        self.monster_system = MonsterSystem(self)
        if NPCSystem:
            self.npc_system = NPCSystem(self)
    
        # Gameplay systems
        self.card_system = CardSystem(self)
    
        # Card generation
        self.card_generator = CardGenerator(self)
    
    def _add_players(self):
        """Initialize players"""
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
            
    def update(self, dt):
        """Update all game systems"""
        if self.paused:
            return
            
        # Update mouse position
        self.mouse_pos = pygame.mouse.get_pos()
            
        # Update phase manager
        self.phase_manager.update(dt)

         # Update auto-combat system
        self.auto_combat.update(dt)
    
        # Update monsters
        self.monster_system.update(dt)
        
        # Update NPCs if available
        if hasattr(self, 'npc_system'):
            self.npc_system.update(dt)
            
        # Update UI
        self.ui_bridge.update(dt)
        
        # Update player movement for controlled player
        self._update_player_movement(dt)
            
    def _update_player_movement(self, dt):
        """Handle player movement controls"""
        if self.typing_mode:
            return
            
        player = self.players[self.current_player]
        if not player.is_controlled:
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
        
        # Draw monsters
        self.monster_system.draw(self.screen)

        # Draw auto-combat indicators (nếu cần)
        if hasattr(self, 'auto_combat'):
            self.auto_combat.draw(self.screen)
        
        # Draw NPCs if available
        if hasattr(self, 'npc_system'):
            self.npc_system.draw(self.screen)
        
        # Draw players
        self._draw_players()
        
        # Draw phase-specific UI
        self.phase_manager.draw()
        
        # Draw UI elements
        self._draw_ui()
        
        # Debug info
        if self.debug_mode:
            self._draw_debug_overlay()
            
        pygame.display.flip()
        
    def _draw_players(self):
        """Draw all players"""
        for player in self.players:
            if player.is_alive:
                # Determine color based on role
                if player.is_controlled:
                    color = (0, 255, 255)  # Cyan for controlled player
                elif player.role == PlayerRole.PROTECTOR:
                    color = (0, 200, 0)    # Green for protector
                elif player.role == PlayerRole.TRAITOR:
                    color = (200, 0, 0)    # Red for traitor
                elif player.role == PlayerRole.CHAOS:
                    color = (200, 0, 200)  # Purple for chaos
                else:
                    color = (100, 100, 255) # Blue for unknown
                
                # Draw player (as a rectangle for now)
                pygame.draw.rect(self.screen, color, 
                               (int(player.position[0])-10, int(player.position[1])-10, 20, 20))
                
                # Draw name and level
                name_text = self.small_font.render(
                    f"{player.name} Lv.{player.level}", True, (255, 255, 255)
                )
                self.screen.blit(name_text, (int(player.position[0])-30, int(player.position[1])+15))
                
                # Draw health bar
                bar_width = 40
                bar_height = 6
                x = int(player.position[0]) - bar_width // 2
                y = int(player.position[1]) - 25
                health_pct = player.hp / 100  # Assuming max HP is 100
                
                pygame.draw.rect(self.screen, (100, 0, 0), (x, y, bar_width, bar_height))
                pygame.draw.rect(self.screen, (0, 200, 0), (x, y, int(bar_width * health_pct), bar_height))
                pygame.draw.rect(self.screen, (255, 255, 255), (x, y, bar_width, bar_height), 1)
    
    def _draw_ui(self):
        """Draw UI elements"""
        # Draw phase info
        phase_color = (255, 255, 0) if self.phase_manager.current_phase == GamePhase.DAY else (100, 100, 255)
        phase_text = self.font.render(self.phase_manager.get_phase_display_text(), True, phase_color)
        self.screen.blit(phase_text, (20, 20))
        
        # Draw day count
        day_text = self.font.render(f"Day {self.phase_manager.day_count}/{MAX_DAYS}", True, (255, 255, 255))
        self.screen.blit(day_text, (20, 60))
        
        # Draw bottom UI panel
        pygame.draw.rect(self.screen, (40, 40, 60), (0, self.SCREEN_HEIGHT - 100, self.SCREEN_WIDTH, 100))
        
        # Draw player info
        player = self.players[self.current_player]
        player_info = self.small_font.render(
            f"{player.name} - HP: {int(player.hp)}/100 - Level: {player.level} - EXP: {player.exp}/{player.level * 100}",
            True, (255, 255, 255)
        )
        self.screen.blit(player_info, (20, self.SCREEN_HEIGHT - 90))
        
        # Draw cards
        self._draw_cards()
        
        # Draw command prompt if in typing mode
        if self.typing_mode:
            prompt_text = self.small_font.render(f"Command: {self.command_input}_", True, (255, 255, 255))
            self.screen.blit(prompt_text, (20, self.SCREEN_HEIGHT - 50))
        else:
            help_text = self.small_font.render("Press T to enter commands", True, (200, 200, 200))
            self.screen.blit(help_text, (20, self.SCREEN_HEIGHT - 50))
            
    def _draw_cards(self):
        """Draw player's cards"""
        player = self.players[self.current_player]
        
        if player.cards:
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
            f"Day: {self.phase_manager.day_count}",
            f"Phase: {self.phase_manager.current_phase.name}",
            f"Time left: {self.phase_manager.time_left:.1f}s",
            f"Players: {len(self.players)}",
            f"Monsters: {len(self.monsters)}"
        ]
        
        y = 10
        for info in debug_info:
            text = self.debug_font.render(info, True, (255, 255, 0))
            self.screen.blit(text, (self.SCREEN_WIDTH - 200, y))
            y += 20
    
    def handle_event(self, event):
        """Process game events"""
        # Handle card selection events if active
        if self.phase_manager.handle_card_selection_event(event):
            return
            
        # Handle key events
        if event.type == pygame.KEYDOWN:
            self._handle_key_event(event)
        
        # Handle mouse events
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_event(event)
    
    def _handle_key_event(self, event):
        """Handle keyboard input"""
        # Global controls
        if event.key == pygame.K_ESCAPE:
            self.paused = not self.paused
        elif event.key == pygame.K_F3:
            self.debug_mode = not self.debug_mode
        elif event.key == pygame.K_x:
            self.game_running = False
            
        # Toggle auto-combat with A key
        elif event.key == pygame.K_a and not self.typing_mode:
            self.auto_combat_active = not self.auto_combat_active
            status = "ON" if self.auto_combat_active else "OFF"
            self.ui_bridge.show_notification(f"Auto-combat: {status}", "info")
            
        # Command mode
        elif event.key == pygame.K_t and not self.typing_mode:
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
                    
        # Card usage with number keys
        elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
            card_index = event.key - pygame.K_1
            self._use_card(card_index)
    
    def _handle_mouse_event(self, event):
        """Handle mouse input"""
        if event.button == 1:  # Left click
            # Attack if in day phase
            if self.phase_manager.is_day_phase():
                self._attack_at_cursor()
    
    def _process_command(self):
        """Process command input"""
        if not self.command_input.strip():
            return
            
        # TODO: Implement command parsing
        self.ui_bridge.show_notification(f"Command entered: {self.command_input}", "info")
        self.command_input = ""
    
    def _use_card(self, card_index):
        """Use a card from player's hand"""
        player = self.players[self.current_player]
        
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
    
    def _attack_at_cursor(self):
        """Attack at the cursor position"""
        player = self.players[self.current_player]
        
        # Calculate attack direction
        direction = (self.mouse_pos[0] - player.position[0], self.mouse_pos[1] - player.position[1])
        
        # TODO: Implement proper attack mechanics
        self.ui_bridge.show_notification("Attack!", "info")
    
    def get_current_player(self):
        """Get currently controlled player"""
        return self.players[self.current_player]
    
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
