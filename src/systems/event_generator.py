# src/systems/event_generator.py
import random
from typing import List, Dict, Any

class EventType:
    MURDER = "murder"
    BLACKOUT = "blackout"
    RITUAL = "ritual"
    STRANGER = "stranger"
    THEFT = "theft"
    LOCKDOWN = "lockdown"
    CONFESSION = "confession"

class EventGenerator:
    def __init__(self, game):
        self.game = game
        self.triggered_events = []
        self.scheduled_events = []
        
        # Khởi tạo sự kiện theo lịch
        self._initialize_scheduled_events()
    
    def _initialize_scheduled_events(self):
        """Khởi tạo các sự kiện theo lịch cố định"""
        # Các sự kiện cố định theo ngày
        fixed_events = [
            {"day": 2, "type": EventType.RITUAL, "title": "Nghi lễ tế đêm", "required": True},
            {"day": 3, "type": EventType.LOCKDOWN, "title": "Phong tỏa làng", "required": True},
            {"day": 5, "type": EventType.STRANGER, "title": "Người lạ xuất hiện", "required": True},
        ]
        
        # Thêm vào danh sách scheduled
        for event in fixed_events:
            self.scheduled_events.append(event)
        
        # Thêm các sự kiện ngẫu nhiên
        self._schedule_random_events()
    
    def _schedule_random_events(self):
        """Lên lịch các sự kiện ngẫu nhiên"""
        possible_events = [
            {"type": EventType.MURDER, "title": "Vụ sát hại bí ẩn", "chance": 0.4},
            {"type": EventType.BLACKOUT, "title": "Mất điện toàn bộ", "chance": 0.6},
            {"type": EventType.THEFT, "title": "Mất cắp vật phẩm quan trọng", "chance": 0.5},
            {"type": EventType.CONFESSION, "title": "Lời thú tội", "chance": 0.3},
        ]
        
        # Phân bố các sự kiện ngẫu nhiên qua các ngày
        for day in range(1, 7):
            for event in possible_events:
                if random.random() < event["chance"] / 2:  # Giảm tần suất
                    new_event = event.copy()
                    new_event["day"] = day
                    new_event["required"] = False
                    self.scheduled_events.append(new_event)
    
    def update(self):
        """Cập nhật và kích hoạt sự kiện theo thời gian game"""
        current_day = self.game.current_day
        is_night = self.game.is_night
        
        # Kiểm tra các sự kiện theo lịch
        for event in self.scheduled_events[:]:
            if event["day"] == current_day:
                # Chỉ kích hoạt sự kiện đêm vào ban đêm
                if "night_only" in event and event["night_only"] and not is_night:
                    continue
                
                # Chỉ kích hoạt sự kiện ngày vào ban ngày
                if "day_only" in event and event["day_only"] and is_night:
                    continue
                
                # Xử lý kích hoạt
                self._trigger_event(event)
                self.scheduled_events.remove(event)
    
    def _trigger_event(self, event):
        """Kích hoạt một sự kiện"""
        event_type = event["type"]
        
        # Ghi log
        print(f"Triggering event: {event['title']} (type: {event_type})")
        
        # Thực hiện tác động theo loại sự kiện
        if event_type == EventType.MURDER:
            self._handle_murder_event(event)
        elif event_type == EventType.BLACKOUT:
            self._handle_blackout_event(event)
        elif event_type == EventType.RITUAL:
            self._handle_ritual_event(event)
        elif event_type == EventType.LOCKDOWN:
            self._handle_lockdown_event(event)
        # Xử lý các loại khác...
        
        # Thêm vào danh sách đã kích hoạt
        self.triggered_events.append(event)
        
        # Thông báo cho người chơi
        if hasattr(self.game, 'ui_bridge'):
            self.game.ui_bridge.show_notification(
                f"Sự kiện: {event['title']}!", "warning"
            )
    
    def _handle_murder_event(self, event):
        """Xử lý sự kiện sát hại"""
        # Chọn nạn nhân (NPC)
        valid_npcs = [npc for npc in self.game.npcs if npc.alive]
        if not valid_npcs:
            return
        
        victim = random.choice(valid_npcs)
        victim.alive = False
        
        # Tạo manh mối
        clue_text = f"Thi thể của {victim.name} được tìm thấy trong tình trạng đáng sợ."
        
        # Tạo clue và thêm vào game
        if hasattr(self.game, 'clue_generator'):
            self.game.clue_generator.create_environmental_clue(
                clue_text, 
                location=victim.position,
                related_to=["murder", victim.name]
            )
    
    def _handle_blackout_event(self, event):
        """Xử lý sự kiện mất điện"""
        # Set global state
        self.game.is_blackout = True
        self.game.blackout_duration = 1  # Kéo dài 1 ngày
        
        # Thay đổi ánh sáng môi trường
        if hasattr(self.game, 'environment'):
            self.game.environment.set_darkness(0.8)  # Tối hơn bình thường
        
        # Thay đổi hành vi NPC
        for npc in self.game.npcs:
            if hasattr(npc, 'behavior'):
                npc.behavior.set_state("nervous")  # NPCs trở nên lo lắng
    
    def _handle_ritual_event(self, event):
        """Xử lý sự kiện nghi lễ"""
        # Tất cả NPC tập trung về một điểm
        ritual_location = (400, 300)  # Vị trí trung tâm
        
        for npc in self.game.npcs:
            if npc.alive:
                npc.target_position = ritual_location
                if hasattr(npc, 'behavior'):
                    npc.behavior.set_state("ritual")
        
        # Tạo hiệu ứng đặc biệt
        if hasattr(self.game, 'effect_system'):
            self.game.effect_system.create_ritual_effect(ritual_location)
        
        # Mở khóa mảnh ký ức đặc biệt cho người chơi nếu tham gia nghi lễ
        ritual_memory = {
            "text": "Trong nghi lễ, bạn thấy một hình xăm quen thuộc trên tay áo của ai đó...",
            "role_hints": {
                # Tùy chỉnh hints theo vai trò người chơi
            },
            "discovered": False
        }
        
        # Thêm vào memory system để người chơi có thể khám phá
        if hasattr(self.game, 'memory_system'):
            self.game.memory_system.add_special_memory(ritual_memory)
    
    def _handle_lockdown_event(self, event):
        """Xử lý sự kiện phong tỏa"""
        # Set global state
        self.game.is_lockdown = True
        self.game.lockdown_duration = 2  # Kéo dài 2 ngày
        
        # Thay đổi ranh giới di chuyển
        if hasattr(self.game, 'map_system'):
            self.game.map_system.restrict_boundaries(0.7)  # Thu hẹp 30%
        
        # NPCs trở nên đề phòng hơn
        for npc in self.game.npcs:
            if hasattr(npc, 'behavior'):
                npc.behavior.set_state("alert")
                npc.behavior.suspicion_multiplier = 1.5  # Dễ nghi ngờ hơn
