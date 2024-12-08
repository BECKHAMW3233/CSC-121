# character.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import logging
from database import Database
import copy

@dataclass
class Character:
    """
    Represents a character in the game.
    """
    name: str
    age: int
    tier: int = 1
    xp: int = 0
    current_health: Optional[int] = None
    inventory: List[Dict] = field(default_factory=list)
    equipped_weapon: Optional[Dict] = None
    equipped_armor: Optional[Dict] = None
    equipped_shield: Optional[Dict] = None
    money: int = 0
    is_player: bool = True
    
    def __post_init__(self):
        """
        Initialize character stats after creation.
        """
        try:
            self._load_stats()
            if self.current_health is None:
                self.current_health = self.max_health

            # Initialize starting inventory for new characters
            if not self.inventory and not self.equipped_weapon:
                self._initialize_starting_equipment()
        except Exception as e:
            logging.error(f"Error initializing character {self.name}: {str(e)}")
            raise

    def _initialize_starting_equipment(self) -> None:
        """
        Give starting equipment to new characters.
        """
        try:
            db = Database()
            
            # Add 5 health potions
            health_potion = db.get_item("Lesser Health Potion")
            if health_potion:
                for _ in range(5):
                    self.inventory.append(copy.deepcopy(health_potion))
                    
            # Add starting money
            self.money = 100

            # Get and equip initial gear from tier data
            tier_data = db.get_tier_data(self.tier)
            if not tier_data:
                logging.error(f"Failed to load tier {self.tier} data for character {self.name}")
                return

            # Equip starting weapon
            if tier_data.get('weapon'):
                weapon = db.get_item(tier_data['weapon'])
                if weapon:
                    self.equipped_weapon = copy.deepcopy(weapon)
                    logging.info(f"Equipped starting weapon: {weapon['name']}")

            # Equip starting armor
            if tier_data.get('armor'):
                armor = db.get_item(tier_data['armor'])
                if armor:
                    self.equipped_armor = copy.deepcopy(armor)
                    logging.info(f"Equipped starting armor: {armor['name']}")

        except Exception as e:
            logging.error(f"Error initializing equipment for {self.name}: {str(e)}")
            raise

    def _load_stats(self) -> None:
        """
        Load base stats and initial equipment for the character tier.
        """
        try:
            db = Database()
            tier_data = db.get_tier_data(self.tier)
            if not tier_data:
                raise ValueError(f"Invalid tier: {self.tier}")

            # Load base stats with defaults
            self.title = tier_data['title']
            self.base_attack = tier_data.get('attack', 1)
            self.base_defense = tier_data.get('defense', 1)
            self.max_health = tier_data.get('health', 20)
            self.special_ability = tier_data.get('special_ability', 'none')

        except Exception as e:
            logging.error(f"Error loading stats for {self.name}: {str(e)}")
            raise

    def add_xp(self, xp_amount: int) -> None:
        """
        Add experience points and check for level up.
        """
        try:
            if xp_amount < 0:
                raise ValueError("XP amount cannot be negative")
                
            self.xp += xp_amount
            logging.info(f"{self.name} gained {xp_amount} XP. Total: {self.xp}")
            self._check_level_up()
            
        except Exception as e:
            logging.error(f"Error adding XP to {self.name}: {str(e)}")

    def _check_level_up(self) -> None:
        """
        Check and process level up if applicable.
        """
        try:
            db = Database()
            next_tier = self.tier + 1
            next_tier_data = db.get_tier_data(next_tier)
            
            if next_tier_data and self.xp >= next_tier_data['min_xp']:
                self._level_up()
                
        except Exception as e:
            logging.error(f"Error checking level up for {self.name}: {str(e)}")

    def _level_up(self) -> None:
        """
        Process level up and adjust stats.
        """
        try:
            old_health = self.max_health
            old_tier = self.tier
            
            self.tier += 1
            self._load_stats()
            
            # Heal proportionally when leveling up
            health_percent = self.current_health / old_health
            self.current_health = int(self.max_health * health_percent)
            
            logging.info(f"{self.name} leveled up from tier {old_tier} to {self.tier} ({self.title})")
            
        except Exception as e:
            logging.error(f"Error processing level up for {self.name}: {str(e)}")
            raise

    def take_damage(self, damage: int) -> bool:
        """
        Take damage and return whether still alive.
        """
        try:
            if damage < 0:
                raise ValueError("Damage amount cannot be negative")
                
            self.current_health = max(0, self.current_health - damage)
            logging.info(f"{self.name} took {damage} damage. Health: {self.current_health}/{self.max_health}")
            return self.current_health > 0
            
        except Exception as e:
            logging.error(f"Error processing damage for {self.name}: {str(e)}")
            return True  # Fail safe to prevent instant death from errors

    def heal(self, amount: int) -> int:
        """
        Heal the character.
        """
        try:
            if amount < 0:
                raise ValueError("Heal amount cannot be negative")
                
            old_health = self.current_health
            self.current_health = min(self.max_health, self.current_health + amount)
            actual_heal = self.current_health - old_health
            
            logging.info(f"{self.name} healed for {actual_heal}. Health: {self.current_health}/{self.max_health}")
            return actual_heal
            
        except Exception as e:
            logging.error(f"Error healing {self.name}: {str(e)}")
            return 0

    def use_healing_potion(self, potion: Dict) -> bool:
        """
        Use a healing potion from inventory.
        """
        try:
            if potion['type'] != 'consumable':
                logging.warning(f"Attempted to use non-consumable item as potion: {potion['name']}")
                return False
                
            if 'effect' not in potion or not potion['effect'].startswith('heal_'):
                logging.warning(f"Invalid potion effect: {potion.get('effect')}")
                return False
                
            heal_amount = int(potion['effect'].split('_')[1])
            self.heal(heal_amount)
            self.remove_item(potion)
            
            logging.info(f"{self.name} used {potion['name']} and healed for {heal_amount}")
            return True
            
        except (IndexError, ValueError) as e:
            logging.error(f"Error using potion: {str(e)}")
            return False

    def add_item(self, item: Dict) -> None:
        """
        Add an item to inventory with proper data loading.
        """
        try:
            if isinstance(item, str):
                db = Database()
                item_data = db.get_item(item)
                if not item_data:
                    raise ValueError(f"Invalid item: {item}")
                self.inventory.append(copy.deepcopy(item_data))
                logging.info(f"{self.name} acquired {item_data['name']}")
            else:
                self.inventory.append(copy.deepcopy(item))
                logging.info(f"{self.name} acquired {item['name']}")
                
        except Exception as e:
            logging.error(f"Error adding item to {self.name}'s inventory: {str(e)}")

    def remove_item(self, item: Dict) -> bool:
        """
        Remove an item from inventory.
        """
        try:
            item_name = item['name']
            for i, inv_item in enumerate(self.inventory):
                if inv_item['name'] == item_name:
                    del self.inventory[i]
                    logging.info(f"{self.name} removed {item_name} from inventory")
                    return True
            logging.warning(f"Failed to remove {item_name} from {self.name}'s inventory - item not found")
            return False
            
        except Exception as e:
            logging.error(f"Error removing item from {self.name}'s inventory: {str(e)}")
            return False

    def equip_item(self, item: Dict) -> bool:
        """
        Equip an item.
        """
        try:
            if item['type'] not in ['weapon', 'armor', 'shield']:
                logging.warning(f"Attempted to equip invalid item type: {item['type']}")
                return False

            # Create deep copies of items
            item_copy = copy.deepcopy(item)
            
            if item['type'] == 'weapon':
                if self.equipped_weapon:
                    self.inventory.append(copy.deepcopy(self.equipped_weapon))
                self.equipped_weapon = item_copy
            elif item['type'] == 'armor':
                if self.equipped_armor:
                    self.inventory.append(copy.deepcopy(self.equipped_armor))
                self.equipped_armor = item_copy
            elif item['type'] == 'shield':
                if self.equipped_shield:
                    self.inventory.append(copy.deepcopy(self.equipped_shield))
                self.equipped_shield = item_copy

            self.remove_item(item)
            logging.info(f"{self.name} equipped {item['name']}")
            return True
            
        except Exception as e:
            logging.error(f"Error equipping item for {self.name}: {str(e)}")
            return False

    def calculate_total_attack(self) -> int:
        """
        Calculate total attack including equipment bonuses.
        """
        try:
            total = self.base_attack
            if self.equipped_weapon:
                min_dmg = float(self.equipped_weapon.get('base_damage_min', 0))
                max_dmg = float(self.equipped_weapon.get('base_damage_max', 0))
                total += (min_dmg + max_dmg) / 2
            return max(0, int(total))
            
        except Exception as e:
            logging.error(f"Error calculating attack for {self.name}: {str(e)}")
            return self.base_attack

    def calculate_total_defense(self) -> int:
        """
        Calculate total defense including equipment bonuses.
        """
        try:
            total = self.base_defense
            if self.equipped_armor:
                total += float(self.equipped_armor.get('base_defense', 0))
            if self.equipped_shield:
                total += float(self.equipped_shield.get('base_defense', 0))
            return max(0, int(total))
            
        except Exception as e:
            logging.error(f"Error calculating defense for {self.name}: {str(e)}")
            return self.base_defense

    def get_equipment_display(self) -> Dict[str, str]:
        """
        Get formatted equipment information for display.
        """
        try:
            weapon = "None"
            armor = "None"
            shield = "None"
            
            if self.equipped_weapon:
                weapon = f"{self.equipped_weapon['name']} (DMG: {self.equipped_weapon['base_damage_min']}-{self.equipped_weapon['base_damage_max']})"
            if self.equipped_armor:
                armor = f"{self.equipped_armor['name']} (DEF: {self.equipped_armor['base_defense']})"
            if self.equipped_shield:
                shield = f"{self.equipped_shield['name']} (DEF: {self.equipped_shield['base_defense']})"
                
            return {
                'weapon': weapon,
                'armor': armor,
                'shield': shield
            }
            
        except Exception as e:
            logging.error(f"Error getting equipment display for {self.name}: {str(e)}")
            return {'weapon': 'Error', 'armor': 'Error', 'shield': 'Error'}

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert character data to a dictionary for saving.
        """
        try:
            return {
                'name': self.name,
                'age': self.age,
                'tier': self.tier,
                'xp': self.xp,
                'current_health': self.current_health,
                'inventory': [item.copy() for item in self.inventory],
                'equipped_weapon': self.equipped_weapon.copy() if self.equipped_weapon else None,
                'equipped_armor': self.equipped_armor.copy() if self.equipped_armor else None,
                'equipped_shield': self.equipped_shield.copy() if self.equipped_shield else None,
                'money': self.money
            }
        except Exception as e:
            logging.error(f"Error converting character {self.name} to dict: {str(e)}")
            raise

    def get_status_effects(self) -> List[str]:
        """
        Get a list of active status effects on the character.
        """
        try:
            effects = []
            if hasattr(self, 'special_ability') and self.special_ability != 'none':
                effects.append(self.special_ability)
            return effects
        except Exception as e:
            logging.error(f"Error getting status effects for {self.name}: {str(e)}")
            return []

    def can_afford(self, price: int) -> bool:
        """
        Check if the character can afford an item.
        """
        try:
            if price < 0:
                raise ValueError("Price cannot be negative")
            return self.money >= price
        except Exception as e:
            logging.error(f"Error checking affordability for {self.name}: {str(e)}")
            return False