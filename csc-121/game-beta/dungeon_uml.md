classDiagram
    GameApp --> GameWindow
    GameApp --> Character
    GameApp --> Dungeon
    GameApp --> Database
    GameApp --> D20CombatSystem
    GameApp --> Merchant
    GameWindow --> GameFrame
    GameWindow --> CombatWindow
    
    class GameApp {
        -Database _db
        -GameWindow _window
        -Character _player
        -Dungeon _current_dungeon
        -Merchant _merchant
        -D20CombatSystem _combat_system
        -str _game_state
        +start()
        +_handle_movement(direction)
        +_handle_combat_end(outcome)
        +_handle_dungeon_completion()
    }

    class Character {
        +str name
        +int age
        +int tier
        +int xp
        +int current_health
        +List inventory
        +Dict equipped_weapon
        +Dict equipped_armor
        +Dict equipped_shield
        +int money
        +calculate_total_attack()
        +calculate_total_defense()
        +add_xp(amount)
        +take_damage(amount)
        +heal(amount)
    }

    class Dungeon {
        -int _tier
        -int _size
        -tuple _player_pos
        -List[List[Room]] _rooms
        +move_player(direction)
        +get_current_room()
        +is_complete()
        +get_treasure_loot()
    }

    class Room {
        +List enemies
        +List items
        +bool is_cleared
        +bool is_visible
        +bool has_merchant
        +bool merchant_visited
        +bool has_treasure
        +bool treasure_looted
        +bool is_end_room
        +Dict doors
    }

    class Database {
        -Dict _instance
        -Dict data_files
        +get_item(name)
        +get_enemy(name)
        +get_tier_data(tier)
        +load_data(table_name)
    }

    class D20CombatSystem {
        +roll_d20()
        +calculate_hit(attacker, defender)
        +process_turn(attacker, defender, action)
        +distribute_rewards(character, enemy)
    }

    class Enemy {
        +str name
        +int tier
        +int current_health
        +int attack
        +int defense
        +int health
        +int xp_value
        +List common_drops
        +List rare_drops
        +get_drops()
    }

    class Merchant {
        -List _inventory
        -float _price_variation
        -float _sell_price_ratio
        +buy_item(player, item_name)
        +sell_item(player, item)
        +refresh_inventory()
    }

    class GameWindow {
        +GameFrame current_frame
        +setup_game_ui()
        +update_game_view()
        +show_inventory_ui()
        +show_merchant_ui()
    }

    class GameFrame {
        +update_stats_view()
        +update_equipment_display()
        +show_inventory_ui()
        +show_merchant_ui()
    }

    class CombatWindow {
        +process_turn()
        +handle_attack()
        +handle_flee()
        +update_stats()
    }