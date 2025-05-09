import pygame
import math
import random
from typing import List, Tuple, Dict, Any, Optional
from ..core.entities import Player, Monster

class GameplayEnhancements:
    def __init__(self, game):
        self.game = game
        self.attack_effects = []
        self.impact_effects = []
        self.skill_effects = []  # Danh sách lưu trữ hiệu ứng kỹ năng
        self.last_attack_time = 0
        self.attack_cooldown = 0.3

        # Định nghĩa màu sắc cho các loại kỹ năng
        self.skill_colors = {
            "fire": (255, 100, 0),        # Cam đỏ cho lửa
            "ice": (100, 200, 255),       # Xanh nhạt cho băng
            "lightning": (255, 255, 0),   # Vàng cho sét
            "shadow": (128, 0, 128),      # Tím cho bóng tối
            "heal": (0, 255, 100),        # Xanh lá cho hồi máu
            "shield": (0, 100, 255),      # Xanh dương cho khiên
            "earth": (150, 75, 0),        # Nâu cho đất
            "wind": (200, 255, 200),      # Xanh trắng cho gió
            "sound": (255, 200, 255),     # Hồng nhạt cho âm thanh
            "void": (50, 0, 50),          # Đen tím cho hư không
            "default": (255, 255, 255)    # Trắng cho mặc định
        }

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
        # Vẽ nền kỹ năng
        pygame.draw.rect(self.game.screen, (80, 80, 100), (x, y, 60, 60))

        # Vẽ phím tắt
        key_text = self.game.small_font.render(key, True, (255, 255, 255))
        self.game.screen.blit(key_text, (x + 5, y + 5))

        if skill:
            # Vẽ biểu tượng kỹ năng
            icon = self.game.font.render(skill.icon, True, (255, 255, 255))
            self.game.screen.blit(icon, (x + 30 - icon.get_width()//2, y + 25))

            # Kiểm tra nếu kỹ năng đang ở chế độ tự động
            if hasattr(self.game, 'skill_system') and skill.skill_id in self.game.skill_system.auto_cast_skills:
                # Vẽ đường viền màu vàng cho kỹ năng tự động
                pygame.draw.rect(self.game.screen, (255, 215, 0), (x, y, 60, 60), 3)

                # Vẽ biểu tượng tự động (A) ở góc
                auto_text = self.game.small_font.render("A", True, (255, 215, 0))
                self.game.screen.blit(auto_text, (x + 45, y + 5))

                # Hiển thị thời gian còn lại đến lần thi triển tiếp theo
                if hasattr(self.game.skill_system, 'auto_cast_timers') and skill.skill_id in self.game.skill_system.auto_cast_timers:
                    interval = self.game.skill_system.auto_cast_skills.get(skill.skill_id, 5.0)
                    elapsed = self.game.skill_system.auto_cast_timers.get(skill.skill_id, 0.0)
                    remaining = max(0, interval - elapsed)

                    # Vẽ thanh thời gian
                    progress = elapsed / interval
                    pygame.draw.rect(self.game.screen, (40, 40, 40), (x, y + 57, 60, 3))
                    pygame.draw.rect(self.game.screen, (255, 215, 0), (x, y + 57, int(60 * progress), 3))

            # Vẽ cooldown nếu kỹ năng đang hồi
            if hasattr(skill, 'cooldown') and skill.cooldown > 0:
                # Overlay màu tối cho kỹ năng đang hồi chiêu
                overlay = pygame.Surface((60, 60), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 150))  # Màu đen bán trong suốt
                self.game.screen.blit(overlay, (x, y))

                # Hiển thị thời gian hồi còn lại
                cooldown_text = self.game.small_font.render(f"{skill.cooldown:.1f}s", True, (255, 255, 255))
                self.game.screen.blit(cooldown_text, (x + 30 - cooldown_text.get_width()//2, y + 25))

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

    def create_impact_effect(self, position: Tuple[float, float], color=None, max_radius=20, lifetime=0.15):
        effect = {
            'pos': list(position),
            'radius': 0,
            'max_radius': max_radius,
            'lifetime': lifetime,
            'current_time': 0.0,
            'color': color or (255, 100, 100)
        }
        self.impact_effects.append(effect)

    def update_visual_effects(self, dt: float):
        # Cập nhật hiệu ứng tấn công
        for effect in self.attack_effects[:]:
            effect['current_time'] += dt
            if effect['current_time'] >= effect['lifetime']:
                self.attack_effects.remove(effect)

        # Cập nhật hiệu ứng va chạm
        for effect in self.impact_effects[:]:
            effect['current_time'] += dt
            progress = effect['current_time'] / effect['lifetime']
            effect['radius'] = effect['max_radius'] * progress
            if effect['current_time'] >= effect['lifetime']:
                self.impact_effects.remove(effect)

        # Cập nhật hiệu ứng kỹ năng
        for effect in self.skill_effects[:]:
            effect['current_time'] += dt

            # Cập nhật các thuộc tính dựa trên loại hiệu ứng
            if effect['type'] == 'aoe_circle':
                # Hiệu ứng hình tròn mở rộng
                progress = effect['current_time'] / effect['lifetime']
                effect['radius'] = effect['max_radius'] * min(progress * 2, 1.0)  # Mở rộng nhanh sau đó giữ nguyên
                effect['opacity'] = int(255 * (1 - progress))  # Mờ dần theo thời gian

            elif effect['type'] == 'projectile':
                # Hiệu ứng đạn bay
                progress = effect['current_time'] / effect['lifetime']
                effect['pos'][0] += effect['speed'] * math.cos(effect['direction']) * dt
                effect['pos'][1] += effect['speed'] * math.sin(effect['direction']) * dt

                # Tạo hiệu ứng hạt nhỏ theo sau
                if random.random() < 0.3:  # 30% cơ hội mỗi frame
                    trail_pos = list(effect['pos'])
                    trail_pos[0] += random.uniform(-5, 5)
                    trail_pos[1] += random.uniform(-5, 5)
                    self.create_impact_effect(tuple(trail_pos), color=effect['color'], max_radius=5, lifetime=0.2)

            elif effect['type'] == 'buff':
                # Hiệu ứng buff xung quanh người chơi hoặc mục tiêu
                if 'target' in effect and hasattr(effect['target'], 'position'):
                    # Cập nhật vị trí nếu mục tiêu di chuyển
                    effect['pos'] = list(effect['target'].position)

                # Hiệu ứng xoay tròn
                effect['angle'] += effect['rotation_speed'] * dt
                effect['opacity'] = max(0, int(255 * (1 - progress)))

            elif effect['type'] == 'beam':
                # Hiệu ứng tia sáng kéo dài
                progress = effect['current_time'] / effect['lifetime']
                effect['width'] = effect['max_width'] * (1 - progress * 0.5)
                effect['length'] = effect['max_length'] * min(progress * 3, 1.0)  # Kéo dài nhanh sau đó giữ nguyên
                effect['opacity'] = int(255 * (1 - progress))

            # Xóa hiệu ứng khi hết thời gian
            if effect['current_time'] >= effect['lifetime']:
                self.skill_effects.remove(effect)

    def draw_visual_effects(self):
        # Vẽ hiệu ứng tấn công
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

        # Vẽ hiệu ứng va chạm
        for effect in self.impact_effects:
            alpha = int(200 * (1 - effect['current_time'] / effect['lifetime']))
            color = (*effect['color'], alpha)
            surf = pygame.Surface((effect['radius'] * 2, effect['radius'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color, (effect['radius'], effect['radius']), effect['radius'])
            rect = surf.get_rect(center=effect['pos'])
            self.game.screen.blit(surf, rect)

        # Vẽ hiệu ứng kỹ năng
        for effect in self.skill_effects:
            if effect['type'] == 'aoe_circle':
                # Vẽ hiệu ứng vòng tròn AOE
                alpha = effect.get('opacity', 200)
                color = (*effect['color'], alpha)

                # Tạo surface trong suốt kích thước phù hợp với bán kính
                surf = pygame.Surface((effect['radius'] * 2, effect['radius'] * 2), pygame.SRCALPHA)

                # Vẽ vòng tròn đầy
                pygame.draw.circle(surf, color, (effect['radius'], effect['radius']), effect['radius'])

                # Vẽ đường viền
                border_color = (*effect['color'], min(255, alpha + 50))
                pygame.draw.circle(surf, border_color, (effect['radius'], effect['radius']), effect['radius'], 3)

                # Hiển thị lên màn hình
                rect = surf.get_rect(center=effect['pos'])
                self.game.screen.blit(surf, rect)

            elif effect['type'] == 'projectile':
                # Vẽ hiệu ứng đạn bay
                alpha = int(255 * (1 - effect['current_time'] / effect['lifetime']))
                color = (*effect['color'], alpha)

                # Tạo surface trong suốt
                surf = pygame.Surface((effect['size'] * 2, effect['size'] * 2), pygame.SRCALPHA)

                # Vẽ hình dạng của đạn
                if effect.get('projectile_shape', 'circle') == 'circle':
                    pygame.draw.circle(surf, color, (effect['size'], effect['size']), effect['size'])
                elif effect.get('projectile_shape', 'circle') == 'triangle':
                    points = [
                        (effect['size'], 0),
                        (0, effect['size'] * 2),
                        (effect['size'] * 2, effect['size'] * 2)
                    ]
                    pygame.draw.polygon(surf, color, points)
                elif effect.get('projectile_shape', 'circle') == 'star':
                    # Vẽ sao 5 cánh
                    points = []
                    for i in range(10):
                        angle = math.pi * 2 * i / 10
                        radius = effect['size'] if i % 2 == 0 else effect['size'] / 2
                        points.append((
                            effect['size'] + radius * math.cos(angle),
                            effect['size'] + radius * math.sin(angle)
                        ))
                    pygame.draw.polygon(surf, color, points)

                # Xoay surface theo hướng chuyển động
                rotated = pygame.transform.rotate(surf, -math.degrees(effect['direction']) - 90)
                rect = rotated.get_rect(center=effect['pos'])
                self.game.screen.blit(rotated, rect)

            elif effect['type'] == 'buff':
                # Vẽ hiệu ứng buff
                alpha = effect.get('opacity', 150)
                color = (*effect['color'], alpha)

                # Tạo surface trong suốt
                surf = pygame.Surface((effect['radius'] * 2, effect['radius'] * 2), pygame.SRCALPHA)

                # Vẽ vòng tròn xung quanh mục tiêu
                pygame.draw.circle(surf, color, (effect['radius'], effect['radius']), effect['radius'], 3)

                # Vẽ các ký hiệu xoay tròn
                num_symbols = effect.get('num_symbols', 4)
                for i in range(num_symbols):
                    angle = effect['angle'] + (2 * math.pi * i / num_symbols)
                    symbol_pos = (
                        effect['radius'] + math.cos(angle) * effect['radius'] * 0.8,
                        effect['radius'] + math.sin(angle) * effect['radius'] * 0.8
                    )
                    symbol_size = effect.get('symbol_size', 5)
                    pygame.draw.circle(surf, color, symbol_pos, symbol_size)

                rect = surf.get_rect(center=effect['pos'])
                self.game.screen.blit(surf, rect)

            elif effect['type'] == 'beam':
                # Vẽ hiệu ứng tia
                alpha = effect.get('opacity', 200)
                color = (*effect['color'], alpha)

                # Tạo surface trong suốt
                length = effect['length']
                width = effect['width']
                surf = pygame.Surface((length, width), pygame.SRCALPHA)

                # Vẽ tia thẳng
                pygame.draw.line(surf, color, (0, width//2), (length, width//2), width)

                # Thêm hiệu ứng gradient
                for i in range(5):
                    gradient_color = (*effect['color'], alpha * (5-i) / 5)
                    pygame.draw.line(surf, gradient_color, (0, width//2), (length, width//2), max(1, width - i*2))

                # Xoay surface theo hướng
                rotated = pygame.transform.rotate(surf, -math.degrees(effect['direction']))
                rect = rotated.get_rect(center=effect['pos'])
                self.game.screen.blit(rotated, rect)

    def create_skill_effect(self, source_position, target_position, effect_type, skill_name=None):
        """Tạo hiệu ứng trực quan cho kỹ năng

        Parameters:
        - source_position: Vị trí nguồn của kỹ năng (thường là vị trí người dùng)
        - target_position: Vị trí mục tiêu (nơi tác động của kỹ năng)
        - effect_type: Loại kỹ năng hoặc hiệu ứng (như "fireball", "heal_wave", "echo_strike", ...)
        - skill_name: Tên kỹ năng (nếu không xác định cụ thể loại hiệu ứng)
        """
        # Xác định màu sắc dựa trên loại kỹ năng
        skill_element = "default"

        # Ánh xạ từ tên kỹ năng đến loại nguyên tố
        skill_to_element = {
            "fireball": "fire",
            "heal_wave": "heal",
            "divine_shield": "shield",
            "shadowstep": "shadow",
            "echo_strike": "sound",
            "void_resonance": "void",
            "blood_lust": "fire",
            "focus_mind": "lightning"
        }

        # Lấy màu từ loại kỹ năng
        if effect_type in skill_to_element:
            skill_element = skill_to_element[effect_type]
        elif skill_name and skill_name in skill_to_element:
            skill_element = skill_to_element[skill_name]
        elif effect_type in self.skill_colors:
            skill_element = effect_type

        # Lấy màu tương ứng
        color = self.skill_colors.get(skill_element, self.skill_colors["default"])

        # Tính toán hướng từ nguồn đến mục tiêu
        dx = target_position[0] - source_position[0]
        dy = target_position[1] - source_position[1]
        direction = math.atan2(dy, dx)
        distance = math.sqrt(dx*dx + dy*dy)

        # Tạo hiệu ứng dựa trên loại kỹ năng
        if effect_type in ["fireball", "projectile", "echo_strike"]:
            # Hiệu ứng đạn bay
            projectile_shape = 'circle'
            if "fire" in skill_element:
                projectile_shape = 'triangle'
            elif "sound" in effect_type or skill_element == "sound":
                projectile_shape = 'star'

            effect = {
                'type': 'projectile',
                'pos': list(source_position),
                'direction': direction,
                'speed': 300,  # pixels/second
                'size': 10,
                'lifetime': max(0.5, distance / 300),  # Thời gian để đến mục tiêu
                'current_time': 0.0,
                'color': color,
                'projectile_shape': projectile_shape
            }
            self.skill_effects.append(effect)

            # Thêm hiệu ứng va chạm ở mục tiêu sau khi hoàn thành
            impact_delay = distance / 300  # Thời gian để đạn bay đến mục tiêu
            pygame.time.set_timer(pygame.USEREVENT, int(impact_delay * 1000))
            # Sau khi hiệu ứng đến đích, thêm hiệu ứng nổ
            pygame.time.set_timer(pygame.USEREVENT, int(impact_delay * 1000), 1)

        elif effect_type in ["heal_wave", "aoe", "divine_shield", "focus_mind"]:
            # Hiệu ứng buff
            effect = {
                'type': 'buff',
                'pos': list(source_position if "self" in effect_type else target_position),
                'radius': 30,
                'lifetime': 1.5,
                'current_time': 0.0,
                'color': color,
                'angle': 0,
                'rotation_speed': 2,  # Tốc độ xoay (rad/s)
                'num_symbols': 6,
                'symbol_size': 6,
                'opacity': 180
            }
            self.skill_effects.append(effect)

            # Nếu là hiệu ứng phạm vi, thêm vòng tròn
            if "wave" in effect_type or "aoe" in effect_type:
                aoe_effect = {
                    'type': 'aoe_circle',
                    'pos': list(source_position if "self" in effect_type else target_position),
                    'radius': 0,
                    'max_radius': 100,
                    'lifetime': 1.0,
                    'current_time': 0.0,
                    'color': color,
                    'opacity': 150
                }
                self.skill_effects.append(aoe_effect)

        elif effect_type in ["beam", "void_resonance"]:
            # Hiệu ứng tia sáng
            effect = {
                'type': 'beam',
                'pos': list(source_position),
                'direction': direction,
                'width': 20,
                'max_width': 20,
                'length': 0,
                'max_length': distance,
                'lifetime': 0.8,
                'current_time': 0.0,
                'color': color,
                'opacity': 200
            }
            self.skill_effects.append(effect)

            # Thêm hiệu ứng nổ ở cuối tia
            impact_delay = 0.3  # Thời gian để tia đạt đến cuối
            pygame.time.set_timer(pygame.USEREVENT, int(impact_delay * 1000), 1)

        else:
            # Hiệu ứng mặc định nếu không khớp với loại cụ thể
            # Hiệu ứng AOE mặc định
            effect = {
                'type': 'aoe_circle',
                'pos': list(target_position),
                'radius': 0,
                'max_radius': 60,
                'lifetime': 0.8,
                'current_time': 0.0,
                'color': color,
                'opacity': 180
            }
            self.skill_effects.append(effect)

        # Thêm hiệu ứng ánh sáng nhỏ ở vị trí nguồn
        self.create_impact_effect(source_position, color=color, max_radius=15, lifetime=0.2)

        return True

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
