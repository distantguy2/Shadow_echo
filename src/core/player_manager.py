# src/core/player_manager.py - PLAYER MANAGEMENT

import random
import math
import pygame
from .core.entities import Player, PlayerRole, AlignmentSystem

class PlayerManager:
    """Manages all player-related operations including cards, alignment, and clues"""
    
    def __init__(self, game):
        self.game = game
        self.players = []
        self.current_player = 0

        # Initialize systems
        from ..systems import CardSystem, AlignmentManager, ClueGenerator
        from ..ui.card_selection_ui import CardSelectionUI
        from ..systems.card_generator import CardGenerator
        
        self.card_system = CardSystem(game)
        self.alignment_manager = AlignmentManager(game)
        self.clue_generator = ClueGenerator(game)
        self.card_generator = CardGenerator(game)
        self.card_selection_ui = None

    def initialize_players(self):
        """Create initial players with randomized roles and positions"""
        names = ["Alice", "Bob", "Charlie"]
        roles = [PlayerRole.PROTECTOR, PlayerRole.TRAITOR, PlayerRole.CHAOS]
        random.shuffle(roles)
        
        for i, name in enumerate(names):
            player = Player(id=i, name=name)
            player.position = [100.0 + i * 100.0, 500.0]
            if i == 0:
                player.is_controlled = True
            player.alignment = AlignmentSystem()
            player.true_role = roles[i]
            player.role = PlayerRole.UNKNOWN
            player.clues = []
            player.cards = []
            self.players.append(player)

    def distribute_initial_cards(self):
        """Distribute initial cards to all players at game start"""
        for player in self.players:
            self.card_system.deal_initial_cards(player)
            card_names = [self.card_system.get_card_info(cid).get("name", cid) for cid in player.cards]
            self.game.logger.info(f"Dealt initial cards to {player.name}: {', '.join(card_names)}")

    def use_card(self, card_index: int):
        """Attempt to use a player's card"""
        player = self.get_current_player()
        if not 0 <= card_index < len(player.cards):
            self.game.ui_bridge.show_notification("Invalid card selection", "error")
            return False

        card_id = player.cards[card_index]
        result = self.card_system.use_card(player, card_id, self.game.phase_manager.phase)

        if result.get("success"):
            self.game.ui_bridge.show_notification(result["message"], "success")
            self.clue_generator.generate_card_usage_clue(player, card_id)
            self.alignment_manager.check_role_reveal(player)
            player.cards.pop(card_index)
            return True
        else:
            self.game.ui_bridge.show_notification(result["message"], "error")
            return False

    def start_night_card_selection(self):
        """Start UI or auto card selection at night"""
        for player in self.players:
            if not player.is_alive:
                continue

            card_options = self.card_generator.generate_card_options(player.level)
            player.card_options = card_options

            if player.is_controlled:
                self.card_selection_ui = CardSelectionUI(self.game)
                self.card_selection_ui.set_card_options(card_options)
                self.game.phase_manager.pause_phase()
            else:
                chosen_card = random.choice(card_options)
                self.card_system.process_night_card(player, chosen_card)

    def update(self, dt):
        """Update all players and UI logic"""
        if self.card_selection_ui:
            self.card_selection_ui.update(dt)
            if self.card_selection_ui.selected_card_index is not None:
                selected = self.card_selection_ui.card_options[self.card_selection_ui.selected_card_index]
                player = self.get_current_player()
                self.card_system.process_night_card(player, selected)
                self.card_selection_ui = None
                self.game.phase_manager.resume_phase()
            return

        for player in self.players:
            if player.is_alive:
                if player.is_controlled:
                    self.handle_controlled_player_movement(player, dt)
                else:
                    self.handle_ai_player(player, dt)

                self.clue_generator.check_and_generate_clues(player)
                self.alignment_manager.update_player_alignment(player)

    def handle_event(self, event):
        """Forward input to card selection UI if active"""
        if self.card_selection_ui:
            return self.card_selection_ui.handle_event(event)
        return None

    def handle_controlled_player_movement(self, player, dt):
        if self.game.input_handler.typing_mode:
            return

        keys = pygame.key.get_pressed()
        dx = dy = 0

        speed_multiplier = 2.0 if self.game.god_mode else 1.0
        speed = 200 * dt * speed_multiplier

        if keys[pygame.K_w]: dy = -speed
        if keys[pygame.K_s]: dy = speed
        if keys[pygame.K_a]: dx = -speed
        if keys[pygame.K_d]: dx = speed

        new_x = player.position[0] + dx
        new_y = player.position[1] + dy

        if 20 <= new_x <= self.game.SCREEN_WIDTH - 20:
            player.position[0] = new_x
        if 20 <= new_y <= self.game.SCREEN_HEIGHT - 70:
            player.position[1] = new_y

    def handle_ai_player(self, player, dt):
        nearest_monster = self.game.combat_system.find_nearest_monster(player)
        if nearest_monster:
            dx = nearest_monster.position[0] - player.position[0]
            dy = nearest_monster.position[1] - player.position[1]
            dist = math.hypot(dx, dy)
            if dist > 0:
                player.position[0] += (dx / dist) * 200 * 0.5 * dt
                player.position[1] += (dy / dist) * 200 * 0.5 * dt

    def draw(self, screen):
        for player in self.players:
            if not player.is_alive:
                continue

            if player.is_controlled:
                color = (0, 255, 255)
            elif player.role == PlayerRole.PROTECTOR:
                color = (0, 200, 0)
            elif player.role == PlayerRole.TRAITOR:
                color = (200, 0, 0)
            elif player.role == PlayerRole.CHAOS:
                color = (200, 0, 200)
            else:
                color = (100, 100, 255)

            pygame.draw.rect(screen, color, (int(player.position[0]) - 10, int(player.position[1]) - 10, 20, 20))
            name_text = self.game.small_font.render(f"{player.name} Lv.{player.level}", True, (255, 255, 255))
            screen.blit(name_text, (int(player.position[0]) - 30, int(player.position[1]) + 15))

    def get_current_player(self):
        return self.players[self.current_player]

    def share_exp_with_nearby_players(self, killer_player, exp_amount):
        from ...config.settings import EXP_SHARE_RADIUS, EXP_SHARE_RATE

        nearby_players = []
        for player in self.players:
            if player.is_alive and player.id != killer_player.id:
                distance = self._calculate_distance(killer_player.position, player.position)
                if distance <= EXP_SHARE_RADIUS:
                    nearby_players.append(player)

        if nearby_players:
            shared_exp = int(exp_amount * EXP_SHARE_RATE)
            for player in nearby_players:
                player.add_exp(shared_exp)
                self.game.ui_bridge.show_notification(f"{player.name} gained {shared_exp} EXP (shared)", "success")

        killer_player.add_exp(exp_amount)
        self.game.ui_bridge.show_notification(f"{killer_player.name} gained {exp_amount} EXP", "success")

    def _calculate_distance(self, pos1, pos2):
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        return math.hypot(dx, dy)
