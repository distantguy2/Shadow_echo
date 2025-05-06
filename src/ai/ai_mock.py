# src/ai/ai_mock.py

import random

class MockAI:
    """Giả lập AI để xử lý hành vi cơ bản trong chế độ offline hoặc testing."""

    def __init__(self, name="AI_NPC"):
        self.name = name
        self.hp = 100
        self.role = random.choice(["♕", "♛", "☢"])
        self.state = "idle"
        self.position = [random.randint(100, 500), random.randint(100, 500)]
        self.ready = False

    def decide_action(self, game_state):
        """Chọn hành động dựa trên trạng thái trò chơi."""
        if self.hp < 30:
            return "use ✚ --target=self"
        elif game_state["phase"] == "night":
            return "scan area"
        else:
            return random.choice(["move north", "move south", "wait", "build barricade"])

    def update(self, game_state):
        """Cập nhật hành động của AI."""
        action = self.decide_action(game_state)
        print(f"[{self.name}] performs action: {action}")
        return action
