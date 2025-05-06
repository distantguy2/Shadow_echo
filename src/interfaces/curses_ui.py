# src/interfaces/curses_ui.py

import curses
import time

class CursesUI:
    def __init__(self, game):
        self.game = game
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(True)
        self.height, self.width = self.screen.getmaxyx()

    def draw_text(self, y, x, text, attr=curses.A_NORMAL):
        if y < self.height and x < self.width:
            try:
                self.screen.addstr(y, x, text, attr)
            except curses.error:
                pass

    def draw_ui(self):
        self.screen.clear()

        # Draw Header
        self.draw_text(0, 2, "=== Shadow Echo (Terminal Mode) ===", curses.A_BOLD)

        # Draw Game Info
        self.draw_text(2, 2, f"Phase      : {self.game.phase.name}")
        self.draw_text(3, 2, f"Day        : {self.game.day_count}")
        self.draw_text(4, 2, f"Time Left  : {int(self.game.time_left)}s")

        # Draw Players
        self.draw_text(6, 2, "Players:")
        for i, player in enumerate(self.game.players):
            self.draw_text(7 + i, 4, f"{player.name} [{player.hp} HP] Role: {player.role.name}")

        # Draw Monsters
        offset = 8 + len(self.game.players)
        self.draw_text(offset, 2, "Monsters:")
        for i, monster in enumerate(self.game.monsters):
            self.draw_text(offset + 1 + i, 4, f"{monster.symbol} at {monster.position} ({monster.hp} HP)")

        # Draw Prompt
        self.draw_text(self.height - 2, 2, "Press Q to quit | Press SPACE to scan")

        self.screen.refresh()

    def handle_input(self):
        self.screen.timeout(100)
        key = self.screen.getch()

        if key == ord('q') or key == ord('Q'):
            self.game.game_running = False
        elif key == ord(' '):
            self.game.perform_action("scan")

    def update(self):
        self.handle_input()
        self.draw_ui()

    def cleanup(self):
        curses.nocbreak()
        self.screen.keypad(False)
        curses.echo()
        curses.endwin()
