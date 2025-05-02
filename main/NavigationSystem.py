"""
Navigation System for A Sound of Distant Thunder
Handles movement between game locations and travel mechanics.
"""
import logging
import random

# Configure logging
logger = logging.getLogger("NavigationSystem")

class NavigationSystem:
    """
    System for handling player navigation between locations.
    Manages pathfinding, transitions, and travel events.
    """
    def __init__(self, game_engine):
        """
        Initialize the navigation system.
        
        Args:
            game_engine: GameEngine instance
        """
        self.game_engine = game_engine
        
        # Register event listeners
        self.game_engine.event_system.subscribe("go_to_location", self._on_go_to_location)
        
        logger.info("Navigation System initialized")
    
    def _on_go_to_location(self, data):
        """
        Handle go to location event.
        
        Args:
            data (dict): Event data with target location
        """
        location_id = data.get("location_id")
        if location_id:
            self.navigate_to_location(location_id)
    
    def navigate_to_location(self, target_location_id):
        """
        Navigate to the specified location.
        
        Args:
            target_location_id (str): ID of the target location
            
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        # Check if location exists
        location_data = self.game_engine.data_manager.get_data("locations", target_location_id)
        if not location_data:
            logger.error(f"Location data not found: {target_location_id}")
            return False
        
        # Check if direct navigation is possible
        current_location_id = self.game_engine.game_state.current_location
        current_location_data = self.game_engine.data_manager.get_data("locations", current_location_id)
        
        if current_location_data:
            # Check if there's a direct connection
            exits = current_location_data.get("exits", {})
            
            # Try to find the target in exits by ID or direction
            direct_connection = False
            
            if isinstance(exits, dict):
                # Check if target is a direct exit
                for direction, exit_id in exits.items():
                    if exit_id == target_location_id:
                        direct_connection = True
                        break
            
            if not direct_connection:
                # No direct connection - try to find a path
                path = self._find_path(current_location_id, target_location_id)
                
                if path:
                    # Start navigation along path
                    return self._navigate_along_path(path)
                else:
                    logger.warning(f"No path found from {current_location_id} to {target_location_id}")
                    
                    # Show message to the player
                    self.game_engine.event_system.emit("message_displayed", {
                        "text": "You can't go there from here."
                    })
                    
                    return False
        
        # Check if there are any special navigation requirements
        requirements = location_data.get("navigation_requirements", {})
        if requirements:
            # Check if requirements are met
            for req_type, req_value in requirements.items():
                if req_type == "item":
                    # Check if player has required item
                    if not self.game_engine.game_state.has_item(req_value):
                        # Show message
                        self.game_engine.event_system.emit("message_displayed", {
                            "text": f"You need a {req_value} to go there."
                        })
                        return False
                elif req_type == "variable":
                    # Check if game variable has required value
                    var_name, var_value = req_value.split("=")
                    if self.game_engine.game_state.get_variable(var_name) != var_value:
                        # Show message
                        self.game_engine.event_system.emit("message_displayed", {
                            "text": "You can't go there yet."
                        })
                        return False
                elif req_type == "flag":
                    # Check if flag is set
                    if not self.game_engine.game_state.get_variable(req_value, False):
                        # Show message
                        self.game_engine.event_system.emit("message_displayed", {
                            "text": "You can't go there yet."
                        })
                        return False
        
        # Check if there are any travel events
        travel_events = self._get_travel_events(current_location_id, target_location_id)
        for event in travel_events:
            # Process travel event
            self.game_engine.event_system.emit("game_event_triggered", {
                "event_id": event
            })
        
        # Navigate to the target location
        success = self.game_engine.game_state.load_location(target_location_id)
        
        if success:
            logger.info(f"Navigated to: {target_location_id}")
            
            # Emit travel completed event
            self.game_engine.event_system.emit("travel_completed", {
                "from_location": current_location_id,
                "to_location": target_location_id
            })
            
            return True
        else:
            logger.error(f"Failed to load location: {target_location_id}")
            return False
    
    def _find_path(self, start_location, target_location):
        """
        Find a path between two locations using BFS.
        
        Args:
            start_location (str): Starting location ID
            target_location (str): Target location ID
            
        Returns:
            list: Sequence of location IDs forming the path, or None if no path found
        """
        # Use breadth-first search to find a path
        queue = [(start_location, [start_location])]
        visited = {start_location}
        
        while queue:
            current, path = queue.pop(0)
            
            # Get the current location's connections
            location_data = self.game_engine.data_manager.get_data("locations", current)
            if not location_data:
                continue
                
            exits = location_data.get("exits", {})
            if not isinstance(exits, dict):
                continue
                
            # Check all exits
            for _, next_location in exits.items():
                if next_location == target_location:
                    # Found the target
                    return path + [next_location]
                    
                if next_location not in visited:
                    visited.add(next_location)
                    queue.append((next_location, path + [next_location]))
        
        # No path found
        return None
    
    def _navigate_along_path(self, path):
        """
        Navigate along a path of locations.
        
        Args:
            path (list): Sequence of location IDs
            
        Returns:
            bool: True if navigation succeeded, False otherwise
        """
        # Skip first location (current location)
        if len(path) <= 1:
            return True
            
        # For now, just go directly to the next location
        next_location = path[1]
        return self.game_engine.game_state.load_location(next_location)
    
    def _get_travel_events(self, from_location, to_location):
        """
        Get events that should trigger during travel.
        
        Args:
            from_location (str): Starting location ID
            to_location (str): Target location ID
            
        Returns:
            list: List of event IDs to trigger
        """
        # Check for global travel events
        global_events = []
        
        # Check time of day for random encounters
        game_time = self.game_engine.game_state.time
        hour = game_time.get("hour", 12)
        
        # Nighttime has more dangerous events
        if 22 <= hour or hour <= 5:
            # Nighttime - higher chance of encounters
            if random.random() < 0.3:
                global_events.append("night_travel_encounter")
        else:
            # Daytime - lower chance of encounters
            if random.random() < 0.1:
                global_events.append("day_travel_encounter")
        
        # Check for specific path events
        path_key = f"{from_location}_{to_location}"
        travel_events = self.game_engine.data_manager.get_data("travel_events", path_key)
        
        if travel_events:
            # Add specific path events
            for event in travel_events:
                # Check if event should trigger
                if "condition" in event:
                    condition = event["condition"]
                    # Check condition (simplified)
                    if self.game_engine.game_state.get_variable(condition["flag"], False) == condition["value"]:
                        global_events.append(event["id"])
                else:
                    # No condition, always trigger
                    global_events.append(event["id"])
        
        return global_events