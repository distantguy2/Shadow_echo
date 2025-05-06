import pygame
import math
from typing import List, Tuple
from ..core.entities import Player, Monster

class GameplayEnhancements:
    def __init__(self, game):
        self.game = game
        self.attack_effects = []
        self.impact_effects = []
        self.last_attack_time = 0
        self.attack_cooldown = 0.3

    def draw_monster_health_bars(self):
        for monster in self.game.monsters:
            health_percent = monster.hp / monster.max_hp
            bar_width, bar_height = 40, 6
            x = int(monster.position[0]) - bar_width // 2
            y = int(monster.position[1]) - 20
            pygame.draw.rect(self.game.screen, (100, 0, 0), (x, y, bar_width, bar_height))
            fill_width = max(0, int(bar_width * health_percent))
            health_color = (0, 200, 0) if health_percent > 0.5 else (255, 255, 0) if health_percent > 0.25 else (255, 0, 0)
            pygame.draw.rect(self.game.screen, health_color, (x, y, fill_width, bar_height))
            pygame.draw.rect(self.game.screen, (255, 255, 255), (x, y, bar_width, bar_height), 1)

    def draw_player_health_bars(self):
        for player in self.game.players:
            if player.is_alive:
                health_percent = player.hp / player.max_hp
                bar_width, bar_height = 40, 6
                x = int(player.position[0]) - bar_width // 2
                y = int(player.position[1]) - 25
                pygame.draw.rect(self.game.screen, (100, 0, 0), (x, y, bar_width, bar_height))
                fill_width = max(0, int(bar_width * health_percent))
                health_color = (0, 255, 255) if player.is_controlled else (100, 100, 255)
                pygame.draw.rect(self.game.screen, health_color, (x, y, fill_width, bar_height))
                pygame.draw.rect(self.game.screen, (255, 255, 255), (x, y, bar_width, bar_height), 1)

    def draw_player_sprites(self):
        for player in self.game.players:
            if player.is_alive:
                color = (0, 255, 255) if player.is_controlled else (100, 100, 255)
                if player.is_controlled:
                    pygame.draw.circle(self.game.screen, (255, 255, 0), (int(player.position[0]), int(player.position[1])), 15, 2)
                pygame.draw.rect(self.game.screen, color, (int(player.position[0])-10, int(player.position[1])-10, 20, 20))
                name = self.game.small_font.render(f"{player.name} Lv.{player.level}", True, (255, 255, 255))
                self.game.screen.blit(name, (int(player.position[0])-30, int(player.position[1])+15))
        self.draw_player_health_bars()

    def draw_player_ui(self):
        player = self.game.player_manager.get_current_player()
        hp_ratio = player.hp / player.max_hp
        pygame.draw.rect(self.game.screen, (100, 0, 0), (20, 20, 200, 20))
        pygame.draw.rect(self.game.screen, (0, 200, 0), (20, 20, 200 * hp_ratio, 20))

        for i, card in enumerate(player.cards[:5]):
            self._draw_card_slot(650 + i * 70, 30, card, i+1)

        self._draw_skill_slot(100, 60, "Q", player.skills[0] if len(player.skills) > 0 else None)
        self._draw_skill_slot(180, 60, "E", player.skills[1] if len(player.skills) > 1 else None)
        self._draw_skill_slot(260, 60, "R", player.skills[2] if len(player.skills) > 2 else None)

    def _draw_card_slot(self, x, y, card, slot_num):
        pygame.draw.rect(self.game.screen, (70, 70, 90), (x, y, 60, 80))
        if card:
            icon = self.game.font.render(card.symbol, True, (255, 255, 255))
            self.game.screen.blit(icon, (x + 30 - icon.get_width()//2, y + 20))
            key = self.game.small_font.render(str(slot_num), True, (200, 200, 200))
            self.game.screen.blit(key, (x + 5, y + 5))

    def _draw_skill_slot(self, x, y, key: str, skill):
        pygame.draw.rect(self.game.screen, (80, 80, 100), (x, y, 60, 60))
        key_text = self.game.small_font.render(key, True, (255, 255, 255))
        self.game.screen.blit(key_text, (x + 5, y + 5))
        if skill:
            icon = self.game.font.render(skill.icon, True, (255, 255, 255))
            self.game.screen.blit(icon, (x + 30 - icon.get_width()//2, y + 25))

    def get_alive_targets(self, entity) -> List:
        targets = []
        for player in self.game.players:
            if player.is_alive:
                targets.append(player)
        if hasattr(self.game, 'npcs'):
            for npc in self.game.npcs:
                if hasattr(npc, 'alive') and npc.alive:
                    targets.append(npc)
        return targets

    def create_attack_effect(self, attacker_pos: Tuple[float, float], direction: float, range: float = 50):
        effect = {
            'pos': list(attacker_pos),
            'direction': direction,
            'range': range,
            'lifetime': 0.2,
            'current_time': 0.0,
            'color': (255, 255, 100),
            'width': 15
        }
        self.attack_effects.append(effect)

    def create_impact_effect(self, position: Tuple[float, float]):
        effect = {
            'pos': list(position),
            'radius': 0,
            'max_radius': 20,
            'lifetime': 0.15,
            'current_time': 0.0,
            'color': (255, 100, 100)
        }
        self.impact_effects.append(effect)

    def update_visual_effects(self, dt: float):
        for effect in self.attack_effects[:]:
            effect['current_time'] += dt
            if effect['current_time'] >= effect['lifetime']:
                self.attack_effects.remove(effect)
        for effect in self.impact_effects[:]:
            effect['current_time'] += dt
            progress = effect['current_time'] / effect['lifetime']
            effect['radius'] = effect['max_radius'] * progress
            if effect['current_time'] >= effect['lifetime']:
                self.impact_effects.remove(effect)

    def draw_visual_effects(self):
        for effect in self.attack_effects:
            progress = effect['current_time'] / effect['lifetime']
            alpha = int(255 * (1 - progress))
            surf = pygame.Surface((2 * effect['range'], effect['width']), pygame.SRCALPHA)
            end_x = effect['range'] * math.cos(effect['direction'])
            end_y = effect['range'] * math.sin(effect['direction'])
            color = (*effect['color'], alpha)
            pygame.draw.line(surf, color, (0, effect['width']//2), (end_x, end_y + effect['width']//2), effect['width'])
            rotated = pygame.transform.rotate(surf, -math.degrees(effect['direction']))
            rect = rotated.get_rect(center=effect['pos'])
            self.game.screen.blit(rotated, rect)
        for effect in self.impact_effects:
            alpha = int(200 * (1 - effect['current_time'] / effect['lifetime']))
            color = (*effect['color'], alpha)
            surf = pygame.Surface((effect['radius'] * 2, effect['radius'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (effect['radius'], effect['radius']), effect['radius'])
            rect = surf.get_rect(center=effect['pos'])
            self.game.screen.blit(surf, rect)

    def handle_mouse_attack(self, player):
        current_time = pygame.time.get_ticks() / 1000.0
        if current_time - self.last_attack_time < self.attack_cooldown:
            return
        self.last_attack_time = current_time
        mouse_pos = pygame.mouse.get_pos()
        dx = mouse_pos[0] - player.position[0]
        dy = mouse_pos[1] - player.position[1]
        angle = math.atan2(dy, dx)
        attack_range = 70
        self.create_attack_effect(tuple(player.position), angle, attack_range)
        for monster in self.game.monsters[:]:
            dx = monster.position[0] - player.position[0]
            dy = monster.position[1] - player.position[1]
            distance = math.sqrt(dx**2 + dy**2)
            if distance <= attack_range:
                monster_angle = math.atan2(dy, dx)
                angle_diff = abs(((angle - monster_angle + math.pi) % (2 * math.pi)) - math.pi)
                if angle_diff < math.pi / 4:
                    monster.hp -= 30
                    self.create_impact_effect(tuple(monster.position))
                    if monster.hp <= 0:
                        self.game.monsters.remove(monster)
                        player.add_exp(50)
