# src/systems/clue_generator.py

import random
import time
from typing import List, Dict, Optional
from src.core.entities import Player, Clue, PlayerRole

class ClueGenerator:
    """Hệ thống tạo clue về người chơi"""
    
    def __init__(self, game):
        self.game = game
        self.clue_templates = {
            "blood": [
                "Thấy vết máu sau nhà kho",
                "Nghe tiếng khóc NPC ban đêm",
                "Tìm thấy dao đầy máu bí ẩn",
                "NPC {npc_name} nói đã bị thương"
            ],
            "holy": [
                "Thấy ánh sáng kỳ lạ ban đêm",
                "NPC {npc_name} được chữa lành đầy màu nhiệm",
                "Phát hiện biểu tượng thánh ẩn",
                "Nghe tiếng cầu nguyện trong đêm"
            ],
            "suspicious": [
                "Người này hành xử đáng ngờ",
                "Thấy họ lẻn lút trong bóng tối",
                "NPC {npc_name} nghi ngờ về họ",
                "Phát hiện yếu tố bất thường"
            ],
            "good_deed": [
                "Giúp NPC trong gian khổ",
                "Chia sẻ tài nguyên với người khác",
                "Bảo vệ người yếu đuối",
                "Thể hiện lòng nhân từ"
            ]
        }
        
        self.npc_names = [
            "Sister Maria", "Brother John", "Father Thomas", 
            "Mother Catherine", "Papa Francisco", "Elder Liu",
            "Nurse Emily", "Baker Hans", "Guard Marcus"
        ]
    
    def generate_clue(self, player: Player, clue_type: str) -> Clue:
        """Tạo clue về player"""
        templates = self.clue_templates.get(clue_type, self.clue_templates["suspicious"])
        template = random.choice(templates)
        
        # Format template with NPC name if needed
        npc_name = random.choice(self.npc_names)
        text = template.format(npc_name=npc_name) if "{npc_name}" in template else template
        
        # Calculate credibility based on player's alignment
        base_credibility = 0.5
        
        # High sin = more credible bad clues
        if clue_type == "blood" and player.alignment.sin > 3:
            base_credibility += (player.alignment.sin - 3) * 0.1
        
        # High grace = more credible good clues
        if clue_type == "good_deed" and player.alignment.grace > 3:
            base_credibility += (player.alignment.grace - 3) * 0.1
        
        # Add randomness
        credibility = min(1.0, max(0.1, base_credibility + random.uniform(-0.2, 0.2)))
        
        clue = Clue(
            text=text,
            credibility=credibility,
            source=npc_name,
            target_player=str(player.id)
        )
        
        return clue
    
    def check_and_generate_clues(self, player: Player):
        """Kiểm tra và tạo clue nếu thỏa điều kiện"""
        # Generate by sin level
        if player.alignment.sin >= 3 and random.random() < 0.2:
            clue = self.generate_clue(player, "blood")
            self.add_clue_to_game(clue)
        
        # Generate by grace level
        if player.alignment.grace >= 3 and random.random() < 0.15:
            clue = self.generate_clue(player, "good_deed")
            self.add_clue_to_game(clue)
        
        # Suspicion-based clues
        if player.alignment.is_suspected() and random.random() < 0.3:
            clue = self.generate_clue(player, "suspicious")
            self.add_clue_to_game(clue)
    
    def add_clue_to_game(self, clue: Clue):
        """Thêm clue vào game state"""
        player = self.get_player_by_id(clue.target_player)
        if player:
            player.add_clue(clue)
            
            # Notify all players
            message = f"Clue found: {clue.text} (Source: {clue.source})"
            self.game.ui_bridge.show_notification(message, "info")
            
            self.game.logger.info(f"Generated clue: {clue.text} about player {player.name}")
    
    def get_player_by_id(self, player_id: str) -> Optional[Player]:
        """Tìm player theo ID"""
        try:
            pid = int(player_id)
            for player in self.game.players:
                if player.id == pid:
                    return player
        except ValueError:
            pass
        return None
    
    def generate_card_usage_clue(self, player: Player, card_id: str):
        """Tạo clue khi sử dụng thẻ bài nguy hiểm"""
        card_info = self.game.card_system.get_card_info(card_id)
        if not card_info:
            return
        
        # Blood cards có chance tạo clue
        if card_info.type.value == "♥" and random.random() < 0.2:
            clue = self.generate_clue(player, "blood")
            self.add_clue_to_game(clue)
        
        # Assassination có thể tạo clue khẩn cấp
        if card_id == "assassination" and random.random() < 0.7:
            clue = Clue(
                text="Nghe tiếng la hét trong đêm!",
                credibility=0.9,
                source="Emergency Witness",
                target_player=str(player.id)
            )
            self.add_clue_to_game(clue)
    
    def get_all_clues_html(self) -> str:
        """Trả về tất cả clues dạng HTML để hiển thị"""
        clues_by_player = {}
        
        for player in self.game.players:
            if player.clues:
                clues_by_player[player.name] = player.clues
        
        html = "<div class='clues-panel'>"
        html += "<h3>Investigation Clues</h3>"
        
        for player_name, clues in clues_by_player.items():
            html += f"<div class='player-clues'>"
            html += f"<h4>{player_name}</h4>"
            for clue in clues[-3:]:  # Show last 3 clues
                credibility_color = "green" if clue.credibility > 0.7 else "orange" if clue.credibility > 0.4 else "red"
                html += f"<p style='color: {credibility_color}'>"
                html += f"📋 {clue.text} - {clue.source} (Credibility: {clue.credibility:.0%})"
                html += f"</p>"
            html += "</div>"
        
        html += "</div>"
        return html
    
    def get_player_suspicion_summary(self, player: Player) -> dict:
        """Lấy tóm tắt độ nghi ngờ của player"""
        return {
            "name": player.name,
            "sin": player.alignment.sin,
            "grace": player.alignment.grace,
            "suspicion": player.alignment.suspicion,
            "clue_count": len(player.clues),
            "trusted": self.game.alignment_manager.npc_trust.get(str(player.id), 1.0)
        }
