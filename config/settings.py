# config/settings.py - IMPROVED VERSION

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Card database path
CARD_DB_PATH = "config/cards.json"

# Phase durations (in seconds) - IMPROVED TIMING
PREPARATION_TIME = 30      # 30 seconds to prepare
DAY_DURATION = 30         # 5 minutes (300 seconds)
NIGHT_DURATION = 30       # 2 minutes (120 seconds)
SKILL_CARD_SELECT_TIME = 30.0
MAX_DAYS = 10

# Game rules
MAX_PLAYERS_PER_LOBBY = 5
MIN_PLAYERS_TO_START = 3

# Role configuration
ROLE_TYPES = ["♕", "♛", "☢"]
ROLE_WEIGHTS = [0.3, 0.3, 0.4]  # Probability for Protector, Traitor, Chaos

# Monster spawn settings - BALANCED
MONSTER_SPAWN_CONFIG = {
    "base_per_player": 1,      # 1 monster per player as base
    "scaling_per_day": 0.5,    # Add 0.5 monsters per day
    "min_monsters": 3,         # Minimum monsters to spawn
    "max_monsters": 10,        # Maximum monsters to spawn
    "types": [
        {"symbol": "§", "hp": 50, "damage": 10, "speed": 1.0, "weight": 0.5},
        {"symbol": "¥", "hp": 80, "damage": 15, "speed": 0.8, "weight": 0.3}, 
        {"symbol": "※", "hp": 30, "damage": 20, "speed": 1.5, "weight": 0.2}
    ]
}

# Experience sharing
EXP_SHARE_RADIUS = 150     # Share EXP within 150 pixels
EXP_SHARE_RATE = 0.4       # Share 40% of EXP with nearby players

# Server config (fallback if env missing)
DEFAULT_HOST = "localhost"
DEFAULT_PORT = 8765

# Logging
LOG_FILE = "logs/game.log"
LOG_LEVEL = "INFO"
