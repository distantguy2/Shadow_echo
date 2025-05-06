# src/systems/card_generator.py

import random
from typing import List, Dict, Any

class CardGenerator:
    """Generates card options for selection screens"""
    
    def __init__(self, game):
        self.game = game
        
        # Card type pools
        self.attack_cards = [
            {
                "id": "kiemstatikk",
                "name": "Kiếm Statikk",
                "type": "attack",
                "icon": "⚡",
                "description": "Phóng ra tia chớp sấy giữa những kẻ địch nhiều mục tiêu.",
                "effect": {"damage": 30, "targets": 3}
            },
            {
                "id": "tuvuongkiem",
                "name": "Tử Vương Kiếm",
                "type": "attack",
                "icon": "⚔️",
                "description": "Gây sát thương cao và làm chậm mục tiêu.",
                "effect": {"damage": 50, "slow": 0.3}
            },
            {
                "id": "thietkiemcuong",
                "name": "Thiết Kiếm Cuồng",
                "type": "attack",
                "icon": "🗡️",
                "description": "Chém liên tục trước mặt, gây sát thương cao.",
                "effect": {"damage": 15, "hits": 4}
            }
        ]
        
        self.utility_cards = [
            {
                # src/systems/card_generator.py (continued)

                "id": "sutudoa",
                "name": "Sư Tử Đọa Đày",
                "type": "utility",
                "icon": "🌊",
                "description": "Bắn ra bong bóng lớn theo chiều ngang.",
                "effect": {"slow": 0.5, "duration": 3}
            },
            {
                "id": "thanthoai",
                "name": "Thần Thoại",
                "type": "utility",
                "icon": "🌀",
                "description": "Tạo lốc xoáy đẩy lùi kẻ địch và làm chậm.",
                "effect": {"knockback": 100, "slow": 0.4}
            },
            {
                "id": "khienbangtiet",
                "name": "Khiên Băng Tiết",
                "type": "utility",
                "icon": "❄️",
                "description": "Tạo khiên bảo vệ và đóng băng kẻ địch xung quanh.",
                "effect": {"shield": 40, "freeze": 2}
            }
        ]
        
        self.support_cards = [
            {
                "id": "mautoi",
                "name": "Máu Tối Đa",
                "type": "support",
                "icon": "❤️",
                "description": "Tăng lượng máu tối đa và hồi phục.",
                "effect": {"max_hp": 150, "heal": 50}
            },
            {
                "id": "hoiphuc",
                "name": "Hồi Phục",
                "type": "support",
                "icon": "✚",
                "description": "Hồi phục liên tục trong thời gian dài.",
                "effect": {"heal_per_sec": 5, "duration": 10}
            },
            {
                "id": "tocbien",
                "name": "Tốc Biến",
                "type": "support",
                "icon": "⚡",
                "description": "Tăng tốc độ di chuyển và tấn công.",
                "effect": {"move_speed": 0.3, "attack_speed": 0.2}
            }
        ]
    
    def generate_card_options(self, player_level: int, num_options: int = 3) -> List[Dict[str, Any]]:
        """Generate a set of card options based on player level"""
        options = []
        
        # Always include at least one attack card
        options.append(random.choice(self.attack_cards))
        
        # Higher chance for support cards at higher levels
        support_chance = min(0.3 + player_level * 0.05, 0.6)
        
        # Fill remaining slots
        remaining_slots = num_options - len(options)
        for _ in range(remaining_slots):
            if random.random() < support_chance:
                card_pool = self.support_cards
            else:
                card_pool = random.choice([self.attack_cards, self.utility_cards])
                
            # Select a card not already in options
            available_cards = [c for c in card_pool if not any(o["id"] == c["id"] for o in options)]
            if available_cards:
                options.append(random.choice(available_cards))
            else:
                # If all cards from the chosen pool are taken, pick from another pool
                alternative_pool = random.choice([self.attack_cards, self.utility_cards, self.support_cards])
                available_cards = [c for c in alternative_pool if not any(o["id"] == c["id"] for o in options)]
                if available_cards:
                    options.append(random.choice(available_cards))
        
        # Shuffle the options
        random.shuffle(options)
        return options
