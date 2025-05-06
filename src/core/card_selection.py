# src/core/card_selection.py
import pygame
import math
from typing import List, Dict
from .entities import Card

class CardSelection:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.width, self.height = self.screen.get_size()
        self.font_large = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_medium = pygame.font.SysFont("Arial", 20)
        self.font_small = pygame.font.SysFont("Arial", 16)
        
        # Card visuals
        self.card_width = 220
        self.card_height = 320
        self.card_spacing = 30
        self.card_radius = 15
        
        # Selection state
        self.cards: List[Card] = []
        self.selected_index = None
        self.hover_index = None
        self.time_left = 15.0  # 15 seconds to choose
        
        # Animation
        self.glow_phase = 0
        self.glow_speed = 2.5

    def set_cards(self, cards: List[Card]):
        """Set the cards available for selection"""
        self.cards = cards
        self.selected_index = None
        self.hover_index = None
        self.time_left = 15.0

    def update(self, dt):
        """Update selection timer and animations"""
        self.time_left -= dt
        self.glow_phase = (self.glow_phase + dt * self.glow_speed) % (2 * math.pi)
        
        # Auto-select if time runs out
        if self.time_left <= 0 and self.selected_index is None and self.cards:
            self.selected_index = 0

    def handle_event(self, event):
        """Handle mouse interactions"""
        if event.type == pygame.MOUSEMOTION:
            self.hover_index = self._get_card_at_pos(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            clicked_index = self._get_card_at_pos(event.pos)
            if clicked_index is not None:
                self.selected_index = clicked_index
                return self.cards[clicked_index]
        
        return None

    def _get_card_at_pos(self, pos):
        """Get card index at mouse position"""
        total_width = len(self.cards) * self.card_width + (len(self.cards)-1) * self.card_spacing
        start_x = (self.width - total_width) // 2
        
        for i in range(len(self.cards)):
            card_x = start_x + i * (self.card_width + self.card_spacing)
            card_rect = pygame.Rect(
                card_x, 
                (self.height - self.card_height) // 2,
                self.card_width,
                self.card_height
            )
            
            if card_rect.collidepoint(pos):
                return i
        return None

    def draw(self):
        """Draw the card selection interface"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Title and timer
        title = f"Chọn Thẻ Bài ({int(self.time_left)}s)"
        title_text = self.font_large.render(title, True, (255, 255, 255))
        self.screen.blit(title_text, (self.width//2 - title_text.get_width()//2, 50))
        
        # Draw all cards
        total_width = len(self.cards) * self.card_width + (len(self.cards)-1) * self.card_spacing
        start_x = (self.width - total_width) // 2
        
        for i, card in enumerate(self.cards):
            card_x = start_x + i * (self.card_width + self.card_spacing)
            card_y = (self.height - self.card_height) // 2
            
            # Highlight hovered/selected cards
            is_hovered = i == self.hover_index
            is_selected = i == self.selected_index
            
            self._draw_card(card_x, card_y, card, is_hovered, is_selected)

    def _draw_card(self, x, y, card, is_hovered, is_selected):
        """Draw an individual card"""
        # Card background
        card_surface = pygame.Surface((self.card_width, self.card_height), pygame.SRCALPHA)
        
        # Card color based on type
        if card.type == "♥":
            base_color = (200, 50, 50)  # Red for attack
        elif card.type == "✝":
            base_color = (50, 50, 200)  # Blue for defense
        else:
            base_color = (50, 200, 50)  # Green for utility
        
        # Glow effect
        glow_intensity = 0.5 + 0.5 * math.sin(self.glow_phase) if is_hovered or is_selected else 0
        glow_color = (
            min(255, base_color[0] + int(100 * glow_intensity)),
            min(255, base_color[1] + int(100 * glow_intensity)),
            min(255, base_color[2] + int(100 * glow_intensity))
        )
        
        # Card border
        pygame.draw.rect(
            card_surface,
            glow_color,
            (0, 0, self.card_width, self.card_height),
            border_radius=self.card_radius
        )
        
        # Card interior
        pygame.draw.rect(
            card_surface,
            (30, 30, 40),
            (5, 5, self.card_width-10, self.card_height-10),
            border_radius=self.card_radius-5
        )
        
        # Card icon
        icon_text = self.font_large.render(card.symbol, True, base_color)
        card_surface.blit(
            icon_text,
            (self.card_width//2 - icon_text.get_width()//2, 50)
        )
        
        # Card name
        name_text = self.font_medium.render(card.name, True, (255, 255, 255))
        card_surface.blit(
            name_text,
            (self.card_width//2 - name_text.get_width()//2, 120)
        )
        
        # Card description (wrapped)
        desc_lines = self._wrap_text(card.description, self.card_width-20)
        for i, line in enumerate(desc_lines):
            desc_text = self.font_small.render(line, True, (200, 200, 200))
            card_surface.blit(
                desc_text,
                (10, 160 + i * 25)
            )
        
        # "NEW" tag
        if card.is_new:
            new_text = self.font_small.render("MỚI", True, (255, 255, 0))
            pygame.draw.rect(
                card_surface,
                base_color,
                (self.card_width-50, 10, 40, 20)
            )
            card_surface.blit(new_text, (self.card_width-45, 12))
        
        # Draw to screen with hover effect
        y_offset = -15 if is_hovered else 0
        self.screen.blit(card_surface, (x, y + y_offset))

    def _wrap_text(self, text, max_width):
        """Wrap text to fit within card width"""
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if self.font_small.size(test_line)[0] <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines[:3]  # Max 3 lines
