# src/systems/npcs.py - NPC SYSTEM
import pygame  # Thêm import pygame nếu chưa có

class NPCSystem:
    """Manages all NPCs"""
    
    def __init__(self, game):
        self.game = game
        self.npcs = []
    
    def initialize_npcs(self):
        """Create initial NPCs"""
        npc_names = ["Sister Maria", "Brother John", "Father Thomas", "Mother Catherine"]
        
        for i, name in enumerate(npc_names):
            npc = {
                "id": i + 100,
                "name": name,
                "position": [200 + i * 150, 300],
                "alive": True,
                "hp": 50,
                "max_hp": 50
            }
            self.npcs.append(npc)
    
    def update(self, dt):
        """Update NPCs logic - phương thức mới thêm vào"""
        # Có thể thêm logic di chuyển NPC ở đây
        pass
    
    def draw(self, screen):
        """Draw all NPCs"""
        for npc in self.npcs:
            if npc["alive"]:
                # Draw NPC
                color = (100, 200, 100)
                pygame.draw.rect(screen, color, 
                               (int(npc["position"][0])-10, int(npc["position"][1])-10, 20, 20))
                
                # Draw health bar
                bar_width = 40
                bar_height = 6
                x = int(npc["position"][0]) - bar_width // 2
                y = int(npc["position"][1]) - 25
                health_ratio = npc["hp"] / npc["max_hp"]
                
                pygame.draw.rect(screen, (100, 0, 0), (x, y, bar_width, bar_height))
                pygame.draw.rect(screen, (0, 255, 0), (x, y, int(bar_width * health_ratio), bar_height))
                pygame.draw.rect(screen, (255, 255, 255), (x, y, bar_width, bar_height), 1)
                
                # Draw name
                name_text = self.game.small_font.render(npc["name"], True, (255, 255, 255))
                screen.blit(name_text, (x - 10, y + 15))
