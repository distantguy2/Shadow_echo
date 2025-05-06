# Shadow Echo - PvPvE Survival Game

## 🌙 Game Overview
Shadow Echo is a hybrid ASCII/Pixel Art survival game where players must survive demon waves by day and discover hidden traitors by night.

## 🚀 Quick Start

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/shadow-echo.git
cd shadow-echo

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

## 🎮 Game Controls

### Day Phase (Pygame Window)
- WASD: Move character
- Mouse click: Attack monsters
- Tab: Open inventory

### Night Phase (Terminal Interface)
- Type commands and press Enter
- Available commands:
  - `build fence --pos=gate --material=wood`
  - `scan player2 --item=✚`
  - `use ⎈ --target=§`
  - `accuse player3 --reason=blood`
  - `end turn`

## 🃏 Game Mechanics

### Roles
- **♕ Protector**: Save NPCs, resurrect fallen allies
- **♛ Traitor**: Sabotage defenses, eliminate Protector
- **☢ Chaos**: Survive through randomness

### Cards System
- **Universal Cards**: AXE (⎈), MEDICINE (✚), MAP (🗺)
- **Role Cards**: Unlock special abilities when discovered

### Objective
- Survive 7 days and defeat the final boss
- Protect NPCs (if Protector) or eliminate targets (if Traitor)

## 🛠️ Development

### Project Structure
```
shadow_echo/
├── main.py          # Entry point
├── config/          # Game configuration
├── src/             # Source code
│   ├── game/        # Core game engine
│   ├── systems/     # Game mechanics
│   ├── ai/          # AI integration
│   └── interfaces/  # UI systems
├── assets/          # Art and sounds
└── tests/           # Unit tests
```

### Adding Content

1. **New Cards**: Add to `config/cards.json`
2. **New NPCs**: Modify `src/entities/npc.py`
3. **Custom Graphics**: Place in `assets/sprites/`

## 🔧 Configuration

### API Setup
Create `.env` file:
```
GROK_API_KEY=your_key_here
DEBUG_MODE=False
MAX_PLAYERS=5
```

## 🧪 Testing
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_roles.py
```

## 📦 Building
```bash
# Create executable
python build_scripts/build.py

# Create installer package
python build_scripts/package.py
```

## 🤝 Contributing
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License
MIT License - see `LICENSE` file

## 🙏 Credits
- Game Design: Your Name
- Art: Pixel Artists
- Music: Composers
- Special Thanks: Beta Testers