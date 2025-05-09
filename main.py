# main.py
import os
import sys
import pygame
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from src.core.game import Game
from src.utils.logger import setup_logger

if __name__ == "__main__":
    # Initialize logger
    logger = setup_logger("Main")
    logger.info("Starting Shadow Echo RPG...")

    # Set SDL environment variable to prefer Vietnamese-compatible font rendering
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    # Validate font paths
    project_root = Path(__file__).resolve().parent
    font_dir = project_root / "assets" / "sounds" / "fonts"
    noto_font = font_dir / "NotoSans-Regular.ttf"

    if noto_font.exists():
        logger.info(f"Found Vietnamese font: {noto_font}")
    else:
        logger.warning(f"Vietnamese font not found at: {noto_font} - will fall back to system fonts")

    try:
        # Initialize game with specified mode if provided
        game_mode = "standard"  # default
        if len(sys.argv) > 1 and sys.argv[1] in ["standard", "swarm"]:
            game_mode = sys.argv[1]

        game = Game(game_mode=game_mode)
        logger.info(f"Running game in {game_mode} mode...")
        game.run()
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
