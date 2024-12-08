# gui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Optional, Dict, List, Callable
from config import WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE
import logging
import copy

class GameWindow(tk.Tk):
    """
    The main game window class.
    
    Attributes:
        current_frame: The currently active game frame
        current_dungeon: Reference to current dungeon (for merchant UI)
    """
    def __init__(self):
        """Initialize the game window."""
        try:
            super().__init__()
            self.title(WINDOW_TITLE)
            self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
            self.configure(bg='black')
            
            self.current_frame = None
            self._player = None
            self.current_dungeon = None
            self._active_popups: List[tk.Toplevel] = []
            
            self._setup_styles()
            self._setup_error_handling()
            
            logging.info("Game window initialized")
            
        except Exception as e:
            logging.critical(f"Error initializing game window: {str(e)}")
            raise

    def _setup_styles(self) -> None:
        """Set up the styles for the game window."""
        try:
            style = ttk.Style()
            
            # Configure basic styles
            style.configure('Game.TFrame', background='black')
            style.configure('Game.TLabel', 
                          background='black', 
                          foreground='white',
                          font=('Arial', 10))
            style.configure('Game.TButton', 
                          padding=5,
                          font=('Arial', 10))
            
            # Equipment display style
            style.configure('Equipment.TLabel',
                          background='dark blue',
                          foreground='white',
                          padding=5,
                          font=('Arial', 10, 'bold'))
            
            # Merchant interface style
            style.configure('Merchant.TFrame',
                          background='brown',
                          padding=5)
            
            logging.debug("UI styles configured")
            
        except Exception as e:
            logging.error(f"Error setting up styles: {str(e)}")
            raise

    def _setup_error_handling(self) -> None:
        """Set up global error handling for the window."""
        try:
            def handle_tk_error(error_type, value, traceback):
                logging.error(f"Tkinter Error: {error_type} - {value}")
                messagebox.showerror("Error", 
                                   "An error occurred in the game interface.\n"
                                   "Please try restarting the game.")
                
            self.report_callback_exception = handle_tk_error
            
        except Exception as e:
            logging.error(f"Error setting up error handling: {str(e)}")

    def clear_menu(self) -> None:
        """Clear the current menu frame."""
        try:
            if self.current_frame:
                self.current_frame.destroy()
                self.current_frame = None
                
            # Close any active popups
            self.close_active_popups()
            
        except Exception as e:
            logging.error(f"Error clearing menu: {str(e)}")

    def close_active_popups(self) -> None:
        """Close all active popup windows."""
        try:
            for popup in self._active_popups[:]:  # Use slice copy to avoid modification during iteration
                try:
                    popup.destroy()
                except:
                    pass
            self._active_popups.clear()
            
        except Exception as e:
            logging.error(f"Error closing popups: {str(e)}")

    def setup_game_ui(self) -> None:
        """Set up the game user interface."""
        try:
            self.clear_menu()
            self.current_frame = GameFrame(self)
            self.current_frame.pack(expand=True, fill='both')
            
            # Setup menu bar
            menu_bar = tk.Menu(self)
            self.config(menu=menu_bar)
            
            game_menu = tk.Menu(menu_bar, tearoff=0)
            menu_bar.add_cascade(label="Game", menu=game_menu)
            
            game_menu.add_command(
                label="Save Game (Ctrl+S)",
                command=lambda: self.event_generate("<<SaveGame>>")
            )
            game_menu.add_command(
                label="Load Game",
                command=lambda: self.event_generate("<<LoadGame>>")
            )
            game_menu.add_separator()
            game_menu.add_command(
                label="Quit",
                command=lambda: self.event_generate("<<QuitGame>>")
            )
            
            logging.info("Game UI setup complete")
            
        except Exception as e:
            logging.error(f"Error setting up game UI: {str(e)}")
            raise

    def bind_keys(self) -> None:
        """Bind the movement and action keys."""
        try:
            # Movement keys
            self.bind('<w>', lambda e: self.event_generate("<<MoveNorth>>"))
            self.bind('<s>', lambda e: self.event_generate("<<MoveSouth>>"))
            self.bind('<a>', lambda e: self.event_generate("<<MoveWest>>"))
            self.bind('<d>', lambda e: self.event_generate("<<MoveEast>>"))
            
            # Action keys
            self.bind('<i>', lambda e: self.event_generate("<<ToggleInventory>>"))
            self.bind('<Escape>', lambda e: self.show_pause_menu())
            
            # System keys
            self.bind('<Control-s>', lambda e: self.event_generate("<<SaveGame>>"))
            self.bind('<Control-l>', lambda e: self.event_generate("<<LoadGame>>"))
            
            logging.debug("Game keys bound")
            
        except Exception as e:
            logging.error(f"Error binding keys: {str(e)}")

    def rebind_movement_keys(self) -> None:
        """Rebind the movement keys after closing inventory/merchant windows."""
        try:
            self.bind('<w>', lambda e: self.event_generate("<<MoveNorth>>"))
            self.bind('<s>', lambda e: self.event_generate("<<MoveSouth>>"))
            self.bind('<a>', lambda e: self.event_generate("<<MoveWest>>"))
            self.bind('<d>', lambda e: self.event_generate("<<MoveEast>>"))
            
        except Exception as e:
            logging.error(f"Error rebinding movement keys: {str(e)}")

    def show_pause_menu(self) -> None:
        """Show the pause menu."""
        try:
            pause_window = tk.Toplevel(self)
            pause_window.title("Pause Menu")
            pause_window.geometry("200x250")
            pause_window.transient(self)
            pause_window.grab_set()
            pause_window.focus_set()

            def on_closing():
                try:
                    pause_window.grab_release()
                    self.focus_force()
                    pause_window.destroy()
                except:
                    pass

            pause_window.protocol("WM_DELETE_WINDOW", on_closing)
            
            # Add menu buttons with consistent styling
            button_style = {'width': 20, 'padding': 5}
            
            ttk.Button(
                pause_window,
                text="Resume",
                command=on_closing,
                **button_style
            ).pack(pady=5)
            
            ttk.Button(
                pause_window,
                text="Save Game",
                command=lambda: [
                    self.event_generate("<<SaveGame>>"),
                    on_closing()
                ],
                **button_style
            ).pack(pady=5)
            
            ttk.Button(
                pause_window,
                text="Load Game",
                command=lambda: [
                    self.event_generate("<<LoadGame>>"),
                    on_closing()
                ],
                **button_style
            ).pack(pady=5)
            
            ttk.Button(
                pause_window,
                text="Quit",
                command=lambda: [
                    self.event_generate("<<QuitGame>>"),
                    on_closing()
                ],
                **button_style
            ).pack(pady=5)
            
            self._active_popups.append(pause_window)
            
        except Exception as e:
            logging.error(f"Error showing pause menu: {str(e)}")

    def update_game_view(self, dungeon: Any, player: Any) -> None:
        """
        Update the game view.
        
        Args:
            dungeon: The current dungeon
            player: The player character
        """
        try:
            if self.current_frame:
                self.current_frame.update_game_view(dungeon, player)
                
        except Exception as e:
            logging.error(f"Error updating game view: {str(e)}")

    def update_stats_view(self, player: Any) -> None:
        """
        Update the stats view.
        
        Args:
            player: The player character
        """
        try:
            self._player = player
            if self.current_frame and hasattr(self.current_frame, 'update_stats_view'):
                self.current_frame.update_stats_view(player)
                
        except Exception as e:
            logging.error(f"Error updating stats: {str(e)}")

    def show_inventory_ui(self, player: Any) -> None:
        """
        Show the inventory user interface.
        
        Args:
            player: The player character
        """
        try:
            if isinstance(self.current_frame, GameFrame):
                self.current_frame.show_inventory_ui(player)
                self.rebind_movement_keys()
                
        except Exception as e:
            logging.error(f"Error showing inventory UI: {str(e)}")

    def show_merchant_ui(self, player: Any, merchant: Any) -> None:
        """
        Show the merchant user interface.
        
        Args:
            player: The player character
            merchant: The merchant NPC
        """
        try:
            if isinstance(self.current_frame, GameFrame):
                self.current_frame.show_merchant_ui(player, merchant)
                self.rebind_movement_keys()
                
        except Exception as e:
            logging.error(f"Error showing merchant UI: {str(e)}")

    def handle_error(self, error: Exception, operation: str) -> None:
        """
        Handle errors in the game window.
        
        Args:
            error: The exception that occurred
            operation: Description of the operation that failed
        """
        logging.error(f"Error during {operation}: {str(error)}")
        messagebox.showerror(
            "Error",
            f"An error occurred during {operation}.\nPlease try again or restart the game."
        )

class GameFrame(ttk.Frame):
    """The main game frame class."""

    def __init__(self, master: tk.Tk):
        """Initialize the game frame."""
        try:
            super().__init__(master, style='Game.TFrame')
            self._setup_ui()
            self._bind_events()
            
            self._popup_windows: List[tk.Toplevel] = []
            
            logging.info("Game frame initialized")
            
        except Exception as e:
            logging.error(f"Error initializing game frame: {str(e)}")
            raise
            
    def _setup_ui(self) -> None:
        """Set up the user interface for the game frame."""
        try:
            # Main game view area
            self._game_view = ttk.Frame(self, style='Game.TFrame')
            self._game_view.pack(side='left', expand=True, fill='both')

            # Sidebar for stats and inventory
            self._sidebar = ttk.Frame(self, style='Game.TFrame', width=250)
            self._sidebar.pack(side='right', fill='y')
            self._sidebar.pack_propagate(False)

            # Set up UI components
            self._setup_equipment_display()
            self._setup_stats_view()
            self._setup_inventory_view()
            self._setup_action_buttons()
            
            logging.debug("Game frame UI setup complete")
            
        except Exception as e:
            logging.error(f"Error setting up game frame UI: {str(e)}")
            raise
            
    def _setup_equipment_display(self) -> None:
        """Set up the equipment display in the sidebar."""
        try:
            self._equipment_frame = ttk.LabelFrame(
                self._sidebar,
                text="Equipment",
                style='Game.TFrame',
                padding=5
            )
            self._equipment_frame.pack(fill='x', padx=5, pady=5)
        
            self._equipment_labels = {}
            for slot in ['Weapon', 'Armor', 'Shield']:
                self._equipment_labels[slot] = ttk.Label(
                    self._equipment_frame,
                    style='Equipment.TLabel',
                    text=f"{slot}: None"
                )
                self._equipment_labels[slot].pack(fill='x', pady=1)
                
        except Exception as e:
            logging.error(f"Error setting up equipment display: {str(e)}")
            raise
            
    def _setup_stats_view(self) -> None:
        """Set up the stats view in the sidebar."""
        try:
            self._stats_frame = ttk.LabelFrame(
                self._sidebar,
                text="Character Stats",
                style='Game.TFrame',
                padding=5
            )
            self._stats_frame.pack(fill='x', padx=5, pady=5)
            
            self._stats_labels = {}
            stats = ['Name', 'Title', 'Level', 'Health', 'Attack', 'Defense', 'XP', 'Money']
            
            for stat in stats:
                self._stats_labels[stat] = ttk.Label(
                    self._stats_frame,
                    style='Game.TLabel',
                    padding=(5, 2)
                )
                self._stats_labels[stat].pack(anchor='w', padx=5)
                
        except Exception as e:
            logging.error(f"Error setting up stats view: {str(e)}")
            raise
            
    def _setup_inventory_view(self) -> None:
        """Set up the inventory view in the sidebar."""
        try:
            self._inventory_frame = ttk.LabelFrame(
                self._sidebar,
                text="Inventory",
                style='Game.TFrame',
                padding=5
            )
            self._inventory_frame.pack(fill='x', padx=5, pady=5)
            
            # Create inventory list with scrollbar
            list_frame = ttk.Frame(self._inventory_frame)
            list_frame.pack(fill='both', expand=True)
            
            scrollbar = ttk.Scrollbar(list_frame)
            scrollbar.pack(side='right', fill='y')
            
            self._inventory_list = tk.Listbox(
                list_frame,
                bg='black',
                fg='white',
                selectmode=tk.SINGLE,
                height=8,
                yscrollcommand=scrollbar.set
            )
            self._inventory_list.pack(fill='both', expand=True)
            scrollbar.config(command=self._inventory_list.yview)
            
        except Exception as e:
            logging.error(f"Error setting up inventory view: {str(e)}")
            raise
            
    def _setup_action_buttons(self) -> None:
        """Set up the action buttons in the sidebar."""
        try:
            button_frame = ttk.Frame(self._sidebar, style='Game.TFrame')
            button_frame.pack(fill='x', pady=5)
            
            # Create action buttons with consistent styling
            button_style = {'width': 20, 'padding': 5}
            
            ttk.Button(
                button_frame,
                text="Save (Ctrl+S)",
                command=lambda: self.event_generate("<<SaveGame>>"),
                **button_style
            ).pack(fill='x', padx=5, pady=2)
            
            ttk.Button(
                button_frame,
                text="Inventory (I)",
                command=lambda: self.event_generate("<<ToggleInventory>>"),
                **button_style
            ).pack(fill='x', padx=5, pady=2)
            
        except Exception as e:
            logging.error(f"Error setting up action buttons: {str(e)}")
            raise
            
    def _bind_events(self) -> None:
        """Bind events for the game frame."""
        try:
            self._inventory_list.bind('<Double-Button-1>', self._handle_inventory_click)
            self._inventory_list.bind('<Button-3>', self._handle_inventory_click)
            
        except Exception as e:
            logging.error(f"Error binding events: {str(e)}")
            
    def update_game_view(self, dungeon: Any, player: Any) -> None:
        """
        Update the game view with current dungeon state.
        
        Args:
            dungeon: The current dungeon
            player: The player character
        """
        try:
            # Clear existing view
            for widget in self._game_view.winfo_children():
                widget.destroy()

            # Create game canvas
            canvas = tk.Canvas(
                self._game_view,
                bg='black',
                width=800,
                height=800
            )
            canvas.pack(expand=True)

            # Calculate view parameters
            room_size = 80
            player_x, player_y = dungeon.player_pos
            offset_x = 400 - player_x * room_size
            offset_y = 400 - player_y * room_size

            # Draw visible rooms
            view_range = 4
            for y in range(max(0, player_y - view_range), min(dungeon.size, player_y + view_range + 1)):
                for x in range(max(0, player_x - view_range), min(dungeon.size, player_x + view_range + 1)):
                    room = dungeon.get_room_at(x, y)
                    if room and room.is_visible:
                        self._draw_room(canvas, x, y, room, room_size, offset_x, offset_y)

            # Draw player
            self._draw_player(canvas, player_x, player_y, room_size, offset_x, offset_y)
            
            logging.debug("Game view updated")
            
        except Exception as e:
            logging.error(f"Error updating game view: {str(e)}")
            
    def _draw_room(self, canvas: tk.Canvas, x: int, y: int, room: Any, 
                  size: int, offset_x: int, offset_y: int) -> None:
        """
        Draw a single room on the game canvas.
        
        Args:
            canvas: The game canvas
            x: Room X coordinate
            y: Room Y coordinate
            room: The room object
            size: Size of room in pixels
            offset_x: X offset for drawing
            offset_y: Y offset for drawing
        """
        try:
            # Calculate room coordinates
            x1 = x * size + offset_x
            y1 = y * size + offset_y
            x2 = x1 + size
            y2 = y1 + size

            # Draw room background
            canvas.create_rectangle(
                x1, y1, x2, y2,
                fill='gray20',
                outline='white',
                width=2
            )

            # Draw doors and walls
            self._draw_room_doors(canvas, x1, y1, x2, y2, size, room)
            
            # Draw room contents
            center_x = x1 + size//2
            center_y = y1 + size//2
            
            self._draw_room_contents(canvas, center_x, center_y, room)
            
        except Exception as e:
            logging.error(f"Error drawing room at ({x}, {y}): {str(e)}")
            
    def _draw_room_doors(self, canvas: tk.Canvas, x1: int, y1: int,
                        x2: int, y2: int, size: int, room: Any) -> None:
        """
        Draw the doors and walls of a room.
        
        Args:
            canvas: The game canvas
            x1, y1: Top-left coordinates
            x2, y2: Bottom-right coordinates
            size: Room size
            room: The room object
        """
        try:
            wall_width = 8
            door_color = 'brown'
            wall_color = 'white'
            
            # North door/wall
            if room.doors['north']:
                canvas.create_rectangle(
                    x1 + size//3, y1-2,
                    x2 - size//3, y1+2,
                    fill=door_color,
                    outline=wall_color
                )
            else:
                canvas.create_line(
                    x1, y1, x2, y1,
                    fill=wall_color,
                    width=wall_width
                )

            # South door/wall
            if room.doors['south']:
                canvas.create_rectangle(
                    x1 + size//3, y2-2,
                    x2 - size//3, y2+2,
                    fill=door_color,
                    outline=wall_color
                )
            else:
                canvas.create_line(
                    x1, y2, x2, y2,
                    fill=wall_color,
                    width=wall_width
                )

            # East door/wall
            if room.doors['east']:
                canvas.create_rectangle(
                    x2-2, y1 + size//3,
                    x2+2, y2 - size//3,
                    fill=door_color,
                    outline=wall_color
                )
            else:
                canvas.create_line(
                    x2, y1, x2, y2,
                    fill=wall_color,
                    width=wall_width
                )

            # West door/wall
            if room.doors['west']:
                canvas.create_rectangle(
                    x1-2, y1 + size//3,
                    x1+2, y2 - size//3,
                    fill=door_color,
                    outline=wall_color
                )
            else:
                canvas.create_line(
                    x1, y1, x1, y2,
                    fill=wall_color,
                    width=wall_width
                )
                
        except Exception as e:
            logging.error(f"Error drawing room doors: {str(e)}")
            
    def _draw_room_contents(self, canvas: tk.Canvas, center_x: int, center_y: int, room: Any) -> None:
        """
        Draw the contents of a room.
        
        Args:
            canvas: The game canvas
            center_x: X coordinate of room center
            center_y: Y coordinate of room center
            room: The room object
        """
        try:
            # Draw enemies
            if room.enemies:
                canvas.create_text(
                    center_x, center_y-10,
                    text='E',
                    fill='red',
                    font=('Arial', 16, 'bold')
                )

            # Draw treasure
            if room.has_treasure and not room.treasure_looted:
                canvas.create_text(
                    center_x, center_y,
                    text='T',
                    fill='yellow',
                    font=('Arial', 16, 'bold')
                )

            # Draw merchant
            if room.has_merchant and not room.merchant_visited:
                canvas.create_text(
                    center_x, center_y,
                    text='M',
                    fill='green',
                    font=('Arial', 16, 'bold')
                )

            # Draw cleared room indicator
            if room.is_cleared:
                canvas.create_text(
                    center_x+15, center_y-15,
                    text='✓',
                    fill='green',
                    font=('Arial', 16, 'bold')
                )

            # Draw end room indicator
            if room.is_end_room:
                canvas.create_text(
                    center_x, center_y+15,
                    text='N',
                    fill='purple',
                    font=('Arial', 16, 'bold')
                )
                
        except Exception as e:
            logging.error(f"Error drawing room contents: {str(e)}")
            
    def _draw_player(self, canvas: tk.Canvas, x: int, y: int, size: int, 
                    offset_x: int, offset_y: int) -> None:
        """
        Draw the player character on the game canvas.
        
        Args:
            canvas: The game canvas
            x: Player X coordinate
            y: Player Y coordinate
            size: Room size
            offset_x: X drawing offset
            offset_y: Y drawing offset
        """
        try:
            player_screen_x = x * size + offset_x + size//2
            player_screen_y = y * size + offset_y + size//2
            radius = 8
            
            canvas.create_oval(
                player_screen_x-radius, player_screen_y-radius,
                player_screen_x+radius, player_screen_y+radius,
                fill='green',
                outline='white',
                width=2
            )
            
        except Exception as e:
            logging.error(f"Error drawing player: {str(e)}")
            
    def update_stats_view(self, player: Any) -> None:
        """
        Update the stats view with current player stats.
        
        Args:
            player: The player character
        """
        try:
            # Update basic stats
            stats = {
                'Name': f"Name: {player.name}",
                'Title': f"Title: {player.title}",
                'Level': f"Level: {player.tier}",
                'Health': f"Health: {player.current_health}/{player.max_health}",
                'Attack': f"Attack: {player.calculate_total_attack()}",
                'Defense': f"Defense: {player.calculate_total_defense()}",
                'XP': f"XP: {player.xp}",
                'Money': f"Money: {player.money} copper"
            }
            
            for stat_name, stat_text in stats.items():
                if stat_name in self._stats_labels:
                    self._stats_labels[stat_name].config(text=stat_text)

            # Update equipment display
            self._update_equipment_display(player)

            # Update inventory list
            self._update_inventory_list(player)
            
        except Exception as e:
            logging.error(f"Error updating stats view: {str(e)}")
            
    def _update_equipment_display(self, player: Any) -> None:
        """
        Update the equipment display.
        
        Args:
            player: The player character
        """
        try:
            equipment_info = player.get_equipment_display()
            
            self._equipment_labels['Weapon'].config(
                text=f"Weapon: {equipment_info['weapon']}"
            )
            self._equipment_labels['Armor'].config(
                text=f"Armor: {equipment_info['armor']}"
            )
            self._equipment_labels['Shield'].config(
                text=f"Shield: {equipment_info['shield']}"
            )
            
        except Exception as e:
            logging.error(f"Error updating equipment display: {str(e)}")
            
    def _update_inventory_list(self, player: Any) -> None:
        """
        Update the inventory list display.
        
        Args:
            player: The player character
        """
        try:
            self._inventory_list.delete(0, tk.END)
            
            for item in player.inventory:
                display_text = item['name']
                
                # Add effect information for consumables
                if item['type'] == 'consumable':
                    if 'effect' in item and item['effect'].startswith('heal_'):
                        try:
                            heal_amount = int(item['effect'].split('_')[1])
                            display_text += f" (Heal: {heal_amount})"
                        except (ValueError, IndexError):
                            pass
                            
                self._inventory_list.insert(tk.END, display_text)
                
        except Exception as e:
            logging.error(f"Error updating inventory list: {str(e)}")
            
    def _handle_inventory_click(self, event: tk.Event) -> None:
        """
        Handle inventory click events.
        
        Args:
            event: The triggering event
        """
        try:
            selection = self._inventory_list.curselection()
            if not selection:
                return
                
            index = selection[0]
            item_name = self._inventory_list.get(index)
            
            popup = tk.Menu(self, tearoff=0)
            
            # Find selected item in inventory
            selected_item = None
            for item in self.master._player.inventory:
                if item['name'] == item_name.split(' (')[0]:
                    selected_item = item
                    break
                    
            if selected_item:
                if selected_item['type'] == 'consumable':
                    popup.add_command(
                        label="Use",
                        command=lambda: self._use_item(
                            self.master._player,
                            selected_item,
                            None
                        )
                    )
                elif selected_item['type'] in ['weapon', 'armor', 'shield']:
                    popup.add_command(
                        label="Equip",
                        command=lambda: self._equip_item(
                            self.master._player,
                            selected_item,
                            None
                        )
                    )
                
                popup.tk_popup(event.x_root, event.y_root)
                popup.grab_release()
                
        except Exception as e:
            logging.error(f"Error handling inventory click: {str(e)}")
            
    def show_inventory_ui(self, player: Any) -> None:
        """
        Show the inventory user interface.
        
        Args:
            player: The player character
        """
        try:
            inventory_window = tk.Toplevel(self)
            inventory_window.title("Inventory")
            inventory_window.geometry("600x400")
            inventory_window.transient(self)
            inventory_window.grab_set()

            def on_closing():
                try:
                    inventory_window.grab_release()
                    self.master.focus_force()
                    inventory_window.destroy()
                except:
                    pass

            inventory_window.protocol("WM_DELETE_WINDOW", on_closing)

            # Equipment section
            equipment_frame = ttk.LabelFrame(
                inventory_window,
                text="Equipment",
                padding=10
            )
            equipment_frame.pack(fill='x', padx=5, pady=5)
            
            equipment_info = player.get_equipment_display()
            ttk.Label(equipment_frame, text=f"Weapon: {equipment_info['weapon']}").pack(anchor='w')
            ttk.Label(equipment_frame, text=f"Armor: {equipment_info['armor']}").pack(anchor='w')
            ttk.Label(equipment_frame, text=f"Shield: {equipment_info['shield']}").pack(anchor='w')

            # Inventory section
            self._create_inventory_section(inventory_window, player)

            # Add close button
            ttk.Button(
                inventory_window,
                text="Close",
                command=on_closing
            ).pack(pady=10)
            
        except Exception as e:
            logging.error(f"Error showing inventory UI: {str(e)}")

    def _create_inventory_section(self, parent: tk.Toplevel, player: Any) -> None:
        """
        Create the inventory section of the inventory window.
        
        Args:
            parent: Parent window
            player: The player character
        """
        try:
            inventory_frame = ttk.LabelFrame(
                parent,
                text="Items",
                padding=10
            )
            inventory_frame.pack(fill='both', expand=True, padx=5, pady=5)

            # Create scrollable frame
            canvas = tk.Canvas(inventory_frame)
            scrollbar = ttk.Scrollbar(
                inventory_frame,
                orient="vertical",
                command=canvas.yview
            )
            scrollable_frame = ttk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            # Populate inventory items
            for item in player.inventory:
                self._create_item_entry(scrollable_frame, player, item)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
        
        except Exception as e:
            logging.error(f"Error creating inventory section: {str(e)}")

    def _create_item_entry(self, parent: ttk.Frame, player: Any, item: Dict) -> None:
        """
        Create an entry for a single inventory item.
        
        Args:
            parent: Parent frame
            player: The player character
            item: The item to display
        """
        try:
            item_frame = ttk.Frame(parent)
            item_frame.pack(fill='x', padx=5, pady=2)
            
            # Item name and stats
            info_text = f"{item['name']}"
            if item['type'] == 'weapon':
                info_text += f" (DMG: {item['base_damage_min']}-{item['base_damage_max']})"
            elif item['type'] in ['armor', 'shield']:
                info_text += f" (DEF: {item['base_defense']})"
            elif item['type'] == 'consumable' and 'effect' in item:
                if item['effect'].startswith('heal_'):
                    heal_amount = int(item['effect'].split('_')[1])
                    info_text += f" (Heals {heal_amount} HP)"
                
            ttk.Label(item_frame, text=info_text).pack(side='left')
            
            # Action buttons based on item type
            if item['type'] in ['weapon', 'armor', 'shield']:
                ttk.Button(
                    item_frame,
                    text="Equip",
                    command=lambda: self._equip_item(player, item, parent.winfo_toplevel())
                ).pack(side='right')
            elif item['type'] == 'consumable':
                ttk.Button(
                    item_frame,
                    text="Use",
                    command=lambda: self._use_item(player, item, parent.winfo_toplevel())
                ).pack(side='right')
                
        except Exception as e:
            logging.error(f"Error creating item entry: {str(e)}")

    def show_merchant_ui(self, player: Any, merchant: Any) -> None:
        """
        Show the merchant user interface.
        
        Args:
            player: The player character
            merchant: The merchant NPC
        """
        try:
            merchant_window = tk.Toplevel(self)
            merchant_window.title("Merchant")
            merchant_window.geometry("800x600")
            merchant_window.transient(self)
            merchant_window.grab_set()

            def on_closing():
                try:
                    merchant_window.grab_release()
                    self.master.focus_force()
                    
                    # Mark merchant as visited
                    if self.master.current_dungeon:
                        current_room = self.master.current_dungeon.get_current_room()
                        if current_room:
                            current_room.merchant_visited = True
                            
                    merchant_window.destroy()
                except:
                    pass

            merchant_window.protocol("WM_DELETE_WINDOW", on_closing)

            # Create main container
            self._create_merchant_interface(merchant_window, player, merchant)

            # Add close button
            ttk.Button(
                merchant_window,
                text="Close",
                command=on_closing
            ).pack(pady=10)
            
        except Exception as e:
            logging.error(f"Error showing merchant UI: {str(e)}")

    def _create_merchant_interface(self, window: tk.Toplevel, player: Any, merchant: Any) -> None:
        """
        Create the merchant interface.
        
        Args:
            window: Parent window
            player: The player character
            merchant: The merchant NPC
        """
        try:
            # Main container with two sides
            container = ttk.Frame(window)
            container.pack(fill='both', expand=True, padx=10, pady=10)

            # Merchant inventory side
            merchant_frame = ttk.LabelFrame(
                container,
                text="Merchant's Goods",
                padding=10
            )
            merchant_frame.pack(side='left', fill='both', expand=True)

            # Create notebook for categorized items
            item_notebook = ttk.Notebook(merchant_frame)
            item_notebook.pack(fill='both', expand=True)

            # Create pages for each item type
            item_types = merchant.get_available_types()
            type_frames = {}

            for item_type in item_types:
                frame = ttk.Frame(item_notebook)
                item_notebook.add(frame, text=item_type.capitalize())
                type_frames[item_type] = frame

                # Add scrollable frame for each type
                self._create_merchant_item_list(
                    frame,
                    merchant.get_inventory_by_type(item_type),
                    player,
                    merchant,
                    window
                )

            # Player inventory side
            player_frame = self._create_player_inventory_section(
                container,
                player,
                merchant,
                window
            )
            
        except Exception as e:
            logging.error(f"Error creating merchant interface: {str(e)}")

    def _create_merchant_item_list(self, parent: ttk.Frame, items: List[Dict],
                                player: Any, merchant: Any, window: tk.Toplevel) -> None:
        """
        Create scrollable list of merchant items.
        
        Args:
            parent: Parent frame
            items: List of items to display
            player: The player character
            merchant: The merchant NPC
            window: Parent window
        """
        try:
            canvas = tk.Canvas(parent)
            scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            # Add items
            for item in items:
                item_frame = ttk.Frame(scrollable_frame)
                item_frame.pack(fill='x', pady=2)
                
                # Item info
                info_text = self._get_item_display_text(item)
                ttk.Label(item_frame, text=info_text).pack(side='left')
                ttk.Label(item_frame, text=f"{item['price_copper']} copper").pack(side='left', padx=10)
                
                # Buy button
                buy_button = ttk.Button(
                    item_frame,
                    text="Buy",
                    command=lambda i=item: self._handle_buy(player, merchant, i, window)
                )
                buy_button.pack(side='right')
                
                # Disable buy button if player can't afford it
                if player.money < item['price_copper']:
                    buy_button.config(state='disabled')

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
        except Exception as e:
            logging.error(f"Error creating merchant item list: {str(e)}")

    def _create_player_inventory_section(self, parent: ttk.Frame, player: Any,
                                    merchant: Any, window: tk.Toplevel) -> ttk.Frame:
        """
        Create the player's inventory section of merchant UI.
        
        Args:
            parent: Parent frame
            player: The player character
            merchant: The merchant NPC
            window: Parent window
            
        Returns:
            The created frame
        """
        try:
            player_frame = ttk.LabelFrame(parent, text="Your Inventory", padding=10)
            player_frame.pack(side='right', fill='both', expand=True)

            # Player money display
            money_frame = ttk.Frame(player_frame)
            money_frame.pack(fill='x', pady=5)
            ttk.Label(
                money_frame,
                text="Your Money:",
                font=('Arial', 10, 'bold')
            ).pack(side='left')
            ttk.Label(
                money_frame,
                text=f"{player.money} copper"
            ).pack(side='left', padx=5)

            # Scrollable inventory
            canvas = tk.Canvas(player_frame)
            scrollbar = ttk.Scrollbar(player_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            # Add player items
            for item in player.inventory:
                item_frame = ttk.Frame(scrollable_frame)
                item_frame.pack(fill='x', pady=2)
                
                sell_value = merchant.get_item_value(item)
                ttk.Label(
                    item_frame,
                    text=f"{item['name']} (Sell: {sell_value} copper)"
                ).pack(side='left')
                
                ttk.Button(
                    item_frame,
                    text="Sell",
                    command=lambda i=item: self._handle_sell(player, merchant, i, window)
                ).pack(side='right')

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

            return player_frame
            
        except Exception as e:
            logging.error(f"Error creating player inventory section: {str(e)}")
            return ttk.Frame(parent)  # Return empty frame on error

    def _get_item_display_text(self, item: Dict) -> str:
        """
        Get formatted display text for an item.
        
        Args:
            item: The item to display
            
        Returns:
            Formatted item description
        """
        try:
            info_text = f"{item['name']}"
            
            if item['type'] == 'weapon':
                info_text += f" (DMG: {item['base_damage_min']}-{item['base_damage_max']})"
            elif item['type'] in ['armor', 'shield']:
                info_text += f" (DEF: {item['base_defense']})"
            elif item['type'] == 'consumable' and 'effect' in item:
                if item['effect'].startswith('heal_'):
                    heal_amount = int(item['effect'].split('_')[1])
                    info_text += f" (Heals {heal_amount} HP)"
                    
            return info_text
            
        except Exception as e:
            logging.error(f"Error getting item display text: {str(e)}")
            return str(item.get('name', 'Unknown Item'))

    def _handle_buy(self, player: Any, merchant: Any, item: Dict, window: tk.Toplevel) -> None:
        """
        Handle buying an item from the merchant.
        
        Args:
            player: The player character
            merchant: The merchant NPC
            item: The item being bought
            window: Parent window
        """
        try:
            if player.money < item['price_copper']:
                messagebox.showwarning("Cannot Buy", "You don't have enough money!")
                return
                
            if merchant.buy_item(player, item['name']):
                self.update_stats_view(player)
                window.grab_release()
                self.master.focus_force()
                window.destroy()
                self.show_merchant_ui(player, merchant)
                messagebox.showinfo("Purchase Successful", f"You bought {item['name']}!")
            else:
                messagebox.showerror("Error", "Failed to complete purchase!")
                
        except Exception as e:
            logging.error(f"Error handling buy: {str(e)}")
            messagebox.showerror("Error", "Failed to complete purchase!")

    def _handle_sell(self, player: Any, merchant: Any, item: Dict, window: tk.Toplevel) -> None:
        """
        Handle selling an item to the merchant.
        
        Args:
            player: The player character
            merchant: The merchant NPC
            item: The item being sold
            window: Parent window
        """
        try:
            sell_confirmation = messagebox.askyesno(
                "Confirm Sale",
                f"Are you sure you want to sell {item['name']} for {merchant.get_item_value(item)} copper?"
            )
            
            if not sell_confirmation:
                return
                
            if merchant.sell_item(player, item):
                self.update_stats_view(player)
                window.grab_release()
                self.master.focus_force()
                window.destroy()
                self.show_merchant_ui(player, merchant)
                messagebox.showinfo("Sale Successful", f"You sold {item['name']}!")
            else:
                messagebox.showerror("Error", "Failed to complete sale!")
                
        except Exception as e:
            logging.error(f"Error handling sell: {str(e)}")
            messagebox.showerror("Error", "Failed to complete sale!")

    def _equip_item(self, player: Any, item: Dict, window: Optional[tk.Toplevel]) -> None:
        """
        Handle equipping items.
        
        Args:
            player: The player character
            item: The item to equip
            window: Optional parent window to refresh
        """
        try:
            if player.equip_item(item):
                self.update_stats_view(player)
                if window:
                    window.grab_release()
                    self.master.focus_force()
                    window.destroy()
                    self.show_inventory_ui(player)
                    
        except Exception as e:
            logging.error(f"Error equipping item: {str(e)}")

    def _use_item(self, player: Any, item: Dict, window: Optional[tk.Toplevel]) -> None:
            """
            Handle using items.
            
            Args:
                player: The player character
                item: The item to use
                window: Optional parent window to refresh
            """
            try:
                if item['type'] == 'consumable' and player.use_healing_potion(item):
                    self.update_stats_view(player)
                    if window:
                        window.grab_release()
                        self.master.focus_force()
                        window.destroy()
                        self.show_inventory_ui(player)
                        
            except Exception as e:
                logging.error(f"Error using item: {str(e)}")