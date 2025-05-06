# src/interfaces/pygame_ui.py

import pygame

class PygameUI:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 24)

    def draw(self, engine):
        self.screen.fill((20, 20, 20))

        # Hiển thị phase, thời gian còn lại và số ngày
        phase_text = self.font.render(f"Phase: {engine.phase_manager.current_phase.name}", True, (255, 255, 255))
        time_text = self.font.render(f"Time Left: {int(engine.phase_manager.time_left)}s", True, (255, 255, 255))
        day_text = self.font.render(f"Day: {engine.phase_manager.day_count}", True, (255, 255, 255))
        self.screen.blit(phase_text, (30, 30))
        self.screen.blit(day_text, (30, 70))
        self.screen.blit(time_text, (30, 110))

        # Hiển thị trạng thái người chơi
        y = 160
        for pid, player in engine.state.players.items():
            text = self.font.render(f"{pid}: HP={player.hp} | Pos={player.position}", True, (200, 200, 100))
            self.screen.blit(text, (30, y))
            y += 40

        # Hiển thị event gần nhất
        if engine.event_log:
            event_text = self.font.render(f"Event: {engine.event_log[-1]['description']}", True, (255, 100, 100))
            self.screen.blit(event_text, (30, y))
