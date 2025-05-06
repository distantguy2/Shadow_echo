# src/systems/monsters.py - MONSTER SYSTEM

import random
import math
import pygame  # Thêm import này để vẽ monsters
from ..core.entities import Monster
from config.settings import MONSTER_SPAWN_CONFIG, SCREEN_WIDTH, SCREEN_HEIGHT

class MonsterSystem:
    """Manages monster spawning and behavior"""
    
    def __init__(self, game):
        self.game = game
        self.monsters = []
    
    def spawn_monsters(self):
        """Spawn monsters based on current day"""
        # Clear existing monsters
        self.monsters.clear()
        
        # Calculate number of monsters - sửa để tránh lỗi
        player_count = 3  # Giá trị mặc định
        
        # Kiểm tra xem có player_manager hay không
        if hasattr(self.game, 'player_manager') and hasattr(self.game.player_manager, 'players'):
            player_count = sum(1 for p in self.game.player_manager.players if p.is_alive)
        elif hasattr(self.game, 'players'):
            # Sử dụng trực tiếp từ game.players nếu không có player_manager
            player_count = sum(1 for p in self.game.players if p.is_alive)
        
        day_count = self.game.phase_manager.day_count
        
        # Base count + scaling
        monster_count = (MONSTER_SPAWN_CONFIG["base_per_player"] * player_count + 
                        int(MONSTER_SPAWN_CONFIG["scaling_per_day"] * (day_count - 1)))
        
        # Clamp between min and max
        monster_count = max(MONSTER_SPAWN_CONFIG["min_monsters"], 
                           min(MONSTER_SPAWN_CONFIG["max_monsters"], monster_count))
        
        # Create monsters
        monster_types = MONSTER_SPAWN_CONFIG["types"]
        weights = [m["weight"] for m in monster_types]
        
        for _ in range(monster_count):
            # Select type
            monster_data = random.choices(monster_types, weights=weights)[0]
            
            # Scale stats
            hp_scale = 1 + (day_count - 1) * 0.2
            damage_scale = 1 + (day_count - 1) * 0.1
            
            hp = int(monster_data["hp"] * hp_scale)
            damage = int(monster_data["damage"] * damage_scale)
            
            # Spawn position
            pos = self._get_spawn_position()
            
            monster = Monster(monster_data["symbol"], hp, damage, pos, monster_data["speed"])
            monster.max_hp = hp
            self.monsters.append(monster)
        
        self.game.logger.info(f"Spawned {monster_count} monsters for day {day_count}")
    
    def _get_spawn_position(self):
        """Get random spawn position from screen edges"""
        edge = random.choice(['top', 'left', 'right'])
        if edge == 'top':
            return [random.randint(100, SCREEN_WIDTH-100), 0]
        elif edge == 'left':
            return [0, random.randint(100, SCREEN_HEIGHT-100)]
        else:
            return [SCREEN_WIDTH, random.randint(100, SCREEN_HEIGHT-100)]
    
    def update(self, dt):
        """Update all monsters"""
        if self.game.phase_manager.is_night_phase():
            return
    
        for monster in self.monsters[:]:
            self._update_monster_movement(monster, dt)
            self._handle_monster_attacks(monster, dt)
    
    def _update_monster_movement(self, monster, dt):
        """Update monster movement towards targets"""
        # Find nearest target
        targets = []
        
        # Add players as targets - sửa để tránh lỗi
        if hasattr(self.game, 'player_manager') and hasattr(self.game.player_manager, 'players'):
            for player in self.game.player_manager.players:
                if player.is_alive:
                    targets.append({"position": player.position, "is_player": True, "obj": player})
        elif hasattr(self.game, 'players'):
            for player in self.game.players:
                if player.is_alive:
                    targets.append({"position": player.position, "is_player": True, "obj": player})
        
        # Add NPCs as targets - sửa để tránh lỗi
        if hasattr(self.game, 'npc_system') and hasattr(self.game.npc_system, 'npcs'):
            for npc in self.game.npc_system.npcs:
                if npc["alive"]:
                    targets.append({"position": npc["position"], "is_player": False, "obj": npc})
        
        if not targets:
            return
        
        # Find nearest target
        nearest = min(targets, key=lambda t: self._distance(monster.position, t["position"]))
        
        # Move towards target
        dx = nearest["position"][0] - monster.position[0]
        dy = nearest["position"][1] - monster.position[1]
        dist = (dx**2 + dy**2)**0.5
        
        if dist > 0:
            monster.position[0] += (dx / dist) * monster.speed * dt * 50
            monster.position[1] += (dy / dist) * monster.speed * dt * 50
    
    def _handle_monster_attacks(self, monster, dt):
        """Handle monster attacks"""
        # Find targets in attack range
        for target in self._get_targets_in_range(monster, 30):
            if target["is_player"]:
                player = target["obj"]
                player.hp = max(0, player.hp - monster.damage * dt)
                if player.hp <= 0:
                    player.is_alive = False
                    if hasattr(self.game, 'ui_bridge'):
                        self.game.ui_bridge.show_notification(f"{player.name} has fallen!", "error")
            else:
                npc = target["obj"]
                npc["hp"] = max(0, npc["hp"] - monster.damage * dt)
                if npc["hp"] <= 0:
                    npc["alive"] = False
                    if hasattr(self.game, 'ui_bridge'):
                        self.game.ui_bridge.show_notification(f"NPC {npc['name']} has died!", "error")
    
    def _get_targets_in_range(self, monster, range):
        """Get all targets within range"""
        targets = []
        
        # Check players - sửa để tránh lỗi
        if hasattr(self.game, 'player_manager') and hasattr(self.game.player_manager, 'players'):
            for player in self.game.player_manager.players:
                if player.is_alive and self._distance(monster.position, player.position) < range:
                    targets.append({"position": player.position, "is_player": True, "obj": player})
        elif hasattr(self.game, 'players'):
            for player in self.game.players:
                if player.is_alive and self._distance(monster.position, player.position) < range:
                    targets.append({"position": player.position, "is_player": True, "obj": player})
        
        # Check NPCs - sửa để tránh lỗi
        if hasattr(self.game, 'npc_system') and hasattr(self.game.npc_system, 'npcs'):
            for npc in self.game.npc_system.npcs:
                if npc["alive"] and self._distance(monster.position, npc["position"]) < range:
                    targets.append({"position": npc["position"], "is_player": False, "obj": npc})
        
        return targets
    
    def _distance(self, pos1, pos2):
        """Calculate distance between positions"""
        dx = pos1[0] - pos2[0]
        dy = pos1[1] - pos2[1]
        return math.sqrt(dx**2 + dy**2)
    
    def draw(self, screen):
        """Draw all monsters"""
        for monster in self.monsters:
            # Chỉ vẽ quái vật khi là ban ngày hoặc chế độ debug
            if not self.game.phase_manager.is_night_phase() or (hasattr(self.game, 'debug_mode') and self.game.debug_mode):
                # Draw monster sprite
                pygame.draw.circle(screen, (255, 0, 0), 
                                 (int(monster.position[0]), int(monster.position[1])), 8)
                
                # Draw symbol
                if hasattr(self.game, 'font'):
                    font_surface = self.game.font.render(monster.symbol, True, (255, 255, 255))
                    rect = font_surface.get_rect(center=(int(monster.position[0]), int(monster.position[1])))
                    screen.blit(font_surface, rect)
                else:
                    # Fallback nếu không có font
                    pygame.draw.rect(screen, (255, 255, 255), 
                                  (int(monster.position[0])-5, int(monster.position[1])-5, 10, 10))
                
                # Sửa: Vẽ thanh máu cho quái vật
                self._draw_monster_health(screen, monster)

    def _draw_monster_health(self, screen, monster):
        """Vẽ thanh máu của quái vật"""
        # Đảm bảo quái vật có thuộc tính max_hp
        if not hasattr(monster, 'max_hp') or monster.max_hp == 0:
            monster.max_hp = monster.hp  # Sử dụng hp hiện tại nếu không có max_hp
        
        # Tính tỷ lệ máu
        health_ratio = max(0, min(1.0, monster.hp / monster.max_hp))
        
        # Kích thước thanh máu
        bar_width = 30
        bar_height = 4
        
        # Vị trí thanh máu (phía trên quái vật)
        x = int(monster.position[0] - bar_width/2)
        y = int(monster.position[1] - 15)
        
        # Vẽ nền thanh máu (màu đỏ tối)
        pygame.draw.rect(screen, (100, 0, 0), (x, y, bar_width, bar_height))
        
        # Vẽ máu hiện tại (màu đỏ sáng)
        if health_ratio > 0:
            current_width = int(bar_width * health_ratio)
            pygame.draw.rect(screen, (255, 0, 0), (x, y, current_width, bar_height))
        
        # Vẽ viền
        pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 1)
                
    def apply_difficulty_scaling(self, scaling_factor):
        """Scale monster stats by difficulty factor"""
        for monster in self.monsters:
            monster.max_hp = int(monster.max_hp * scaling_factor)
            monster.hp = monster.max_hp
            monster.damage = int(monster.damage * scaling_factor)
    
    def spawn_boss(self, day):
        """Spawn boss on certain days"""
        # Thêm boss vào monsters
        boss_types = {
            3: {"symbol": "♛", "hp": 500, "damage": 25, "speed": 0.7},
            6: {"symbol": "♞", "hp": 800, "damage": 35, "speed": 0.8},
            10: {"symbol": "♟", "hp": 1200, "damage": 50, "speed": 1.0}
        }
        
        if day not in boss_types:
            return
            
        boss_data = boss_types[day]
        boss_pos = self._get_spawn_position()
        
        boss = Monster(
            boss_data["symbol"], 
            boss_data["hp"], 
            boss_data["damage"], 
            boss_pos, 
            boss_data["speed"]
        )
        boss.is_boss = True
        self.monsters.append(boss)
        
        if hasattr(self.game, 'ui_bridge'):
            self.game.ui_bridge.show_notification(f"BOSS HAS APPEARED!", "warning")
    
    def reset(self):
        """Reset the monster system"""
        self.monsters.clear()
