# merchant.py
from typing import List, Dict, Any, Optional
from database import Database
import random
import logging
import copy
import math

class Merchant:
    """
    Represents a merchant in the game.
    """
    def __init__(self):
        """Initialize the merchant with inventory and settings."""
        self._db = Database()
        self._inventory: List[Dict] = []
        self._refresh_timer = 0
        self._price_variation = 0.2  # ±20% price variation
        self._sell_price_ratio = 0.5  # 50% of base price for selling
        self._restock_counts = {
            'weapon': 3,
            'armor': 3,
            'shield': 2,
            'consumable': 5,
            'tool': 3
        }
        self._initialize_inventory()

    def _initialize_inventory(self) -> None:
        """
        Generate the merchant's initial inventory.
        """
        try:
            self._inventory = self._generate_inventory()
            logging.info(f"Merchant initialized with {len(self._inventory)} items")
        except Exception as e:
            logging.error(f"Error initializing merchant inventory: {str(e)}")
            self._inventory = []

    def _generate_inventory(self) -> List[Dict]:
        """
        Generate a varied inventory with balanced item selection.
        
        Returns:
            List of items for the merchant's inventory
        """
        inventory = []
        try:
            # Get all possible items
            all_items = self._db.get_all_items_by_tier(6)
            if all_items.empty:
                raise ValueError("No items found in database")

            # Select items by type with specified counts
            for item_type, count in self._restock_counts.items():
                type_items = all_items[all_items['type'] == item_type]
                if not type_items.empty:
                    # Ensure we don't try to select more items than available
                    count = min(count, len(type_items))
                    selected = type_items.sample(n=count)
                    items = selected.to_dict('records')
                    
                    # Apply price variations
                    for item in items:
                        self._apply_price_variation(item)
                    
                    inventory.extend(items)

            # Add some random additional items (20% chance per tier)
            for tier in range(1, 7):
                if random.random() < 0.2:
                    tier_items = all_items[all_items['tier'] == tier]
                    if not tier_items.empty:
                        item = tier_items.sample(n=1).iloc[0].to_dict()
                        self._apply_price_variation(item)
                        inventory.append(item)

            logging.info(f"Generated merchant inventory with {len(inventory)} items")
            return inventory

        except Exception as e:
            logging.error(f"Error generating merchant inventory: {str(e)}")
            return []

    def _apply_price_variation(self, item: Dict) -> None:
        """
        Apply random price variation to an item.
        
        Args:
            item: The item to modify
        """
        try:
            base_price = item.get('price_copper', 0)
            variation = random.uniform(1 - self._price_variation, 1 + self._price_variation)
            item['price_copper'] = max(1, int(base_price * variation))
        except Exception as e:
            logging.error(f"Error applying price variation: {str(e)}")

    def refresh_inventory(self) -> None:
        """Refresh the merchant's inventory."""
        try:
            self._inventory = self._generate_inventory()
            self._refresh_timer = 0
            logging.info("Merchant inventory refreshed")
        except Exception as e:
            logging.error(f"Error refreshing merchant inventory: {str(e)}")

    def buy_item(self, player: Any, item_name: str) -> bool:
        """
        Handle the player buying an item from the merchant.
        
        Args:
            player: The player character
            item_name: Name of the item to buy
            
        Returns:
            bool: Whether the purchase was successful
        """
        try:
            # Find item in merchant inventory
            item = next((i for i in self._inventory if i['name'] == item_name), None)
            if not item:
                logging.warning(f"Item not found in merchant inventory: {item_name}")
                return False

            # Verify player can afford item
            if not player.can_afford(item['price_copper']):
                logging.info(f"Player cannot afford {item_name}")
                return False

            # Process transaction
            player.money -= item['price_copper']
            player.add_item(copy.deepcopy(item))
            self._inventory.remove(item)

            logging.info(f"Player bought {item_name} for {item['price_copper']} copper")
            return True

        except Exception as e:
            logging.error(f"Error processing buy transaction: {str(e)}")
            return False

    def sell_item(self, player: Any, item: Dict) -> bool:
        """
        Handle the player selling an item to the merchant.
        
        Args:
            player: The player character
            item: The item to sell
            
        Returns:
            bool: Whether the sale was successful
        """
        try:
            if item not in player.inventory:
                logging.warning(f"Item not found in player inventory: {item['name']}")
                return False

            # Calculate sell price
            sell_price = self.get_item_value(item)

            # Process transaction
            player.money += sell_price
            player.remove_item(item)

            logging.info(f"Player sold {item['name']} for {sell_price} copper")
            return True

        except Exception as e:
            logging.error(f"Error processing sell transaction: {str(e)}")
            return False

    def get_item_value(self, item: Dict) -> int:
        """
        Calculate the sell value of an item.
        
        Args:
            item: The item to evaluate
            
        Returns:
            int: The sell value of the item
        """
        try:
            base_price = item.get('price_copper', 0)
            return max(1, int(base_price * self._sell_price_ratio))
        except Exception as e:
            logging.error(f"Error calculating item value: {str(e)}")
            return 1

    def get_inventory_by_type(self, item_type: str) -> List[Dict]:
        """
        Get filtered inventory by item type.
        
        Args:
            item_type: Type of items to retrieve
            
        Returns:
            List of items of the specified type
        """
        try:
            return [
                item.copy() for item in self._inventory 
                if item.get('type') == item_type
            ]
        except Exception as e:
            logging.error(f"Error getting inventory by type: {str(e)}")
            return []

    def get_available_types(self) -> List[str]:
        """
        Get a list of available item types in the inventory.
        
        Returns:
            List of available item types
        """
        try:
            return sorted(list(set(
                item.get('type') for item in self._inventory 
                if item.get('type')
            )))
        except Exception as e:
            logging.error(f"Error getting available types: {str(e)}")
            return []

    def can_purchase(self, player: Any, item_name: str) -> bool:
        """
        Check if a player can purchase a specific item.
        
        Args:
            player: The player character
            item_name: Name of the item to check
            
        Returns:
            bool: Whether the player can purchase the item
        """
        try:
            item = next((i for i in self._inventory if i['name'] == item_name), None)
            if not item:
                return False
            return player.can_afford(item['price_copper'])
        except Exception as e:
            logging.error(f"Error checking purchase possibility: {str(e)}")
            return False

    def get_inventory_value(self) -> int:
        """
        Get total value of merchant's inventory.
        
        Returns:
            int: Total value in copper
        """
        try:
            return sum(item.get('price_copper', 0) for item in self._inventory)
        except Exception as e:
            logging.error(f"Error calculating inventory value: {str(e)}")
            return 0

    def has_item(self, item_name: str) -> bool:
        """
        Check if merchant has a specific item.
        
        Args:
            item_name: Name of the item to check
            
        Returns:
            bool: Whether the merchant has the item
        """
        try:
            return any(item.get('name') == item_name for item in self._inventory)
        except Exception as e:
            logging.error(f"Error checking item availability: {str(e)}")
            return False

    def get_item_price(self, item_name: str) -> Optional[int]:
        """
        Get the price of a specific item.
        
        Args:
            item_name: Name of the item
            
        Returns:
            int: Price of the item, or None if not found
        """
        try:
            item = next((i for i in self._inventory if i['name'] == item_name), None)
            return item.get('price_copper') if item else None
        except Exception as e:
            logging.error(f"Error getting item price: {str(e)}")
            return None