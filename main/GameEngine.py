"""
Game Engine for A Sound of Distant Thunder
Main engine class that coordinates all systems.
"""
import logging
import os
import pygame
import json
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("game.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("GameEngine")

class GameEngine:
    """
    Main game engine that coordinates all systems.
    """
    def __init__(self, data_path="./data/", asset_path="./assets/", debug_mode=False):
        """
        Initialize the game engine.
        
        Args:
            data_path (str): Path to game data directory
            asset_path (str): Path to game assets directory
            debug_mode (bool): Enable debug features
        """
        # Game configuration
        self.data_path = data_path
        self.asset_path = asset_path
        self.debug_mode = debug_mode
        
        # Ensure directories exist
        os.makedirs(data_path, exist_ok=True)
        os.makedirs(asset_path, exist_ok=True)
        os.makedirs(os.path.join(data_path, "saves"), exist_ok=True)
        
        # Create systems in dependency order
        self.event_system = None
        self.data_manager = None
        self.game_state = None
        self.asset_manager = None
        self.dialog_manager = None
        self.ui_manager = None
        self.scene_manager = None
        self.interaction_system = None
        self.navigation_system = None
        self.assimilation_system = None
        self.message_box = None
        self.character_selection = None
        
        # Initialize systems
        self._init_systems()
        
        logger.info("Game engine initialized")
    
    def _init_systems(self):
        """Initialize all game systems in the correct order"""
        # Create event system first (no dependencies)
        from event_system import EventSystem
        self.event_system = EventSystem()
        
        # Create data manager (depends on nothing)
        from data_manager import DataManager
        self.data_manager = DataManager(self.data_path)
        
        # Create game state (depends on data manager and event system)
        from game_state import GameState
        self.game_state = GameState(self.data_manager, self.event_system)
        
        # Create asset manager (depends on nothing)
        from ui_framework import AssetManager
        self.asset_manager = AssetManager(self.asset_path)
        
        # Create dialog manager (depends on data manager, game state, and event system)
        from dialog_manager import DialogManager
        self.dialog_manager = DialogManager(self.data_manager, self.game_state, self.event_system)
        
        # Create assimilation system (depends on game state and event system)
        from assimilation_system import AssimilationSystem
        self.assimilation_system = AssimilationSystem(self.game_state, self.event_system)
        
        # Create navigation system (depends on game state, data manager, and event system)
        from navigation_system import NavigationSystem
        self.navigation_system = NavigationSystem(self)
        
        # Create interaction system (depends on many other systems)
        from interaction_system import InteractionSystem
        self.interaction_system = InteractionSystem(self)
        
        # Create scene manager (depends on game state, asset manager, and event system)
        from scene_system import SceneManager
        self.scene_manager = SceneManager(self, self.asset_manager)
        
        # Create message box (depends on asset manager and event system)
        from message_box import MessageBox
        self.message_box = MessageBox(self, self.asset_manager)
        
        # Create character selection screen (depends on asset manager and event system)
        from character_questionnaire import CharacterSelectionScreen
        self.character_selection = CharacterSelectionScreen(self, self.asset_manager)
        
        # Create UI manager (depends on all other systems)
        from ui_framework import UIManager
        self.ui_manager = UIManager(self, 800, 600)
        
        logger.info("All systems initialized")
    
    def initialize(self):
        """Initialize the game, loading necessary resources"""
        # Initialize UI
        self.ui_manager.initialize()
        
        # Initialize other systems as needed
        self.asset_manager.load_common_assets()
        
        # Register event handlers
        self._register_event_handlers()
        
        logger.info("Game initialization complete")
        # Initialize Phase 2 components
        from Phase2Integration import initialize_phase2
        self.phase2_integration = initialize_phase2(self)
    
    def _register_event_handlers(self):
        """Register handlers for game events"""
        self.event_system.subscribe("message_displayed", self._on_message_displayed)
        self.event_system.subscribe("description_displayed", self._on_description_displayed)
        self.event_system.subscribe("dialog_started", self._on_dialog_started)
        self.event_system.subscribe("dialog_ended", self._on_dialog_ended)
        self.event_system.subscribe("game_event_triggered", self._on_game_event_triggered)
        self.event_system.subscribe("combat_initiated", self._on_combat_initiated)
        
        logger.info("Event handlers registered")
    
    def _on_message_displayed(self, data):
        """Handle message displayed event"""
        # Message box will handle this directly via its own subscription
        pass
    
    def _on_description_displayed(self, data):
        """Handle description displayed event"""
        # Message box will handle this directly via its own subscription
        pass
    
    def _on_dialog_started(self, data):
        """Handle dialog started event"""
        # Dialog UI will handle this directly via its own subscription
        pass
    
    def _on_dialog_ended(self, data):
        """Handle dialog ended event"""
        # Dialog UI will handle this directly via its own subscription
        pass
    
    def _on_game_event_triggered(self, data):
        """Handle game event triggered"""
        event_id = data.get("event_id")
        if event_id:
            self.handle_game_event(event_id, data.get("params"))
    
    def _on_combat_initiated(self, data):
        """Handle combat initiated event"""
        # TODO: Implement combat system
        enemy_ids = data.get("enemy_ids", [])
        surprise = data.get("surprise", False)
        
        # For now, just log the event
        logger.info(f"Combat initiated against: {enemy_ids}, surprise: {surprise}")
        
        # Display message
        self.event_system.emit("message_displayed", {
            "text": "Combat feature not implemented yet."
        })
    
    def run(self):
        """Run the game main loop"""
        # Show character selection on first run
        self.character_selection.show()
        
        # Start UI main loop (this will block until the game exits)
        self.ui_manager.run()
    
    def initialize_new_game(self, character_class=None):
        """
        Start a new game.
        
        Args:
            character_class (str, optional): Character class to use
        """
        self.game_state.initialize_new_game(character_class)
        
        # Emit event
        self.event_system.emit("game_started", {
            "character_class": character_class
        })
        
        logger.info(f"New game started with character class: {character_class}")
    
    def save_game(self, save_name):
        """
        Save the current game state.
        
        Args:
            save_name (str): Name to use for the save file
            
        Returns:
            bool: True if save succeeded, False otherwise
        """
        save_dir = os.path.join(self.data_path, "saves")
        save_path = os.path.join(save_dir, f"{save_name}.json")
        
        try:
            # Serialize game state
            state_data = self._serialize_game_state()
            
            # Write to file
            with open(save_path, 'w') as f:
                json.dump(state_data, f, indent=2)
            
            # Emit event
            self.event_system.emit("game_saved", {
                "save_name": save_name
            })
            
            logger.info(f"Game saved: {save_name}")
            return True
        except Exception as e:
            logger.error(f"Error saving game: {e}")
            return False
    
    def load_game(self, save_name):
        """
        Load a saved game.
        
        Args:
            save_name (str): Name of the save file to load
            
        Returns:
            bool: True if load succeeded, False otherwise
        """
        save_dir = os.path.join(self.data_path, "saves")
        save_path = os.path.join(save_dir, f"{save_name}.json")
        
        if not os.path.exists(save_path):
            logger.error(f"Save file not found: {save_name}")
            return False
        
        try:
            # Load from file
            with open(save_path, 'r') as f:
                state_data = json.load(f)
            
            # Deserialize game state
            self._deserialize_game_state(state_data)
            
            # Emit event
            self.event_system.emit("game_loaded", {
                "save_name": save_name
            })
            
            logger.info(f"Game loaded: {save_name}")
            return True
        except Exception as e:
            logger.error(f"Error loading game: {e}")
            return False
    
    def _serialize_game_state(self):
        """
        Serialize game state to a dictionary.
        
        Returns:
            dict: Serialized game state
        """
        # Basic game state
        state_data = {
            "player": self._serialize_player(),
            "current_location": self.game_state.current_location,
            "time": self.game_state.time,
            "npcs": self._serialize_npcs(),
            "coalition_members": self.game_state.coalition_members,
            "known_assimilated": self.game_state.known_assimilated,
            "visited_locations": list(self.game_state.visited_locations),
            "global_variables": self.game_state.global_variables,
            "quest_status": self.game_state.quest_status
        }
        
        return state_data
    
    def _serialize_player(self):
        """
        Serialize player state.
        
        Returns:
            dict: Serialized player state
        """
        player = self.game_state.player
        
        # Basic player attributes
        player_data = {
            "stats": {
                "health": player.get_health_points(),
                "health_max": player.get_hp_limit(),
                "defence": player.get_defence_points(),
                "strength": player.get_strength_attribute(),
                "gun_skill": player.get_gun_skill(),
                "luck": player.get_luck(),
                "charm": player.get_charm_attribute(),
                "stealth": player.get_stealth_attribute()
            },
            "inventory": player.get_inventory(),
            "equipped": {
                "gun": player.get_equipped_gun(),
                "melee": player.get_equipped_melee(),
                "armour": player.get_equipped_armour()
            }
        }
        
        return player_data
    
    def _serialize_npcs(self):
        """
        Serialize NPC states.
        
        Returns:
            dict: Dictionary of serialized NPC states
        """
        npcs_data = {}
        
        for npc_id, npc in self.game_state.npcs.items():
            # Serialize NPC state
            npc_data = {
                "health": getattr(npc, "health", 100),
                "suspicion": getattr(npc, "suspicion", 0),
                "trust_level": getattr(npc, "trust_level", 0),
                "is_assimilated": getattr(npc, "is_assimilated", False),
                "behavior_type": getattr(npc, "behavior_type", "neutral"),
                "observed_behaviors": getattr(npc, "observed_behaviors", [])
            }
            
            npcs_data[npc_id] = npc_data
        
        return npcs_data
    
    def _deserialize_game_state(self, state_data):
        """
        Deserialize game state from a dictionary.
        
        Args:
            state_data (dict): Serialized game state
        """
        # Create a new game state
        from game_state import GameState
        self.game_state = GameState(self.data_manager, self.event_system)
        
        # Load player state
        self._deserialize_player(state_data.get("player", {}))
        
        # Set current location
        self.game_state.current_location = state_data.get("current_location")
        
        # Set game time
        self.game_state.time = state_data.get("time", {"day": 1, "hour": 8, "minute": 0})
        
        # Load NPCs
        self._deserialize_npcs(state_data.get("npcs", {}))
        
        # Load progress
        self.game_state.coalition_members = state_data.get("coalition_members", [])
        self.game_state.known_assimilated = state_data.get("known_assimilated", [])
        self.game_state.visited_locations = set(state_data.get("visited_locations", []))
        self.game_state.global_variables = state_data.get("global_variables", {})
        self.game_state.quest_status = state_data.get("quest_status", {})
        
        # Recreate other systems that depend on game state
        self._recreate_dependent_systems()
    
    def _deserialize_player(self, player_data):
        """
        Deserialize player state.
        
        Args:
            player_data (dict): Serialized player state
        """
        # Create player
        from hero import Hero
        
        # Get stats
        stats = player_data.get("stats", {})
        
        # Create hero with stats
        self.game_state.player = Hero(
            dp=stats.get("defence", 0),
            strength=stats.get("strength", 5),
            gun_skill=stats.get("gun_skill", 0),
            luck=stats.get("luck", 0),
            charm=stats.get("charm", 0),
            stealth=stats.get("stealth", 0),
            game_items_data=self.data_manager.get_data("items")
        )
        
        # Set health
        self.game_state.player.set_health_points(stats.get("health", 100))
        self.game_state.player.set_hp_limit(stats.get("health_max", 100))
        
        # Load inventory
        for item in player_data.get("inventory", []):
            self.game_state.inventory.append(item)
        
        # Set equipped items
        equipped = player_data.get("equipped", {})
        if "gun" in equipped:
            self.game_state.player.set_equipped_gun(equipped["gun"])
        if "melee" in equipped:
            self.game_state.player.set_equipped_melee(equipped["melee"])
        if "armour" in equipped:
            self.game_state.player.set_equipped_armour(equipped["armour"])
    
    def _deserialize_npcs(self, npcs_data):
        """
        Deserialize NPC states.
        
        Args:
            npcs_data (dict): Dictionary of serialized NPC states
        """
        from npc import NPC
        
        for npc_id, npc_state in npcs_data.items():
            # Get base NPC data
            npc_data = self.data_manager.get_data("npcs", npc_id)
            
            if npc_data:
                # Create NPC with base data
                npc = NPC(npc_id, npc_data)
                
                # Apply saved state
                npc.health = npc_state.get("health", 100)
                npc.suspicion = npc_state.get("suspicion", 0)
                npc.trust_level = npc_state.get("trust_level", 0)
                npc.is_assimilated = npc_state.get("is_assimilated", False)
                npc.behavior_type = npc_state.get("behavior_type", "neutral")
                npc.observed_behaviors = npc_state.get("observed_behaviors", [])
                
                # Add to game state
                self.game_state.npcs[npc_id] = npc
    
    def _recreate_dependent_systems(self):
        """Recreate systems that depend on game state"""
        # Recreate dialog manager
        from dialog_manager import DialogManager
        self.dialog_manager = DialogManager(self.data_manager, self.game_state, self.event_system)
        
        # Recreate assimilation system
        from assimilation_system import AssimilationSystem
        self.assimilation_system = AssimilationSystem(self.game_state, self.event_system)
    
    def get_save_games(self):
        """
        Get list of available save games.
        
        Returns:
            list: List of save game names
        """
        save_dir = os.path.join(self.data_path, "saves")
        
        # Check if directory exists
        if not os.path.exists(save_dir):
            return []
        
        # Get all JSON files in the saves directory
        saves = []
        for filename in os.listdir(save_dir):
            if filename.endswith(".json"):
                saves.append(filename[:-5])  # Remove .json extension
                
        return saves
    
    def handle_event(self, event_id, data=None):
        """
        Handle a game event.
        
        Args:
            event_id (str): Event identifier
            data (dict, optional): Event data
        """
        # Process event based on ID
        if event_id == "game_start":
            # Start a new game
            character_class = data.get("character_class") if data else None
            self.initialize_new_game(character_class)
        elif event_id == "game_save":
            # Save the game
            save_name = data.get("save_name") if data else "quicksave"
            self.save_game(save_name)
        elif event_id == "game_load":
            # Load a saved game
            save_name = data.get("save_name") if data else None
            if save_name:
                self.load_game(save_name)
        elif event_id == "game_exit":
            # Exit the game
            pygame.quit()
            import sys
            sys.exit()
        elif event_id == "toggle_debug":
            # Toggle debug mode
            self.debug_mode = not self.debug_mode
            logger.info(f"Debug mode: {self.debug_mode}")
    
    def handle_game_event(self, event_id, data=None):
        """
        Handle a narrative game event from event data.
        
        Args:
            event_id (str): Event identifier
            data (dict, optional): Additional event data
        """
        # Get event data
        event_data = self.data_manager.get_data("events", event_id)
        
        if not event_data:
            logger.error(f"Event data not found: {event_id}")
            return
            
        # Process event based on type
        event_type = event_data.get("event_type")
        
        if event_type == "display_text":
            # Display text message
            text = event_data.get("payload", {}).get("text", "")
            self.event_system.emit("message_displayed", {
                "text": text
            })
        elif event_type == "display_chapter":
            # Display chapter introduction
            chapter_number = event_data.get("payload", {}).get("chapter_number", 1)
            chapter_text = event_data.get("payload", {}).get("chapter_text", "")
            self.event_system.emit("chapter_displayed", {
                "chapter_number": chapter_number,
                "text": chapter_text
            })
        elif event_type == "trigger_combat":
            # Start combat
            enemies = event_data.get("payload", {}).get("spawn_npcs", [])
            surprise = event_data.get("payload", {}).get("surprise", False)
            self.event_system.emit("combat_initiated", {
                "enemy_ids": enemies,
                "surprise": surprise
            })
        elif event_type == "modify_variable":
            # Modify a game variable
            var_name = event_data.get("payload", {}).get("variable")
            operation = event_data.get("payload", {}).get("operation", "set")
            value = event_data.get("payload", {}).get("value")
            
            if var_name and value is not None:
                current = self.game_state.get_variable(var_name, 0)
                
                if operation == "set":
                    self.game_state.set_variable(var_name, value)
                elif operation == "increment":
                    self.game_state.set_variable(var_name, current + value)
                elif operation == "decrement":
                    self.game_state.set_variable(var_name, current - value)
                elif operation == "multiply":
                    self.game_state.set_variable(var_name, current * value)
        elif event_type == "set_flag":
            # Set a game flag
            flag_name = event_data.get("payload", {}).get("flag_name")
            flag_value = event_data.get("payload", {}).get("flag_value", True)
            
            if flag_name:
                self.game_state.set_variable(flag_name, flag_value)
        elif event_type == "give_item":
            # Give item to player
            item_id = event_data.get("payload", {}).get("item_id")
            
            if item_id:
                self.game_state.add_item_to_inventory(item_id)
        elif event_type == "modify_location":
            # Modify the current location
            modifications = event_data.get("payload", {}).get("modifications", {})
            current_location_id = self.game_state.current_location
            current_location_data = self.data_manager.get_data("locations", current_location_id)
            
            if current_location_data:
                # Apply modifications
                for key, value in modifications.items():
                    current_location_data[key] = value
                    
                # Force reload of location
                self.game_state.load_location(current_location_id)
        elif event_type == "loot_container":
            # Open container to view contents
            container_id = event_data.get("payload", {}).get("container_id")
            
            if container_id:
                # Find container in current location
                current_location_id = self.game_state.current_location
                current_location_data = self.data_manager.get_data("locations", current_location_id)
                
                if current_location_data:
                    for obj in current_location_data.get("objects", []):
                        if obj.get("id") == container_id:
                            # Found container
                            items = obj.get("contains_items", [])
                            
                            # Show container contents
                            self.event_system.emit("container_opened", {
                                "container_id": container_id,
                                "items": items
                            })
                            break
        elif event_type == "custom":
            # Custom event handler
            handler_type = event_data.get("payload", {}).get("handler_type")
            
            if handler_type == "npc_dialog":
                # Start dialog with NPC
                npc_id = event_data.get("payload", {}).get("npc_id")
                dialog_ref = event_data.get("payload", {}).get("dialog_ref")
                
                if npc_id and dialog_ref:
                    self.event_system.emit("dialog_started", {
                        "npc_id": npc_id,
                        "dialog_id": dialog_ref
                    })
            elif handler_type == "check_and_trigger":
                # Check condition and trigger events
                condition_checks = event_data.get("payload", {}).get("condition_checks", [])
                on_true = event_data.get("payload", {}).get("on_true", [])
                on_false = event_data.get("payload", {}).get("on_false", [])
                
                # Check all conditions
                all_conditions_met = True
                for check in condition_checks:
                    check_type = check.get("type")
                    
                    if check_type == "check_flag":
                        flag_name = check.get("flag_name")
                        expected_value = check.get("expected_value", True)
                        
                        if self.game_state.get_variable(flag_name, False) != expected_value:
                            all_conditions_met = False
                            break
                    elif check_type == "check_item":
                        item_id = check.get("item_id")
                        
                        if not self.game_state.has_item(item_id):
                            all_conditions_met = False
                            break
                    elif check_type == "check_coalition_size":
                        min_size = check.get("min_size", 0)
                        
                        if len(self.game_state.coalition_members) < min_size:
                            all_conditions_met = False
                            break
                
                # Trigger appropriate events
                if all_conditions_met and on_true:
                    for event_id in on_true:
                        self.handle_game_event(event_id)
                elif not all_conditions_met and on_false:
                    for event_id in on_false:
                        self.handle_game_event(event_id)
            elif handler_type == "random_event":
                # Random event selection
                events = event_data.get("payload", {}).get("events", [])
                weights = event_data.get("payload", {}).get("weights", [])
                
                if events:
                    if weights and len(weights) == len(events):
                        # Weighted random selection
                        selected_event = random.choices(events, weights=weights, k=1)[0]
                    else:
                        # Uniform random selection
                        selected_event = random.choice(events)
                        
                    self.handle_game_event(selected_event)
            elif handler_type == "time_advance":
                # Advance game time
                hours = event_data.get("payload", {}).get("hours", 0)
                minutes = event_data.get("payload", {}).get("minutes", 0)
                
                if hours > 0 or minutes > 0:
                    self._advance_time(hours, minutes)
        
        # Check for chain events
        chain_events = event_data.get("chain_events", [])
        for chain_event_id in chain_events:
            self.handle_game_event(chain_event_id)
        
        # Check win condition after processing event
        end_state = self.game_state.check_win_condition()
        if end_state:
            self._handle_game_end(end_state)
    
    def _advance_time(self, hours, minutes):
        """
        Advance game time by the specified amount.
        
        Args:
            hours (int): Hours to advance
            minutes (int): Minutes to advance
        """
        time = self.game_state.time
        
        # Convert to total minutes
        total_minutes = time.get("hour", 0) * 60 + time.get("minute", 0) + hours * 60 + minutes
        
        # Calculate new values
        new_day = time.get("day", 1) + total_minutes // (24 * 60)
        new_hour = (total_minutes % (24 * 60)) // 60
        new_minute = total_minutes % 60
        
        # Update time
        time["day"] = new_day
        time["hour"] = new_hour
        time["minute"] = new_minute
        
        # Emit time changed event
        self.event_system.emit("time_changed", {
            "time": time
        })
    
    def _handle_game_end(self, end_state):
        """
        Handle game ending.
        
        Args:
            end_state (str): Type of ending ('victory', 'escape', or 'defeat')
        """
        if end_state == "victory":
            logger.info("Game complete: Victory!")
            self.event_system.emit("game_ended", {
                "outcome": "victory",
                "message": "The coalition has gained control of the station!"
            })
        elif end_state == "escape":
            logger.info("Game complete: Escape!")
            self.event_system.emit("game_ended", {
                "outcome": "escape",
                "message": "You and your coalition have escaped the station!"
            })
        elif end_state == "defeat":
            logger.info("Game complete: Defeat!")
            self.event_system.emit("game_ended", {
                "outcome": "defeat",
                "message": "The station has been overrun by the assimilated!"
            })