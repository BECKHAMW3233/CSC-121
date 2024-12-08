# combat.py
from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Any, List
import random
import logging
import math
from config import FLEE_BASE_CHANCE, CRITICAL_HIT_MULTIPLIER
from database import Database

@dataclass
class CombatAction:
    """
    Represents a combat action.
    
    Attributes:
        type: The type of action ('attack', 'use_item', 'flee')
        target: Optional target of the action
        item: Optional item being used
    """
    type: str
    target: Optional[str] = None
    item: Optional[Dict] = None

class D20CombatSystem:
    """
    Implements a D20-based combat system.
    """
    def __init__(self):
        """Initialize the combat system."""
        self._status_effects: Dict[str, Dict] = {}
        self._combat_log: List[str] = []

    def roll_d20(self) -> int:
        """
        Simulate rolling a 20-sided die.
        
        Returns:
            int: The result of the die roll (1-20)
        """
        return random.randint(1, 20)

    def calculate_hit(self, attacker: Any, defender: Any) -> Tuple[bool, int, bool]:
        """
        Calculate if an attack hits using the D20 system.
        
        Args:
            attacker: The attacking character
            defender: The defending character
            
        Returns:
            Tuple containing (hit successful, roll value, critical hit)
        """
        if not hasattr(attacker, 'calculate_total_attack') or not hasattr(defender, 'calculate_total_defense'):
            raise ValueError("Invalid combatant objects")

        try:
            roll = self.roll_d20()
            
            # Natural 20 always hits and crits
            if roll == 20:
                return True, roll, True
                
            # Natural 1 always misses
            if roll == 1:
                return False, roll, False
                
            attack_bonus = attacker.calculate_total_attack()
            defense_class = 10 + defender.calculate_total_defense()
            
            # Player advantage: +2 to hit for players
            if hasattr(attacker, 'is_player') and attacker.is_player:
                attack_bonus += 2
                
            return (roll + attack_bonus >= defense_class), roll, False
            
        except Exception as e:
            logging.error(f"Error calculating hit: {str(e)}")
            return False, 1, False

    def process_turn(self, attacker: Any, defender: Any, action: CombatAction) -> Dict[str, Any]:
        """
        Process a single combat turn.
        
        Args:
            attacker: The attacking character
            defender: The defending character
            action: The combat action to process
            
        Returns:
            Dictionary containing the results of the turn
        """
        result = {
            'success': False,
            'damage_dealt': 0,
            'item_used': None,
            'fled': False,
            'messages': [],
            'roll_info': {}
        }

        try:
            if action.type == 'attack':
                result.update(self._process_attack(attacker, defender))
            elif action.type == 'use_item':
                result.update(self._process_item_use(attacker, action.item))
            elif action.type == 'flee':
                result.update(self._process_flee_attempt(attacker))
            else:
                raise ValueError(f"Invalid action type: {action.type}")
                
        except Exception as e:
            logging.error(f"Error processing turn: {str(e)}")
            result['messages'].append("An error occurred processing the turn")
            
        return result

    def _process_attack(self, attacker: Any, defender: Any) -> Dict[str, Any]:
        """
        Process an attack action.
        
        Args:
            attacker: The attacking character
            defender: The defending character
            
        Returns:
            Dictionary containing the results of the attack
        """
        result = {
            'success': False,
            'damage_dealt': 0,
            'messages': [],
            'roll_info': {}
        }

        try:
            hit_success, roll, is_crit = self.calculate_hit(attacker, defender)
            result['roll_info']['hit_roll'] = roll
            result['roll_info']['attack_bonus'] = attacker.calculate_total_attack()
            result['roll_info']['defense_class'] = 10 + defender.calculate_total_defense()
            
            if hit_success:
                damage = self._calculate_damage(attacker, defender, is_crit)
                result['roll_info']['damage_base'] = damage / (CRITICAL_HIT_MULTIPLIER if is_crit else 1)
                result['roll_info']['is_crit'] = is_crit
                
                defender.take_damage(damage)
                result['damage_dealt'] = damage
                result['success'] = True
                
                crit_text = " **CRITICAL HIT!**" if is_crit else ""
                roll_text = f"[Roll: {roll} + {attacker.calculate_total_attack()} vs AC {result['roll_info']['defense_class']}]"
                
                message = (f"{attacker.name} attacks {defender.name}{crit_text}! "
                          f"{roll_text} "
                          f"Dealing {damage} damage!")
                
                result['messages'].append(message)
                logging.info(f"Combat hit - {attacker.name} vs {defender.name}: {damage} damage")
            else:
                miss_reason = "Critical Miss!" if roll == 1 else "Miss!"
                message = f"{attacker.name}'s attack missed! {miss_reason} {roll} + {attacker.calculate_total_attack()} vs AC {result['roll_info']['defense_class']}"
                result['messages'].append(message)
                logging.info(f"Combat miss - {attacker.name} vs {defender.name}")
                
        except Exception as e:
            logging.error(f"Error processing attack: {str(e)}")
            result['messages'].append("Error processing attack")
            
        return result

    def _calculate_damage(self, attacker: Any, defender: Any, is_crit: bool = False) -> int:
        """
        Calculate damage for an attack.
        
        Args:
            attacker: The attacking character
            defender: The defending character
            is_crit: Whether this is a critical hit
            
        Returns:
            int: The calculated damage amount
        """
        try:
            base_damage = attacker.calculate_total_attack()
            
            # Calculate weapon damage
            if hasattr(attacker, 'equipped_weapon') and attacker.equipped_weapon:
                try:
                    min_dmg = float(attacker.equipped_weapon.get('base_damage_min', 1))
                    max_dmg = float(attacker.equipped_weapon.get('base_damage_max', 4))
                    weapon_damage = random.uniform(min_dmg, max_dmg)
                    base_damage += weapon_damage
                except (ValueError, TypeError):
                    logging.warning(f"Invalid weapon damage values for {attacker.name}")
            
            # Apply defense reduction
            defense = defender.calculate_total_defense()
            damage = max(1, base_damage - (defense / 2))
            
            # Critical hits double damage
            if is_crit:
                damage *= CRITICAL_HIT_MULTIPLIER
                
            # Player advantage: 20% bonus damage for players
            if hasattr(attacker, 'is_player') and attacker.is_player:
                damage *= 1.2
                
            return max(1, int(damage))
            
        except Exception as e:
            logging.error(f"Error calculating damage: {str(e)}")
            return 1

    def _process_item_use(self, character: Any, item: Optional[Dict]) -> Dict[str, Any]:
        """
        Process an item use action.
        
        Args:
            character: The character using the item
            item: The item being used
            
        Returns:
            Dictionary containing the results of the item use
        """
        result = {
            'success': False,
            'item_used': None,
            'messages': []
        }

        try:
            if not item:
                result['messages'].append("No item selected")
                return result
                
            if item not in character.inventory:
                result['messages'].append("Item not in inventory")
                return result
                
            self._apply_item_effect(character, item)
            character.inventory.remove(item)
            result['item_used'] = item
            result['success'] = True
            result['messages'].append(f"{character.name} used {item['name']}")
            
        except Exception as e:
            logging.error(f"Error processing item use: {str(e)}")
            result['messages'].append("Error using item")
            
        return result

    def _process_flee_attempt(self, character: Any) -> Dict[str, Any]:
        """
        Process a flee attempt action.
        
        Args:
            character: The character attempting to flee
            
        Returns:
            Dictionary containing the results of the flee attempt
        """
        result = {
            'fled': False,
            'success': False,
            'messages': [],
            'roll_info': {}
        }

        try:
            flee_roll = self.roll_d20()
            result['roll_info']['flee_roll'] = flee_roll
            flee_dc = 10
            
            flee_bonus = 2 if hasattr(character, 'is_player') and character.is_player else 0
            
            if flee_roll + flee_bonus >= flee_dc:
                result['fled'] = True
                result['success'] = True
                message = f"{character.name} successfully fled! [Roll: {flee_roll} + {flee_bonus} vs DC {flee_dc}]"
                result['messages'].append(message)
                logging.info(f"Flee success - {character.name}")
            else:
                message = f"{character.name} failed to flee! [Roll: {flee_roll} + {flee_bonus} vs DC {flee_dc}]"
                result['messages'].append(message)
                logging.info(f"Flee failure - {character.name}")
                
        except Exception as e:
            logging.error(f"Error processing flee attempt: {str(e)}")
            result['messages'].append("Error processing flee attempt")
            
        return result

    def _apply_item_effect(self, character: Any, item: Dict[str, Any]) -> None:
        """
        Apply the effect of an item.
        
        Args:
            character: The character using the item
            item: The item being used
        """
        try:
            if 'type' not in item:
                raise ValueError(f"Item missing 'type' field: {item}")
                
            if item['type'] == 'consumable':
                if 'effect' not in item:
                    raise ValueError(f"Consumable item missing 'effect' field: {item}")
                    
                effect_type, value = item['effect'].split('_')
                if effect_type == 'heal':
                    heal_amount = int(value)
                    character.heal(heal_amount)
                    logging.info(f"Applied healing effect: {heal_amount}")
            elif item['type'] == 'buff':
                self._status_effects[character.name] = {
                    'effect': item['effect'],
                    'duration': item.get('duration', 1)
                }
                
        except Exception as e:
            logging.error(f"Error applying item effect: {str(e)}")

    def check_combat_status(self, character: Any, enemy: Any) -> Tuple[bool, str]:
        """
        Check if combat has ended and determine the outcome.
        
        Args:
            character: The player character
            enemy: The enemy character
            
        Returns:
            Tuple containing (combat ended, outcome)
        """
        try:
            if character.current_health <= 0:
                return True, 'defeat'
            if enemy.current_health <= 0:
                return True, 'victory'
            return False, ''
            
        except Exception as e:
            logging.error(f"Error checking combat status: {str(e)}")
            return True, 'defeat'

    def distribute_rewards(self, character: Any, enemy: Any) -> Dict[str, Any]:
        """
        Calculate and distribute rewards from defeating an enemy.
        
        Args:
            character: The player character
            enemy: The defeated enemy
            
        Returns:
            Dictionary containing the rewards earned
        """
        rewards = {
            'xp': 0,
            'items': [],
            'copper': 0
        }

        try:
            db = Database()
            rewards['xp'] = enemy.xp_value

            # Get drops from enemy
            drops = enemy.get_drops()
            for drop_type, value in drops:
                if drop_type == 'copper':
                    rewards['copper'] = value
                    character.money += value
                elif drop_type == 'item':
                    item_data = db.get_item(value)
                    if item_data:
                        rewards['items'].append(item_data['name'])
                        character.add_item(item_data)
                    else:
                        logging.error(f"Failed to load item data for drop: {value}")

            # Add XP
            character.add_xp(rewards['xp'])
            logging.info(f"Combat rewards distributed: {rewards}")
            
        except Exception as e:
            logging.error(f"Error distributing rewards: {str(e)}")
            
        return rewards