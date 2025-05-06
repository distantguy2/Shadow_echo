# src/systems/card_generator_enhanced.py
import random
from typing import List, Dict, Any

class EnhancedCardGenerator:
    def __init__(self, game):
        self.game = game
        
        # Card pools theo vai trò
        self.role_card_pools = {
            "sát thủ": [
                {
                    "id": "shadow_blade",
                    "name": "Lưỡi Dao Bóng Đêm",
                    "type": "attack",
                    "icon": "🗡️",
                    "description": "Giết một NPC mà không để lại dấu vết",
                    "effect": {"silent_kill": True, "cooldown": 2}
                },
                # Thêm nhiều thẻ khác...
            ],
            "điều tra viên": [
                {
                    "id": "truth_serum",
                    "name": "Huyết Thanh Sự Thật",
                    "type": "investigate",
                    "icon": "💉",
                    "description": "Buộc một NPC nói thật trong lần đối thoại tiếp theo",
                    "effect": {"force_truth": True, "uses": 1}
                },
                # Thêm nhiều thẻ khác...
            ],
            # Các vai trò khác...
        }
        
        # Thẻ chung cho mọi vai trò
        self.universal_cards = [
            {
                "id": "memory_recall",
                "name": "Hồi Ức Lãng Quên",
                "type": "utility",
                "icon": "🧠",
                "description": "Khám phá thêm một mảnh ký ức",
                "effect": {"discover_memory": 1}
            },
            # Thêm nhiều thẻ khác...
        ]
    
    def generate_role_based_options(self, num_options: int = 3) -> List[Dict[str, Any]]:
        """Tạo thẻ bài dựa trên vai trò tiềm năng của người chơi"""
        options = []
        
        # Lấy % gợi ý thẻ từ memory system
        card_suggestions = self.game.memory_system.get_suggested_cards()
        
        # Dùng cơ số ngẫu nhiên để chọn thẻ
        rng = random.Random()
        
        # 60% thẻ theo vai trò có % cao nhất
        top_role_cards = 1 if num_options <= 3 else 2
        for _ in range(top_role_cards):
            if not card_suggestions:
                card_type = random.choice(list(self.role_card_pools.keys()))
            else:
                # Chọn ngẫu nhiên weighted theo % gợi ý
                card_types = list(card_suggestions.keys())
                weights = list(card_suggestions.values())
                card_type = rng.choices(card_types, weights=weights, k=1)[0]
            
            # Tìm pool phù hợp
            pool = None
            for role, types in self.role_card_pools.items():
                if card_type in types:
                    pool = self.role_card_pools[role]
                    break
            
            if pool:
                card = random.choice(pool)
                options.append(card)
            else:
                # Fallback to universal cards
                card = random.choice(self.universal_cards)
                options.append(card)
        
        # 30% thẻ ngẫu nhiên
        universal_count = num_options - top_role_cards - 1
        for _ in range(universal_count):
            card = random.choice(self.universal_cards)
            if not any(c["id"] == card["id"] for c in options):
                options.append(card)
        
        # 10% thẻ đánh lạc hướng
        misleading_roles = [r for r, c in self.game.memory_system.get_top_roles(5) if c < 0.15]
        if misleading_roles:
            role = random.choice(misleading_roles)
            if role in self.role_card_pools:
                card = random.choice(self.role_card_pools[role])
                options.append(card)
            else:
                card = random.choice(self.universal_cards)
                options.append(card)
        else:
            card = random.choice(self.universal_cards)
            options.append(card)
        
        # Xáo trộn kết quả
        random.shuffle(options)
        return options[:num_options]
