# src/systems/alignment.py

import time
import random
from typing import Dict, List, Optional

class AlignmentManager:
    """Quản lý hệ thống Alignment (Sin/Grace)"""
    
    def __init__(self, game):
        self.game = game
        self.clues: List[dict] = []
        self.npc_trust: Dict[str, float] = {}  # Độ tin tưởng của NPC
        
    def update_player_alignment(self, player, card_effect=None):
        """Cập nhật alignment của player"""
        player.alignment.update(card_effect)
        
        # Kiểm tra có cần tạo clue không
        if player.alignment.should_generate_clue():
            if random.random() < 0.2:  # 20% chance
                self.generate_clue(player)
        
        # Kiểm tra NPC reaction
        self.check_npc_reactions(player)
        
        # Log status
        self.game.logger.info(f"{player.name} - Sin: {player.alignment.sin}, Grace: {player.alignment.grace}, Suspicion: {player.alignment.suspicion:.1f}%")
    
    def generate_clue(self, player):
        """Tạo clue về player"""
        clue_templates = [
            "Thấy vết máu sau nhà kho",
            "Nghe tiếng khóc NPC ban đêm",
            "Tìm thấy dấu hiệu đắc tội",
            "Người này hành xử đáng ngờ",
            "Phát hiện yếu tố bất thường"
        ]
        
        npc_names = ["Sister Maria", "Brother John", "Father Thomas", "Mother Catherine"]
        
        clue = {
            "text": random.choice(clue_templates),
            "credibility": random.uniform(0.5, 1.0),
            "source": random.choice(npc_names),
            "target_player": player.id,
            "sin_level": player.alignment.sin
        }
        
        self.clues.append(clue)
        player.add_clue(clue)
        
        self.game.logger.info(f"Generated clue about {player.name}: {clue['text']}")
    
    def check_npc_reactions(self, player):
        """Kiểm tra phản ứng NPC"""
        if player.alignment.is_suspected():
            # NPC bắt đầu nghi ngờ
            self.update_npc_trust(player, -0.1)
            
        if player.alignment.is_role_revealed():
            # Lộ role
            self.reveal_player_role(player)
    
    def update_npc_trust(self, player, trust_change: float):
        """Cập nhật độ tin tưởng NPC"""
        key = str(player.id)
        if key not in self.npc_trust:
            self.npc_trust[key] = 1.0
        
        self.npc_trust[key] = max(0.0, min(1.0, self.npc_trust[key] + trust_change))
        
        self.game.logger.info(f"NPC trust for {player.name}: {self.npc_trust[key]:.2f}")
    
    def reveal_player_role(self, player):
        """Tiết lộ role của player"""
        if player.role == player.PlayerRole.UNKNOWN and player.true_role != player.PlayerRole.UNKNOWN:
            player.role = player.true_role
            
            message = f"{player.name}'s true role is revealed: {player.role.value}"
            self.game.ui_bridge.show_notification(message, "warning")
            self.game.logger.info(message)
    
    def get_player_clues(self, target_player_id: int) -> List[dict]:
        """Lấy tất cả clues về một player"""
        return [clue for clue in self.clues if clue.get("target_player") == target_player_id]
    
    def calculate_total_suspicion(self, player_id: int) -> float:
        """Tính tổng độ nghi ngờ từ alignment và clues"""
        player = None
        for p in self.game.players:
            if p.id == player_id:
                player = p
                break
        
        if not player:
            return 0.0
        
        # Độ nghi ngờ từ alignment
        base_suspicion = player.alignment.suspicion
        
        # Thêm điểm từ clues
        clues = self.get_player_clues(player_id)
        clue_bonus = sum(clue.get("credibility", 0) * 20 for clue in clues)
        
        total = base_suspicion + clue_bonus
        
        return min(100.0, total)  # Giới hạn 100%
    
    def combo_check(self, player, cards_used: List[str]):
        """Kiểm tra và áp dụng combo cards"""
        # Combo: Ám Sát + Hút Máu
        if "assassination" in cards_used and "blood_drain" in cards_used:
            player.alignment.sin += 2  # Penalty
            player.hp = min(player.hp + 15, player.max_hp)
            self.generate_clue(player)  # Force clue generation
            self.game.ui_bridge.show_notification(f"{player.name} used forbidden combo!", "error")
        
        # Combo: Rào Thánh + Lời Cầu
        elif "holy_barrier" in cards_used and "prayer" in cards_used:
            player.alignment.grace += 1
            self.update_npc_trust(player, 0.2)
            self.game.ui_bridge.show_notification(f"{player.name} gained NPC trust!", "success")
