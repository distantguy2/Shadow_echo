# src/interfaces/ui_bridge.py

class UIBridge:
    def __init__(self, game, mode="pygame"):
        self.game = game
        self.mode = mode.lower()

        if self.mode == "pygame":
            from src.interfaces.pygame_ui import PygameUI
            self.ui = PygameUI(game)
        elif self.mode == "curses":
            from src.interfaces.curses_ui import CursesUI
            self.ui = CursesUI(game)
        else:
            raise ValueError(f"Unknown UI mode: {mode}")

    def update(self, dt):
        """Cập nhật UI theo thời gian delta"""
        if hasattr(self.ui, "update"):
            self.ui.update(dt)
        else:
            self.ui.draw_ui()

    def draw(self):
        """Vẽ lại UI nếu dùng Pygame"""
        if hasattr(self.ui, "draw_ui"):
            self.ui.draw_ui()

    def cleanup(self):
        """Dọn dẹp nếu dùng Curses"""
        if hasattr(self.ui, "cleanup"):
            self.ui.cleanup()
