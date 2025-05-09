# src/core/card_selection_ui.py

import pygame
import math
import random
from typing import List, Dict, Optional, Tuple, Any
from src.core.skill_system import get_skill_registry
from src.utils.font_utils import get_font, render_text, normalize_vietnamese

class CardSelectionUI:
    """Card selection UI for selecting cards in various game contexts"""
    
    def __init__(self, game, card_type="all"):
        self.game = game
        self.screen = game.screen
        self.screen_width = game.screen.get_width()
        self.screen_height = game.screen.get_height()
        self.skill_registry = get_skill_registry()
        self.card_type = card_type  # "all", "weapon", "character", "role", etc.
        
        # Fonts with Vietnamese support
        self.title_font = get_font(24, bold=True)
        self.desc_font = get_font(18)
        self.small_font = get_font(14)
        
        # Card properties
        self.card_width = 200
        self.card_height = 360
        self.card_spacing = 30
        
        # Card options and selection
        self.card_options: List[Dict[str, Any]] = []
        self.selected_card_index: Optional[int] = None
        self.hover_card_index: Optional[int] = None
        self.time_left = 15.0  # 15 seconds to select
        
        # Background overlay
        self.overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        
        # Animation
        self.animation_time = 0
        self.glow_intensity = 0
        
        # Load cards based on type
        self._load_cards()
    
    def _load_cards(self):
        """Load cards based on the specified card type"""
        cards = []
        
        # Load based on card_type
        if self.card_type in ["all", "weapon"]:
            self._load_weapon_cards(cards)
            
        if self.card_type in ["all", "character"]:
            self._load_character_cards(cards)
            
        if self.card_type in ["all", "role"]:
            self._load_role_cards(cards)
        
        self.card_options = cards
    
    def _load_weapon_cards(self, cards):
        """Load weapon cards from registry"""
        for weapon_id, weapon_data in self.skill_registry.weapons.items():
            category = weapon_data.get('category', 'unknown')
            cards.append({
                'id': weapon_id,
                'type': 'weapon',
                'subtype': category,
                'name': weapon_data['data']['name'],
                'description': weapon_data['data']['description'],
                'icon': weapon_data['data'].get('icon', '🗡️'),
                'data': weapon_data['data']
            })
    
    def _load_character_cards(self, cards):
        """Load character cards from registry"""
        for char_id, char_data in self.skill_registry.characters.items():
            passive_skill = {}
            if 'passive_skill' in char_data:
                passive_skill = char_data['passive_skill']
                
            cards.append({
                'id': char_id,
                'type': 'character',
                'name': char_data['name'],
                'description': char_data['description'],
                'icon': char_data.get('icon', '👤'),
                'passive_skill': passive_skill,
                'potential_roles': char_data.get('potential_roles', []),
                'data': char_data
            })
    
    def _load_role_cards(self, cards):
        """Load role cards from registry"""
        for role_id, role_data in self.skill_registry.roles.items():
            special_ability = {}
            if 'special_ability' in role_data:
                special_ability = role_data['special_ability']
                
            cards.append({
                'id': role_id,
                'type': 'role',
                'name': role_data['name'],
                'description': role_data['description'],
                'icon': role_data.get('symbol', '?'),
                'special_ability': special_ability,
                'data': role_data
            })
    
    def set_card_options(self, cards: List[Dict[str, Any]]):
        """Set the card options to display"""
        self.card_options = cards
        self.selected_card_index = None
        self.hover_card_index = None
    
    def update(self, dt: float):
        """Update the UI state"""
        # Update timer
        self.time_left -= dt
        if self.time_left <= 0:
            # Auto-select if time runs out
            if self.selected_card_index is None and self.card_options:
                self.selected_card_index = 0
        
        # Update animation
        self.animation_time += dt
        self.glow_intensity = (math.sin(self.animation_time * 2) + 1) / 2  # 0 to 1 sine wave
    
    def handle_event(self, event):
        """Handle mouse and keyboard events"""
        if event.type == pygame.MOUSEMOTION:
            # Handle hover
            self.hover_card_index = self._get_card_at_position(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Handle left-click
            clicked_card = self._get_card_at_position(event.pos)
            if clicked_card is not None:
                self.selected_card_index = clicked_card
                # Return result immediately for single-click selection
                selected_card = self.card_options[clicked_card]
                return {
                    "type": selected_card.get('type', 'unknown'),
                    "id": selected_card.get('id', 'unknown'),
                    "data": selected_card.get('data', {})
                }
        
        # Check for confirm button click (if a card is selected but we're using confirm button)
        elif (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and 
              self.selected_card_index is not None):
            button_width = 100
            button_height = 40
            button_x = (self.screen_width - button_width) / 2
            button_y = self.screen_height - 100
            button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
            
            if button_rect.collidepoint(event.pos):
                selected_card = self.card_options[self.selected_card_index]
                return {
                    "type": selected_card.get('type', 'unknown'),
                    "id": selected_card.get('id', 'unknown'),
                    "data": selected_card.get('data', {})
                }
        
        # Keyboard shortcuts for selection
        elif event.type == pygame.KEYDOWN:
            # Number keys 1-9 for quick selection
            if pygame.K_1 <= event.key <= pygame.K_9:
                index = event.key - pygame.K_1
                if 0 <= index < len(self.card_options):
                    self.selected_card_index = index
                    selected_card = self.card_options[index]
                    return {
                        "type": selected_card.get('type', 'unknown'),
                        "id": selected_card.get('id', 'unknown'),
                        "data": selected_card.get('data', {})
                    }
            
            # Enter to confirm selection
            elif event.key == pygame.K_RETURN and self.selected_card_index is not None:
                selected_card = self.card_options[self.selected_card_index]
                return {
                    "type": selected_card.get('type', 'unknown'),
                    "id": selected_card.get('id', 'unknown'),
                    "data": selected_card.get('data', {})
                }
        
        return None
    
    def _get_card_at_position(self, pos) -> Optional[int]:
        """Get the card index at the given mouse position"""
        # Calculate the starting X position for the first card
        total_width = min(len(self.card_options), 4) * (self.card_width + self.card_spacing) - self.card_spacing
        start_x = (self.screen_width - total_width) / 2
        
        # Only show 4 cards at a time
        visible_cards = self.card_options[:4]
        
        for i, card in enumerate(visible_cards):
            card_x = start_x + i * (self.card_width + self.card_spacing)
            card_rect = pygame.Rect(card_x, (self.screen_height - self.card_height) / 2, 
                                  self.card_width, self.card_height)
            
            if card_rect.collidepoint(pos):
                return i
        
        return None
    
    def draw(self):
        """Draw the card selection UI"""
        # Draw the background overlay
        self.screen.blit(self.overlay, (0, 0))
        
        # Draw title based on card type
        title = f"Select {self.card_type.capitalize()}"
        if self.card_type == "all":
            title = "Select Card"
        
        time_text = render_text(self.title_font, f"{title}: {int(self.time_left)}s", (255, 255, 255))
        time_rect = time_text.get_rect(center=(self.screen_width / 2, 50))
        self.screen.blit(time_text, time_rect)

        # Draw instructions
        instructions = render_text(self.small_font, "Click to select or press number keys (1-4)", (200, 200, 200))
        instructions_rect = instructions.get_rect(center=(self.screen_width / 2, 80))
        self.screen.blit(instructions, instructions_rect)
        
        # Calculate the starting X position for the first card
        visible_count = min(len(self.card_options), 4)
        total_width = visible_count * (self.card_width + self.card_spacing) - self.card_spacing
        start_x = (self.screen_width - total_width) / 2
        
        # Draw each card (up to 4 visible at once)
        for i, card in enumerate(self.card_options[:4]):
            card_x = start_x + i * (self.card_width + self.card_spacing)
            card_y = (self.screen_height - self.card_height) / 2
            
            # Determine card color based on type and subtype
            card_color = self._get_card_color(card)
            is_selected = i == self.selected_card_index
            is_hovered = i == self.hover_card_index
            
            self._draw_card(card_x, card_y, card, card_color, is_selected, is_hovered)
        
        # Draw confirmation button if a card is selected
        if self.selected_card_index is not None:
            self._draw_confirm_button()
    
    def _get_card_color(self, card: Dict[str, Any]) -> Tuple[int, int, int]:
        """Get the color for a card based on its type and subtype"""
        card_type = card.get('type', 'unknown').lower()
        card_subtype = card.get('subtype', '').lower()
        
        colors = {
            # Weapon types
            "weapon": {
                "default": (50, 200, 180),     # Cyan for generic weapons
                "area_attack": (50, 180, 200), # Blue for area attack weapons
                "ranged_attack": (180, 50, 50), # Red for ranged attack weapons
                "effect": (200, 180, 50),      # Yellow for effect weapons
                "summon": (180, 50, 180),      # Purple for summon weapons
            },
            # Character types
            "character": (180, 50, 200),       # Purple for character cards
            # Role types
            "role": {
                "default": (150, 150, 150),    # Grey for generic roles
                "protector": (0, 200, 0),      # Green for protector role
                "traitor": (200, 0, 0),        # Red for traitor role
                "chaos": (200, 0, 200),        # Purple for chaos role
            },
            # Default
            "default": (150, 150, 150)         # Grey for unknown types
        }
        
        if card_type == "weapon" and card_subtype in colors["weapon"]:
            return colors["weapon"][card_subtype]
        elif card_type == "weapon":
            return colors["weapon"]["default"]
        elif card_type == "role" and card.get('id', '') in colors["role"]:
            return colors["role"][card.get('id', '')]
        elif card_type == "role":
            return colors["role"]["default"]
        elif card_type in colors:
            return colors[card_type]
        
        return colors["default"]
    
    def _draw_card(self, x: float, y: float, card: Dict[str, Any], color: Tuple[int, int, int], 
                  is_selected: bool, is_hovered: bool):
        """Draw a single card with the specified design"""
        # Card dimensions
        width = self.card_width
        height = self.card_height
        
        # Create the card shape (with rounded corners)
        card_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw the base of the card (dark background)
        pygame.draw.rect(
            card_surface,
            (20, 40, 40),  # Dark background
            (0, 0, width, height),
            border_radius=15
        )
        
        # Draw glowing border effect
        border_thickness = 3
        glow_alpha = int(100 + 155 * self.glow_intensity) if is_selected or is_hovered else 160
        border_color = color + (glow_alpha,)
        
        pygame.draw.rect(
            card_surface,
            border_color,
            (0, 0, width, height),
            border_radius=15,
            width=border_thickness
        )
        
        # Draw card header with type
        card_type = card.get('type', 'unknown').upper()
        subtype = card.get('subtype', '')
        type_label = card_type
        if subtype:
            type_label = f"{card_type}: {subtype.upper()}"
            
        # Draw card type label at top
        header_width = min(150, len(type_label) * 10)
        header_rect = pygame.Rect(width//2 - header_width//2, 10, header_width, 25)
        pygame.draw.rect(card_surface, color, header_rect)
        type_text = self.small_font.render(type_label, True, (255, 255, 255))
        card_surface.blit(type_text, (width//2 - type_text.get_width()//2, 12))
        
        # Draw selection number at top left
        idx_text = self.small_font.render(str(self.card_options.index(card) + 1), True, (255, 255, 0))
        card_surface.blit(idx_text, (10, 10))
        
        # Draw card icon area (centered)
        icon_size = 80
        icon_rect = pygame.Rect((width - icon_size)//2, 50, icon_size, icon_size)
        pygame.draw.rect(card_surface, (30, 30, 50), icon_rect)
        
        # Draw card icon (if available)
        card_icon = card.get("icon", "?")
        if isinstance(card_icon, str):
            # Draw text icon
            icon_text = self.title_font.render(card_icon, True, (255, 255, 255))
            card_surface.blit(icon_text, (icon_rect.centerx - icon_text.get_width()//2, 
                                         icon_rect.centery - icon_text.get_height()//2))
        
        # Draw card title
        title_text = self.title_font.render(card.get("name", "Unknown Card"), True, (255, 255, 255))
        card_surface.blit(title_text, ((width - title_text.get_width())//2, 150))
        
        # Draw card description
        description = card.get("description", "No description available.")
        desc_lines = self._wrap_text(description, width - 20, self.desc_font)
        
        line_y = 180
        for line in desc_lines[:4]:  # Limit to first 4 lines
            desc_text = self.desc_font.render(line, True, (200, 200, 200))
            card_surface.blit(desc_text, (10, line_y))
            line_y += 20
        
        # Draw special info based on card type
        y_pos = 260
        
        # For character cards, show passive skill
        if card.get('type') == 'character' and 'passive_skill' in card:
            passive = card['passive_skill']
            passive_title = self.small_font.render("Passive: " + passive.get('name', ''), True, (180, 220, 255))
            card_surface.blit(passive_title, (10, y_pos))
            y_pos += 20
            
            passive_desc = passive.get('description', '')
            passive_lines = self._wrap_text(passive_desc, width - 20, self.small_font)
            for line in passive_lines[:2]:  # Limit to 2 lines
                passive_text = self.small_font.render(line, True, (160, 200, 240))
                card_surface.blit(passive_text, (10, y_pos))
                y_pos += 16
        
        # For role cards, show special ability
        if card.get('type') == 'role' and 'special_ability' in card:
            ability = card['special_ability']
            ability_title = self.small_font.render("Ability: " + ability.get('name', ''), True, (220, 220, 180))
            card_surface.blit(ability_title, (10, y_pos))
            y_pos += 20
            
            ability_desc = ability.get('description', '')
            ability_lines = self._wrap_text(ability_desc, width - 20, self.small_font)
            for line in ability_lines[:2]:  # Limit to 2 lines
                ability_text = self.small_font.render(line, True, (200, 200, 160))
                card_surface.blit(ability_text, (10, y_pos))
                y_pos += 16
        
        # For weapon cards, show upgrade info
        if card.get('type') == 'weapon' and 'upgrade' in card.get('data', {}):
            upgrade = card['data']['upgrade']
            upgrade_title = self.small_font.render("Upgrade: " + upgrade.get('name', ''), True, (180, 255, 180))
            card_surface.blit(upgrade_title, (10, y_pos))
            y_pos += 20
            
            condition = upgrade.get('condition', '')
            condition_text = self.small_font.render("Condition: " + condition, True, (160, 220, 160))
            card_surface.blit(condition_text, (10, y_pos))
            y_pos += 16
        
        # Draw potential roles for character cards
        if card.get('type') == 'character' and 'potential_roles' in card:
            roles = card['potential_roles']
            roles_text = self.small_font.render("Potential Roles: " + ", ".join(roles), True, (220, 180, 220))
            card_surface.blit(roles_text, (10, height - 30))
        
        # Draw the card to the screen with hover effect
        offset_y = -10 if is_hovered else 0
        self.screen.blit(card_surface, (x, y + offset_y))
    
    def _draw_confirm_button(self):
        """Draw a confirmation button at the bottom"""
        button_width = 100
        button_height = 40
        button_x = (self.screen_width - button_width) / 2
        button_y = self.screen_height - 100
        
        pygame.draw.rect(
            self.screen,
            (80, 80, 30),  # Button color
            (button_x, button_y, button_width, button_height),
            border_radius=5
        )
        
        pygame.draw.rect(
            self.screen,
            (180, 180, 50),  # Border color
            (button_x, button_y, button_width, button_height),
            border_radius=5,
            width=2
        )
        
        confirm_text = self.desc_font.render("CONFIRM", True, (255, 255, 255))
        text_rect = confirm_text.get_rect(center=(button_x + button_width/2, button_y + button_height/2))
        self.screen.blit(confirm_text, text_rect)
    
    def _wrap_text(self, text: str, max_width: int, font: pygame.font.Font) -> List[str]:
        """Wrap text to fit within a given width"""
        words = text.split(' ')
        lines = []
        current_line = []
        current_width = 0
        
        for word in words:
            word_surface = font.render(word, True, (0, 0, 0))
            word_width = word_surface.get_width()
            
            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width + font.size(' ')[0]
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines


# Enhanced CardSelectionUI for character/role selection in the game menu
class MenuCardSelectionUI:
    """Card selection UI designed specifically for the menu screens"""
    def __init__(self, screen, card_type="character"):
        """Initialize the selection UI for menu screens"""
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.skill_registry = get_skill_registry()
        self.card_type = card_type  # "character" or "role"
        
        # Card dimensions and layout
        self.card_width = 240
        self.card_height = 400
        self.card_spacing = 40
        
        # Selection state
        self.cards = []
        self.selected_card = None
        self.hover_card = None
        
        # Load cards
        self._load_cards()
        # Arrange cards in layout
        self._arrange_cards()
        
    def _load_cards(self):
        """Load available cards of the appropriate type"""
        self.cards = []
        
        if self.card_type == "character":
            # Load character cards
            for char_id, char_data in self.skill_registry.characters.items():
                self.cards.append({
                    'id': char_id,
                    'type': 'character',
                    'name': char_data['name'],
                    'description': char_data['description'],
                    'icon': char_data.get('icon', '👤'),
                    'passive_skill': char_data.get('passive_skill', {}),
                    'potential_roles': char_data.get('potential_roles', []),
                    'data': char_data,
                    'rect': pygame.Rect(0, 0, self.card_width, self.card_height)
                })
        elif self.card_type == "role":
            # Load role cards
            for role_id, role_data in self.skill_registry.roles.items():
                self.cards.append({
                    'id': role_id,
                    'type': 'role',
                    'name': role_data['name'],
                    'description': role_data['description'],
                    'icon': role_data.get('symbol', '?'),
                    'special_ability': role_data.get('special_ability', {}),
                    'data': role_data,
                    'rect': pygame.Rect(0, 0, self.card_width, self.card_height)
                })
    
    def _arrange_cards(self):
        """Arrange cards in horizontal layout"""
        max_visible = 4  # Maximum number of visible cards
        visible_count = min(len(self.cards), max_visible)
        total_width = visible_count * (self.card_width + self.card_spacing) - self.card_spacing
        start_x = (self.screen_width - total_width) / 2
        
        # Position the visible cards
        for i, card in enumerate(self.cards[:max_visible]):
            x = start_x + i * (self.card_width + self.card_spacing)
            y = (self.screen_height - self.card_height) / 2
            card['rect'].x = x
            card['rect'].y = y
    
    def handle_event(self, event):
        """Handle user interface events"""
        if event.type == pygame.MOUSEMOTION:
            # Update hover state
            self.hover_card = None
            mouse_pos = pygame.mouse.get_pos()
            for card in self.cards:
                if card['rect'].collidepoint(mouse_pos):
                    self.hover_card = card
                    break
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Handle mouse clicks
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                for card in self.cards:
                    if card['rect'].collidepoint(mouse_pos):
                        self.selected_card = card
                        return True
        
        elif event.type == pygame.KEYDOWN:
            # Handle numeric key selection
            if pygame.K_1 <= event.key <= pygame.K_9:
                index = event.key - pygame.K_1
                if 0 <= index < len(self.cards):
                    self.selected_card = self.cards[index]
                    return True
            
            # Handle confirm key
            elif event.key == pygame.K_RETURN and self.selected_card:
                return True
        
        return False
    
    def render(self, screen):
        """Render the card selection UI"""
        # Draw card selection title
        title = f"Select Your {self.card_type.capitalize()}"

        title_font = get_font(32, bold=True)
        title_text = render_text(title_font, title, (255, 255, 255))
        title_rect = title_text.get_rect(centerx=self.screen_width//2, top=30)
        screen.blit(title_text, title_rect)

        # Draw instruction text
        small_font = get_font(18)
        instructions = render_text(small_font, "Click on a card or press 1-4 to select", (200, 200, 200))
        instructions_rect = instructions.get_rect(centerx=self.screen_width//2, top=title_rect.bottom + 10)
        screen.blit(instructions, instructions_rect)
        
        # Draw each card
        for card in self.cards:
            is_selected = card == self.selected_card
            is_hovered = card == self.hover_card
            
            self._draw_card(screen, card, is_selected, is_hovered)
        
        # Draw details panel for selected card
        if self.selected_card:
            self._draw_details_panel(screen, self.selected_card)
    
    def _draw_card(self, screen, card, is_selected, is_hovered):
        """Draw a single card"""
        # Get card color based on type
        color = self._get_card_color(card)
        
        # Apply visual effects based on selection/hover state
        offset_y = -10 if is_hovered else 0
        border_width = 3 if is_selected else 1
        
        # Draw card background with border
        rect = card['rect'].copy()
        rect.y += offset_y
        
        # Draw card base
        pygame.draw.rect(screen, (30, 30, 50), rect, border_radius=15)
        
        # Draw card border
        pygame.draw.rect(screen, color, rect, width=border_width, border_radius=15)
        
        # Draw card title
        title_font = pygame.font.SysFont("Arial", 24, bold=True)
        title_text = title_font.render(card['name'], True, (255, 255, 255))
        title_rect = title_text.get_rect(centerx=rect.centerx, top=rect.top + 20)
        screen.blit(title_text, title_rect)
        
        # Draw selection number in top-left corner
        idx_font = pygame.font.SysFont("Arial", 18, bold=True)
        idx_text = idx_font.render(str(self.cards.index(card) + 1), True, (255, 255, 0))
        screen.blit(idx_text, (rect.left + 10, rect.top + 10))
        
        # Draw card icon
        icon_font = pygame.font.SysFont("Arial", 36)
        icon_text = icon_font.render(card.get('icon', '?'), True, (255, 255, 255))
        icon_rect = icon_text.get_rect(center=(rect.centerx, rect.top + 80))
        screen.blit(icon_text, icon_rect)
        
        # Draw card description (abbreviated)
        desc_font = pygame.font.SysFont("Arial", 16)
        description = card.get("description", "")
        if len(description) > 100:
            description = description[:97] + "..."
            
        desc_lines = self._wrap_text(description, desc_font, rect.width - 20)
        
        for i, line in enumerate(desc_lines[:3]):  # Show max 3 lines
            text = desc_font.render(line, True, (200, 200, 200))
            screen.blit(text, (rect.left + 10, rect.top + 120 + i * 20))
        
        # Draw passive skill/special ability (based on card type)
        if card['type'] == 'character' and 'passive_skill' in card:
            self._draw_passive_skill(screen, card, rect)
        elif card['type'] == 'role' and 'special_ability' in card:
            self._draw_special_ability(screen, card, rect)
    
    def _draw_passive_skill(self, screen, card, rect):
        """Draw passive skill info on character card"""
        passive = card['passive_skill']
        if not passive:
            return
            
        y_pos = rect.top + 200
        
        # Draw passive skill header
        header_font = pygame.font.SysFont("Arial", 18, bold=True)
        header_text = header_font.render("Passive Skill", True, (180, 220, 255))
        screen.blit(header_text, (rect.left + 10, y_pos))
        
        # Draw passive skill name
        name_font = pygame.font.SysFont("Arial", 16)
        name_text = name_font.render(passive.get('name', ''), True, (160, 200, 240))
        screen.blit(name_text, (rect.left + 10, y_pos + 25))
        
        # Draw abbreviated description
        desc_font = pygame.font.SysFont("Arial", 14)
        desc = passive.get('description', '')
        if len(desc) > 80:
            desc = desc[:77] + "..."
            
        desc_lines = self._wrap_text(desc, desc_font, rect.width - 20)
        for i, line in enumerate(desc_lines[:2]):  # Show max 2 lines
            text = desc_font.render(line, True, (160, 200, 240))
            screen.blit(text, (rect.left + 10, y_pos + 45 + i * 16))
    
    def _draw_special_ability(self, screen, card, rect):
        """Draw special ability info on role card"""
        ability = card['special_ability']
        if not ability:
            return
            
        y_pos = rect.top + 200
        
        # Draw ability header
        header_font = pygame.font.SysFont("Arial", 18, bold=True)
        header_text = header_font.render("Special Ability", True, (220, 220, 180))
        screen.blit(header_text, (rect.left + 10, y_pos))
        
        # Draw ability name
        name_font = pygame.font.SysFont("Arial", 16)
        name_text = name_font.render(ability.get('name', ''), True, (200, 200, 160))
        screen.blit(name_text, (rect.left + 10, y_pos + 25))
        
        # Draw abbreviated description
        desc_font = pygame.font.SysFont("Arial", 14)
        desc = ability.get('description', '')
        if len(desc) > 80:
            desc = desc[:77] + "..."
            
        desc_lines = self._wrap_text(desc, desc_font, rect.width - 20)
        for i, line in enumerate(desc_lines[:2]):  # Show max 2 lines
            text = desc_font.render(line, True, (200, 200, 160))
            screen.blit(text, (rect.left + 10, y_pos + 45 + i * 16))
    
    def _draw_details_panel(self, screen, card):
        """Draw detailed information panel for the selected card"""
        panel_width = 300
        panel_height = 500
        panel_x = self.screen_width - panel_width - 20
        panel_y = (self.screen_height - panel_height) // 2
        
        # Draw panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, (40, 40, 60), panel_rect, border_radius=10)
        pygame.draw.rect(screen, (100, 100, 150), panel_rect, width=2, border_radius=10)
        
        # Draw details title
        title_font = pygame.font.SysFont("Arial", 24, bold=True)
        title_text = title_font.render(card['name'], True, (255, 255, 255))
        title_rect = title_text.get_rect(centerx=panel_rect.centerx, top=panel_rect.top + 20)
        screen.blit(title_text, title_rect)
        
        # Draw card type
        type_font = pygame.font.SysFont("Arial", 18)
        type_text = type_font.render(card['type'].capitalize(), True, (200, 200, 200))
        type_rect = type_text.get_rect(centerx=panel_rect.centerx, top=title_rect.bottom + 10)
        screen.blit(type_text, type_rect)
        
        # Draw card description
        desc_font = pygame.font.SysFont("Arial", 16)
        description = card.get("description", "No description available.")
        desc_lines = self._wrap_text(description, desc_font, panel_rect.width - 40)
        
        y_offset = type_rect.bottom + 20
        for line in desc_lines:
            line_text = desc_font.render(line, True, (220, 220, 220))
            screen.blit(line_text, (panel_rect.left + 20, y_offset))
            y_offset += 20
        
        # Draw more detailed information based on card type
        if card['type'] == 'character':
            self._draw_character_details(screen, card, panel_rect, y_offset)
        elif card['type'] == 'role':
            self._draw_role_details(screen, card, panel_rect, y_offset)
    
    def _draw_character_details(self, screen, card, panel_rect, y_offset):
        """Draw detailed character information"""
        y_offset += 20  # Add spacing
        
        # Draw passive skill section
        if 'passive_skill' in card and card['passive_skill']:
            passive = card['passive_skill']
            
            section_font = pygame.font.SysFont("Arial", 20, bold=True)
            section_text = section_font.render("Passive Skill", True, (180, 220, 255))
            screen.blit(section_text, (panel_rect.left + 20, y_offset))
            
            # Draw passive skill name
            y_offset += 30
            name_font = pygame.font.SysFont("Arial", 18)
            name_text = name_font.render(passive.get('name', ''), True, (160, 200, 240))
            screen.blit(name_text, (panel_rect.left + 20, y_offset))
            
            # Draw passive skill description
            y_offset += 25
            desc_font = pygame.font.SysFont("Arial", 16)
            description = passive.get('description', '')
            desc_lines = self._wrap_text(description, desc_font, panel_rect.width - 40)
            
            for line in desc_lines:
                line_text = desc_font.render(line, True, (160, 200, 240))
                screen.blit(line_text, (panel_rect.left + 20, y_offset))
                y_offset += 20
            
            # Draw upgrade info if available
            if 'upgrade' in passive:
                y_offset += 15
                upgrade_font = pygame.font.SysFont("Arial", 16)
                upgrade_text = upgrade_font.render("Upgrade: " + passive['upgrade'].get('name', ''), True, (180, 180, 255))
                screen.blit(upgrade_text, (panel_rect.left + 20, y_offset))
                
                y_offset += 20
                condition_text = upgrade_font.render("Condition: " + passive['upgrade'].get('condition', ''), True, (160, 160, 240))
                screen.blit(condition_text, (panel_rect.left + 20, y_offset))
                
                # Draw upgrade description
                y_offset += 20
                upgrade_desc = passive['upgrade'].get('description', '')
                upgrade_lines = self._wrap_text(upgrade_desc, desc_font, panel_rect.width - 40)
                
                for line in upgrade_lines:
                    line_text = desc_font.render(line, True, (160, 160, 240))
                    screen.blit(line_text, (panel_rect.left + 20, y_offset))
                    y_offset += 20
        
        # Draw potential roles
        if 'potential_roles' in card and card['potential_roles']:
            y_offset += 20  # Add spacing
            
            roles_font = pygame.font.SysFont("Arial", 18, bold=True)
            roles_text = roles_font.render("Potential Roles:", True, (220, 180, 220))
            screen.blit(roles_text, (panel_rect.left + 20, y_offset))
            
            y_offset += 25
            role_font = pygame.font.SysFont("Arial", 16)
            for role in card['potential_roles']:
                role_text = role_font.render("• " + role.capitalize(), True, (200, 160, 200))
                screen.blit(role_text, (panel_rect.left + 40, y_offset))
                y_offset += 20
    
    def _draw_role_details(self, screen, card, panel_rect, y_offset):
        """Draw detailed role information"""
        y_offset += 20  # Add spacing
        
        # Draw special ability section
        if 'special_ability' in card and card['special_ability']:
            ability = card['special_ability']
            
            section_font = pygame.font.SysFont("Arial", 20, bold=True)
            section_text = section_font.render("Special Ability", True, (220, 220, 180))
            screen.blit(section_text, (panel_rect.left + 20, y_offset))
            
            # Draw ability name
            y_offset += 30
            name_font = pygame.font.SysFont("Arial", 18)
            name_text = name_font.render(ability.get('name', ''), True, (200, 200, 160))
            screen.blit(name_text, (panel_rect.left + 20, y_offset))
            
            # Draw ability description
            y_offset += 25
            desc_font = pygame.font.SysFont("Arial", 16)
            description = ability.get('description', '')
            desc_lines = self._wrap_text(description, desc_font, panel_rect.width - 40)
            
            for line in desc_lines:
                line_text = desc_font.render(line, True, (200, 200, 160))
                screen.blit(line_text, (panel_rect.left + 20, y_offset))
                y_offset += 20
        
        # Draw role-specific gameplay information
        y_offset += 20
        info_font = pygame.font.SysFont("Arial", 18, bold=True)
        info_text = info_font.render("Victory Conditions:", True, (180, 220, 180))
        screen.blit(info_text, (panel_rect.left + 20, y_offset))
        
        y_offset += 25
        cond_font = pygame.font.SysFont("Arial", 16)
        
        if card['id'] == 'protector':
            cond_text = cond_font.render("• Survive until the end of the game", True, (160, 200, 160))
            screen.blit(cond_text, (panel_rect.left + 40, y_offset))
            y_offset += 20
            cond_text = cond_font.render("• Complete the main objective", True, (160, 200, 160))
            screen.blit(cond_text, (panel_rect.left + 40, y_offset))
        elif card['id'] == 'traitor':
            cond_text = cond_font.render("• Eliminate all Protectors", True, (160, 200, 160))
            screen.blit(cond_text, (panel_rect.left + 40, y_offset))
            y_offset += 20
            cond_text = cond_font.render("• Sabotage the main objective", True, (160, 200, 160))
            screen.blit(cond_text, (panel_rect.left + 40, y_offset))
        elif card['id'] == 'chaos':
            cond_text = cond_font.render("• Collect 10 or more clues/artifacts", True, (160, 200, 160))
            screen.blit(cond_text, (panel_rect.left + 40, y_offset))
            y_offset += 20
            cond_text = cond_font.render("• Create maximum disruption", True, (160, 200, 160))
            screen.blit(cond_text, (panel_rect.left + 40, y_offset))
    
    def _get_card_color(self, card):
        """Get color based on card type and id"""
        card_type = card.get('type', 'unknown')
        card_id = card.get('id', '')
        
        if card_type == 'character':
            return (180, 50, 200)  # Purple for characters
        elif card_type == 'role':
            if card_id == 'protector':
                return (0, 200, 0)  # Green for protector
            elif card_id == 'traitor':
                return (200, 0, 0)  # Red for traitor
            elif card_id == 'chaos':
                return (200, 0, 200)  # Purple for chaos
        
        return (150, 150, 150)  # Default grey
    
    def _wrap_text(self, text, font, max_width):
        """Wrap text to fit within a given width"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # If a single word is too long, add it to its own line
                    lines.append(word)
            
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines