# src/core/game_manager.py
from typing import Optional, List, Dict, Any
import pygame
import sys
import time
import json

from src.core.entities import Player, NPC, Monster, Boss, PlayerRole
from src.systems.memory_system import MemorySystem
from src.systems.card_generator_enhanced import EnhancedCardGenerator
from src.systems.dialogue_system import DialogueSystem
from src.systems.player_behavior_analysis import PlayerBehaviorAnalysis
from src.systems.social_suspicion import SocialSuspicionSystem
from src.systems.event_generator import EventGenerator

class GameManager:
    def __init__(self):
        # Khởi tạo pygame
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Shadow Echo")
        self.clock = pygame.time.Clock()
        
        # Thiết lập font
        self.font = pygame.font.SysFont("Arial", 24)
        self.small_font = pygame.font.SysFont("Arial", 16)
        
        # Trạng thái game
        self.running = True
        self.current_day = 1
        self.is_night = False
        self.current_time = "day"
        self.pause = False
        
        # Các nhân vật trong game
        self.players = []        # Danh sách người chơi
        self.real_player = None  # Người chơi thật (do người dùng điều khiển)
        self.npcs = []           # Danh sách NPC
        self.monsters = []       # Danh sách quái vật
        
        # Thiết lập hệ thống
        self.memory_system = MemorySystem(self)
        self.card_generator = EnhancedCardGenerator(self)
        self.dialogue_system = DialogueSystem(self)
        self.behavior_analysis = PlayerBehaviorAnalysis(self)
        self.social_suspicion = SocialSuspicionSystem(self)
        self.event_generator = EventGenerator(self)
        
        # Khởi tạo game
        self._initialize_game()
    
    def _initialize_game(self):
        """Khởi tạo game từ đầu"""
        # Tạo người chơi thật
        self.real_player = Player(id=1, name="Unknown", role=PlayerRole.UNKNOWN)
        self.real_player.is_controlled = True
        self.real_player.position = (640, 360)
        self.players.append(self.real_player)
        
        # Tạo người chơi thật ẩn
        hidden_player = Player(id=2, name="Villager", role=PlayerRole.UNKNOWN)
        hidden_player.true_role = random.choice([PlayerRole.PROTECTOR, PlayerRole.TRAITOR])
        hidden_player.position = (400, 300)
        self.players.append(hidden_player)
        
        # Tạo các NPC
        self._initialize_npcs()
        
        # Khởi tạo event đầu game
        self.event_generator.update()
    
    def _initialize_npcs(self):
        """Khởi tạo các NPC"""
        npc_data = [
            {
                "id": 101,
                "name": "Father Thomas",
                "position": (200, 200),
                "personality": "từ tốn, đạo mạo",
                "dialogue": ["Cầu Chúa phù hộ con, người lạ.", "Vị khách từ phương xa, ta có thể giúp gì?"]
            },
            {
                "id": 102,
                "name": "Sister Maria",
                "position": (400, 200),
                "personality": "lo lắng, nhưng tốt bụng",
                "dialogue": ["Làng này không còn an toàn...", "Cẩn thận với những kẻ đeo mặt nạ."]
            },
            {
                "id": 103,
                "name": "Old Man Liu",
                "position": (600, 200),
                "personality": "già cỗi, nhiều bí mật",
                "dialogue": ["Hmm... lại một kẻ lạ mặt nữa.", "Ta đã sống đủ lâu để biết khi nào có chuyện chẳng lành."]
            },
            # Thêm nhiều NPC khác...
        ]
        
        for data in npc_data:
            npc = NPC(
                npc_id=data["id"],
                name=data["name"],
                dialogue_list=data["dialogue"],
                position=data["position"]
            )
            setattr(npc, "personality", data["personality"])
            self.npcs.append(npc)
    
    def run(self):
        """Vòng lặp game chính"""
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            
            self._handle_events()
            
            if not self.pause:
                self._update(dt)
            
            self._draw()
            
            pygame.display.flip()
    
    def _handle_events(self):
        """Xử lý input từ người chơi"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Handle key events
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.pause = not self.pause
                elif event.key == pygame.K_k:  # Giết nhân vật
                    self._handle_kill_attempt()
                elif event.key == pygame.K_e:  # Tương tác
                    self._handle_interaction()
                elif event.key == pygame.K_TAB:  # Mở nhật ký
                    self._handle_open_journal()
    
    def _update(self, dt):
        """Cập nhật trạng thái game"""
        # Cập nhật di chuyển người chơi
        self._update_player_movement(dt)
        
        # Cập nhật các NPC
        self._update_npcs(dt)
        
        # Cập nhật hệ thống event
        self.event_generator.update()
    
    def _update_player_movement(self, dt):
        """Cập nhật di chuyển người chơi"""
        if not self.real_player:
            return
        
        keys = pygame.key.get_pressed()
        speed = 200 * dt
        
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy -= speed
        if keys[pygame.K_s]: dy += speed
        if keys[pygame.K_a]: dx -= speed
        if keys[pygame.K_d]: dx += speed
        
        # Cập nhật vị trí
        new_x = self.real_player.position[0] + dx
        new_y = self.real_player.position[1] + dy
        
        # Giới hạn trong màn hình
        new_x = max(20, min(1260, new_x))
        new_y = max(20, min(700, new_y))
        
        # Set vị trí mới
        if dx != 0 or dy != 0:
            self.real_player.position = (new_x, new_y)
            
            # Ghi nhận chuyển động cho phân tích hành vi
            self.behavior_analysis.record_movement(
                self.real_player.id, 
                self.real_player.position,
                time.time()
            )
    
    def _update_npcs(self, dt):
        """Cập nhật hành vi NPC"""
        for npc in self.npcs:
            # TODO: Implement NPC behavior update
            pass
    
    def _draw(self):
        """Vẽ giao diện game"""
        # Fill background
        self.screen.fill((20, 20, 30))
        
        # Vẽ nhân vật và NPC
        self._draw_characters()
        
        # Vẽ UI
        self._draw_ui()
        
        # Vẽ debug info nếu cần
        if hasattr(self, 'debug_mode') and self.debug_mode:
            self._draw_debug_info()
    
    def _draw_characters(self):
        """Vẽ người chơi và NPC"""
        # Vẽ người chơi
        for player in self.players:
            if player.is_alive:
                color = (0, 200, 200) if player.is_controlled else (100, 100, 200)
                pygame.draw.rect(
                    self.screen, 
                    color, 
                    (int(player.position[0])-15, int(player.position[1])-15, 30, 30)
                )
                
                name_text = self.small_font.render(player.name, True, (255, 255, 255))
                self.screen.blit(
                    name_text, 
                    (int(player.position[0]) - name_text.get_width()//2, int(player.position[1]) + 20)
                )
        
        # Vẽ NPC
        for npc in self.npcs:
            if npc.alive:
                pygame.draw.rect(
                    self.screen, 
                    (100, 200, 100), 
                    (int(npc.position[0])-10, int(npc.position[1])-10, 20, 20)
                )
                
                name_text = self.small_font.render(npc.name, True, (200, 200, 200))
                self.screen.blit(
                    name_text, 
                    (int(npc.position[0]) - name_text.get_width()//2, int(npc.position[1]) + 15)
                )
    
    def _draw_ui(self):
        """Vẽ UI game"""
        # Vẽ thông tin ngày/đêm
        day_text = self.font.render(f"Ngày {self.current_day}: {'Đêm' if self.is_night else 'Ngày'}", True, (255, 255, 255))
        self.screen.blit(day_text, (20, 20))
        
        # Vẽ trợ giúp điều khiển
        controls_text = self.small_font.render("W/A/S/D: Di chuyển | E: Tương tác | K: Giết | TAB: Nhật ký", True, (200, 200, 200))
        self.screen.blit(controls_text, (20, 680))
    
    def _handle_kill_attempt(self):
        """Xử lý khi người chơi cố gắng giết ai đó"""
        if not self.real_player:
            return
        
        # Tìm target gần nhất
        target = self._find_nearest_target()
        if not target:
            return
        
        # Xử lý giết
        if isinstance(target, Player):
            # Kiểm tra nếu là người chơi thật khác
            if target.id != self.real_player.id and not target.is_controlled:
                if target.true_role not in [PlayerRole.UNKNOWN]:
                    # Thắng nếu đây là người chơi thật ẩn
                    self._handle_win_condition()
                else:
                    # NPC giả dạng - xử lý sai lầm
                    self._handle_wrong_kill()
        elif isinstance(target, NPC):
            # Giết nhầm NPC
            self._handle_wrong_kill()
    
    def _find_nearest_target(self):
        """Tìm target gần nhất với người chơi"""
        if not self.real_player:
            return None
        
        min_distance = float('inf')
        nearest_target = None
        
        # Kiểm tra các người chơi khác
        for player in self.players:
            if player.id == self.real_player.id or not player.is_alive:
                continue
                
            dx = player.position[0] - self.real_player.position[0]
            dy = player.position[1] - self.real_player.position[1]
            distance = (dx**2 + dy**2)**0.5
            
            if distance < 50 and distance < min_distance:
                min_distance = distance
                nearest_target = player
        
        # Kiểm tra các NPC
        for npc in self.npcs:
            if not npc.alive:
                continue
                
            dx = npc.position[0] - self.real_player.position[0]
            dy = npc.position[1] - self.real_player.position[1]
            distance = (dx**2 + dy**2)**0.5
            
            if distance < 50 and distance < min_distance:
                min_distance = distance
                nearest_target = npc
        
        return nearest_target
    
    def _handle_win_condition(self):
        """Xử lý khi người chơi thắng"""
        print("Thắng cuộc! Bạn đã tìm ra người chơi thật ẩn.")
        # TODO: Hiển thị màn hình thắng cuộc
    
    def _handle_wrong_kill(self):
        """Xử lý khi giết nhầm"""
        print("Bạn đã giết nhầm! Hãy cẩn thận.")
        # TODO: Xử lý trừ mạng hoặc debuff
    
    def _handle_interaction(self):
        """Xử lý khi người chơi tương tác (E)"""
        if not self.real_player:
            return
        
        # Tìm NPC gần nhất
        nearest_npc = None
        min_distance = float('inf')
        
        for npc in self.npcs:
            if not npc.alive:
                continue
                
            dx = npc.position[0] - self.real_player.position[0]
            dy = npc.position[1] - self.real_player.position[1]
            distance = (dx**2 + dy**2)**0.5
            
            if distance < 50 and distance < min_distance:
                min_distance = distance
                nearest_npc = npc
        
        if nearest_npc:
            self._start_dialogue(nearest_npc)
        else:
            # Tìm manh mối xung quanh
            memory = self.memory_system.discover_memory()
            if memory:
                print(f"Bạn tìm thấy một ký ức: {memory.text}")
                # TODO: Hiển thị UI ký ức
    
    def _start_dialogue(self, npc):
        """Bắt đầu hội thoại với NPC"""
        greeting = self.dialogue_system.start_conversation(self.real_player, npc.npc_id)
        print(f"[{npc.name}]: {greeting}")
        
        # TODO: Hiển thị UI hội thoại
    
    def _handle_open_journal(self):
        """Mở nhật ký ký ức"""
        # TODO: Hiển thị UI nhật ký
        pass
