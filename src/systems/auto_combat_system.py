# src/systems/auto_combat_system.py

import math
import random
import pygame
from typing import List, Tuple, Optional

class AutoCombatSystem:
    """Hệ thống tự động tấn công quái vật"""
    
    def __init__(self, game):
        self.game = game
        self.attack_cooldown = 1.0     # Tần suất tấn công (giây)
        self.current_cooldown = 0.0    # Thời gian cooldown hiện tại
        self.attack_range = 150.0      # Phạm vi tấn công
        self.attack_damage = 20        # Sát thương mỗi đòn
        self.attack_only_monsters = True  # Chỉ tấn công quái vật
    
    def update(self, dt):
        """Cập nhật hệ thống tự động tấn công"""
        if not getattr(self.game, 'auto_combat_active', True):
            return
            
        # Giảm cooldown
        if self.current_cooldown > 0:
            self.current_cooldown -= dt
        
        # Kiểm tra có thể tấn công không
        if self.current_cooldown <= 0:
            # Tìm người chơi và quái vật
            players = self._get_controlled_players()
            monsters = self._get_nearby_monsters(players)
            
            # Nếu có quái vật, thực hiện tấn công
            if monsters:
                self._perform_auto_attacks(players, monsters)
                self.current_cooldown = self.attack_cooldown
    
    def draw(self, screen):
        """Vẽ hiệu ứng tấn công và thông tin debug"""
        # Vẽ phạm vi tấn công khi ở chế độ debug
        if getattr(self.game, 'debug_mode', False):
            for player in self._get_controlled_players():
                # Vẽ vòng tròn phạm vi tấn công (màu đỏ trong suốt)
                pygame.draw.circle(
                    screen,
                    (255, 0, 0, 50),  # Màu đỏ với độ trong suốt
                    (int(player.position[0]), int(player.position[1])),
                    int(self.attack_range),
                    1  # Độ dày viền
                )
                
                # Vẽ thanh cooldown nhỏ trên đầu nhân vật
                cooldown_pct = 1 - (self.current_cooldown / self.attack_cooldown)
                bar_width = 30
                bar_height = 4
                bar_x = int(player.position[0]) - bar_width // 2
                bar_y = int(player.position[1]) - 30  # Phía trên nhân vật
                
                pygame.draw.rect(
                    screen,
                    (100, 100, 100),  # Màu nền xám
                    (bar_x, bar_y, bar_width, bar_height)
                )
                pygame.draw.rect(
                    screen,
                    (0, 200, 0),  # Màu xanh lá
                    (bar_x, bar_y, int(bar_width * cooldown_pct), bar_height)
                )
    
    def _get_controlled_players(self):
        """Lấy danh sách người chơi có thể tấn công"""
        if not hasattr(self.game, 'players'):
            return []
        
        return [p for p in self.game.players if getattr(p, 'is_alive', True)]
    
    def _get_nearby_monsters(self, players):
        """Lấy danh sách quái vật gần người chơi"""
        if not hasattr(self.game, 'monsters'):
            return []
        
        nearby_monsters = []
        for monster in self.game.monsters:
            if not getattr(monster, 'alive', True) or getattr(monster, 'hp', 0) <= 0:
                continue
                
            # Kiểm tra có trong tầm tấn công của bất kỳ người chơi nào không
            for player in players:
                distance = self._calculate_distance(
                    player.position, 
                    getattr(monster, 'position', (0, 0))
                )
                
                if distance <= self.attack_range:
                    nearby_monsters.append(monster)
                    break
        
        return nearby_monsters
    
    def _perform_auto_attacks(self, players, monsters):
        """Thực hiện tấn công tự động"""
        for player in players:
            # Tìm quái vật gần nhất
            nearest_monster = self._find_nearest_monster(player, monsters)
            if nearest_monster:
                # Tấn công
                self._attack_target(player, nearest_monster)
    
    def _find_nearest_monster(self, player, monsters):
        """Tìm quái vật gần nhất"""
        if not monsters:
            return None
            
        nearest = None
        min_distance = float('inf')
        
        for monster in monsters:
            distance = self._calculate_distance(
                player.position, 
                getattr(monster, 'position', (0, 0))
            )
            
            if distance < min_distance:
                min_distance = distance
                nearest = monster
        
        return nearest
    
    def _attack_target(self, player, target):
        """Thực hiện đòn tấn công"""
        # Kiểm tra nếu chỉ tấn công quái vật
        if self.attack_only_monsters and not hasattr(target, 'is_boss') and not hasattr(target, 'symbol'):
            return
        
        # Xử lý sát thương
        if hasattr(target, 'take_damage'):
            target.take_damage(self.attack_damage)
        else:
            # Fallback nếu không có phương thức take_damage
            setattr(target, 'hp', getattr(target, 'hp', 100) - self.attack_damage)
            if getattr(target, 'hp', 0) <= 0:
                setattr(target, 'alive', False)
        
        # Tạo hiệu ứng tấn công nếu có
        if hasattr(self.game, 'gameplay_enhancements') and hasattr(self.game.gameplay_enhancements, 'create_impact_effect'):
            self.game.gameplay_enhancements.create_impact_effect(getattr(target, 'position', (0, 0)))
        
        # Kiểm tra nếu target đã chết
        if getattr(target, 'hp', 0) <= 0:
            # Xử lý khi tiêu diệt quái vật
            if hasattr(self.game, 'monsters') and target in self.game.monsters:
                self.game.monsters.remove(target)
                
                # Tăng exp nếu cần
                if hasattr(player, 'add_exp'):
                    player.add_exp(50)  # 50 điểm exp cho mỗi quái
                
                # Thông báo
                if hasattr(self.game, 'ui_bridge') and hasattr(self.game.ui_bridge, 'show_notification'):
                    self.game.ui_bridge.show_notification(f"Defeated monster!", "success")
    
    def _calculate_distance(self, pos1, pos2):
        """Tính khoảng cách giữa hai điểm"""
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        return math.sqrt(dx*dx + dy*dy)
