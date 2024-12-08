# config.py
import os
import logging
from datetime import datetime
from typing import Final, Dict

# Directory Configuration
BASE_DIR: Final = os.path.dirname(os.path.abspath(__file__))
DATA_DIR: Final = os.path.join(BASE_DIR, 'data')
SAVE_DIR: Final = os.path.join(BASE_DIR, 'saves')
LOG_DIR: Final = os.path.join(BASE_DIR, 'logs')

# Window Configuration
WINDOW_WIDTH: Final = 1000
WINDOW_HEIGHT: Final = 1000
WINDOW_TITLE: Final = "Dungeon RPG"

# Game Constants
VISIBLE_RANGE: Final = 4  # How far the player can see
CAMP_HEAL_RATE: Final = 5  # Health restored when camping
FLEE_BASE_CHANCE: Final = 0.3  # Base chance to successfully flee
CRITICAL_HIT_CHANCE: Final = 0.15  # Chance for critical hit
CRITICAL_HIT_MULTIPLIER: Final = 2.0  # Damage multiplier for critical hits
PLAYER_DAMAGE_BONUS: Final = 1.2  # 20% bonus damage for players
PLAYER_HIT_BONUS: Final = 2  # +2 to hit for players

# Enemy Configuration
ENEMY_SPAWN_CHANCE: Final = 0.4  # Chance for room to have enemies
COMMON_DROP_CHANCE: Final = 0.6  # Chance for common item drops
RARE_DROP_CHANCE: Final = 0.1  # Chance for rare item drops
LEGENDARY_DROP_CHANCE: Final = 0.02  # Chance for legendary item drops
BONUS_MONEY_CHANCE: Final = 0.2  # Chance for bonus money drops
BONUS_MONEY_MULTIPLIER: Final = (1.5, 3.0)  # Range for bonus money multiplier

# Merchant Configuration
MERCHANT_PRICE_VARIATION: Final = 0.2  # ±20% price variation
MERCHANT_SELL_PRICE_RATIO: Final = 0.5  # 50% of base price when selling to merchant
MERCHANT_RESTOCK_COUNTS: Final[Dict[str, int]] = {
    'weapon': 3,
    'armor': 3,
    'shield': 2,
    'consumable': 5,
    'tool': 3
}

# Dungeon Generation
MIN_DUNGEON_SIZE: Final = 5
MAX_DUNGEON_SIZE: Final = 15
TREASURE_ROOM_COUNT_MULTIPLIER: Final = 1  # Multiply by tier for treasure room count
REQUIRED_EXPLORATION_PERCENT: Final = 75  # Required exploration percentage
MIN_DISTANCE_TO_EXIT: Final = 5  # Minimum distance for exit room placement

# Combat Configuration
BASE_DEFENSE_VALUE: Final = 10  # Base defense class value
DEFENSE_DAMAGE_REDUCTION: Final = 2.0  # Divide defense by this for damage reduction
MIN_DAMAGE: Final = 1  # Minimum damage that can be dealt
FLEE_DIFFICULTY_CLASS: Final = 10  # Base difficulty for flee attempts
EXTRA_DROP_CHANCE_PER_TIER: Final = 0.1  # Additional drop chance per enemy tier

# Save/Load Configuration
SAVE_FILE_VERSION: Final = "1.0"
REQUIRED_SAVE_KEYS: Final = {
    'player': ['name', 'age', 'tier', 'xp', 'current_health', 'inventory',
               'equipped_weapon', 'equipped_armor', 'equipped_shield', 'money'],
    'dungeon': ['tier', 'size', 'player_pos', 'rooms']
}

# Initialize directories
try:
    for directory in [DATA_DIR, SAVE_DIR, LOG_DIR]:
        os.makedirs(directory, exist_ok=True)

    # Logging Configuration
    LOG_FILE = os.path.join(LOG_DIR, f'game_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Add console handler for critical errors
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.CRITICAL)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logging.getLogger().addHandler(console_handler)

    logging.info("Configuration initialized successfully")
    
except Exception as e:
    print(f"Critical error in configuration initialization: {str(e)}")
    raise