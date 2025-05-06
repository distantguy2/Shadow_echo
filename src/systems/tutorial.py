# src/systems/tutorial.py

class TutorialManager:
    def __init__(self, game):
        self.game = game
        self.current_step = 0
        self.tutorial_steps = [
            {"title": "Welcome", "text": "Use WASD to move around."},
            {"title": "Combat", "text": "Press SPACE to attack enemies."},
            {"title": "Cards", "text": "Type 'use ⎈' to activate a card."},
            {"title": "Objectives", "text": "Find out who the other real player is."},
            {"title": "Hints", "text": "Talk to NPCs and follow event clues."},
        ]

    def show_next(self):
        if self.current_step < len(self.tutorial_steps):
            step = self.tutorial_steps[self.current_step]
            self.game.show_notification(step["title"], step["text"])
            self.current_step += 1

    def restart(self):
        self.current_step = 0

    def is_completed(self):
        return self.current_step >= len(self.tutorial_steps)
