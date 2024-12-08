# database.py
import csv
import pandas as pd
from typing import Dict, Optional, Any, List
import os
from config import DATA_DIR
import logging

class Database:
    _instance = None

    def __new__(cls) -> 'Database':
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self) -> None:
        self.data_files = {
            'items': os.path.join(DATA_DIR, 'items.csv'),
            'enemies': os.path.join(DATA_DIR, 'enemies.csv'),
            'player_tiers': os.path.join(DATA_DIR, 'player_tiers.csv')
        }
        
        # Add the _required_columns attribute
        self._required_columns = {
            'items': ['name', 'type', 'base_damage_min', 'base_damage_max', 'base_defense', 'price_copper', 'tier', 'durability', 'effect'],
            'enemies': ['name', 'tier', 'attack', 'defense', 'health', 'xp_value', 'min_copper', 'max_copper', 'common_drops', 'rare_drops', 'spawn_chance'],
            'player_tiers': ['tier', 'title', 'attack', 'defense', 'health', 'min_xp', 'weapon', 'armor', 'special_ability']
        }
        
        self._verify_data_files()

    def _verify_data_files(self) -> None:
        """Verify existence of required data files and their structure."""
        for file_name, file_path in self.data_files.items():
            if not os.path.exists(file_path):
                logging.error(f"Missing data file: {file_path}")
                raise FileNotFoundError(f"Required data file missing: {file_name}")
            
            # Verify file structure
            try:
                df = pd.read_csv(file_path)
                missing_columns = set(self._required_columns[file_name]) - set(df.columns)
                if missing_columns:
                    logging.error(f"Missing required columns in {file_name}: {missing_columns}")
                    raise ValueError(f"Invalid file structure in {file_name}")
            except Exception as e:
                logging.error(f"Error verifying {file_name}: {str(e)}")
                raise

    def load_data(self, table_name: str) -> pd.DataFrame:
        """
        Load and validate data from CSV files.
        
        Args:
            table_name: Name of the table to load
            
        Returns:
            DataFrame containing the loaded and validated data
        """
        try:
            df = pd.read_csv(self.data_files[table_name])
            
            # Validate required columns
            if table_name in self._required_columns:
                missing = [col for col in self._required_columns[table_name] if col not in df.columns]
                if missing:
                    logging.error(f"Missing required columns in {table_name}: {missing}")
                    return pd.DataFrame()
                    
            # Clean and validate numeric columns
            numeric_columns = {
                'items': ['base_damage_min', 'base_damage_max', 'base_defense', 'price_copper', 'tier', 'durability'],
                'enemies': ['tier', 'attack', 'defense', 'health', 'xp_value', 'min_copper', 'max_copper', 'spawn_chance'],
                'player_tiers': ['tier', 'attack', 'defense', 'health', 'min_xp']
            }
            
            if table_name in numeric_columns:
                for col in numeric_columns[table_name]:
                    if col in df.columns:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                
                # Drop rows with invalid numeric values
                invalid_rows = df[numeric_columns[table_name]].isna().any(axis=1)
                if invalid_rows.any():
                    invalid_indices = df[invalid_rows].index
                    logging.warning(f"Dropping rows with invalid numeric values in {table_name}: {invalid_indices}")
                    df = df[~invalid_rows]
            
            return df

        except Exception as e:
            logging.error(f"Error loading {table_name}: {str(e)}")
            return pd.DataFrame()

    def save_data(self, table_name: str, data: pd.DataFrame) -> None:
        """
        Save data to CSV files with validation.
        
        Args:
            table_name: Name of the table to save
            data: DataFrame containing the data to save
        """
        try:
            # Validate required columns
            if table_name in self._required_columns:
                missing = [col for col in self._required_columns[table_name] if col not in data.columns]
                if missing:
                    raise ValueError(f"Missing required columns: {missing}")
                    
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.data_files[table_name]), exist_ok=True)
            
            # Save with index=False to avoid extra column
            data.to_csv(self.data_files[table_name], index=False)
            logging.info(f"Successfully saved data to {table_name}")
            
        except Exception as e:
            logging.error(f"Error saving {table_name}: {str(e)}")
            raise

    def get_item(self, item_name: str) -> Optional[Dict[str, Any]]:
        """
        Get complete item data by name with improved error handling.
        
        Args:
            item_name: Name of the item to retrieve
            
        Returns:
            Dictionary containing item data or None if not found
        """
        items_df = self.load_data('items')
        try:
            item = items_df[items_df['name'] == item_name].iloc[0]
            return {
                'name': item['name'],
                'type': item['type'],
                'base_damage_min': float(item['base_damage_min']) if pd.notna(item['base_damage_min']) else 0,
                'base_damage_max': float(item['base_damage_max']) if pd.notna(item['base_damage_max']) else 0,
                'base_defense': float(item['base_defense']) if pd.notna(item['base_defense']) else 0,
                'price_copper': int(item['price_copper']) if pd.notna(item['price_copper']) else 0,
                'tier': int(item['tier']) if pd.notna(item['tier']) else 1,
                'durability': int(item['durability']) if pd.notna(item['durability']) else 100,
                'effect': item['effect'] if pd.notna(item['effect']) else 'none'
            }
        except (IndexError, KeyError) as e:
            logging.warning(f"Item not found or invalid data: {item_name} - {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Error retrieving item {item_name}: {str(e)}")
            return None

    def get_enemy(self, enemy_name: str) -> Optional[Dict[str, Any]]:
        """
        Get complete enemy data by name with improved error handling.
        
        Args:
            enemy_name: Name of the enemy to retrieve
            
        Returns:
            Dictionary containing enemy data or None if not found
        """
        enemies_df = self.load_data('enemies')
        try:
            enemy = enemies_df[enemies_df['name'] == enemy_name].iloc[0]
            return {
                'name': enemy['name'],
                'tier': int(enemy['tier']) if pd.notna(enemy['tier']) else 1,
                'attack': int(enemy['attack']) if pd.notna(enemy['attack']) else 0,
                'defense': int(enemy['defense']) if pd.notna(enemy['defense']) else 0,
                'health': int(enemy['health']) if pd.notna(enemy['health']) else 10,
                'xp_value': int(enemy['xp_value']) if pd.notna(enemy['xp_value']) else 1,
                'min_copper': int(enemy['min_copper']) if pd.notna(enemy['min_copper']) else 0,
                'max_copper': int(enemy['max_copper']) if pd.notna(enemy['max_copper']) else 0,
                'common_drops': [x.strip() for x in enemy['common_drops'].split(',')] if pd.notna(enemy['common_drops']) else [],
                'rare_drops': [x.strip() for x in enemy['rare_drops'].split(',')] if pd.notna(enemy['rare_drops']) else [],
                'spawn_chance': float(enemy['spawn_chance']) if pd.notna(enemy['spawn_chance']) else 0.1
            }
        except (IndexError, KeyError) as e:
            logging.warning(f"Enemy not found or invalid data: {enemy_name} - {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Error retrieving enemy {enemy_name}: {str(e)}")
            return None

    def get_tier_data(self, tier: int) -> Optional[Dict[str, Any]]:
        """
        Get complete tier data with improved error handling.
        
        Args:
            tier: The tier level to retrieve
            
        Returns:
            Dictionary containing tier data or None if not found
        """
        tiers_df = self.load_data('player_tiers')
        try:
            tier_data = tiers_df[tiers_df['tier'] == tier].iloc[0]
            return {
                'tier': int(tier_data['tier']),
                'title': tier_data['title'],
                'attack': int(tier_data['attack']) if pd.notna(tier_data['attack']) else 1,
                'defense': int(tier_data['defense']) if pd.notna(tier_data['defense']) else 1,
                'health': int(tier_data['health']) if pd.notna(tier_data['health']) else 20,
                'min_xp': int(tier_data['min_xp']) if pd.notna(tier_data['min_xp']) else 0,
                'weapon': tier_data['weapon'] if pd.notna(tier_data['weapon']) else None,
                'armor': tier_data['armor'] if pd.notna(tier_data['armor']) else None,
                'special_ability': tier_data['special_ability'] if pd.notna(tier_data['special_ability']) else 'none'
            }
        except (IndexError, KeyError) as e:
            logging.warning(f"Tier data not found or invalid: {tier} - {str(e)}")
            return None
        except Exception as e:
            logging.error(f"Error retrieving tier {tier} data: {str(e)}")
            return None

    def get_all_items_by_tier(self, tier: int) -> pd.DataFrame:
        """Get all items available for a specific tier."""
        items_df = self.load_data('items')
        return items_df[items_df['tier'] <= tier].copy()

    def get_all_enemies_by_tier(self, tier: int) -> pd.DataFrame:
        """Get all enemies that can appear in a specific tier."""
        enemies_df = self.load_data('enemies')
        return enemies_df[enemies_df['tier'] <= tier].copy()

    def update_item(self, item_name: str, updates: Dict[str, Any]) -> None:
        """
        Update specific attributes of an item with validation.
        
        Args:
            item_name: Name of the item to update
            updates: Dictionary of updates to apply
        """
        items_df = self.load_data('items')
        idx = items_df[items_df['name'] == item_name].index
        
        if len(idx) == 0:
            raise ValueError(f"Item not found: {item_name}")
            
        for key, value in updates.items():
            if key not in items_df.columns:
                raise ValueError(f"Invalid item attribute: {key}")
            items_df.loc[idx, key] = value
            
        self.save_data('items', items_df)
        logging.info(f"Updated item {item_name} with {updates}")