# enemy.py
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Tuple
from database import Database
import random
import logging
import copy
from config import COMMON_DROP_CHANCE, RARE_DROP_CHANCE

@dataclass
class Enemy:
    """
    Represents an enemy character in the game.
    
    Attributes:
        name: Enemy name
        tier: Enemy tier level
        current_health: Current health points
        attack: Base attack value
        defense: Base defense value
        health: Maximum health points
        xp_value: Experience points granted when defeated
        min_copper: Minimum copper coins dropped
        max_copper: Maximum copper coins dropped
        common_drops: List of possible common item drops
        rare_drops: List of possible rare item drops
        is_player: Always False for enemies
    """
    name: str
    tier: int
    current_health: Optional[int] = None
    attack: int = 0
    defense: int = 0
    health: int = 0
    xp_value: int = 0
    min_copper: int = 0
    max_copper: int = 0
    common_drops: List[str] = field(default_factory=list)
    rare_drops: List[str] = field(default_factory=list)
    spawn_chance: float = 0.1
    is_player: bool = False

    def __post_init__(self):
        """Initialize enemy stats after creation."""
        try:
            self._load_stats()
            if self.current_health is None:
                self.current_health = self.health
                
        except Exception as e:
            logging.error(f"Error initializing enemy {self.name}: {str(e)}")
            raise

    def _load_stats(self) -> None:
        """
        Load enemy stats from the database.
        
        Raises:
            ValueError: If enemy data is invalid or missing
        """
        try:
            db = Database()
            enemy_data = db.get_enemy(self.name)
            if not enemy_data:
                raise ValueError(f"Invalid enemy: {self.name}")

            # Load base stats with validation
            self.attack = max(0, enemy_data.get('attack', 0))
            self.defense = max(0, enemy_data.get('defense', 0))
            self.health = max(1, enemy_data.get('health', 10))
            self.xp_value = max(1, enemy_data.get('xp_value', 1))
            self.min_copper = max(0, enemy_data.get('min_copper', 0))
            self.max_copper = max(self.min_copper, enemy_data.get('max_copper', 0))
            
            # Process drop lists with proper string handling
            self.common_drops = []
            if enemy_data.get('common_drops'):
                self.common_drops = [
                    drop.strip() 
                    for drop in enemy_data['common_drops'] 
                    if isinstance(drop, str) and drop.strip()
                ]
                
            self.rare_drops = []
            if enemy_data.get('rare_drops'):
                self.rare_drops = [
                    drop.strip() 
                    for drop in enemy_data['rare_drops'] 
                    if isinstance(drop, str) and drop.strip()
                ]
                
            self.spawn_chance = max(0.01, min(1.0, enemy_data.get('spawn_chance', 0.1)))

        except Exception as e:
            logging.error(f"Error loading stats for enemy {self.name}: {str(e)}")
            raise

    def take_damage(self, damage: int) -> bool:
        """
        Take damage and return whether still alive.
        
        Args:
            damage: Amount of damage to take
            
        Returns:
            bool: True if still alive, False if defeated
        """
        try:
            if damage < 0:
                raise ValueError("Damage amount cannot be negative")
                
            self.current_health = max(0, self.current_health - damage)
            logging.info(f"{self.name} took {damage} damage. Health: {self.current_health}/{self.health}")
            return self.current_health > 0
            
        except Exception as e:
            logging.error(f"Error processing damage for {self.name}: {str(e)}")
            return True  # Fail safe to prevent instant death from errors

    def is_defeated(self) -> bool:
        """
        Check if the enemy is defeated.
        
        Returns:
            bool: True if defeated (health <= 0), False otherwise
        """
        return self.current_health <= 0

    def get_drops(self) -> List[Tuple[str, Any]]:
        """
        Generate loot drops with improved variety and chances.
        
        Returns:
            List of tuples (drop_type, value) representing drops
        """
        drops = []
        try:
            db = Database()
            
            # Base money drops with bonus chance
            base_copper = random.randint(self.min_copper, self.max_copper)
            if random.random() < 0.2:  # 20% chance for bonus money
                bonus_multiplier = random.uniform(1.5, 3.0)
                base_copper = int(base_copper * bonus_multiplier)
            drops.append(('copper', base_copper))
            
            # Legendary drop chance (tier 6 items)
            if random.random() < 0.02:  # 2% chance
                legendary_items = db.get_all_items_by_tier(6)
                if not legendary_items.empty:
                    item = legendary_items.sample(n=1).iloc[0]
                    drops.append(('item', item['name']))
                    logging.info(f"Legendary item dropped: {item['name']}")

            # Rare drop chance
            if random.random() < RARE_DROP_CHANCE:  # Configuration value
                # Try rare drops first
                if self.rare_drops:
                    item_name = random.choice(self.rare_drops)
                    drops.append(('item', item_name))
                    logging.info(f"Rare item dropped: {item_name}")
                else:
                    # Fallback to tier+1 items
                    max_tier = min(self.tier + 1, 5)
                    rare_items = db.get_all_items_by_tier(max_tier)
                    if not rare_items.empty:
                        item = rare_items.sample(n=1).iloc[0]
                        drops.append(('item', item['name']))
                        logging.info(f"Rare item dropped: {item['name']}")

            # Common drops
            if random.random() < COMMON_DROP_CHANCE:  # Configuration value
                drop_pool = []
                
                # Add tier-appropriate items
                tier_items = db.get_all_items_by_tier(self.tier)
                if not tier_items.empty:
                    drop_pool.extend(tier_items['name'].tolist())
                
                # Add specific common drops
                drop_pool.extend(self.common_drops)
                
                if drop_pool:
                    item_name = random.choice(drop_pool)
                    drops.append(('item', item_name))
                    logging.info(f"Common item dropped: {item_name}")

            # Extra drops based on enemy tier
            extra_drop_chance = 0.1 * self.tier  # Higher tier = more chances
            while random.random() < extra_drop_chance and extra_drop_chance > 0:
                tier_items = db.get_all_items_by_tier(self.tier)
                if not tier_items.empty:
                    item = tier_items.sample(n=1).iloc[0]
                    drops.append(('item', item['name']))
                    logging.info(f"Extra item dropped: {item['name']}")
                extra_drop_chance -= 0.1

        except Exception as e:
            logging.error(f"Error generating drops for {self.name}: {str(e)}")
            # Return at least some copper if error occurs
            if not drops:
                drops.append(('copper', self.min_copper))
                
        return drops

    def calculate_total_attack(self) -> int:
        """
        Calculate total attack (for combat system compatibility).
        
        Returns:
            int: Total attack value
        """
        try:
            return max(0, self.attack)
        except Exception as e:
            logging.error(f"Error calculating attack for {self.name}: {str(e)}")
            return 0

    def calculate_total_defense(self) -> int:
        """
        Calculate total defense (for combat system compatibility).
        
        Returns:
            int: Total defense value
        """
        try:
            return max(0, self.defense)
        except Exception as e:
            logging.error(f"Error calculating defense for {self.name}: {str(e)}")
            return 0

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert enemy data to a dictionary for saving.
        
        Returns:
            Dict containing all enemy data
        """
        try:
            return {
                'name': self.name,
                'tier': self.tier,
                'current_health': self.current_health,
                'attack': self.attack,
                'defense': self.defense,
                'health': self.health,
                'xp_value': self.xp_value,
                'min_copper': self.min_copper,
                'max_copper': self.max_copper,
                'common_drops': self.common_drops.copy(),
                'rare_drops': self.rare_drops.copy(),
                'spawn_chance': self.spawn_chance
            }
        except Exception as e:
            logging.error(f"Error converting {self.name} to dict: {str(e)}")
            raise

    @staticmethod
    def get_random_enemy(tier: int) -> Optional['Enemy']:
        """
        Create a random enemy of the specified tier.
        
        Args:
            tier: The tier level for the enemy
            
        Returns:
            Enemy: A new random enemy of the specified tier
            
        Raises:
            ValueError: If no enemies are found for the specified tier
        """
        try:
            db = Database()
            tier_enemies = db.get_all_enemies_by_tier(tier)
            
            if tier_enemies.empty:
                raise ValueError(f"No enemies found for tier {tier}")
                
            # Weight probabilities based on spawn_chance
            total_chance = tier_enemies['spawn_chance'].sum()
            roll = random.random() * total_chance
            cumulative = 0
            
            for _, enemy in tier_enemies.iterrows():
                cumulative += enemy['spawn_chance']
                if roll <= cumulative:
                    return Enemy(
                        name=enemy['name'],
                        tier=enemy['tier']
                    )
            
            # Fallback to random selection if weighting fails
            enemy_data = tier_enemies.sample().iloc[0]
            return Enemy(
                name=enemy_data['name'],
                tier=enemy_data['tier']
            )
            
        except Exception as e:
            logging.error(f"Error creating random enemy for tier {tier}: {str(e)}")
            return None

    def heal(self, amount: int) -> int:
        """
        Heal the enemy (for compatibility with combat system).
        
        Args:
            amount: Amount of health to restore
            
        Returns:
            int: Actual amount healed
        """
        try:
            if amount < 0:
                raise ValueError("Heal amount cannot be negative")
                
            old_health = self.current_health
            self.current_health = min(self.health, self.current_health + amount)
            actual_heal = self.current_health - old_health
            
            logging.info(f"{self.name} healed for {actual_heal}. Health: {self.current_health}/{self.health}")
            return actual_heal
            
        except Exception as e:
            logging.error(f"Error healing {self.name}: {str(e)}")
            return 0