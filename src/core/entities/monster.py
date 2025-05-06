# src/core/entities/monster.py

class Monster:
    def __init__(self, symbol: str, hp: int, damage: int, position: tuple[float, float], speed: float = 1.0):
        self.symbol = symbol
        self.hp = hp
        self.max_hp = hp  # Thêm max_hp để phù hợp với các hệ thống khác
        self.damage = damage
        self.position = position
        self.speed = speed
        self.alive = True
        self.is_boss = False  # Thêm thuộc tính để phân biệt với boss

    def move_toward(self, target_position: tuple[float, float]):
        # Simple linear movement logic
        tx, ty = target_position
        x, y = self.position
        dx = tx - x
        dy = ty - y
        if abs(dx) > abs(dy):
            x += self.speed if dx > 0 else -self.speed
        else:
            y += self.speed if dy > 0 else -self.speed
        self.position = (x, y)  # Giữ nguyên float để di chuyển mềm mại hơn

    def take_damage(self, amount: int):
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.alive = False

    def is_dead(self) -> bool:
        return not self.alive

    def __repr__(self):
        return f"<Monster {self.symbol} HP: {self.hp}/{self.max_hp} Pos: {self.position}>"
