# src/core/card_selection_ui.py

import pygame
import math
from typing import List, Dict, Optional

class CardSelectionUI:
    """Card selection UI that matches the style in the screenshot"""
    
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.screen_width = game.screen.get_width()
        self.screen_height = game.screen.get_height()
        
        # Fonts
        self.title_font = pygame.font.SysFont("Arial", 22, bold=True)
        self.desc_font = pygame.font.SysFont("Arial", 16)
        self.small_font = pygame.font.SysFont("Arial", 14)
        
        # Card properties
        self.card_width = 200
        self.card_height = 360
        self.card_spacing = 20
        
        # Card options and selection
        self.card_options = []
        self.selected_card_index = None
        self.hover_card_index = None
        self.time_left = 15.0  # 15 seconds to select
        
        # Background overlay
        self.overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))  # Semi-transparent black
        
        # Animation
        self.animation_time = 0
        self.glow_intensity = 0
    
    def set_card_options(self, cards: List[Dict]):
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
        """Handle mouse events"""
        if event.type == pygame.MOUSEMOTION:
            # Handle hover
            self.hover_card_index = self._get_card_at_position(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Handle click
            clicked_card = self._get_card_at_position(event.pos)
            if clicked_card is not None:
                self.selected_card_index = clicked_card
                return {"action": "select_card", "index": clicked_card}
        
        return None
    
    def _get_card_at_position(self, pos):
        """Get the card index at the given position"""
        # Calculate the starting X position for the first card
        total_width = len(self.card_options) * (self.card_width + self.card_spacing) - self.card_spacing
        start_x = (self.screen_width - total_width) / 2
        
        for i, card in enumerate(self.card_options):
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
        
        # Draw time remaining
        time_text = self.title_font.render(f"Select a card: {int(self.time_left)}s", True, (255, 255, 255))
        time_rect = time_text.get_rect(center=(self.screen_width / 2, 50))
        self.screen.blit(time_text, time_rect)
        
        # Calculate the starting X position for the first card
        total_width = len(self.card_options) * (self.card_width + self.card_spacing) - self.card_spacing
        start_x = (self.screen_width - total_width) / 2
        
        # Draw each card
        for i, card in enumerate(self.card_options):
            card_x = start_x + i * (self.card_width + self.card_spacing)
            card_y = (self.screen_height - self.card_height) / 2
            
            # Determine card color based on type
            card_color = self._get_card_color(card.get("type", "normal"))
            is_selected = i == self.selected_card_index
            is_hovered = i == self.hover_card_index
            
            self._draw_card(card_x, card_y, card, card_color, is_selected, is_hovered)
        
        # Draw confirmation button if a card is selected
        if self.selected_card_index is not None:
            self._draw_confirm_button()
    
    def _get_card_color(self, card_type):
        """Get the color for a card based on its type"""
        colors = {
            "attack": (50, 200, 180),    # Cyan for attack cards
            "utility": (50, 180, 200),   # Blue for utility cards 
            "support": (180, 50, 200),   # Purple for support/heal cards
            "normal": (150, 150, 150)    # Grey for normal cards
        }
        return colors.get(card_type.lower(), colors["normal"])
    
    def _draw_card(self, x, y, card, color, is_selected, is_hovered):
        """Draw a single card with the design from the screenshot"""
        # Card dimensions
        width = self.card_width
        height = self.card_height
        
        # Create the card shape (with rounded corners)
        card_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Draw the base of the card (dark)
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
        
        # Draw "NEW" label at top
        new_rect = pygame.Rect(width//2 - 30, 10, 60, 25)
        pygame.draw.rect(card_surface, color, new_rect)
        new_text = self.small_font.render("MỚI", True, (255, 255, 255))
        card_surface.blit(new_text, (width//2 - 20, 12))
        
        # Draw card icon area (centered)
        icon_size = 100
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
        card_surface.blit(title_text, ((width - title_text.get_width())//2, 170))
        
        # Draw card description
        description = card.get("description", "No description available.")
        desc_lines = self._wrap_text(description, width - 20, self.desc_font)
        
        line_y = 210
        for line in desc_lines:
            desc_text = self.desc_font.render(line, True, (200, 200, 200))
            card_surface.blit(desc_text, (10, line_y))
            line_y += 25
        
        # Draw "Available for Mage" note at bottom
        bottom_text = self.small_font.render("Có thể cho Mạng", True, (150, 150, 150))
        card_surface.blit(bottom_text, (10, height - 30))
        
        # Draw the card to the screen
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
        
        confirm_text = self.small_font.render("CONFIRM", True, (255, 255, 255))
        text_rect = confirm_text.get_rect(center=(button_x + button_width/2, button_y + button_height/2))
        self.screen.blit(confirm_text, text_rect)
    
    def _wrap_text(self, text, max_width, font):
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
