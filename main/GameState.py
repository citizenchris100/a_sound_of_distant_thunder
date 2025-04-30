import os
import json
import logging
import random
from enum import Enum

class GameState:
    """
    Manages the current state of the game, including player, NPCs, locations, etc.
    """
    def __init__(self, data_manager, event_system):
        """
        Initialize the game state.
        
        Args:
            data_manager: DataManager instance for loading game data
            event_system: EventSystem instance for game events
        """
        self.data_manager = data_manager
        self.event_system = event_system
        self.logger = logging.getLogger("GameState")
        
        # Core state
        self.player = None
        self.current_location = None
        self.time = {"day": 1, "hour": 8, "minute": 0}  # Start at day 1, 8:00 AM
        
        # Entity tracking
        self.npcs = {}  # npc_id -> NPC object
        self.objects = {}  # object_id -> Object data
        
        # Player progress
        self.visited_locations = set()
        self.coalition_members = []
        self.known_assimilated = []
        self.inventory = []
        
        # Quest status
        self.quest_status = {}
        self.global_variables = {}
        
    def initialize_new_game(self, character_class=None):
        """
        Set up a new game.
        
        Args:
            character_class (str, optional): Player character class
        """
        # Create player character
        self.player = self._create_player(character_class)
        
        # Set starting location
        self.load_location("boat_zone")
        
        # Reset progress
        self.visited_locations = set(["boat_zone"])
        self.coalition_members = []
        self.known_assimilated = []
        self.inventory = []
        self.quest_status = {}
        self.global_variables = {}
        
        # Emit game started event
        self.event_system.emit("game_started", {
            "character_class": character_class
        })
        
    def _create_player(self, character_class=None):
        """
        Create the player character using existing Hero class.
        
        Args:
            character_class (str, optional): Player character class
            
        Returns:
            Hero: New player object
        """
        import hero  # Import existing Hero module
        
        if character_class:
            # Load class data
            class_data = self.data_manager.get_data("character_classes", character_class)
            if class_data:
                # Create hero with stats from class data
                player = hero.Hero(
                    dp=class_data["stats"]["defence_points"],
                    strength=class_data["stats"]["strength"],
                    gun_skill=class_data["stats"]["gun_skill"],
                    luck=class_data["stats"]["luck"],
                    charm=class_data["stats"]["charm"],
                    stealth=class_data["stats"]["stealth"]
                )
                
                # Add starting inventory items
                for item_id in class_data.get("starting_inventory", []):
                    # Convert data-driven item to existing Item object
                    item_data = self.data_manager.get_data("items", item_id)
                    if item_data:
                        import items
                        
                        # Determine which item factory function to use
                        item_type = item_data["type"]
                        item_name = item_data["name"].lower()
                        
                        # Try to find matching factory function
                        item_func = None
                        for attr_name in dir(items):
                            if attr_name.endswith("_" + item_type) or attr_name == item_name:
                                item_func = getattr(items, attr_name)
                                if callable(item_func):
                                    break
                        
                        if item_func:
                            item = item_func()
                            player.add_inventory(item)
                
                return player
        
        # If no class specified or class data no