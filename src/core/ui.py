# src/core/ui.py
"""
UI Components - Skill Selection UI
"""
import pygame
from typing import List, Optional
from .entities import SkillCard, SkillType

# UI Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
SKILL_CARD_SELECT_TIME = 10
MAX_ROLLS_PER_NIGHT = 2

class SkillSelectUI:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.skill_options = []
        self.time_left = SKILL_CARD_SELECT_TIME
        self.rolls_left = MAX_ROLLS_PER_NIGHT
        self.selected_skill = None
        
    def update(self, dt):
        """Update the skill selection UI"""
        if self.time_left > 0:
            self.time_left -= dt
    
    def wrap_text(self, text: str, max_width: int) -> List[str]:
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        current_width = 0
        
        for word in words:
            word_width = self.small_font.size(word)[0]
            if current_width + word_width < max_width:
                current_line.append(word)
                current_width += word_width + self.small_font.size(" ")[0]
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_width = word_width
        
        if current_line:
            lines.append(" ".join(current_line))
        
        return lines
    
    def draw(self, player=None):
        # Draw semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        # Draw player info header
        if player:
            player_info = self.font.render(f"{player.name} (Level {player.level}) - Skill Selection", True, (255, 255, 0))
            self.screen.blit(player_info, (SCREEN_WIDTH//2 - 200, 20))
        
        # Draw timer
        timer_text = self.font.render(f"Time: {self.time_left:.1f}s", True, (255, 255, 255))
        self.screen.blit(timer_text, (10, 10))
        
        # Draw rolls left
        rolls_text = self.font.render(f"Rolls left: {self.rolls_left}", True, (255, 255, 255))
        self.screen.blit(rolls_text, (10, 50))
        
        # Draw instructions
        instructions = self.small_font.render("1/2/3: Select Skill | ENTER: Confirm | R: Reroll", True, (200, 200, 200))
        self.screen.blit(instructions, (SCREEN_WIDTH//2 - 200, 100))
        
        # Draw skill cards
        card_width = 350
        card_height = 300
        spacing = 50
        start_x = (SCREEN_WIDTH - (card_width * 3 + spacing * 2)) // 2
        start_y = 150
        
        for i, skill_card in enumerate(self.skill_options):
            if skill_card:
                x = start_x + i * (card_width + spacing)
                
                # Draw card background
                card_color = (40, 60, 80) if self.selected_skill != i else (60, 100, 140)
                border_color = (200, 200, 200) if self.selected_skill != i else (255, 255, 0)
                
                pygame.draw.rect(self.screen, card_color, (x, start_y, card_width, card_height))
                pygame.draw.rect(self.screen, border_color, (x, start_y, card_width, card_height), 3)
                
                # Draw skill type badge
                type_color = (200, 100, 100) if skill_card.type == SkillType.ACTIVE else (100, 200, 100) if skill_card.type == SkillType.PASSIVE else (100, 100, 200)
                pygame.draw.rect(self.screen, type_color, (x + 5, start_y + 5, 100, 30))
                type_text = self.small_font.render(skill_card.type.value.upper(), True, (255, 255, 255))
                self.screen.blit(type_text, (x + 10, start_y + 10))
                
                # Draw skill icon (larger)
                icon_font = pygame.font.Font(None, 96)
                icon_text = icon_font.render(skill_card.icon, True, (255, 255, 255))
                icon_bg = pygame.Surface((80, 80))
                icon_bg.fill((0, 0, 0))
                icon_bg.set_alpha(100)
                self.screen.blit(icon_bg, (x + 10, start_y + 50))
                self.screen.blit(icon_text, (x + 10, start_y + 45))
                
                # Draw skill name
                name_text = self.font.render(skill_card.name, True, (255, 255, 255))
                self.screen.blit(name_text, (x + 100, start_y + 50))
                
                # Draw cooldown info
                cooldown_text = self.small_font.render(f"Cooldown: {skill_card.cooldown}s", True, (200, 200, 200))
                self.screen.blit(cooldown_text, (x + 100, start_y + 80))
                
                # Draw description
                desc_lines = self.wrap_text(skill_card.description, card_width - 40)
                for j, line in enumerate(desc_lines):
                    desc_text = self.small_font.render(line, True, (200, 200, 200))
                    self.screen.blit(desc_text, (x + 20, start_y + 140 + j * 20))
                
                # Draw effect details
                effect_y = start_y + 180
                if "damage" in skill_card.effect:
                    damage_values = skill_card.effect["damage"]
                    if isinstance(damage_values, (list, tuple)):
                        damage_text = self.small_font.render(f"Damage: {damage_values[0]} → {damage_values[-1]}", True, (255, 100, 100))
                    else:
                        damage_text = self.small_font.render(f"Damage: {damage_values}", True, (255, 100, 100))
                    self.screen.blit(damage_text, (x + 20, effect_y))
                    effect_y += 20
                
                if "heal" in skill_card.effect:
                    heal_values = skill_card.effect["heal"]
                    if isinstance(heal_values, (list, tuple)):
                        heal_text = self.small_font.render(f"Heal: {heal_values[0]} → {heal_values[-1]}", True, (100, 255, 100))
                    else:
                        heal_text = self.small_font.render(f"Heal: {heal_values}", True, (100, 255, 100))
                    self.screen.blit(heal_text, (x + 20, effect_y))
                    effect_y += 20
                
                if "range" in skill_card.effect:
                    range_values = skill_card.effect["range"]
                    if isinstance(range_values, (list, tuple)):
                        range_text = self.small_font.render(f"Range: {range_values[0]} → {range_values[-1]}", True, (100, 100, 255))
                    else:
                        range_text = self.small_font.render(f"Range: {range_values}", True, (100, 100, 255))
                    self.screen.blit(range_text, (x + 20, effect_y))
                    effect_y += 20
                
                # Draw skill level progression
                level_text = self.small_font.render("Level 1 → Level 5", True, (200, 200, 200))
                self.screen.blit(level_text, (x + 20, start_y + card_height - 40))

                # Auto-cast feature info
                auto_cast_text = self.small_font.render("ALT+# to toggle auto-cast", True, (255, 215, 0))
                self.screen.blit(auto_cast_text, (x + 20, start_y + card_height - 20))
                
                # Draw number indicator
                num_font = pygame.font.Font(None, 60)
                num_text = num_font.render(str(i + 1), True, (255, 255, 0))
                num_bg = pygame.Surface((40, 40))
                num_bg.fill((0, 0, 0))
                num_bg.set_alpha(200)
                self.screen.blit(num_bg, (x + card_width - 45, start_y + 5))
                self.screen.blit(num_text, (x + card_width - 40, start_y + 5))
        
        # Draw select button
        button_y = start_y + card_height + 30
        button_width = 120
        
        # Select button (centered)
        select_button_x = SCREEN_WIDTH // 2 - button_width - 10
        select_color = (80, 200, 80) if self.selected_skill is not None else (100, 100, 100)
        pygame.draw.rect(self.screen, select_color, (select_button_x, button_y, button_width, 40))
        select_text = self.font.render("Select (Enter)", True, (0, 0, 0))
        self.screen.blit(select_text, (select_button_x + 10, button_y + 8))
        
        # Reroll button
        reroll_button_x = SCREEN_WIDTH // 2 + 10
        reroll_color = (200, 80, 80) if self.rolls_left > 0 else (100, 100, 100)
        pygame.draw.rect(self.screen, reroll_color, (reroll_button_x, button_y, button_width, 40))
        reroll_text = self.font.render("Reroll (R)", True, (0, 0, 0))
        self.screen.blit(reroll_text, (reroll_button_x + 20, button_y + 8))
        
