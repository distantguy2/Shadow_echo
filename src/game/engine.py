# src/game/engine.py

from .state import GameState
from .phases import PhaseManager
from .events import EventGenerator, GameEvent
from ..systems.commands import CommandProcessor


class GameEngine:
    def __init__(self):
        self.state = GameState()
        self.phase_manager = PhaseManager()
        self.event_generator = EventGenerator(self.state)
        self.command_processor = CommandProcessor()
        self.event_log = []  # log sự kiện cho client

    def update(self, dt):
        self.phase_manager.update(dt)
        # Khi vừa đổi pha -> phát sinh sự kiện
        if self.phase_manager.just_switched_phase:
            new_event = self.event_generator.generate_event(self.state.phase.upper())
            if new_event:
                self.event_log.append(new_event.to_dict())
                # Nếu muốn áp dụng vào state tại đây thì xử lý ở đây

    def handle_command(self, player_id, command_str):
        player = self.state.players.get(player_id)
        if not player:
            return "❌ Player not found"
        return self.command_processor.process_command(player, command_str, self.state)

    def add_player(self, player_id, player_data):
        self.state.players[player_id] = player_data

    def get_state_dict(self):
        """Trả về game state để gửi tới client"""
        return {
            "phase": self.state.phase,
            "time_left": self.state.time_left,
            "players": {
                pid: {
                    "hp": p.hp,
                    "cards": p.cards,
                    "position": p.position
                } for pid, p in self.state.players.items()
            },
            "events": self.event_log[-5:]  # gửi tối đa 5 event gần nhất
        }
