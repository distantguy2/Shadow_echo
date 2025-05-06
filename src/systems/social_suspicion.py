# src/systems/social_suspicion.py
from typing import Dict, List, Tuple
import math

class SocialSuspicionSystem:
    def __init__(self, game):
        self.game = game
        self.suspicion_levels = {}  # {character_id: {target_id: suspicion_level}}
        self.suspicious_behaviors = []
        self.accusations = []
        
        # Khởi tạo mức nghi ngờ ban đầu
        self._initialize_suspicion()
    
    def _initialize_suspicion(self):
        """Khởi tạo mức nghi ngờ ban đầu giữa các nhân vật"""
        characters = self.game.players + self.game.npcs
        
        for char in characters:
            char_id = char.id if hasattr(char, 'id') else char.npc_id
            self.suspicion_levels[char_id] = {}
            
            for target in characters:
                if char == target:
                    continue
                    
                target_id = target.id if hasattr(target, 'id') else target.npc_id
                
                # Mức nghi ngờ ban đầu ngẫu nhiên nhỏ
                initial_suspicion = 0.05 + (0.1 * random.random())
                self.suspicion_levels[char_id][target_id] = initial_suspicion
    
    def record_suspicious_behavior(self, character_id, behavior_type, witnesses=None, target=None):
        """Ghi nhận hành vi đáng ngờ"""
        behavior = {
            "character_id": character_id,
            "behavior_type": behavior_type,
            "day": self.game.current_day,
            "witnesses": witnesses or [],
            "target": target,
            "time": self.game.current_time  # Ngày/đêm
        }
        
        self.suspicious_behaviors.append(behavior)
        
        # Cập nhật mức nghi ngờ
        self._update_suspicion_for_behavior(behavior)
    
    def _update_suspicion_for_behavior(self, behavior):
        """Cập nhật mức nghi ngờ dựa trên một hành vi đáng ngờ"""
        # Cấu hình suspicion gain dựa trên loại hành vi
        suspicion_gains = {
            "sneaking": 0.15,
            "lying": 0.25,
            "investigating": 0.1,
            "hostile_question": 0.2,
            "loitering": 0.05,
            "tampering": 0.3,
            "possession": 0.2
        }
        
        char_id = behavior["character_id"]
        behavior_type = behavior["behavior_type"]
        
        # Xác định mức tăng nghi ngờ
        suspicion_gain = suspicion_gains.get(behavior_type, 0.1)
        
        # Cập nhật nghi ngờ cho các nhân chứng
        for witness_id in behavior["witnesses"]:
            if witness_id in self.suspicion_levels and char_id in self.suspicion_levels[witness_id]:
                current = self.suspicion_levels[witness_id][char_id]
                # Sử dụng sigmoid để không tăng quá 1.0
                self.suspicion_levels[witness_id][char_id] = min(
                    1.0, 
                    current + suspicion_gain * (1.0 - current)
                )
    
    def get_suspicion_level(self, observer_id, target_id):
        """Lấy mức độ nghi ngờ của observer đối với target"""
        if observer_id in self.suspicion_levels and target_id in self.suspicion_levels[observer_id]:
            return self.suspicion_levels[observer_id][target_id]
        return 0.0
    
    def make_accusation(self, accuser_id, accused_id, reason, evidence_ids=None):
        """Tạo một lời buộc tội"""
        accusation = {
            "accuser_id": accuser_id,
            "accused_id": accused_id,
            "reason": reason,
            "evidence": evidence_ids or [],
            "day": self.game.current_day,
            "supporters": [],
            "opponents": []
        }
        
        self.accusations.append(accusation)
        
        # Spread suspicion to other characters
        self._process_accusation_impact(accusation)
        
        return accusation
    
    def _process_accusation_impact(self, accusation):
        """Xử lý tác động của lời buộc tội đến mạng lưới xã hội"""
        accuser_id = accusation["accuser_id"]
        accused_id = accusation["accused_id"]
        
        # Độ tin cậy của người buộc tội ảnh hưởng đến mức lan truyền nghi ngờ
        accuser_credibility = self._calculate_character_credibility(accuser_id)
        
        # Lan truyền nghi ngờ đến những nhân vật khác
        for observer_id in self.suspicion_levels:
            if observer_id == accuser_id or observer_id == accused_id:
                continue
                
            # Mức tin tưởng của observer đối với accuser
            trust_in_accuser = 1.0 - self.get_suspicion_level(observer_id, accuser_id)
            
            # Mức nghi ngờ hiện tại đối với accused
            current_suspicion = self.get_suspicion_level(observer_id, accused_id)
            
            # Tăng nghi ngờ dựa trên độ tin cậy và quan hệ
            suspicion_increase = 0.2 * accuser_credibility * trust_in_accuser
            new_suspicion = current_suspicion + suspicion_increase * (1.0 - current_suspicion)
            
            self.suspicion_levels[observer_id][accused_id] = min(1.0, new_suspicion)
    
    def _calculate_character_credibility(self, character_id):
        """Tính độ tin cậy của một nhân vật dựa trên các yếu tố xã hội"""
        # Lấy character
        character = None
        for char in self.game.players + self.game.npcs:
            char_id = char.id if hasattr(char, 'id') else char.npc_id
            if char_id == character_id:
                character = char
                break
        
        if not character:
            return 0.5  # Default
        
        # Các yếu tố ảnh hưởng đến độ tin cậy
        # 1. Mức độ nghi ngờ trung bình từ người khác
        average_suspicion = 0.0
        suspicion_count = 0
        for observer_id, targets in self.suspicion_levels.items():
            if observer_id != character_id and character_id in targets:
                average_suspicion += targets[character_id]
                suspicion_count += 1
        
        if suspicion_count > 0:
            average_suspicion /= suspicion_count
        
        # 2. Lịch sử buộc tội (đúng/sai)
        accusation_accuracy = 0.5  # Default - chưa có dữ liệu
        
        # TODO: Tính độ chính xác của các lời buộc tội trước đây
        
        # Tổng hợp
        credibility = 0.7 * (1.0 - average_suspicion) + 0.3 * accusation_accuracy
        
        return max(0.1, min(0.9, credibility))  # Giữ trong khoảng hợp lý
