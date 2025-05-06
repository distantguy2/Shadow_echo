from enum import Enum, auto

class GamePhase(Enum):
    PREPARATION = auto()
    DAY = auto()
    NIGHT = auto()
    END = auto()

class PhaseManager:
    def __init__(self):
        self.current_phase = GamePhase.PREPARATION
        self.day_count = 0
        self.time_left = 60  # seconds
        self.just_switched_phase = False  # ✅ thêm dòng này

    def update(self, dt):
        self.just_switched_phase = False  # reset mỗi lần update
        self.time_left -= dt
        if self.time_left <= 0:
            self.advance_phase()
            self.time_left = 60
            self.just_switched_phase = True  # ✅ đánh dấu đã chuyển pha

    def advance_phase(self):
        if self.current_phase == GamePhase.PREPARATION:
            self.current_phase = GamePhase.DAY
            self.day_count = 1
        elif self.current_phase == GamePhase.DAY:
            self.current_phase = GamePhase.NIGHT
        elif self.current_phase == GamePhase.NIGHT:
            self.day_count += 1
            self.current_phase = GamePhase.DAY
        elif self.current_phase == GamePhase.END:
            self.reset()

    def is_day(self):
        return self.current_phase == GamePhase.DAY

    def is_night(self):
        return self.current_phase == GamePhase.NIGHT

    def is_game_over(self):
        return self.current_phase == GamePhase.END

    def reset(self):
        self.current_phase = GamePhase.PREPARATION
        self.day_count = 0
        self.time_left = 60
        self.just_switched_phase = False
