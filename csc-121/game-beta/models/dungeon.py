# dungeon.py
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Any, Optional, Set
import random
import math
import logging
from database import Database
from models.enemy import Enemy
from models.merchant import Merchant
from config import ENEMY_SPAWN_CHANCE
import copy

@dataclass
class Room:
    """
    Represents a single room in the dungeon.
    """
    enemies: List[Enemy] = field(default_factory=list)
    items: List[Dict] = field(default_factory=list)
    is_cleared: bool = False
    is_visible: bool = False
    has_merchant: bool = False
    merchant_visited: bool = False
    has_treasure: bool = False
    treasure_looted: bool = False
    is_end_room: bool = False
    doors: Dict[str, bool] = field(default_factory=lambda: {
        'north': False, 'south': False, 'east': False, 'west': False
    })

    def has_enemy(self) -> bool:
        """Check if the room has any enemies."""
        return bool(self.enemies)

    def get_enemy(self) -> Optional[Enemy]:
        """Get the first enemy in the room."""
        return self.enemies[0] if self.enemies else None

    def to_dict(self) -> Dict[str, Any]:
        """Convert the room to a dictionary for saving."""
        try:
            return {
                'enemies': [enemy.to_dict() for enemy in self.enemies],
                'items': [item.copy() for item in self.items],
                'is_cleared': self.is_cleared,
                'is_visible': self.is_visible,
                'has_merchant': self.has_merchant,
                'merchant_visited': self.merchant_visited,
                'has_treasure': self.has_treasure,
                'treasure_looted': self.treasure_looted,
                'is_end_room': self.is_end_room,
                'doors': self.doors.copy()
            }
        except Exception as e:
            logging.error(f"Error converting room to dict: {str(e)}")
            raise

class Dungeon:
    """
    Represents a dungeon with rooms, enemies, and treasures.
    """
    def __init__(self, tier: int, size: int = 10, player_pos: tuple = None, rooms: list = None):
        """
        Initialize the dungeon.
        
        Args:
            tier: Dungeon difficulty tier
            size: Size of the dungeon grid
            player_pos: Starting player position
            rooms: Predefined rooms for loading saved dungeons
        """
        if tier < 1:
            raise ValueError("Tier must be at least 1")
        if size < 5:
            raise ValueError("Dungeon size must be at least 5x5")
            
        self._tier = tier
        self._size = size
        self._db = Database()
        
        # Handle player position loading
        if isinstance(player_pos, (list, tuple)) and len(player_pos) == 2:
            self._player_pos = (min(max(0, player_pos[0]), size-1), 
                              min(max(0, player_pos[1]), size-1))
        else:
            self._player_pos = (0, 0)
        
        try:
            if rooms:
                self._load_rooms(rooms)
            else:
                self._rooms = [[Room() for _ in range(size)] for _ in range(size)]
                self._generate_dungeon()
            
            logging.info(f"Generated tier {tier} dungeon of size {size}x{size}")
            
        except Exception as e:
            logging.error(f"Error initializing dungeon: {str(e)}")
            raise

    def _load_rooms(self, rooms_data: List[List[Dict]]) -> None:
        """Load rooms from saved data."""
        try:
            self._rooms = []
            for row in rooms_data:
                room_row = []
                for room_data in row:
                    enemies = []
                    for enemy_data in room_data.get('enemies', []):
                        if isinstance(enemy_data, dict):
                            try:
                                enemy = Enemy(**enemy_data)
                                enemies.append(enemy)
                            except Exception as e:
                                logging.error(f"Error creating enemy: {str(e)}")
                                continue
                    
                    items = [item.copy() for item in room_data.get('items', [])]
                    
                    room = Room(
                        enemies=enemies,
                        items=items,
                        is_cleared=room_data.get('is_cleared', False),
                        is_visible=room_data.get('is_visible', False),
                        has_merchant=room_data.get('has_merchant', False),
                        merchant_visited=room_data.get('merchant_visited', False),
                        has_treasure=room_data.get('has_treasure', False),
                        treasure_looted=room_data.get('treasure_looted', False),
                        is_end_room=room_data.get('is_end_room', False),
                        doors=room_data.get('doors', {
                            'north': False, 'south': False, 'east': False, 'west': False
                        }).copy()
                    )
                    room_row.append(room)
                self._rooms.append(room_row)
                
        except Exception as e:
            logging.error(f"Error loading rooms: {str(e)}")
            raise

    @property
    def player_pos(self) -> Tuple[int, int]:
        """Get the player's position."""
        return self._player_pos

    @property
    def size(self) -> int:
        """Get the dungeon size."""
        return self._size

    @property
    def rooms(self) -> List[List[Room]]:
        """Get the dungeon rooms."""
        return self._rooms

    def _generate_maze(self) -> None:
        """Generate the maze layout using depth-first search."""
        def carve_path(x: int, y: int, visited: Set[Tuple[int, int]]) -> None:
            visited.add((x, y))
            directions = [(0, 1, 'south', 'north'), (0, -1, 'north', 'south'),
                         (1, 0, 'east', 'west'), (-1, 0, 'west', 'east')]
            random.shuffle(directions)
            
            for dx, dy, dir1, dir2 in directions:
                new_x, new_y = x + dx, y + dy
                if (0 <= new_x < self._size and 0 <= new_y < self._size and 
                    (new_x, new_y) not in visited):
                    self._rooms[y][x].doors[dir1] = True
                    self._rooms[new_y][new_x].doors[dir2] = True
                    carve_path(new_x, new_y, visited)

        try:
            carve_path(0, 0, set())
        except Exception as e:
            logging.error(f"Error generating maze: {str(e)}")
            raise

    def _generate_dungeon(self) -> None:
        """Generate the complete dungeon."""
        try:
            self._generate_maze()
            self._populate_rooms()
            self._place_treasure_rooms()
            self._place_merchant()
            self._place_end_room()
            self._rooms[0][0].is_visible = True
            self._update_visibility()
        except Exception as e:
            logging.error(f"Error generating dungeon: {str(e)}")
            raise

    def _populate_rooms(self) -> None:
        """Populate rooms with enemies."""
        enemies_df = self._db.get_all_enemies_by_tier(self._tier)
        
        if enemies_df.empty:
            logging.warning(f"No enemies found for tier {self._tier}")
            return

        try:
            for y in range(self._size):
                for x in range(self._size):
                    if ((x, y) != (0, 0) and  # Skip starting room
                        random.random() < ENEMY_SPAWN_CHANCE):
                        enemy = Enemy.get_random_enemy(self._tier)
                        if enemy:
                            self._rooms[y][x].enemies.append(enemy)
        except Exception as e:
            logging.error(f"Error populating rooms: {str(e)}")

    def _place_treasure_rooms(self) -> None:
        """Place treasure rooms in the dungeon."""
        try:
            num_treasures = random.randint(1, self._tier)
            empty_rooms = [
                (x, y) for x in range(self._size) for y in range(self._size)
                if (x, y) != (0, 0) and not self._rooms[y][x].enemies
            ]
            
            if empty_rooms:
                for _ in range(num_treasures):
                    if not empty_rooms:
                        break
                    x, y = empty_rooms.pop(random.randrange(len(empty_rooms)))
                    self._rooms[y][x].has_treasure = True
                    logging.info(f"Placed treasure room at ({x}, {y})")
                    
        except Exception as e:
            logging.error(f"Error placing treasure rooms: {str(e)}")

    def _place_merchant(self) -> None:
        """Place a merchant in the dungeon."""
        try:
            empty_rooms = [
                (x, y) for x in range(self._size) for y in range(self._size)
                if (x, y) != (0, 0) and not self._rooms[y][x].enemies 
                and not self._rooms[y][x].has_treasure
            ]
            
            if empty_rooms:
                x, y = random.choice(empty_rooms)
                self._rooms[y][x].has_merchant = True
                logging.info(f"Placed merchant at ({x}, {y})")
                
        except Exception as e:
            logging.error(f"Error placing merchant: {str(e)}")

    def _place_end_room(self) -> None:
        """Place the end room in the dungeon."""
        try:
            farthest_room = None
            max_distance = 0
            
            for y in range(self._size):
                for x in range(self._size):
                    distance = self._calculate_manhattan_distance((x, y), self._player_pos)
                    if distance > max_distance:
                        max_distance = distance
                        farthest_room = (x, y)
            
            if farthest_room:
                x, y = farthest_room
                self._rooms[y][x].is_end_room = True
                logging.info(f"Placed end room at ({x}, {y})")
                
        except Exception as e:
            logging.error(f"Error placing end room: {str(e)}")

    def _calculate_manhattan_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        """Calculate Manhattan distance between two points."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

    def move_player(self, direction: str) -> bool:
        """
        Move player in the specified direction.
        
        Args:
            direction: Direction to move ('north', 'south', 'east', 'west')
            
        Returns:
            bool: Whether the movement was successful
        """
        try:
            current_room = self.get_current_room()
            if not current_room.doors.get(direction, False):
                return False

            direction_map = {
                'north': (0, -1),
                'south': (0, 1),
                'east': (1, 0),
                'west': (-1, 0)
            }
            
            if direction not in direction_map:
                return False

            dx, dy = direction_map[direction]
            new_x = self._player_pos[0] + dx
            new_y = self._player_pos[1] + dy

            if 0 <= new_x < self._size and 0 <= new_y < self._size:
                self._player_pos = (new_x, new_y)
                self._update_visibility()
                logging.info(f"Player moved to position {self._player_pos}")
                return True
                
            return False
            
        except Exception as e:
            logging.error(f"Error moving player: {str(e)}")
            return False

    def move_player_random_adjacent(self) -> bool:
        """Move player to a random adjacent room."""
        try:
            current_room = self.get_current_room()
            available_directions = [
                dir for dir, has_door in current_room.doors.items() 
                if has_door
            ]
            
            if not available_directions:
                return False
                
            direction = random.choice(available_directions)
            return self.move_player(direction)
            
        except Exception as e:
            logging.error(f"Error moving player randomly: {str(e)}")
            return False

    def get_current_room(self) -> Room:
        """Get the room the player is currently in."""
        try:
            return self._rooms[self._player_pos[1]][self._player_pos[0]]
        except IndexError:
            logging.error(f"Invalid player position: {self._player_pos}")
            raise

    def _update_visibility(self) -> None:
        """Update room visibility using circular visibility."""
        try:
            x, y = self._player_pos
            view_range = 4
            for dy in range(-view_range, view_range + 1):
                for dx in range(-view_range, view_range + 1):
                    if (dx*dx + dy*dy) <= view_range*view_range:  # Circular visibility
                        new_x, new_y = x + dx, y + dy
                        if 0 <= new_x < self._size and 0 <= new_y < self._size:
                            self._rooms[new_y][new_x].is_visible = True
                            
        except Exception as e:
            logging.error(f"Error updating visibility: {str(e)}")

    def get_treasure_loot(self) -> List[Any]:
        """Generate treasure room loot."""
        loot = []
        try:
            base_money = 100 * self._tier
            bonus_money = random.randint(0, base_money)
            loot.append(('copper', base_money + bonus_money))
            
            num_items = random.randint(2, 3 + self._tier)
            max_tier = min(self._tier + 2, 6)
            items_df = self._db.get_all_items_by_tier(max_tier)
            
            if not items_df.empty:
                selected_items = items_df.sample(n=min(num_items, len(items_df)))
                loot.extend(selected_items['name'].tolist())
                
            logging.info(f"Generated treasure loot: {loot}")
            
        except Exception as e:
            logging.error(f"Error generating treasure loot: {str(e)}")
            
        return loot

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the dungeon to a dictionary for saving.
        
        Returns:
            Dict containing all dungeon data
        
        Raises:
            Exception: If there's an error during conversion
        """
        try:
            return {
                'tier': self._tier,
                'size': self._size,
                'player_pos': self._player_pos,
                'rooms': [[room.to_dict() for room in row] for row in self._rooms]
            }
        except Exception as e:
            logging.error(f"Error converting dungeon to dict: {str(e)}")
            raise

    def validate_position(self, x: int, y: int) -> bool:
        """
        Validate if a position is within dungeon bounds.
        
        Args:
            x: X coordinate to validate
            y: Y coordinate to validate
            
        Returns:
            bool: Whether the position is valid
        """
        return 0 <= x < self._size and 0 <= y < self._size

    def get_room_at(self, x: int, y: int) -> Optional[Room]:
        """
        Get room at specific coordinates with validation.
        
        Args:
            x: X coordinate of room
            y: Y coordinate of room
            
        Returns:
            Room if coordinates are valid, None otherwise
        """
        try:
            if self.validate_position(x, y):
                return self._rooms[y][x]
            return None
        except Exception as e:
            logging.error(f"Error getting room at ({x}, {y}): {str(e)}")
            return None

    def get_adjacent_rooms(self, x: int, y: int) -> List[Tuple[str, Room]]:
        """
        Get all adjacent rooms with their directions.
        
        Args:
            x: X coordinate of current room
            y: Y coordinate of current room
            
        Returns:
            List of tuples containing (direction, Room)
        """
        adjacent_rooms = []
        directions = {
            'north': (0, -1),
            'south': (0, 1),
            'east': (1, 0),
            'west': (-1, 0)
        }
        
        try:
            current_room = self.get_room_at(x, y)
            if not current_room:
                return []

            for direction, (dx, dy) in directions.items():
                new_x, new_y = x + dx, y + dy
                if (self.validate_position(new_x, new_y) and 
                    current_room.doors.get(direction, False)):
                    adjacent_room = self.get_room_at(new_x, new_y)
                    if adjacent_room:
                        adjacent_rooms.append((direction, adjacent_room))
                        
            return adjacent_rooms
            
        except Exception as e:
            logging.error(f"Error getting adjacent rooms: {str(e)}")
            return []

    def calculate_path_to_end(self) -> Optional[List[Tuple[int, int]]]:
        """
        Calculate shortest path to end room using A* algorithm.
        
        Returns:
            List of coordinates forming path to end room, or None if no path exists
        """
        def heuristic(pos: Tuple[int, int], goal: Tuple[int, int]) -> float:
            return math.sqrt((pos[0] - goal[0])**2 + (pos[1] - goal[1])**2)

        try:
            # Find end room
            end_pos = None
            for y in range(self._size):
                for x in range(self._size):
                    if self._rooms[y][x].is_end_room:
                        end_pos = (x, y)
                        break
                if end_pos:
                    break

            if not end_pos:
                return None

            # A* implementation
            start = self._player_pos
            frontier = [(0, start)]
            came_from = {start: None}
            cost_so_far = {start: 0}

            while frontier:
                current = frontier.pop(0)[1]

                if current == end_pos:
                    # Reconstruct path
                    path = []
                    while current:
                        path.append(current)
                        current = came_from[current]
                    return list(reversed(path))

                for direction, adj_room in self.get_adjacent_rooms(*current):
                    next_pos = (
                        current[0] + {'east': 1, 'west': -1, 'north': 0, 'south': 0}[direction],
                        current[1] + {'north': -1, 'south': 1, 'east': 0, 'west': 0}[direction]
                    )

                    new_cost = cost_so_far[current] + 1
                    if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                        cost_so_far[next_pos] = new_cost
                        priority = new_cost + heuristic(next_pos, end_pos)
                        frontier.append((priority, next_pos))
                        frontier.sort()  # Sort by priority
                        came_from[next_pos] = current

            return None  # No path found
            
        except Exception as e:
            logging.error(f"Error calculating path to end: {str(e)}")
            return None

    def get_exploration_percentage(self) -> float:
        """
        Calculate percentage of dungeon explored.
        
        Returns:
            float: Percentage of rooms visited/visible
        """
        try:
            visible_rooms = sum(
                1 for row in self._rooms 
                for room in row 
                if room.is_visible
            )
            total_rooms = self._size * self._size
            return (visible_rooms / total_rooms) * 100
            
        except Exception as e:
            logging.error(f"Error calculating exploration percentage: {str(e)}")
            return 0.0

    def is_complete(self) -> bool:
        """
        Check if dungeon is completed.
        
        Returns:
            bool: True if end room is reached and all required objectives are met
        """
        try:
            current_room = self.get_current_room()
            return (
                current_room.is_end_room and
                current_room.is_cleared and
                self.get_exploration_percentage() >= 75  # Require 75% exploration
            )
        except Exception as e:
            logging.error(f"Error checking dungeon completion: {str(e)}")
            return False