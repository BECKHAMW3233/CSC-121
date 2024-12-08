# gui/combat_window.py
from tkinter import ttk
import tkinter as tk
from typing import Any, Callable, Dict, Optional
import logging
from models.combat import CombatAction

class CombatWindow(tk.Toplevel):
    """
    Combat interface window.
    
    Attributes:
        character: The player character
        enemy: The enemy being fought
        combat_system: The combat system handling the fight
        on_combat_end: Callback for when combat ends
    """
    def __init__(
        self, 
        master: tk.Tk, 
        character: Any, 
        enemy: Any, 
        combat_system: Any, 
        on_combat_end: Callable
    ):
        """Initialize the combat window."""
        try:
            super().__init__(master)
            self.title("Combat")
            self.geometry("500x600")
            self.resizable(False, False)
            
            # Make window modal
            self.transient(master)
            self.grab_set()
            self.protocol("WM_DELETE_WINDOW", self.disable_close)
            self.lift()
            self.focus_force()
            
            # Store combat data
            self.character = character
            self.enemy = enemy
            self.combat_system = combat_system
            self.on_combat_end = on_combat_end
            self.combat_ended = False
            
            # Initialize UI elements
            self.attack_button: Optional[ttk.Button] = None
            self.item_button: Optional[ttk.Button] = None
            self.flee_button: Optional[ttk.Button] = None
            self.combat_log: Optional[tk.Text] = None
            
            self.setup_ui()
            self.update_stats()
            
            # Initial combat message
            self.log_message(f"Combat initiated between {self.character.name} and {self.enemy.name}!")
            self.log_message("-" * 50)
            
            logging.info(f"Combat window initialized: {character.name} vs {enemy.name}")
            
        except Exception as e:
            logging.error(f"Error initializing combat window: {str(e)}")
            self.end_combat('defeat')
            self.destroy()

    def disable_close(self) -> None:
        """Prevent window from being closed by the X button."""
        pass
        
    def setup_ui(self) -> None:
        """Set up the combat user interface."""
        try:
            # Main container
            main_container = ttk.Frame(self, padding="5")
            main_container.pack(fill='both', expand=True)
            
            # Stats Frame
            self.stats_frame = ttk.LabelFrame(main_container, text="Combat Stats", padding="5")
            self.stats_frame.pack(fill='x', pady=(0, 5))
            
            # Character stats
            char_frame = ttk.Frame(self.stats_frame)
            char_frame.pack(fill='x', pady=2)
            ttk.Label(char_frame, text="Player:", width=10).pack(side='left')
            self.character_stats = ttk.Label(char_frame, text="")
            self.character_stats.pack(side='left', fill='x', expand=True)
            
            # Enemy stats
            enemy_frame = ttk.Frame(self.stats_frame)
            enemy_frame.pack(fill='x', pady=2)
            ttk.Label(enemy_frame, text="Enemy:", width=10).pack(side='left')
            self.enemy_stats = ttk.Label(enemy_frame, text="")
            self.enemy_stats.pack(side='left', fill='x', expand=True)
            
            # Combat Log Frame with Scrollbar
            self.log_frame = ttk.LabelFrame(main_container, text="Combat Log", padding="5")
            self.log_frame.pack(fill='both', expand=True, pady=(0, 5))
            
            log_scroll = ttk.Scrollbar(self.log_frame)
            log_scroll.pack(side='right', fill='y')
            
            self.combat_log = tk.Text(
                self.log_frame,
                height=20,
                wrap='word',
                yscrollcommand=log_scroll.set,
                background='white',
                font=('Courier', 10),
                state='disabled'  # Make read-only
            )
            self.combat_log.pack(fill='both', expand=True)
            log_scroll.config(command=self.combat_log.yview)
            
            # Action Buttons Frame
            self.actions_frame = ttk.LabelFrame(main_container, text="Actions", padding="5")
            self.actions_frame.pack(fill='x')
            
            # Action buttons
            button_frame = ttk.Frame(self.actions_frame)
            button_frame.pack(fill='x', expand=True)
            
            # Create buttons with consistent styling
            button_style = {'width': 20}
            
            self.attack_button = ttk.Button(
                button_frame,
                text="Attack",
                command=self.handle_attack,
                **button_style
            )
            self.attack_button.pack(side='left', padx=5)
            
            self.item_button = ttk.Button(
                button_frame,
                text="Use Item",
                command=self.show_item_selection,
                **button_style
            )
            self.item_button.pack(side='left', padx=5)
            
            self.flee_button = ttk.Button(
                button_frame,
                text="Flee",
                command=self.handle_flee,
                **button_style
            )
            self.flee_button.pack(side='left', padx=5)
            
            logging.debug("Combat UI setup complete")
            
        except Exception as e:
            logging.error(f"Error setting up combat UI: {str(e)}")
            self.end_combat('defeat')
            self.destroy()
        
    def update_stats(self) -> None:
        """Update the displayed combat stats."""
        try:
            char_attack = self.character.calculate_total_attack()
            char_defense = self.character.calculate_total_defense()
            
            self.character_stats.config(
                text=f"HP: {self.character.current_health}/{self.character.max_health} "
                     f"ATK: {char_attack} DEF: {char_defense}"
            )
            
            self.enemy_stats.config(
                text=f"HP: {self.enemy.current_health}/{self.enemy.health} "
                     f"ATK: {self.enemy.attack} DEF: {self.enemy.defense}"
            )
            
        except Exception as e:
            logging.error(f"Error updating combat stats: {str(e)}")
        
    def log_message(self, message: str) -> None:
        """
        Add a message to the combat log.
        
        Args:
            message: The message to add
        """
        try:
            self.combat_log.config(state='normal')
            self.combat_log.insert('end', f"{message}\n")
            self.combat_log.see('end')
            self.combat_log.config(state='disabled')
        except Exception as e:
            logging.error(f"Error logging combat message: {str(e)}")
        
    def disable_buttons(self) -> None:
        """Disable all action buttons."""
        try:
            for button in [self.attack_button, self.item_button, self.flee_button]:
                if button:
                    button.config(state='disabled')
        except Exception as e:
            logging.error(f"Error disabling buttons: {str(e)}")
        
    def enable_buttons(self) -> None:
        """Enable all action buttons if combat hasn't ended."""
        try:
            if not self.combat_ended:
                for button in [self.attack_button, self.item_button, self.flee_button]:
                    if button:
                        button.config(state='normal')
        except Exception as e:
            logging.error(f"Error enabling buttons: {str(e)}")

    def show_item_selection(self) -> None:
        """Show the item selection window."""
        try:
            usable_items = [
                item for item in self.character.inventory 
                if item['type'] == 'consumable'
            ]
            
            if not usable_items:
                self.log_message("\nNo usable items in inventory!")
                return
                
            # Create item selection window
            item_window = tk.Toplevel(self)
            item_window.title("Select Item")
            item_window.geometry("300x400")
            item_window.transient(self)
            item_window.grab_set()
            
            # Create scrollable frame
            canvas = tk.Canvas(item_window)
            scrollbar = ttk.Scrollbar(item_window, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Add items to scrollable frame
            for item in usable_items:
                item_frame = ttk.Frame(scrollable_frame)
                item_frame.pack(fill='x', padx=5, pady=2)
                
                # Get effect description
                effect_desc = ""
                if 'effect' in item and item['effect'].startswith('heal_'):
                    try:
                        heal_amount = int(item['effect'].split('_')[1])
                        effect_desc = f" (Heals {heal_amount} HP)"
                    except (IndexError, ValueError):
                        effect_desc = ""
                
                item_info = f"{item['name']}{effect_desc}"
                ttk.Label(item_frame, text=item_info).pack(side='left', padx=5)
                
                ttk.Button(
                    item_frame,
                    text="Use",
                    command=lambda i=item: self.use_selected_item(i, item_window)
                ).pack(side='right', padx=5)
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            logging.debug("Item selection window displayed")
            
        except Exception as e:
            logging.error(f"Error showing item selection: {str(e)}")

    def use_selected_item(self, item: Dict, window: tk.Toplevel) -> None:
        """
        Use a selected item in combat.
        
        Args:
            item: The item to use
            window: The item selection window
        """
        try:
            window.destroy()
            self.disable_buttons()
            
            success = False
            if item['type'] == 'consumable':
                success = self.character.use_healing_potion(item)
                
                if success:
                    heal_amount = int(item['effect'].split('_')[1])
                    self.log_message(f"\n{self.character.name} used {item['name']} and healed for {heal_amount} HP!")
                    self.update_stats()
                    # Process enemy turn after using item
                    self.after(1000, self.process_enemy_turn)
                else:
                    self.log_message(f"\nFailed to use {item['name']}!")
                    self.enable_buttons()
            
            logging.info(f"Combat item use attempt - Item: {item['name']}, Success: {success}")
            
            # Check combat status
            is_ended, outcome = self.combat_system.check_combat_status(self.character, self.enemy)
            if is_ended:
                self.handle_combat_end(outcome)
            elif not success:
                self.enable_buttons()
                
        except Exception as e:
            logging.error(f"Error using selected item: {str(e)}")
            self.enable_buttons()

    def handle_attack(self) -> None:
        """Handle player attack action."""
        try:
            self.disable_buttons()
            
            # Process player's attack
            result = self.combat_system.process_turn(
                self.character,
                self.enemy,
                CombatAction(type='attack')
            )
            
            # Log all messages from the combat system
            self.log_message("\n=== Player Turn ===")
            for message in result['messages']:
                self.log_message(message)
                
            self.update_stats()
            
            # Check if enemy is defeated
            is_ended, outcome = self.combat_system.check_combat_status(self.character, self.enemy)
            if is_ended:
                self.handle_combat_end(outcome)
                return
                
            # Process enemy's turn after a short delay
            self.after(1000, self.process_enemy_turn)
            
        except Exception as e:
            logging.error(f"Error handling attack: {str(e)}")
            self.enable_buttons()
        
    def process_enemy_turn(self) -> None:
        """Process the enemy's combat turn."""
        try:
            self.log_message("\n=== Enemy Turn ===")
            result = self.combat_system.process_turn(
                self.enemy,
                self.character,
                CombatAction(type='attack')
            )
            
            for message in result['messages']:
                self.log_message(message)
                
            self.update_stats()
            
            # Check combat status after enemy turn
            is_ended, outcome = self.combat_system.check_combat_status(self.character, self.enemy)
            if is_ended:
                self.handle_combat_end(outcome)
            else:
                self.enable_buttons()
                
        except Exception as e:
            logging.error(f"Error processing enemy turn: {str(e)}")
            self.enable_buttons()
            
    def handle_flee(self) -> None:
        """Handle player flee attempt."""
        try:
            self.disable_buttons()
            
            self.log_message("\n=== Flee Attempt ===")
            result = self.combat_system.process_turn(
                self.character,
                self.enemy,
                CombatAction(type='flee')
            )
            
            for message in result['messages']:
                self.log_message(message)
                
            if result['fled']:
                self.log_message("\nEscaped successfully!")
                self.after(1500, lambda: self.handle_combat_end('fled'))
            else:
                self.log_message("\nFailed to escape!")
                self.after(1000, self.process_enemy_turn)
                
        except Exception as e:
            logging.error(f"Error handling flee attempt: {str(e)}")
            self.enable_buttons()
            
    def handle_combat_end(self, outcome: str) -> None:
        """
        Handle the end of combat.
        
        Args:
            outcome: The combat outcome ('victory', 'defeat', 'fled')
        """
        try:
            self.combat_ended = True
            self.disable_buttons()
            self.log_message("\n" + "=" * 50)
            
            if outcome == 'victory':
                rewards = self.combat_system.distribute_rewards(self.character, self.enemy)
                self.log_message("\nVictory!")
                self.log_message(f"Gained {rewards['xp']} XP and {rewards['copper']} copper")
                for item in rewards['items']:
                    self.log_message(f"Received item: {item}")
            elif outcome == 'defeat':
                self.log_message("\nDefeat... You have been slain!")
            elif outcome == 'fled':
                self.log_message("\nYou have escaped from combat!")
                
            # Add a close button
            ttk.Button(
                self.actions_frame,
                text="Close",
                command=lambda: self.end_combat(outcome),
                width=20
            ).pack(pady=10)
            
            logging.info(f"Combat ended - Outcome: {outcome}")
            
        except Exception as e:
            logging.error(f"Error handling combat end: {str(e)}")
            self.end_combat('defeat')

    def end_combat(self, outcome: str) -> None:
        """
        Clean up and exit the combat window.
        
        Args:
            outcome: The final combat outcome
        """
        try:
            self.grab_release()
            self.on_combat_end(outcome)
            self.destroy()
            logging.info("Combat window closed")
            
        except Exception as e:
            logging.error(f"Error ending combat: {str(e)}")
            # Force close window in case of error
            try:
                self.destroy()
            except:
                pass

    def validate_combat_state(self) -> bool:
        """
        Validate that combat can continue.
        
        Returns:
            bool: Whether combat can continue
        """
        try:
            if not self.character or not self.enemy:
                return False
            if not hasattr(self.character, 'current_health') or not hasattr(self.enemy, 'current_health'):
                return False
            if self.combat_ended:
                return False
            return True
            
        except Exception as e:
            logging.error(f"Error validating combat state: {str(e)}")
            return False

    def update_ui(self) -> None:
        """Update all UI elements."""
        try:
            self.update_stats()
            self.update_idletasks()
        except Exception as e:
            logging.error(f"Error updating UI: {str(e)}")

    def handle_error(self, error: Exception, fallback_outcome: str = 'defeat') -> None:
        """
        Handle critical errors during combat.
        
        Args:
            error: The exception that occurred
            fallback_outcome: The outcome to use if combat must end
        """
        try:
            logging.error(f"Critical combat error: {str(error)}")
            self.log_message("\nAn error occurred during combat!")
            self.handle_combat_end(fallback_outcome)
        except Exception as e:
            logging.error(f"Error handling combat error: {str(e)}")
            self.end_combat(fallback_outcome)

    def bind_shortcut_keys(self) -> None:
        """Bind keyboard shortcuts for combat actions."""
        try:
            self.bind('<space>', lambda e: self.handle_attack())
            self.bind('<i>', lambda e: self.show_item_selection())
            self.bind('<Escape>', lambda e: self.handle_flee())
        except Exception as e:
            logging.error(f"Error binding shortcut keys: {str(e)}")

    def validate_player_turn(self) -> bool:
        """
        Validate that the player can take their turn.
        
        Returns:
            bool: Whether the player can take their turn
        """
        try:
            if not self.validate_combat_state():
                return False
                
            # Check if any buttons are enabled
            buttons_enabled = any(
                button and str(button.cget('state')) == 'normal'
                for button in [self.attack_button, self.item_button, self.flee_button]
            )
            
            return buttons_enabled
            
        except Exception as e:
            logging.error(f"Error validating player turn: {str(e)}")
            return False

    def validate_enemy_turn(self) -> bool:
        """
        Validate that the enemy can take their turn.
        
        Returns:
            bool: Whether the enemy can take their turn
        """
        try:
            if not self.validate_combat_state():
                return False
                
            # Check if buttons are disabled (indicating enemy turn)
            buttons_disabled = all(
                button and str(button.cget('state')) == 'disabled'
                for button in [self.attack_button, self.item_button, self.flee_button]
            )
            
            return buttons_disabled and not self.combat_ended
            
        except Exception as e:
            logging.error(f"Error validating enemy turn: {str(e)}")
            return False

    def reset_turn_state(self) -> None:
        """Reset the state between turns."""
        try:
            self.update_ui()
            self.enable_buttons()
        except Exception as e:
            logging.error(f"Error resetting turn state: {str(e)}")

    def cleanup(self) -> None:
        """Perform cleanup before window closes."""
        try:
            self.combat_ended = True
            self.disable_buttons()
            self.grab_release()
            
            # Clear any scheduled after events
            for after_id in self.tk.eval('after info').split():
                self.after_cancel(after_id)
                
        except Exception as e:
            logging.error(f"Error during cleanup: {str(e)}")