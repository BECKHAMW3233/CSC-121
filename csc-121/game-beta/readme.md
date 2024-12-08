# Dungeon RPG

A turn-based dungeon crawler RPG featuring procedurally generated dungeons, character progression, and a D20-based combat system.

## Project Information

**Author:** William Beckham  
**Course:** CSC-121  
**Semester:** Fall 2024  
**Institution:** Fayetteville Technical Community College  
**Contact:** BECKHAMW3233@STUDENT.FAYTECHCC.EDU

## Features

- **Character Progression**: Start as a Farmer and progress through 6 unique tiers
- **Dynamic Combat**: D20-based combat system with critical hits and special abilities
- **Procedural Dungeons**: Randomly generated dungeons with increasing difficulty
- **Equipment System**: Various weapons, armor, and items to collect and equip
- **Merchant Trading**: Buy and sell items with dynamic pricing
- **Save System**: Save and load game progress

## Requirements

- Python 3.8 or higher
- tkinter (usually included with Python)
- pandas

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/dungeon-rpg.git
cd dungeon-rpg
```

2. Install dependencies:
```bash
pip install pandas
```

3. Run the game:
```bash
python game_app.py
```

## How to Play

### Controls
- **W/A/S/D**: Move character (North/West/South/East)
- **I**: Open inventory
- **ESC**: Open pause menu/Game menu
- **Ctrl+S**: Quick save
- **Space**: Attack (in combat)

### Game Elements
- 🟢 Green Circle: Player
- 🔴 Red 'E': Enemy
- 💛 Yellow 'T': Treasure
- 💚 Green 'M': Merchant
- ✓ Green Check: Cleared Room
- 🟣 Purple 'N': Exit Room

### Gameplay Loop
1. Explore dungeons room by room
2. Combat enemies for experience and loot
3. Find treasure and trade with merchants
4. Level up through tiers by gaining experience
5. Complete dungeons to progress to higher tiers

### Dungeon Completion
To complete a dungeon:
1. Find the exit room (marked with 'N')
2. Clear at least 75% of the dungeon
3. Defeat enemies in the exit room
4. Enter the cleared exit room

### Character Progression
- **Tier 1**: Farmer (Starting tier)
- **Tier 2**: Scout (Improved defense)
- **Tier 3**: Warrior (Balanced stats)
- **Tier 4**: Captain (High defense)
- **Tier 5**: Champion (High attack)
- **Tier 6**: King (Highest overall stats)

## Game Systems

### Combat System
- D20 roll system for attack resolution
- Critical hits on natural 20
- Automatic miss on natural 1
- Defense reduces incoming damage
- Flee option available

### Item System
- **Weapons**: Determine attack damage
- **Armor**: Provides defense
- **Consumables**: Healing and status effects
- **Tools**: Utility items

### Merchant System
- Dynamic pricing with ±20% variation
- Sell items for 50% base value
- Tier-appropriate inventory
- Regular stock refreshes

## Development

### Project Structure
```
dungeon-rpg/
├── data/
│   ├── items.csv
│   ├── enemies.csv
│   └── player_tiers.csv
├── models/
│   ├── character.py
│   ├── combat.py
│   ├── dungeon.py
│   ├── enemy.py
│   └── merchant.py
├── gui/
│   ├── main_window.py
│   └── combat_window.py
├── game_app.py
├── database.py
└── config.py
```

### Save Files
Save files are stored in the `saves/` directory as JSON files containing:
- Character data
- Current dungeon state
- Inventory and equipment

### Logging
Game logs are stored in the `logs/` directory with timestamps for debugging.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your branch
5. Submit a pull request

## Credits

Created by William Beckham  
CSC-121 Fall 2024  
Fayetteville Technical Community College

## Support

For support or questions about this project, please contact:
- Email: BECKHAMW3233@STUDENT.FAYTECHCC.EDU
- Course: CSC-121
- Institution: Fayetteville Technical Community College