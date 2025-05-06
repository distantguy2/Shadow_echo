# src/core/commands.py

import re
from typing import Dict, Optional
from .core.entities import Player
from .skills import SKILL_LIBRARY
from ..utils.logger import setup_logger

logger = setup_logger("Commands")

class CommandHandler:
    """Xử lý các lệnh trong game"""
    
    def __init__(self, game):
        self.game = game
        self.commands = {
            'use': self.use_card,
            'status': self.show_status,
            'scan': self.scan_area,
            'inventory': self.show_inventory,
            'help': self.show_help,
            'save': self.save_game,
            'load': self.load_game,
            'clues': self.show_clues,
            'accuse': self.accuse_player,
            'build': self.build_structure
        }
    
    def process_command(self, command_str: str) -> str:
        """Xử lý chuỗi lệnh"""
        if not command_str.strip():
            return "❌ Vui lòng nhập lệnh"
        
        parts = command_str.strip().split(' ', 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        handler = self.commands.get(cmd)
        if handler:
            return handler(args)
        else:
            return f"❌ Lệnh không hợp lệ: {cmd}. Gõ 'help' để xem danh sách lệnh."
    
    def use_card(self, args: str) -> str:
        """Sử dụng thẻ bài"""
        if not args:
            return "❌ Cú pháp: use <card_id>"
        
        player = self.game.players[self.game.current_player]
        card_id = args.split()[0]
        
        if card_id in player.cards:
            result = self.game.card_system.use_card(player, card_id, self.game.phase)
            if result.get("success"):
                # Generate clue if needed
                self.game.clue_generator.generate_card_usage_clue(player, card_id)
                return f"✅ {result['message']}"
            else:
                return f"❌ {result['message']}"
        else:
            return f"❌ Bạn không có thẻ '{card_id}'"
    
    def show_status(self, args: str) -> str:
        """Hiển thị trạng thái"""
        player = self.game.players[self.game.current_player]
        status = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{player.name}'s Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❤️ HP: {player.hp}/{player.max_hp}
⭐ Level: {player.level} (EXP: {player.exp}/{player.level * 100})
🎭 Role: {player.role.value} (True: {player.true_role.value})
📍 Position: {player.position}
😈 Sin: {player.alignment.sin} / ✨ Grace: {player.alignment.grace}
🔍 Suspicion: {player.alignment.suspicion:.1f}%

Cards:
"""
        for i, card_id in enumerate(player.cards):
            card_info = self.game.card_system.get_card_info(card_id)
            if card_info:
                status += f"  {i+1}. {card_info.symbol} {card_info.name}\n"
        
        status += "\nSkills:\n"
        for skill in player.skills:
            skill_data = SKILL_LIBRARY.get(skill.skill_id)
            if skill_data:
                status += f"  {skill_data.icon} {skill_data.name} (Lvl {skill.level})"
                if skill.cooldown > 0:
                    status += f" [Cooldown: {skill.cooldown:.1f}s]"
                status += "\n"
        
        status += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        return status
    
    def scan_area(self, args: str) -> str:
        """Quét khu vực"""
        player = self.game.players[self.game.current_player]
        scan_range = 150
        
        result = f"Scanning area... (range: {scan_range})\n\n"
        
        # Quét monsters
        monsters_found = []
        for i, monster in enumerate(self.game.monsters):
            dx = monster.position[0] - player.position[0]
            dy = monster.position[1] - player.position[1]
            distance = (dx**2 + dy**2)**0.5
            
            if distance <= scan_range:
                monsters_found.append(f"  🔴 Monster {monster.symbol} - HP: {monster.hp}/{monster.max_hp} - Distance: {distance:.1f}")
        
        # Quét NPCs
        npcs_found = []
        for npc in self.game.npcs:
            if npc["alive"]:
                dx = npc["position"][0] - player.position[0]
                dy = npc["position"][1] - player.position[1]
                distance = (dx**2 + dy**2)**0.5
                
                if distance <= scan_range:
                    npcs_found.append(f"  🟢 NPC {npc['name']} - HP: {npc['hp']}/{npc['max_hp']} - Distance: {distance:.1f}")
        
        # Quét clues about other players
        other_players = [p for p in self.game.players if p.id != player.id]
        player_clues = []
        for p in other_players:
            if p.clues:
                clue = p.clues[-1]  # Most recent clue
                player_clues.append(f"  💭 About {p.name}: '{clue['text']}' (Credibility: {clue['credibility']:.0%})")
        
        if monsters_found:
            result += f"Monsters ({len(monsters_found)}):\n" + "\n".join(monsters_found) + "\n\n"
        else:
            result += "No monsters in range\n\n"
            
        if npcs_found:
            result += f"NPCs ({len(npcs_found)}):\n" + "\n".join(npcs_found) + "\n\n"
        else:
            result += "No NPCs in range\n\n"
            
        if player_clues:
            result += "Clues about others:\n" + "\n".join(player_clues)
        else:
            result += "No clues found"
        
        return result
    
    def show_inventory(self, args: str) -> str:
        """Hiển thị túi đồ"""
        player = self.game.players[self.game.current_player]
        if not player.cards:
            return "📦 Inventory is empty"
        
        inventory = "📦 Card Inventory:\n\n"
        for i, card_id in enumerate(player.cards):
            card_info = self.game.card_system.get_card_info(card_id)
            if card_info:
                inventory += f"  {i+1}. {card_info.symbol} {card_info.name}\n"
                inventory += f"     Sin: {card_info.sin}, Grace: {card_info.grace}\n"
                inventory += f"     Day: {card_info.day_effect.get('description', 'None')}\n"
                inventory += f"     Night: {card_info.night_effect.get('description', 'None')}\n\n"
        
        return inventory
    
    def show_clues(self, args: str) -> str:
        """Hiển thị clues"""
        result = "📋 Investigation Clues:\n\n"
        
        for player in self.game.players:
            if player.clues:
                result += f"{player.name}:\n"
                for clue in player.clues[-3:]:  # Show last 3 clues
                    credibility_icon = "🟢" if clue.credibility > 0.7 else "🟡" if clue.credibility > 0.4 else "🔴"
                    result += f"  {credibility_icon} {clue.text} - {clue.source}\n"
                result += "\n"
        
        return result
    
    def accuse_player(self, args: str) -> str:
        """Buộc tội người chơi khác"""
        if not args:
            return "❌ Cú pháp: accuse <player_name> --reason=<reason>"
        
        parts = args.split("--reason=")
        if len(parts) != 2:
            return "❌ Phải có lý do: accuse <player_name> --reason=<reason>"
        
        target_name = parts[0].strip()
        reason = parts[1].strip()
        
        # Tìm player bị tố
        target_player = None
        for p in self.game.players:
            if p.name.lower() == target_name.lower():
                target_player = p
                break
        
        if not target_player:
            return f"❌ Không tìm thấy player: {target_name}"
        
        # Tính toán credibility của lời tố
        accuser = self.game.players[self.game.current_player]
        credibility = 0.5
        
        # Người tố có grace cao -> lời tố đáng tin hơn
        credibility += accuser.alignment.grace * 0.1
        
        # Người bị tố có sin cao -> lời tố đáng tin hơn
        credibility += target_player.alignment.sin * 0.15
        
        # Kiểm tra if có clues hỗ trợ
        if target_player.clues:
            credibility += len(target_player.clues) * 0.1
        
        credibility = min(1.0, credibility)
        
        # Thêm accusation vào game state
        accusation = {
            "accuser": accuser.name,
            "target": target_player.name,
            "reason": reason,
            "credibility": credibility,
            "timestamp": self.game.day_count
        }
        
        # Nếu credibility cao, ảnh hưởng đến NPC trust
        if credibility > 0.7:
            self.game.alignment_manager.update_npc_trust(target_player, -0.3)
            
        message = f"🗣️ {accuser.name} accuses {target_player.name} of {reason}"
        message += f"\nCredibility: {credibility:.0%}"
        
        return message
    
    def build_structure(self, args: str) -> str:
        """Xây dựng cấu trúc phòng thủ"""
        if not args:
            return "❌ Cú pháp: build <structure> --pos=<location>"
        
        if "--pos=" not in args:
            return "❌ Phải chỉ định vị trí: build <structure> --pos=<location>"
        
        parts = args.split("--pos=")
        structure = parts[0].strip()
        position = parts[1].strip()
        
        # Simple structure building (to be expanded)
        allowed_structures = ["barricade", "fence", "wall"]
        if structure not in allowed_structures:
            return f"❌ Cấu trúc không hợp lệ. Cho phép: {', '.join(allowed_structures)}"
        
        return f"🛠️ Built {structure} at {position}"
    
    def save_game(self, args: str) -> str:
        """Lưu game"""
        # TODO: Implement save system
        return "✅ Game saved successfully!"
    
    def load_game(self, args: str) -> str:
        """Tải game"""
        # TODO: Implement load system
        return "✅ Game loaded successfully!"
    
    def show_help(self, args: str) -> str:
        """Hiển thị hướng dẫn"""
        return """
📜 Available Commands:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎴 Card Management:
  use <card_id>   - Use a card (e.g., use axe)
  inventory       - Show your cards

🔍 Information:
  status          - Show character status
  scan            - Scan the area for entities
  clues           - Show investigation clues

🤝 Social:
  accuse <name> --reason=<reason>
                  - Accuse a player
  
🏗️ Building:
  build <structure> --pos=<location>
                  - Build defenses

💾 Game:
  save            - Save game
  load            - Load game
  help            - Show this help

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Use '1', '2', '3' keys to quickly use cards
"""
