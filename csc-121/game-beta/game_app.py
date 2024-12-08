# game_app.py
import tkinter as tk
from tkinter import messagebox, ttk
import logging
import json
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import copy

from config import WINDOW_WIDTH, WINDOW_HEIGHT, SAVE_DIR, WINDOW_TITLE
from database import Database
from models.character import Character
from models.enemy import Enemy
from models.dungeon import Dungeon
from models.combat import D20CombatSystem
from models.merchant import Merchant
from gui.main_window import GameWindow, GameFrame
from gui.combat_window import CombatWindow

class GameApp:
    """
    Main game application class.
    """
    def __init__(self):
        """Initialize the game application."""
        self._db = Database()
        self._window: Optional[GameWindow] = None
        self._player: Optional[Character] = None
        self._current_dungeon: Optional[Dungeon] = None
        self._merchant: Optional[Merchant] = None
        self._combat_system = D20CombatSystem()
        self._game_state = 'menu'
        self._active_windows = []
        self._initialize_logging()

    def _initialize_logging(self) -> None:
        """Initialize logging configuration."""
        try:
            log_file = os.path.join('logs', f'game_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
            os.makedirs('logs', exist_ok=True)
            logging.basicConfig(
                filename=log_file,
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
            logging.info("Game application initialized")
        except Exception as e:
            print(f"Error initializing logging: {str(e)}")

    def start(self) -> None:
        """Start the game application."""
        try:
            self._window = GameWindow()
            self._window.protocol("WM_DELETE_WINDOW", self._quit_game)
            self._setup_menu()
            self._bind_events()
            self._window.mainloop()
        except Exception as e:
            logging.critical(f"Error starting game: {str(e)}")
            messagebox.showerror("Critical Error", "Failed to start game application")
            raise

    def _setup_menu(self) -> None:
        """Set up the main menu interface."""
        try:
            menu_frame = ttk.Frame(self._window)
            menu_frame.pack(expand=True)
            
            # Title with custom font and styling
            title_label = ttk.Label(
                menu_frame, 
                text="Dungeon RPG", 
                font=('Arial', 24, 'bold')
            )
            title_label.pack(pady=20)
            
            # Menu buttons with consistent styling
            button_style = {'width': 20, 'padding': 5}
            
            ttk.Button(
                menu_frame, 
                text="New Game", 
                command=self._new_game,
                **button_style
            ).pack(pady=5)
            
            ttk.Button(
                menu_frame, 
                text="Load Game", 
                command=self._load_game,
                **button_style
            ).pack(pady=5)
            
            ttk.Button(
                menu_frame, 
                text="Quit", 
                command=self._window.quit,
                **button_style
            ).pack(pady=5)

        except Exception as e:
            logging.error(f"Error setting up menu: {str(e)}")
            raise

    def _bind_events(self) -> None:
        """Bind game events to their handlers."""
        try:
            event_bindings = {
                '<Control-s>': lambda e: self._save_game(),
                '<<SaveGame>>': lambda e: self._save_game(),
                '<<LoadGame>>': lambda e: self._load_game(),
                '<<QuitGame>>': lambda e: self._quit_game(),
                '<<MoveNorth>>': lambda e: self._handle_movement('north'),
                '<<MoveSouth>>': lambda e: self._handle_movement('south'),
                '<<MoveEast>>': lambda e: self._handle_movement('east'),
                '<<MoveWest>>': lambda e: self._handle_movement('west'),
                '<<ToggleInventory>>': lambda e: self._handle_inventory(),
                '<<OpenShop>>': lambda e: self._handle_shop()
            }
            
            for event, handler in event_bindings.items():
                self._window.bind_all(event, handler)
                
            logging.info("Game events bound successfully")
            
        except Exception as e:
            logging.error(f"Error binding events: {str(e)}")
            raise

    def _new_game(self) -> None:
        """Create a new game session."""
        try:
            dialog = tk.Toplevel(self._window)
            dialog.title("Create Character")
            dialog.geometry("300x200")
            dialog.transient(self._window)
            dialog.grab_set()
            
            # Character creation form
            ttk.Label(dialog, text="Character Name:").pack(pady=5)
            name_entry = ttk.Entry(dialog)
            name_entry.pack(pady=5)
            
            ttk.Label(dialog, text="Age:").pack(pady=5)
            age_entry = ttk.Entry(dialog)
            age_entry.pack(pady=5)
            
            def validate_and_create():
                try:
                    name = name_entry.get().strip()
                    if not name:
                        messagebox.showerror("Error", "Name cannot be empty")
                        return
                        
                    try:
                        age = int(age_entry.get())
                        if not 1 <= age <= 100:
                            raise ValueError("Age must be between 1 and 100")
                    except ValueError as e:
                        messagebox.showerror("Error", str(e))
                        return
                        
                    dialog.destroy()
                    self._create_character(name, age)
                    
                except Exception as e:
                    logging.error(f"Error in character creation: {str(e)}")
                    messagebox.showerror("Error", "Failed to create character")
                
            ttk.Button(
                dialog, 
                text="Create", 
                command=validate_and_create
            ).pack(pady=20)
            
        except Exception as e:
            logging.error(f"Error creating new game: {str(e)}")
            messagebox.showerror("Error", "Failed to start new game")

    def _create_character(self, name: str, age: int) -> None:
        """
        Create a new character and start the game.
        
        Args:
            name: Character name
            age: Character age
        """
        try:
            self._player = Character(name=name, age=age)
            self._current_dungeon = Dungeon(tier=1)
            self._start_game()
            logging.info(f"Created new character: {name}, age {age}")
            
        except Exception as e:
            logging.error(f"Error creating character: {str(e)}")
            messagebox.showerror("Error", "Failed to create character")
            raise

    def _start_game(self) -> None:
        """Start or resume a game session."""
        try:
            logging.info("Starting game...")
            self._game_state = 'playing'
            
            if not self._merchant:
                self._merchant = Merchant()
                
            if self._window:
                logging.info("Setting up game UI...")
                self._window.clear_menu()
                self._window.setup_game_ui()
                self._window.bind_keys()
                self._update_display()
                logging.info("Game UI setup complete")
            else:
                raise RuntimeError("Window not initialized")
                
        except Exception as e:
            logging.error(f"Error starting game: {str(e)}")
            messagebox.showerror("Error", "Failed to start game")
            raise

    def _update_display(self) -> None:
        """Update the game display."""
        try:
            if not all([self._window, self._player, self._current_dungeon]):
                raise ValueError("Missing required game components")
                
            self._window.update_game_view(self._current_dungeon, self._player)
            self._window.update_stats_view(self._player)
            
            if isinstance(self._window.current_frame, GameFrame):
                self._window.current_frame.update_equipment_display(self._player)
                
            logging.debug("Display updated successfully")
            
        except Exception as e:
            logging.error(f"Error updating display: {str(e)}")

    def _handle_dungeon_completion(self) -> None:
        """Handle the completion of the current dungeon."""
        try:
            current_tier = self._current_dungeon._tier
            # Award completion bonus based on tier
            completion_bonus = current_tier * 100  # 100 XP per tier
            bonus_gold = current_tier * 50  # 50 gold per tier
            
            self._player.add_xp(completion_bonus)
            self._player.money += bonus_gold
            
            next_tier = min(current_tier + 1, 6)
            
            message = (
                f"Congratulations! You have completed the tier {current_tier} dungeon!\n\n"
                f"Rewards:\n"
                f"- {completion_bonus} XP\n"
                f"- {bonus_gold} copper\n\n"
            )
            
            if next_tier > current_tier:
                message += f"A new dungeon of tier {next_tier} will be generated."
            else:
                message += "You have reached the maximum tier (6)!"
                
            messagebox.showinfo("Victory!", message)
            
            # Generate new dungeon of next tier
            self._current_dungeon = Dungeon(tier=next_tier)
            self._update_display()
            
            logging.info(f"Completed tier {current_tier} dungeon, generated new tier {next_tier} dungeon")
            
        except Exception as e:
            logging.error(f"Error handling dungeon completion: {str(e)}")
            messagebox.showerror("Error", "Failed to process dungeon completion")

    def _handle_movement(self, direction: str) -> None:
        """
        Handle player movement in the dungeon.
        
        Args:
            direction: Direction to move ('north', 'south', 'east', 'west')
        """
        try:
            if self._game_state != 'playing' or not self._current_dungeon:
                return

            if self._current_dungeon.move_player(direction):
                current_room = self._current_dungeon.get_current_room()
                
                # Handle room events in order of priority
                if current_room.enemies and not current_room.is_cleared:
                    self._start_combat(current_room.enemies[0])
                elif current_room.has_treasure and not current_room.treasure_looted:
                    self._handle_treasure(current_room)
                elif current_room.has_merchant and not current_room.merchant_visited:
                    self._handle_shop()
                
                # Check for dungeon completion
                if self._current_dungeon.is_complete():
                    self._handle_dungeon_completion()
                    
                self._update_display()
                
        except Exception as e:
            logging.error(f"Error handling movement: {str(e)}")

    def _load_game(self) -> None:
        """Load a saved game."""
        try:
            if not os.path.exists(SAVE_DIR):
                messagebox.showinfo("Load Game", "No saves directory found.")
                return

            save_files = [f for f in os.listdir(SAVE_DIR) if f.endswith('.json')]
            if not save_files:
                messagebox.showinfo("Load Game", "No saved games found.")
                return

            self._show_load_dialog(save_files)
            
        except Exception as e:
            logging.error(f"Error accessing save files: {str(e)}")
            messagebox.showerror("Error", "Failed to access save files")

    def _show_load_dialog(self, save_files: list) -> None:
        """
        Show the load game dialog.
        
        Args:
            save_files: List of available save files
        """
        try:
            dialog = tk.Toplevel(self._window)
            dialog.title("Load Game")
            dialog.geometry("400x300")
            dialog.transient(self._window)
            dialog.grab_set()

            ttk.Label(dialog, text="Select Save File:").pack(pady=5)

            # Create scrollable frame for save files
            frame = ttk.Frame(dialog)
            frame.pack(fill='both', expand=True, padx=5, pady=5)
            
            scrollbar = ttk.Scrollbar(frame)
            scrollbar.pack(side='right', fill='y')
            
            save_list = tk.Listbox(frame, yscrollcommand=scrollbar.set)
            save_list.pack(side='left', fill='both', expand=True)
            
            scrollbar.config(command=save_list.yview)

            # Populate save files list
            for file in sorted(save_files, reverse=True):
                save_list.insert(tk.END, file)

            def load_selected():
                selection = save_list.curselection()
                if not selection:
                    messagebox.showwarning("Load Game", "Please select a save file.")
                    return
                    
                save_file = save_list.get(selection[0])
                self._load_save_file(save_file)
                dialog.destroy()

            # Add control buttons
            button_frame = ttk.Frame(dialog)
            button_frame.pack(fill='x', padx=5, pady=5)
            
            ttk.Button(
                button_frame, 
                text="Load", 
                command=load_selected
            ).pack(side='left', padx=5)
            
            ttk.Button(
                button_frame, 
                text="Cancel", 
                command=dialog.destroy
            ).pack(side='right', padx=5)

        except Exception as e:
            logging.error(f"Error showing load dialog: {str(e)}")
            raise

    def _load_save_file(self, filename: str) -> None:
        """
        Load a specific save file.
        
        Args:
            filename: Name of the save file to load
        """
        try:
            with open(os.path.join(SAVE_DIR, filename), 'r', encoding='utf-8') as f:
                save_data = json.load(f)

            if not self._validate_save_data(save_data):
                raise ValueError("Invalid save file format")

            self._player = Character(**save_data['player'])
            self._current_dungeon = Dungeon(**save_data['dungeon'])
            self._start_game()
            
            logging.info(f"Successfully loaded save file: {filename}")
            
        except Exception as e:
            logging.error(f"Error loading save file {filename}: {str(e)}")
            messagebox.showerror("Error", f"Failed to load game: {str(e)}")

    def _save_game(self) -> None:
        """Save the current game state."""
        try:
            if not self._player or not self._current_dungeon:
                raise ValueError("No active game to save")

            save_data = {
                'player': self._player.to_dict(),
                'dungeon': self._current_dungeon.to_dict()
            }

# Use character name for save file
            filename = f"{self._player.name.lower().replace(' ', '_')}_save.json"
            filepath = os.path.join(SAVE_DIR, filename)
            
            os.makedirs(SAVE_DIR, exist_ok=True)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)

            logging.info(f"Game saved: {filename}")
            messagebox.showinfo("Save Game", f"Game saved successfully!\nFile: {filename}")
            
        except Exception as e:
            logging.error(f"Error saving game: {str(e)}")
            messagebox.showerror("Error", f"Failed to save game: {str(e)}")

    def _validate_save_data(self, save_data: Dict[str, Any]) -> bool:
        """
        Validate the structure of save data.
        
        Args:
            save_data: The save data to validate
            
        Returns:
            bool: Whether the save data is valid
        """
        try:
            # Check required top-level keys
            required_keys = {'player', 'dungeon'}
            if not all(key in save_data for key in required_keys):
                return False

            # Validate player data
            player_keys = {
                'name', 'age', 'tier', 'xp', 'current_health', 
                'inventory', 'equipped_weapon', 'equipped_armor', 
                'equipped_shield', 'money'
            }
            if not all(key in save_data['player'] for key in player_keys):
                return False

            # Validate dungeon data
            dungeon_keys = {'tier', 'size', 'player_pos', 'rooms'}
            if not all(key in save_data['dungeon'] for key in dungeon_keys):
                return False

            # Validate data types
            if not isinstance(save_data['player']['name'], str):
                return False
            if not isinstance(save_data['player']['age'], int):
                return False
            if not isinstance(save_data['dungeon']['rooms'], list):
                return False

            return True

        except Exception as e:
            logging.error(f"Error validating save data: {str(e)}")
            return False

    def _handle_inventory(self) -> None:
        """Handle opening the inventory interface."""
        try:
            if self._game_state == 'combat' or not self._window or not self._player:
                return

            self._game_state = 'inventory'
            self._window.show_inventory_ui(self._player)
            
        except Exception as e:
            logging.error(f"Error handling inventory: {str(e)}")

    def _handle_shop(self) -> None:
        """Handle merchant interaction."""
        try:
            if not self._merchant or not self._player:
                return
                
            self._game_state = 'shopping'
            self._window.current_dungeon = self._current_dungeon
            self._window.show_merchant_ui(self._player, self._merchant)
            
        except Exception as e:
            logging.error(f"Error handling shop: {str(e)}")

    def _handle_treasure(self, room: Any) -> None:
        """
        Handle treasure room interaction.
        
        Args:
            room: The treasure room being looted
        """
        try:
            if not self._current_dungeon or not self._player:
                return

            loot = self._current_dungeon.get_treasure_loot()
            message = "You found a treasure chest!\n\nContents:\n"
            
            for item_name in loot:
                if isinstance(item_name, tuple) and item_name[0] == 'copper':
                    self._player.money += item_name[1]
                    message += f"- {item_name[1]} copper\n"
                else:
                    item = self._db.get_item(item_name)
                    if item:
                        self._player.add_item(copy.deepcopy(item))
                        message += f"- {item['name']}\n"
                        
            room.treasure_looted = True
            messagebox.showinfo("Treasure!", message)
            logging.info(f"Player looted treasure room: {loot}")
            
        except Exception as e:
            logging.error(f"Error handling treasure: {str(e)}")

    def _start_combat(self, enemy: Enemy) -> None:
        """
        Start a combat encounter.
        
        Args:
            enemy: The enemy to fight
        """
        try:
            if self._game_state == 'combat' or not self._window or not self._player:
                return
                
            self._game_state = 'combat'
            
            # Close any existing combat windows
            self._close_combat_windows()
            
            combat_window = CombatWindow(
                self._window,
                self._player,
                enemy,
                self._combat_system,
                self._handle_combat_end
            )
            self._active_windows.append(combat_window)
            
            logging.info(f"Started combat with {enemy.name}")
            
        except Exception as e:
            logging.error(f"Error starting combat: {str(e)}")
            self._game_state = 'playing'

    def _close_combat_windows(self) -> None:
        """Close any existing combat windows."""
        try:
            for window in self._active_windows:
                if isinstance(window, CombatWindow):
                    window.destroy()
            self._active_windows = [w for w in self._active_windows if not isinstance(w, CombatWindow)]
        except Exception as e:
            logging.error(f"Error closing combat windows: {str(e)}")

    def _handle_combat_end(self, outcome: str) -> None:
        """
        Handle the end of a combat encounter.
        
        Args:
            outcome: The result of the combat ('victory', 'defeat', 'fled')
        """
        try:
            if not self._current_dungeon:
                return
                
            self._game_state = 'playing'
            current_room = self._current_dungeon.get_current_room()

            if outcome == 'victory':
                current_room.is_cleared = True
                current_room.enemies = []
                logging.info("Combat ended in victory")
            elif outcome == 'fled':
                self._current_dungeon.move_player_random_adjacent()
                logging.info("Player fled from combat")
            else:
                logging.info("Combat ended in defeat")

            self._update_display()
            
        except Exception as e:
            logging.error(f"Error handling combat end: {str(e)}")

    def _quit_game(self) -> None:
        """Handle game quit with save prompt."""
        try:
            if self._game_state != 'menu' and messagebox.askyesno("Quit Game", "Do you want to save before quitting?"):
                self._save_game()
                
            # Close all active windows
            for window in self._active_windows:
                try:
                    window.destroy()
                except:
                    pass
                    
            self._active_windows = []
            
            if self._window:
                self._window.quit()
                
            logging.info("Game closed")
            
        except Exception as e:
            logging.error(f"Error quitting game: {str(e)}")
            # Force quit in case of error
            if self._window:
                self._window.destroy()

def main():
    """Main entry point for the game."""
    try:
        # Ensure required directories exist
        os.makedirs(SAVE_DIR, exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Initialize game
        game = GameApp()
        game.start()
        
    except Exception as e:
        logging.critical(f"Critical error in main game loop: {str(e)}")
        messagebox.showerror("Critical Error", f"A critical error occurred: {str(e)}")
        
    finally:
        logging.info("Game session ended")

if __name__ == "__main__":
    main()