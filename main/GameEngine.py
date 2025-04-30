import logging
import os
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GameEngine")

class GameEngine:
    """
    Main game engine that coordinates all systems.
    """
    def __init__(self, data_path="./data/"):
        # Set up data directory
        os.makedirs(data_path, exist_ok=True)
        
        # Create core systems
        self.event_system = EventSystem()
        self.data_manager = DataManager(data_path)
        self.game_state = GameState(self.data_manager, self.event_system)
        self.dialog_manager = DialogManager(self.data_manager, self.game_state, self.event_system)
        self.assimilation_system = AssimilationSystem(self.game_state, self.event_system)
        
        # Set up event listeners
        self._setup_event_listeners()
        
        logger.info("Game engine initialized")
        
    def _setup_event_listeners(self):
        """Set up core event listeners"""
        # Location changes
        self.event_system.subscribe("location_changed", self._on_location_changed)
        
        # Assimilation events
        self.event_system.subscribe("npc_assimilated", self._on_npc_assimilated)
        self.event_system.subscribe("coalition_infiltrated", self._on_coalition_infiltrated)
        
        # Game progress
        self.event_system.subscribe("npc_joined_coalition", self._on_npc_joined_coalition)
        
    def _on_location_changed(self, data):
        """Handle location change events"""
        logger.info(f"Location changed: {data['old_location']} -> {data['new_location']}")
        
        # Check for win/lose conditions when location changes
        end_state = self.game_state.check_win_condition()
        if end_state:
            self._handle_game_end(end_state)
            
    def _on_npc_assimilated(self, data):
        """Handle NPC assimilation events"""
        npc_id = data["npc_id"]
        logger.info(f"NPC assimilated: {npc_id}")
        
        # Adjust game difficulty - more assimilated NPCs means more challenges
        assimilated_count = sum(1 for npc in self.game_state.npcs.values() if npc.is_assimilated)
        total_npcs = len(self.game_state.npcs)
        
        # If high percentage assimilated, trigger special events
        if assimilated_count / total_npcs > 0.5:
            self.event_system.emit("assimilation_crisis", {
                "severity": "high",
                "assimilated_percentage": assimilated_count / total_npcs
            })
            
    def _on_coalition_infiltrated(self, data):
        """Handle coalition infiltration events"""
        npc_id = data["npc_id"]
        logger.info(f"Coalition infiltrated by: {npc_id}")
        
        # Infiltrators might sabotage coalition
        infiltrator = self.game_state.npcs.get(npc_id)
        if infiltrator and random.random() < 0.3:
            self._trigger_sabotage(npc_id)
            
    def _on_npc_joined_coalition(self, data):
        """Handle NPCs joining the coalition"""
        npc_id = data["npc_id"]
        logger.info(f"NPC joined coalition: {npc_id}")
        
        # Check coalition size for progress events
        coalition_size = len(self.game_state.coalition_members)
        if coalition_size == 3:
            self.event_system.emit("coalition_milestone", {
                "milestone": "small_group_formed",
                "size": coalition_size
            })
        elif coalition_size == 10:
            self.event_system.emit("coalition_milestone", {
                "milestone": "significant_force",
                "size": coalition_size
            })
            
    def _trigger_sabotage(self, infiltrator_id):
        """Trigger sabotage by an infiltrator"""
        # Choose a sabotage type
        sabotage_types = [
            "reveal_plans",
            "steal_item",
            "disable_security",
            "mislead_coalition"
        ]
        
        sabotage = random.choice(sabotage_types)
        
        self.event_system.emit("coalition_sabotaged", {
            "infiltrator_id": infiltrator_id,
            "sabotage_type": sabotage
        })
        
    def _handle_game_end(self, end_state):
        """Handle game ending"""
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
            
    def initialize_new_game(self, character_class=None):
        """Start a new game"""
        self.game_state.initialize_new_game(character_class)
        logger.info(f"New game started with character class: {character_class}")
        
    def save_game(self, save_name):
        """Save the current game state"""
        save_dir = os.path.join(self.data_manager.data_path, "saves")
        os.makedirs(save_dir, exist_ok=True)
        
        save_path = os.path.join(save_dir, f"{save_name}.json")
        
        # Serialize game state
        state_data = {
            "player": {
                "stats": vars(self.game_state.player),
                "inventory": self.game_state.inventory
            },
            "current_location": self.game_state.current_location,
            "npcs": {npc_id: vars(npc) for npc_id, npc in self.game_state.npcs.items()},
            "coalition_members": self.game_state.coalition_members,
            "known_assimilated": self.game_state.known_assimilated,
            "visited_locations": list(self.game_state.visited_locations),
            "global_variables": self.game_state.global_variables,
            "quest_status": self.game_state.quest_status,
            "game_time": self.game_state.time
        }
        
        with open(save_path, 'w') as f:
            json.dump(state_data, f, indent=2)
            
        logger.info(f"Game saved: {save_name}")
        return True
        
    def load_game(self, save_name):
        """Load a saved game"""
        save_dir = os.path.join(self.data_manager.data_path, "saves")
        save_path = os.path.join(save_dir, f"{save_name}.json")
        
        if not os.path.exists(save_path):
            logger.error(f"Save file not found: {save_name}")
            return False
            
        try:
            with open(save_path, 'r') as f:
                state_data = json.load(f)
                
            # Create a new game state
            self.game_state = GameState(self.data_manager, self.event_system)
            
            # Restore player
            from player import Player
            self.game_state.player = Player(state_data["player"]["stats"])
            self.game_state.inventory = state_data["player"]["inventory"]
            
            # Restore location
            self.game_state.current_location = state_data["current_location"]
            
            # Restore NPCs
            for npc_id, npc_data in state_data["npcs"].items():
                from npc import NPC
                self.game_state.npcs[npc_id] = NPC(npc_id, npc_data)
                
            # Restore progress
            self.game_state.coalition_members = state_data["coalition_members"]
            self.game_state.known_assimilated = state_data["known_assimilated"]
            self.game_state.visited_locations = set(state_data["visited_locations"])
            self.game_state.global_variables = state_data["global_variables"]
            self.game_state.quest_status = state_data["quest_status"]
            self.game_state.time = state_data["game_time"]
            
            # Recreate other systems
            self.dialog_manager = DialogManager(self.data_manager, self.game_state, self.event_system)
            self.assimilation_system = AssimilationSystem(self.game_state, self.event_system)
            
            # Set up event listeners again
            self._setup_event_listeners()
            
            logger.info(f"Game loaded: {save_name}")
            
            # Emit game loaded event
            self.event_system.emit("game_loaded", {
                "save_name": save_name
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Error loading game: {e}")
            return False