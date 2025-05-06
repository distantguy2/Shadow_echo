# src/core/input_handler.py - INPUT PROCESSING

import pygame

class InputHandler:
    """Handles all input events"""
    
    def __init__(self, game):
        self.game = game
        self.typing_mode = False
        self.command_input = ""
        
        # Keybinds
        self.keybinds = {
            'skill1': pygame.K_q,
            'skill2': pygame.K_e,
            'skill3': pygame.K_r,
            'card1': pygame.K_1,
            'card2': pygame.K_2,
            'card3': pygame.K_3,
            'card4': pygame.K_4,
            'card5': pygame.K_5,
        }
    
    def handle_event(self, event):
        """Process pygame events"""
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)
    
    def _handle_keydown(self, event):
        """Handle keydown events"""
        # Debug commands
        if event.key == pygame.K_F1:
            self.toggle_debug_mode()
        elif event.key == pygame.K_F2:
            self.toggle_god_mode()
        
        # Exit game
        elif event.key == pygame.K_x:
            self.game.game_running = False
        
        # Command input mode
        elif event.key == pygame.K_t and not self.typing_mode:
            self.start_typing()
        elif self.typing_mode:
            self.handle_typing(event)
        
        # Card usage
        elif not self.typing_mode:
            self.handle_card_input(event)
            self.handle_skill_input(event)
        
        # Skill selection
        if self.is_skill_selection_phase():
            self.handle_skill_selection(event)
    
    def toggle_debug_mode(self):
        self.game.debug_mode = not self.game.debug_mode
        self.game.ui_bridge.show_notification(
            f"Debug mode: {'ON' if self.game.debug_mode else 'OFF'}", "info"
        )
    
    def toggle_god_mode(self):
        self.game.god_mode = not self.game.god_mode
        player = self.game.player_manager.get_current_player()
        
        if self.game.god_mode:
            player.hp = 1000
            player.max_hp = 1000
        else:
            player.max_hp = 100
            player.hp = 100
        
        self.game.ui_bridge.show_notification(
            f"God mode: {'ON' if self.game.god_mode else 'OFF'}", "info"
        )
    
    def start_typing(self):
        self.typing_mode = True
        self.command_input = ""
    
    def handle_typing(self, event):
        if event.key == pygame.K_RETURN:
            if self.command_input.strip():
                result = self.game.command_handler.process_command(self.command_input)
                self.game.ui_bridge.show_notification(result, "info")
            self.command_input = ""
            self.typing_mode = False
        elif event.key == pygame.K_ESCAPE:
            self.command_input = ""
            self.typing_mode = False
        elif event.key == pygame.K_BACKSPACE:
            self.command_input = self.command_input[:-1]
        else:
            if event.unicode and event.unicode.isprintable():
                self.command_input += event.unicode
    
    def handle_card_input(self, event):
        player = self.game.player_manager.get_current_player()
        cards = player.cards
        key_map = {
            pygame.K_1: 0,
            pygame.K_2: 1,
            pygame.K_3: 2,
            pygame.K_4: 3,
            pygame.K_5: 4,
        }
        if event.key in key_map and key_map[event.key] < len(cards):
            self.game.card_system.use_card(player, key_map[event.key])
    
    def handle_skill_input(self, event):
        if event.key == self.keybinds['skill1']:
            self.game.skill_system.use_skill(0)
        elif event.key == self.keybinds['skill2']:
            self.game.skill_system.use_skill(1)
        elif event.key == self.keybinds['skill3']:
            self.game.skill_system.use_skill(2)

    def is_skill_selection_phase(self):
        return self.game.phase_manager.current_phase.name == "SKILL_SELECT"

    def handle_skill_selection(self, event):
        ui = self.game.skill_select_ui
        if event.key == pygame.K_1:
            ui.selected_skill = 0
        elif event.key == pygame.K_2:
            ui.selected_skill = 1
        elif event.key == pygame.K_3:
            ui.selected_skill = 2
        elif event.key == pygame.K_r and ui.rolls_left > 0:
            ui.rolls_left -= 1
            ui.roll_new_skills()
        elif event.key == pygame.K_RETURN and ui.selected_skill is not None:
            selected_skill = ui.skill_options[ui.selected_skill]
            self.game.player_manager.get_current_player().skills.append(selected_skill)
            self.game.phase_manager.advance_phase()
