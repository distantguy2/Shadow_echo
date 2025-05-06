# src/systems/memory_system.py
from typing import Dict, List, Tuple, Optional
import json
import random

class MemoryFragment:
    def __init__(self, text: str, role_hints: Dict[str, float], discovered: bool = False):
        self.text = text
        self.role_hints = role_hints  # {"sát thủ": 0.7, "điều tra viên": 0.2}
        self.discovered = discovered
        self.timestamp = 0  # Ngày tìm thấy

class MemorySystem:
    def __init__(self, game):
        self.game = game
        self.memories: List[MemoryFragment] = []
        self.discovered_memories: List[MemoryFragment] = []
        self.role_confidence: Dict[str, float] = {
            "sát thủ": 0.0,
            "điều tra viên": 0.0,
            "học giả": 0.0,
            "giáo sĩ": 0.0,
            "người thường": 0.0,
            "kẻ mạo danh": 0.0
        }
        self.load_memories()
    
    def load_memories(self):
        """Tải mảnh ký ức từ file cấu hình"""
        try:
            with open('data/memories.json', 'r', encoding='utf-8') as f:
                memory_data = json.load(f)
                for mem in memory_data:
                    fragment = MemoryFragment(
                        text=mem["text"],
                        role_hints=mem["role_hints"]
                    )
                    self.memories.append(fragment)
            random.shuffle(self.memories)  # Xáo trộn để mỗi lần chơi khác nhau
        except Exception as e:
            print(f"Error loading memories: {e}")
    
    def discover_memory(self, index: int = None):
        """Khám phá một mảnh ký ức mới"""
        if not self.memories:
            return None
        
        # Chọn mảnh ký ức ngẫu nhiên nếu không chỉ định cụ thể
        if index is None:
            memory = self.memories.pop(0)
        else:
            memory = self.memories.pop(index)
        
        memory.discovered = True
        memory.timestamp = self.game.current_day
        self.discovered_memories.append(memory)
        
        # Cập nhật % vai trò
        self._update_role_confidence()
        
        return memory
    
    def _update_role_confidence(self):
        """Cập nhật % vai trò dựa trên các mảnh ký ức đã khám phá"""
        # Reset confidence
        for role in self.role_confidence:
            self.role_confidence[role] = 0.0
        
        if not self.discovered_memories:
            return
        
        # Tính tổng weight của từng vai trò
        total_memories = len(self.discovered_memories)
        for memory in self.discovered_memories:
            for role, confidence in memory.role_hints.items():
                if role in self.role_confidence:
                    self.role_confidence[role] += confidence / total_memories
        
        # Chuẩn hóa để tổng = 1.0
        total = sum(self.role_confidence.values())
        if total > 0:
            for role in self.role_confidence:
                self.role_confidence[role] /= total
    
    def get_top_roles(self, limit: int = 3) -> List[Tuple[str, float]]:
        """Lấy N vai trò có % cao nhất"""
        sorted_roles = sorted(
            self.role_confidence.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        return sorted_roles[:limit]
    
    def get_suggested_cards(self) -> Dict[str, float]:
        """Lấy gợi ý các loại thẻ dựa trên vai trò hiện tại"""
        top_roles = self.get_top_roles()
        card_suggestions = {}
        
        # Map vai trò sang loại thẻ phù hợp
        role_to_card_type = {
            "sát thủ": ["attack", "stealth"],
            "điều tra viên": ["investigate", "perception"],
            "học giả": ["knowledge", "analyze"],
            "giáo sĩ": ["heal", "protect"],
            "người thường": ["utility", "survival"],
            "kẻ mạo danh": ["deception", "manipulation"]
        }
        
        # Tính weight cho mỗi loại thẻ
        for role, confidence in top_roles:
            if role in role_to_card_type:
                for card_type in role_to_card_type[role]:
                    card_suggestions[card_type] = card_suggestions.get(card_type, 0) + confidence
        
        return card_suggestions
