# src/core/entities/boss.py

from typing import List, Dict, Tuple, Optional

class Boss:
    def __init__(self, name: str, max_hp: int, phases: list[dict], position: tuple[float, float]):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.phases = phases
        self.position = position
        self.current_phase_index = 0
        self.active_skills = []
        self.is_boss = True  # Đánh dấu là boss
        self.alive = True
        self.symbol = "♟"  # Symbol mặc định cho boss

    def take_damage(self, amount: int):
        self.hp = max(self.hp - amount, 0)
        self.update_phase()
        if self.hp <= 0:
            self.alive = False

    def update_phase(self):
        for i, phase in enumerate(self.phases):
            if self.hp <= phase["hp_threshold"]:
                self.current_phase_index = i
                self.active_skills = phase["skills"]
                break

    def get_current_skills(self) -> list[str]:
        return self.active_skills

    def move_toward(self, target_position: tuple[float, float]):
        """Thêm method này để boss có thể di chuyển tương tự monster"""
        tx, ty = target_position
        x, y = self.position
        dx = tx - x
        dy = ty - y
        
        # Tốc độ di chuyển cho boss (thường chậm hơn)
        speed = 0.7
        
        # Di chuyển theo hướng của target
        dist = (dx**2 + dy**2)**0.5
        if dist > 0:
            x += (dx / dist) * speed
            y += (dy / dist) * speed
            
        self.position = (x, y)

    def is_dead(self) -> bool:
        return not self.alive

    def __repr__(self):
        return f"<Boss {self.name} HP: {self.hp}/{self.max_hp}, Phase: {self.current_phase_index}>"
