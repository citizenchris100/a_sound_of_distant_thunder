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
        
        # If no class specified or class data not found, use class selection
        return hero.class_selection()
    
    def load_location(self, location_id):
        """
        Load a location and its contents.
        
        Args:
            location_id (str): ID of location to load
            
        Returns:
            bool: True if location loaded successfully, False otherwise
        """
        # Get location data
        location_data = self.data_manager.get_data("locations", location_id)
        if not location_data:
            self.logger.error(f"Location data not found: {location_id}")
            return False
            
        # Update current location
        old_location = self.current_location
        self.current_location = location_id
        
        # Add to visited locations
        first_visit = location_id not in self.visited_locations
        self.visited_locations.add(location_id)
        
        # Load NPCs for this location
        self._load_location_npcs(location_data)
        
        # Load objects for this location
        self._load_location_objects(location_data)
        
        # Trigger location events
        if first_visit and "first_visit_events" in location_data:
            for event_id in location_data["first_visit_events"]:
                self._trigger_location_event(event_id)
        elif not first_visit and "revisit_events" in location_data:
            for event_id in location_data["revisit_events"]:
                self._trigger_location_event(event_id)
        
        # Emit location changed event
        self.event_system.emit("location_changed", {
            "old_location": old_location,
            "new_location": location_id,
            "first_visit": first_visit
        })
        
        self.logger.info(f"Loaded location: {location_id}")
        return True
    
    def _load_location_npcs(self, location_data):
        """
        Load NPCs for a location.
        
        Args:
            location_data (dict): Location data with NPCs
        """
        from npc import NPC
        
        # Clear NPCs that shouldn't persist
        self.npcs = {npc_id: npc for npc_id, npc in self.npcs.items() 
                    if getattr(npc, 'persistent', False)}
        
        # Load NPCs for this location
        for npc_id in location_data.get("npcs", []):
            if npc_id not in self.npcs:
                npc_data = self.data_manager.get_data("npcs", npc_id)
                if npc_data:
                    # Check if we have a factory function for this NPC in the old system
                    import NPC as old_npc_module
                    factory_func = None
                    
                    # Try to find direct factory function by name
                    if hasattr(old_npc_module, npc_id):
                        factory_func = getattr(old_npc_module, npc_id)
                        if callable(factory_func):
                            self.npcs[npc_id] = factory_func()
                            continue
                    
                    # Otherwise create new NPC from data
                    self.npcs[npc_id] = NPC(npc_id, npc_data)
                    self.logger.debug(f"Created NPC from data: {npc_id}")
    
    def _load_location_objects(self, location_data):
        """
        Load objects for a location.
        
        Args:
            location_data (dict): Location data with objects
        """
        # Clear existing objects
        self.objects = {}
        
        # Load new objects
        for obj_data in location_data.get("objects", []):
            obj_id = obj_data["id"]
            self.objects[obj_id] = obj_data
            self.logger.debug(f"Loaded object: {obj_id}")
    
    def _trigger_location_event(self, event_id):
        """
        Trigger a location event.
        
        Args:
            event_id (str): ID of the event to trigger
        """
        event_data = self.data_manager.get_data("events", event_id)
        if not event_data:
            self.logger.warning(f"Event data not found: {event_id}")
            return
            
        event_type = event_data.get("type")
        self.logger.info(f"Triggering event: {event_id} ({event_type})")
        
        if event_type == "spawn_npcs":
            for npc_id in event_data.get("npcs", []):
                npc_data = self.data_manager.get_data("npcs", npc_id)
                if npc_data:
                    from npc import NPC
                    self.npcs[npc_id] = NPC(npc_id, npc_data)
                    self.logger.debug(f"Spawned NPC: {npc_id}")
        
        elif event_type == "dialog":
            dialog_id = event_data.get("dialog_id")
            npc_id = event_data.get("npc_id")
            if dialog_id and npc_id:
                self.event_system.emit("auto_start_dialog", {
                    "dialog_id": dialog_id,
                    "npc_id": npc_id
                })
        
        elif event_type == "combat":
            enemy_ids = event_data.get("enemies", [])
            self.event_system.emit("combat_initiated", {
                "enemy_ids": enemy_ids,
                "surprise": event_data.get("surprise", False)
            })
            
        elif event_type == "modify_variable":
            var_name = event_data.get("variable")
            operation = event_data.get("operation", "set")
            value = event_data.get("value")
            
            if var_name and value is not None:
                current = self.get_variable(var_name, 0)
                
                if operation == "set":
                    self.set_variable(var_name, value)
                elif operation == "increment":
                    self.set_variable(var_name, current + value)
                elif operation == "decrement":
                    self.set_variable(var_name, current - value)
                elif operation == "multiply":
                    self.set_variable(var_name, current * value)
                
                self.logger.debug(f"Modified variable: {var_name} ({operation}) = {self.get_variable(var_name)}")
        
        elif event_type == "give_item":
            item_id = event_data.get("item_id")
            if item_id:
                success = self.add_item_to_inventory(item_id)
                self.logger.debug(f"Give item {item_id}: {'success' if success else 'failed'}")
        
        elif event_type == "custom":
            custom_action = event_data.get("custom_action")
            params = event_data.get("params", {})
            
            if custom_action:
                self.event_system.emit("custom_event", {
                    "action": custom_action,
                    "params": params
                })
            
        # Emit event triggered
        self.event_system.emit("location_event_triggered", {
            "event_id": event_id
        })
    
    def update_npc_suspicion(self, npc_id, amount):
        """
        Update an NPC's suspicion of the player.
        
        Args:
            npc_id (str): ID of the NPC
            amount (int): Amount to change suspicion by
            
        Returns:
            str or None: Behavior change if suspicion threshold crossed, None otherwise
        """
        npc = self.npcs.get(npc_id)
        if npc:
            if hasattr(npc, 'update_suspicion'):
                # New-style NPC
                behavior_change = npc.update_suspicion(amount)
                
                if behavior_change:
                    self.event_system.emit("npc_behavior_changed", {
                        "npc_id": npc_id,
                        "change": behavior_change
                    })
                    
                return behavior_change
            else:
                # Legacy NPC - update happy attribute as inverse of suspicion
                if hasattr(npc, 'set_happy'):
                    # Negative amount means increase suspicion
                    npc.set_happy(amount >= 0, abs(amount))
                    self.logger.debug(f"Updated legacy NPC happiness: {npc_id}")
        return None
    
    def update_npc_trust(self, npc_id, amount):
        """
        Update an NPC's trust of the player.
        
        Args:
            npc_id (str): ID of the NPC
            amount (int): Amount to change trust by
            
        Returns:
            str or None: Relationship change if trust threshold crossed, None otherwise
        """
        npc = self.npcs.get(npc_id)
        if npc:
            if hasattr(npc, 'update_trust'):
                # New-style NPC
                relationship_change = npc.update_trust(amount)
                
                if relationship_change:
                    self.event_system.emit("npc_relationship_changed", {
                        "npc_id": npc_id,
                        "change": relationship_change
                    })
                    
                return relationship_change
            else:
                # Legacy NPC - update happy attribute
                if hasattr(npc, 'set_happy'):
                    npc.set_happy(amount >= 0, abs(amount))
                    self.logger.debug(f"Updated legacy NPC happiness: {npc_id}")
        return None
    
    def add_to_coalition(self, npc_id):
        """
        Add an NPC to the player's coalition.
        
        Args:
            npc_id (str): ID of the NPC to add
            
        Returns:
            bool: True if NPC added successfully, False otherwise
        """
        if npc_id in self.npcs and npc_id not in self.coalition_members:
            npc = self.npcs[npc_id]
            
            # Check if NPC would join
            would_join = True
            
            if hasattr(npc, 'would_join_coalition'):
                # New-style NPC
                would_join = npc.would_join_coalition()
            elif hasattr(npc, 'get_happy'):
                # Legacy NPC - check happiness
                would_join = npc.get_happy() >= 50
            
            if not would_join:
                return False
                
            self.coalition_members.append(npc_id)
            
            # Check for assimilation
            is_assimilated = False
            if hasattr(npc, 'is_assimilated'):
                is_assimilated = npc.is_assimilated
            
            # If NPC is assimilated but player doesn't know, it's infiltration
            if is_assimilated and npc_id not in self.known_assimilated:
                self.event_system.emit("coalition_infiltrated", {
                    "npc_id": npc_id
                })
            else:
                self.event_system.emit("npc_joined_coalition", {
                    "npc_id": npc_id
                })
                
            self.logger.info(f"NPC joined coalition: {npc_id}")
            return True
        return False
    
    def add_item_to_inventory(self, item_id):
        """
        Add an item to player inventory.
        
        Args:
            item_id (str): ID of item to add
            
        Returns:
            bool: True if item added, False otherwise
        """
        if self.player is None:
            self.logger.error("Cannot add item: Player not initialized")
            return False
            
        item_data = self.data_manager.get_data("items", item_id)
        if not item_data:
            self.logger.error(f"Item data not found: {item_id}")
            return False
            
        # Check inventory limit
        if len(self.player.get_inventory()) >= self.player.get_inventory_limit():
            self.logger.debug(f"Cannot add item: Inventory full")
            return False
            
        # Create item object from data
        import items
        
        # Determine which item factory function to use
        item_type = item_data.get("type", "")
        item_name = item_data.get("name", "").lower()
        
        # Try to find matching factory function
        item_func = None
        for attr_name in dir(items):
            if attr_name.endswith("_" + item_type) or attr_name == item_name:
                item_func = getattr(items, attr_name)
                if callable(item_func):
                    break
        
        if item_func:
            item = item_func()
            self.player.add_inventory(item)
            
            self.event_system.emit("item_acquired", {
                "item_id": item_id,
                "item_name": item.get_item_name()
            })
            
            self.logger.info(f"Item added to inventory: {item_id}")
            return True
        else:
            # Fallback to generic item
            if hasattr(items, 'Item'):
                item = items.Item(
                    item_data.get("name", item_id),
                    item_data.get("value", 1),
                    item_data.get("type", "quest")
                )
                self.player.add_inventory(item)
                
                self.event_system.emit("item_acquired", {
                    "item_id": item_id,
                    "item_name": item.get_item_name()
                })
                
                self.logger.info(f"Generic item added to inventory: {item_id}")
                return True
        
        self.logger.error(f"Failed to create item: {item_id}")
        return False
    
    def has_item(self, item_id):
        """
        Check if player has an item.
        
        Args:
            item_id (str): ID or name of item to check
            
        Returns:
            bool: True if player has item, False otherwise
        """
        if self.player is None:
            return False
            
        # Convert to lowercase for case-insensitive comparison
        item_id_lower = item_id.lower()
        
        # Check inventory for matching item
        for item in self.player.get_inventory():
            if (item.get_item_name().lower() == item_id_lower or
                (hasattr(item, 'id') and item.id == item_id)):
                return True
        
        return False
    
    def remove_item(self, item_id):
        """
        Remove an item from inventory.
        
        Args:
            item_id (str): ID or name of item to remove
            
        Returns:
            bool: True if item removed, False otherwise
        """
        if self.player is None:
            return False
            
        # Convert to lowercase for case-insensitive comparison
        item_id_lower = item_id.lower()
        
        # Find matching item in inventory
        for i, item in enumerate(self.player.get_inventory()):
            if (item.get_item_name().lower() == item_id_lower or
                (hasattr(item, 'id') and item.id == item_id)):
                self.player.del_inventory(i)
                
                self.event_system.emit("item_removed", {
                    "item_id": item_id,
                    "item_name": item.get_item_name()
                })
                
                self.logger.info(f"Item removed from inventory: {item_id}")
                return True
        
        return False
    
    def get_variable(self, name, default=None):
        """
        Get a global variable value.
        
        Args:
            name (str): Variable name
            default: Default value if variable not set
            
        Returns:
            Variable value or default
        """
        return self.global_variables.get(name, default)
    
    def set_variable(self, name, value):
        """
        Set a global variable value.
        
        Args:
            name (str): Variable name
            value: Variable value
        """
        self.global_variables[name] = value
    
    def check_win_condition(self):
        """
        Check if player has met win/lose conditions.
        
        Returns:
            str or None: 'victory', 'escape', 'defeat', or None if game continues
        """
        # Count total NPCs and assimilated NPCs
        total_npc_count = len(self.data_manager.get_all_ids("npcs"))
        
        # Count assimilated NPCs
        assimilated_count = 0
        for npc in self.npcs.values():
            if hasattr(npc, 'is_assimilated') and npc.is_assimilated:
                assimilated_count += 1
        
        coalition_size = len(self.coalition_members)
        
        # Win condition: Coalition controls station
        if coalition_size > (total_npc_count / 2) and coalition_size > assimilated_count:
            self.logger.info("Win condition met: Coalition victory")
            return "victory"
            
        # Escape condition: Player at ship with enough coalition members
        if (self.current_location == "shipping_dock" and 
            coalition_size >= 5 and 
            any(self.has_item(item) for item in ["ship_key", "escape_code"])):
            self.logger.info("Win condition met: Escape")
            return "escape"
            
        # Lose condition: Too many assimilated
        if assimilated_count > (total_npc_count * 0.7):
            self.logger.info("Lose condition met: Too many assimilated")
            return "defeat"
            
        # Player is discovered as threat
        player_threat_level = 0
        npc_count = 0
        
        for npc in self.npcs.values():
            if hasattr(npc, 'suspicion'):
                player_threat_level += npc.suspicion
                npc_count += 1
            elif hasattr(npc, 'get_happy'):
                # Convert happy to suspicion (0-100)
                player_threat_level += (100 - npc.get_happy())
                npc_count += 1
        
        if npc_count > 0 and (player_threat_level / npc_count) > 75:
            self.logger.info("Lose condition met: Player discovered as threat")
            return "defeat"
            
        return None  # Game continues
        
    def get_current_location_data(self):
        """
        Get data for the current location.
        
        Returns:
            dict: Location data or None if not found
        """
        if not self.current_location:
            return None
        return self.data_manager.get_data("locations", self.current_location)
    
    def get_npc(self, npc_id):
        """
        Get an NPC by ID.
        
        Args:
            npc_id (str): ID of the NPC
            
        Returns:
            NPC: NPC object or None if not found
        """
        return self.npcs.get(npc_id)
    
    def get_object(self, object_id):
        """
        Get an object by ID.
        
        Args:
            object_id (str): ID of the object
            
        Returns:
            dict: Object data or None if not found
        """
        return self.objects.get(object_id)
    
    def get_player_stats(self):
        """
        Get player stats as a dictionary.
        
        Returns:
            dict: Player stats
        """
        if not self.player:
            return {}
            
        return {
            "health": self.player.get_health_points(),
            "health_max": self.player.get_hp_limit(),
            "defence": self.player.get_defence_points(),
            "strength": self.player.get_strength_attribute(),
            "gun_skill": self.player.get_gun_skill(),
            "luck": self.player.get_luck(),
            "charm": self.player.get_charm_attribute(),
            "stealth": self.player.get_stealth_attribute(),
            "inventory_size": len(self.player.get_inventory()),
            "inventory_limit": self.player.get_inventory_limit()
        }