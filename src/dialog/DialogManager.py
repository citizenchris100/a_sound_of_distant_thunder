"""
Dialog System for A Sound of Distant Thunder
Handles conversation flow, conditions, and effects in a highly data-driven way.
Reduces complexity through modular design and clear separation of concerns.
"""
import logging
from enum import Enum

# Configure logging
logger = logging.getLogger("DialogSystem")

class DialogResult(Enum):
    """Enumeration of possible dialog action results for better code clarity"""
    SUCCESS = "success"
    FAILED = "failed"
    CONDITION_FAILED = "condition_failed"
    ACTION_INVALID = "action_invalid"
    NODE_NOT_FOUND = "node_not_found"
    DIALOG_END = "dialog_end"

class DialogNodeType(Enum):
    """Enumeration of dialog node types for better code clarity"""
    TEXT = "text"  # Simple text with auto-advance
    OPTIONS = "options"  # Text with player-selectable responses
    RESPONSE = "response"  # NPC response to player
    END = "end"  # Dialog end node

class DialogManager:
    """
    Manages dialog flow, conditions, and effects.
    Uses a data-driven approach to reduce complexity.
    """
    def __init__(self, data_manager, game_state, event_system):
        """
        Initialize the dialog manager.
        
        Args:
            data_manager: DataManager instance
            game_state: GameState instance
            event_system: EventSystem instance
        """
        self.data_manager = data_manager
        self.game_state = game_state
        self.event_system = event_system
        
        # Dialog state
        self.current_dialog = None
        self.current_node = None
        self.current_npc = None
        self.dialog_history = []
        self.dialog_variables = {}
        self.visited_nodes = set()
        
        # Register for events
        self.event_system.subscribe("auto_start_dialog", self._on_auto_start_dialog)
        self.event_system.subscribe("skip_dialog", self._on_skip_dialog)
        self.event_system.subscribe("dialog_request_advance", self._on_dialog_request_advance)
        
        logger.info("Dialog Manager initialized")
    
    def _on_auto_start_dialog(self, data):
        """
        Handle auto-start dialog event.
        
        Args:
            data (dict): Event data with dialog_id and npc_id
        """
        dialog_id = data.get("dialog_id")
        npc_id = data.get("npc_id")
        
        if dialog_id and npc_id:
            self.start_dialog(dialog_id, npc_id)
    
    def _on_skip_dialog(self, data):
        """
        Handle skip dialog event.
        
        Args:
            data (dict): Event data
        """
        if self.current_dialog and self.current_node:
            self._advance_to_next_node()
    
    def _on_dialog_request_advance(self, data):
        """
        Handle dialog advance request event.
        
        Args:
            data (dict): Event data
        """
        if self.current_dialog and self.current_node:
            node_data = self.current_dialog["nodes"].get(self.current_node)
            if node_data and node_data.get("type") in [DialogNodeType.TEXT.value, DialogNodeType.RESPONSE.value]:
                # Auto-advance for text and response nodes
                self._advance_to_next_node()
    
    def start_dialog(self, dialog_id, npc_id):
        """
        Start a dialog with the specified NPC.
        
        Args:
            dialog_id (str): ID of the dialog tree to use
            npc_id (str): ID of the NPC to converse with
            
        Returns:
            dict: Initial dialog node data, or None if dialog not found
        """
        # Get dialog data
        dialog_data = self.data_manager.get_data("dialogs", dialog_id)
        if not dialog_data:
            logger.error(f"Dialog not found: {dialog_id}")
            return None
        
        # Reset dialog state
        self.current_dialog = dialog_data
        self.current_node = dialog_data.get("start_node")
        self.current_npc = npc_id
        self.dialog_history = []
        self.visited_nodes = set()
        
        # Initialize dialog variables
        self._initialize_dialog_variables()
        
        # Emit dialog started event
        self.event_system.emit("dialog_started", {
            "dialog_id": dialog_id,
            "npc_id": npc_id
        })
        
        logger.info(f"Started dialog: {dialog_id} with NPC: {npc_id}")
        
        # Process and return the first node
        return self.process_current_node()
    
    def _initialize_dialog_variables(self):
        """Initialize dialog variables from game state and NPC"""
        # Reset dialog variables
        self.dialog_variables = {
            "player_name": self.game_state.player.get_name()
        }
        
        # Add game time variables
        game_time = getattr(self.game_state, "time", {})
        if game_time:
            self.dialog_variables["game_day"] = game_time.get("day", 1)
            self.dialog_variables["game_hour"] = game_time.get("hour", 8)
            
            # Add time of day description
            hour = game_time.get("hour", 8)
            if 5 <= hour < 12:
                time_of_day = "morning"
            elif 12 <= hour < 17:
                time_of_day = "afternoon"
            elif 17 <= hour < 21:
                time_of_day = "evening"
            else:
                time_of_day = "night"
            self.dialog_variables["time_of_day"] = time_of_day
        
        # Add NPC-specific variables
        npc = self.game_state.get_npc(self.current_npc)
        if npc:
            self.dialog_variables["npc_name"] = getattr(npc, "name", "Unknown")
            self.dialog_variables["npc_suspicion"] = getattr(npc, "suspicion", 0)
            self.dialog_variables["npc_trust"] = getattr(npc, "trust_level", 0)
            self.dialog_variables["is_assimilated"] = getattr(npc, "is_assimilated", False)
            self.dialog_variables["in_coalition"] = self.current_npc in self.game_state.coalition_members
        
        # Add game state variables
        self.dialog_variables["coalition_size"] = len(self.game_state.coalition_members)
        self.dialog_variables["known_assimilated"] = len(self.game_state.known_assimilated)
        
        # Copy global variables that start with "dialog_"
        for var_name, var_value in self.game_state.global_variables.items():
            if var_name.startswith("dialog_"):
                self.dialog_variables[var_name] = var_value
    
    def select_option(self, option_id):
        """
        Choose a dialog option.
        
        Args:
            option_id (str): ID of the selected option
            
        Returns:
            dict: Next dialog node data, or None if dialog ends
        """
        if not self.current_dialog or not self.current_node:
            logger.error("No active dialog")
            return None
        
        # Find the current node data
        node_data = self.current_dialog["nodes"].get(self.current_node)
        if not node_data:
            logger.error(f"Node not found: {self.current_node}")
            return None
        
        # Find the selected option
        options = node_data.get("options", [])
        selected_option = None
        
        for option in options:
            if option.get("id") == option_id:
                selected_option = option
                break
        
        if not selected_option:
            logger.error(f"Option not found: {option_id}")
            return None
        
        # Record this choice in history
        option_text = selected_option.get("text", "")
        self.dialog_history.append({
            "type": "player_choice",
            "node": self.current_node,
            "option_id": option_id,
            "text": option_text
        })
        
        # Create a response node for the player's choice
        response_node = {
            "type": DialogNodeType.RESPONSE.value,
            "text": option_text,
            "speaker": "player"
        }
        
        # Emit response node
        self.event_system.emit("dialog_node_updated", {
            "id": f"player_response_{len(self.dialog_history)}",
            "type": DialogNodeType.RESPONSE.value,
            "text": option_text,
            "speaker": "player",
            "npc_id": self.current_npc
        })
        
        # Apply effects from this option
        result = self._apply_option_effects(selected_option)
        
        if result == DialogResult.DIALOG_END:
            # Option ended the dialog
            self.end_dialog()
            return None
        
        # Move to the next node
        next_node = selected_option.get("next")
        if not next_node:
            # Dialog ends
            self.end_dialog()
            return None
        
        self.current_node = next_node
        return self.process_current_node()
    
    def process_current_node(self):
        """
        Process the current dialog node and return its data.
        
        Returns:
            dict: Processed node data, or None if node doesn't exist or dialog ends
        """
        if not self.current_node or not self.current_dialog:
            logger.error("No active dialog or current node")
            return None
        
        # Get node data
        node_data = self.current_dialog["nodes"].get(self.current_node)
        if not node_data:
            logger.error(f"Node not found: {self.current_node}")
            self.end_dialog()
            return None
        
        # Mark this node as visited
        self.visited_nodes.add(self.current_node)
        
        # Process node conditions if present
        if "condition" in node_data:
            condition_result = self._evaluate_condition(node_data["condition"])
            
            if not condition_result:
                # Condition failed, go to fallback node if available
                fallback = node_data.get("fallback")
                if fallback:
                    logger.debug(f"Node condition failed, going to fallback: {fallback}")
                    self.current_node = fallback
                    return self.process_current_node()
                else:
                    # No fallback, end dialog
                    logger.info("Node condition failed with no fallback, ending dialog")
                    self.end_dialog()
                    return None
        
        # Apply node effects if present
        if "effects" in node_data:
            self._apply_node_effects(node_data["effects"])
        
        # Determine node type
        node_type = node_data.get("type", DialogNodeType.TEXT.value)
        
        # Process text with variable substitution
        text = node_data.get("text", "")
        processed_text = self._process_text_variables(text)
        
        # Determine speaker
        speaker = node_data.get("speaker", "npc")
        
        # Record in history
        self.dialog_history.append({
            "type": node_type,
            "node": self.current_node,
            "text": processed_text,
            "speaker": speaker
        })
        
        # Prepare the response data
        response_data = {
            "id": self.current_node,
            "type": node_type,
            "text": processed_text,
            "npc_id": self.current_npc,
            "speaker": speaker
        }
        
        # Process based on node type
        if node_type == DialogNodeType.OPTIONS.value:
            # Process options if present
            options = []
            
            for option in node_data.get("options", []):
                # Check if this option has a condition
                if "condition" in option and not self._evaluate_condition(option["condition"]):
                    continue
                
                # Process option text with variables
                option_text = self._process_text_variables(option.get("text", ""))
                
                # Add processed option
                options.append({
                    "id": option.get("id"),
                    "text": option_text
                })
            
            response_data["options"] = options
            
            # Check if we have no valid options
            if not options:
                if node_data.get("no_options_next"):
                    # Auto-advance to the next node
                    logger.debug(f"No valid options, auto-advancing to: {node_data['no_options_next']}")
                    self.current_node = node_data["no_options_next"]
                    return self.process_current_node()
                else:
                    # No valid options and no fallback, end dialog
                    logger.debug("No valid options and no fallback, ending dialog")
                    self.end_dialog()
                    return None
        else:
            # Handle automatic progression for non-option nodes
            if "next" in node_data:
                response_data["auto_advance"] = True
                auto_delay = node_data.get("auto_delay", 1.5)
                
                if auto_delay > 0:
                    response_data["auto_delay"] = auto_delay
                
                # Store next node for later
                response_data["next_node"] = node_data["next"]
            else:
                # No next node, so this is an end node
                response_data["end_dialog"] = True
        
        # Emit dialog node updated event
        self.event_system.emit("dialog_node_updated", response_data)
        
        return response_data
    
    def _advance_to_next_node(self):
        """
        Advance to the next node for auto-progression.
        
        Returns:
            dict: Next dialog node data, or None if dialog ends
        """
        if not self.current_dialog or not self.current_node:
            return None
        
        node_data = self.current_dialog["nodes"].get(self.current_node)
        if not node_data or "next" not in node_data:
            self.end_dialog()
            return None
        
        # Record this in history
        self.dialog_history.append({
            "type": "auto_advance",
            "from_node": self.current_node,
            "to_node": node_data["next"]
        })
        
        # Move to next node
        self.current_node = node_data["next"]
        return self.process_current_node()
    
    def _process_text_variables(self, text):
        """
        Process text template with variables.
        
        Args:
            text (str): Text template with {variable} placeholders
            
        Returns:
            str: Processed text with variables replaced
        """
        if not text:
            return ""
        
        try:
            return text.format(**self.dialog_variables)
        except KeyError as e:
            logger.warning(f"Missing dialog variable: {e}")
            return text.replace(f"{{{e.args[0]}}}", f"[{e.args[0]}]")
        except Exception as e:
            logger.error(f"Error processing text variables: {e}")
            return text
    
    def _apply_option_effects(self, option):
        """
        Apply effects from a dialog option.
        
        Args:
            option (dict): Option data with effects
            
        Returns:
            DialogResult: Result of applying effects
        """
        # Apply suspicion effect
        if "suspicion_effect" in option and self.current_npc:
            amount = option["suspicion_effect"]
            self.game_state.update_npc_suspicion(self.current_npc, amount)
            logger.debug(f"Applied suspicion effect: {amount}")
            
            # Update dialog variable
            npc = self.game_state.get_npc(self.current_npc)
            if npc:
                self.dialog_variables["npc_suspicion"] = getattr(npc, "suspicion", 0)
        
        # Apply trust effect
        if "trust_effect" in option and self.current_npc:
            amount = option["trust_effect"]
            self.game_state.update_npc_trust(self.current_npc, amount)
            logger.debug(f"Applied trust effect: {amount}")
            
            # Update dialog variable
            npc = self.game_state.get_npc(self.current_npc)
            if npc:
                self.dialog_variables["npc_trust"] = getattr(npc, "trust_level", 0)
        
        # Set dialog variables
        if "set_variable" in option:
            for var_name, var_value in option["set_variable"].items():
                self.dialog_variables[var_name] = var_value
                logger.debug(f"Set dialog variable: {var_name}={var_value}")
        
        # Set global variables
        if "set_global" in option:
            for var_name, var_value in option["set_global"].items():
                self.game_state.set_variable(var_name, var_value)
                logger.debug(f"Set global variable: {var_name}={var_value}")
        
        # Execute actions
        if "actions" in option:
            actions = option["actions"]
            if isinstance(actions, list):
                for action in actions:
                    result = self._execute_action(action)
                    if result == DialogResult.DIALOG_END:
                        return DialogResult.DIALOG_END
            else:
                result = self._execute_action(actions)
                if result == DialogResult.DIALOG_END:
                    return DialogResult.DIALOG_END
        
        # Check for end_dialog flag
        if option.get("end_dialog", False):
            return DialogResult.DIALOG_END
        
        return DialogResult.SUCCESS
    
    def _apply_node_effects(self, effects):
        """
        Apply effects from a dialog node.
        
        Args:
            effects (dict or list): Node effects to apply
            
        Returns:
            DialogResult: Result of applying effects
        """
        if isinstance(effects, list):
            for effect in effects:
                result = self._apply_node_effects(effect)
                if result == DialogResult.DIALOG_END:
                    return DialogResult.DIALOG_END
            return DialogResult.SUCCESS
        
        # Apply individual effect
        if "set_variable" in effects:
            for var_name, var_value in effects["set_variable"].items():
                self.dialog_variables[var_name] = var_value
                logger.debug(f"Set dialog variable: {var_name}={var_value}")
        
        if "set_global" in effects:
            for var_name, var_value in effects["set_global"].items():
                self.game_state.set_variable(var_name, var_value)
                logger.debug(f"Set global variable: {var_name}={var_value}")
        
        if "action" in effects:
            result = self._execute_action(effects["action"])
            if result == DialogResult.DIALOG_END:
                return DialogResult.DIALOG_END
        
        return DialogResult.SUCCESS
    
    def _execute_action(self, action):
        """
        Execute a dialog action.
        
        Args:
            action (str or dict): Action to execute
            
        Returns:
            DialogResult: Result of the action
        """
        if isinstance(action, str):
            # Simple action by name
            if action == "end_dialog":
                return DialogResult.DIALOG_END
            elif action == "initiate_combat":
                self.event_system.emit("combat_initiated", {
                    "enemy_ids": [self.current_npc]
                })
                logger.info(f"Initiated combat with NPC: {self.current_npc}")
                return DialogResult.DIALOG_END
            elif action == "join_coalition":
                self.game_state.add_to_coalition(self.current_npc)
                logger.info(f"Added NPC to coalition: {self.current_npc}")
                return DialogResult.SUCCESS
            elif action.startswith("give_item:"):
                item_id = action.split(":")[1]
                self.game_state.add_item_to_inventory(item_id)
                logger.info(f"Gave item to player: {item_id}")
                return DialogResult.SUCCESS
            elif action.startswith("take_item:"):
                item_id = action.split(":")[1]
                self.game_state.remove_item(item_id)
                logger.info(f"Took item from player: {item_id}")
                return DialogResult.SUCCESS
        elif isinstance(action, dict):
            # Complex action with parameters
            action_type = action.get("type")
            params = action.get("params", {})
            
            if not action_type:
                logger.error("Action missing type")
                return DialogResult.ACTION_INVALID
            
            if action_type == "end_dialog":
                return DialogResult.DIALOG_END
            
            elif action_type == "modify_variable":
                var_name = params.get("variable")
                operation = params.get("operation", "set")
                value = params.get("value")
                
                if var_name and value is not None:
                    if operation == "set":
                        self.game_state.set_variable(var_name, value)
                    elif operation == "increment":
                        current = self.game_state.get_variable(var_name, 0)
                        self.game_state.set_variable(var_name, current + value)
                    elif operation == "decrement":
                        current = self.game_state.get_variable(var_name, 0)
                        self.game_state.set_variable(var_name, current - value)
                    elif operation == "multiply":
                        current = self.game_state.get_variable(var_name, 0)
                        self.game_state.set_variable(var_name, current * value)
                    
                    logger.debug(f"Modified variable: {var_name} ({operation}) = {self.game_state.get_variable(var_name)}")
                    return DialogResult.SUCCESS
                return DialogResult.ACTION_INVALID
            
            elif action_type == "give_item":
                item_id = params.get("item_id")
                if item_id:
                    success = self.game_state.add_item_to_inventory(item_id)
                    logger.info(f"Gave item to player: {item_id} (success: {success})")
                    return DialogResult.SUCCESS if success else DialogResult.FAILED
                return DialogResult.ACTION_INVALID
            
            elif action_type == "take_item":
                item_id = params.get("item_id")
                if item_id:
                    success = self.game_state.remove_item(item_id)
                    logger.info(f"Took item from player: {item_id} (success: {success})")
                    return DialogResult.SUCCESS if success else DialogResult.FAILED
                return DialogResult.ACTION_INVALID
            
            elif action_type == "assimilate_npc":
                target_npc_id = params.get("npc_id", self.current_npc)
                method = params.get("method", "dialog")
                
                # Check if assimilation system exists
                if hasattr(self.game_engine, "assimilation_system"):
                    success = self.game_engine.assimilation_system.assimilate_npc(target_npc_id, method)
                    logger.info(f"Assimilated NPC via dialog: {target_npc_id} (success: {success})")
                    return DialogResult.SUCCESS if success else DialogResult.FAILED
                else:
                    logger.error("Assimilation system not available")
                    return DialogResult.FAILED
            
            elif action_type == "start_event":
                event_id = params.get("event_id")
                if event_id:
                    self.game_engine.event_system.emit("game_event_triggered", {
                        "event_id": event_id
                    })
                    logger.info(f"Started game event: {event_id}")
                    return DialogResult.SUCCESS
                return DialogResult.ACTION_INVALID
            
            elif action_type == "join_coalition":
                target_npc_id = params.get("npc_id", self.current_npc)
                success = self.game_state.add_to_coalition(target_npc_id)
                logger.info(f"Added NPC to coalition: {target_npc_id} (success: {success})")
                return DialogResult.SUCCESS if success else DialogResult.FAILED
            
            elif action_type == "change_location":
                location_id = params.get("location_id")
                transition = params.get("transition", "fade")
                
                if location_id:
                    # End dialog first
                    self.end_dialog()
                    
                    # Then change location
                    event_data = {
                        "new_location": location_id
                    }
                    
                    if transition:
                        event_data["transition"] = transition
                    
                    self.game_engine.event_system.emit("location_changed", event_data)
                    logger.info(f"Changed location via dialog: {location_id}")
                    return DialogResult.DIALOG_END
                return DialogResult.ACTION_INVALID
            
            elif action_type == "conditional":
                condition = params.get("condition")
                if_action = params.get("if_true")
                else_action = params.get("if_false")
                
                if self._evaluate_condition(condition):
                    if if_action:
                        return self._execute_action(if_action)
                else:
                    if else_action:
                        return self._execute_action(else_action)
                return DialogResult.SUCCESS
            
            elif action_type == "multiple":
                actions = params.get("actions", [])
                
                for sub_action in actions:
                    result = self._execute_action(sub_action)
                    if result == DialogResult.DIALOG_END:
                        return DialogResult.DIALOG_END
                
                return DialogResult.SUCCESS
            
            else:
                logger.warning(f"Unknown action type: {action_type}")
                return DialogResult.ACTION_INVALID
        
        # Default success
        return DialogResult.SUCCESS
    
    # Updated DialogManager class (excerpt)

    def _evaluate_condition(self, condition):
        """
        Evaluate a dialog condition using the condition evaluator.
        
        Args:
            condition (dict or str): Condition to evaluate
            
        Returns:
            bool: True if condition is met, False otherwise
        """
        # Use the condition evaluator
        condition_evaluator = self.game_engine.condition_evaluator
        
        # Set dialog-specific context
        condition_evaluator.current_npc = self.current_npc
        condition_evaluator.dialog_variables = self.dialog_variables
        condition_evaluator.visited_nodes = self.visited_nodes
        
        # Evaluate condition
        return condition_evaluator.evaluate_condition(condition)
    
    def _compare_values(self, value1, value2, operation="equals"):
        """
        Compare two values using the specified operation.
        
        Args:
            value1: First value
            value2: Second value
            operation (str): Comparison operation
            
        Returns:
            bool: Result of the comparison
        """
        if operation == "equals":
            return value1 == value2
        elif operation == "not_equals":
            return value1 != value2
        elif operation == "greater_than":
            return value1 > value2
        elif operation == "less_than":
            return value1 < value2
        elif operation == "greater_equal":
            return value1 >= value2
        elif operation == "less_equal":
            return value1 <= value2
        elif operation == "contains":
            if isinstance(value1, (list, str, dict)):
                return value2 in value1
            return False
        else:
            logger.warning(f"Unknown comparison operation: {operation}")
            return value1 == value2
    
    def end_dialog(self):
        """End the current dialog"""
        if self.current_dialog:
            self.event_system.emit("dialog_ended", {
                "npc_id": self.current_npc,
                "dialog_id": self.current_dialog.get("id")
            })
            
            logger.info(f"Dialog ended with NPC: {self.current_npc}")
        
        # Clear dialog state
        self.current_dialog = None
        self.current_node = None
        self.current_npc = None
        self.dialog_variables = {}
        self.visited_nodes = set()


class DialogUI:
    """UI component for displaying dialogs"""
    def __init__(self, game_engine, asset_manager, rect):
        """
        Initialize the dialog UI.
        
        Args:
            game_engine: GameEngine instance
            asset_manager: AssetManager instance
            rect (pygame.Rect): Rectangle defining UI position and size
        """
        self.game_engine = game_engine
        self.asset_manager = asset_manager
        self.rect = rect
        self.visible = False
        
        # Dialog state
        self.current_npc = None
        self.current_text = ""
        self.current_speaker = "npc"
        self.current_node_type = DialogNodeType.TEXT.value
        self.current_options = []
        self.selected_option = -1
        
        # Animation
        self.text_reveal_index = 0
        self.text_reveal_speed = 30  # Characters per second
        self.text_reveal_timer = 0
        self.auto_advance = False
        self.auto_advance_delay = 1.5
        self.auto_advance_timer = 0
        
        # Visual elements
        self.background = asset_manager.get_image("ui_dialog_bg")
        self.npc_portrait = None
        self.player_portrait = None  # Could load player portrait here
        
        # Theme
        self.theme = None
        
        # Register events
        game_engine.event_system.subscribe("dialog_node_updated", self._on_dialog_node_updated)
        game_engine.event_system.subscribe("dialog_ended", self._on_dialog_ended)
        
        logger.info("Dialog UI initialized")
    
    def set_theme(self, theme):
        """
        Set the UI theme.
        
        Args:
            theme: UITheme instance
        """
        self.theme = theme
    
    def _on_dialog_node_updated(self, data):
        """
        Handle dialog node updated event.
        
        Args:
            data (dict): Dialog node data
        """
        self.visible = True
        
        # Update NPC
        npc_id = data.get("npc_id")
        if npc_id != self.current_npc:
            self.current_npc = npc_id
            
            # Load NPC portrait
            self.npc_portrait = self.asset_manager.get_image(f"portrait_{npc_id}")
        
        # Update text and options
        self.current_text = data.get("text", "")
        self.current_node_type = data.get("type", DialogNodeType.TEXT.value)
        self.current_speaker = data.get("speaker", "npc")
        self.current_options = data.get("options", [])
        self.selected_option = -1
        
        # Reset text reveal animation
        self.text_reveal_index = 0
        self.text_reveal_timer = 0
        
        # Setup auto-advance if needed
        self.auto_advance = data.get("auto_advance", False)
        self.auto_advance_delay = data.get("auto_delay", 1.5)
        self.auto_advance_timer = 0
    
    def _on_dialog_ended(self, data):
        """
        Handle dialog ended event.
        
        Args:
            data (dict): Dialog ended data
        """
        self.visible = False
        self.current_npc = None
        self.current_text = ""
        self.current_options = []
        self.selected_option = -1
    
    def update(self, dt):
        """
        Update dialog UI state.
        
        Args:
            dt (float): Time delta in seconds
        """
        if not self.visible:
            return
        
        # Update text reveal animation
        if self.text_reveal_index < len(self.current_text):
            self.text_reveal_timer += dt
            chars_to_reveal = int(self.text_reveal_speed * self.text_reveal_timer)
            if chars_to_reveal > 0:
                self.text_reveal_timer = 0
                self.text_reveal_index = min(
                    self.text_reveal_index + chars_to_reveal,
                    len(self.current_text)
                )
        elif self.auto_advance:
            # Text is fully revealed, update auto-advance timer
            self.auto_advance_timer += dt
            if self.auto_advance_timer >= self.auto_advance_delay:
                # Time to advance
                self.auto_advance = False
                self.auto_advance_timer = 0
                
                # Request dialog advance
                self.game_engine.event_system.emit("dialog_request_advance", {})
    
    def render(self, surface):
        """
        Render the dialog UI to the given surface.
        
        Args:
            surface (pygame.Surface): Surface to render on
        """
        if not self.visible:
            return
        
        # Draw background using theme if available
        if self.theme:
            self.theme.draw_panel(surface, self.rect)
        elif self.background:
            surface.blit(self.background, self.rect)
        else:
            # Fallback to a simple rect
            pygame.draw.rect(surface, (30, 30, 50), self.rect, 0)
        
        # Draw speaker portrait
        if self.current_speaker == "npc" and self.npc_portrait:
            portrait_rect = pygame.Rect(self.rect.left + 10, self.rect.top + 10, 80, 80)
            surface.blit(self.npc_portrait, portrait_rect)
        elif self.current_speaker == "player" and self.player_portrait:
            portrait_rect = pygame.Rect(self.rect.left + 10, self.rect.top + 10, 80, 80)
            surface.blit(self.player_portrait, portrait_rect)
        
        # Draw speaker name
        speaker_name = "You" if self.current_speaker == "player" else "NPC"
        
        if self.current_npc:
            npc = self.game_engine.game_state.get_npc(self.current_npc)
            if npc and self.current_speaker == "npc":
                speaker_name = getattr(npc, "name", "NPC")
        
        # Render name with theme if available
        if self.theme:
            name_pos = (self.rect.left + 100, self.rect.top + 10)
            self.theme.draw_text(
                surface,
                speaker_name,
                self.asset_manager.get_font("dialog"),
                name_pos,
                color=self.theme.highlight_color
            )
        else:
            # Fallback
            font = self.asset_manager.get_font("dialog")
            name_surface = font.render(speaker_name, True, (200, 200, 255))
            surface.blit(name_surface, (self.rect.left + 100, self.rect.top + 10))
        
        # Draw text
        revealed_text = self.current_text[:self.text_reveal_index]
        text_rect = pygame.Rect(
            self.rect.left + 100,
            self.rect.top + 40,
            self.rect.width - 110,
            80
        )
        
        if self.theme:
            self.theme.draw_text(
                surface, 
                revealed_text, 
                self.asset_manager.get_font("dialog"),
                (text_rect.left, text_rect.top),
                max_width=text_rect.width
            )
        else:
            self._render_text(surface, revealed_text, text_rect)
        
        # Draw options if text is fully revealed and we have options
        if self.text_reveal_index >= len(self.current_text) and self.current_node_type == DialogNodeType.OPTIONS.value:
            self._render_options(surface)
        
        # Draw advance indicator for non-option nodes
        elif self.text_reveal_index >= len(self.current_text) and self.current_node_type != DialogNodeType.OPTIONS.value:
            # Draw indicator to show dialog can be advanced
            indicator_rect = pygame.Rect(
                self.rect.right - 30,
                self.rect.bottom - 30,
                20,
                20
            )
            
            # Pulsing effect based on auto-advance timer
            if self.auto_advance:
                alpha = 128 + int(127 * (1 - self.auto_advance_timer / self.auto_advance_delay))
            else:
                alpha = 255
            
            if self.theme:
                pygame.draw.polygon(
                    surface,
                    (*self.theme.highlight_color[:3], alpha),
                    [
                        (indicator_rect.left, indicator_rect.top),
                        (indicator_rect.right, indicator_rect.centery),
                        (indicator_rect.left, indicator_rect.bottom)
                    ]
                )
            else:
                # Fallback
                pygame.draw.polygon(
                    surface,
                    (200, 200, 255, alpha),
                    [
                        (indicator_rect.left, indicator_rect.top),
                        (indicator_rect.right, indicator_rect.centery),
                        (indicator_rect.left, indicator_rect.bottom)
                    ]
                )
    
    def _render_text(self, surface, text, rect):
        """
        Render dialog text with word wrapping.
        
        Args:
            surface (pygame.Surface): Surface to render on
            text (str): Text to render
            rect (pygame.Rect): Rectangle to contain the text
        """
        font = self.asset_manager.get_font("dialog")
        
        # Word wrap implementation
        words = text.split(' ')
        space_width = font.size(' ')[0]
        x, y = rect.left, rect.top
        
        for word in words:
            word_surface = font.render(word, True, (255, 255, 255))
            word_width, word_height = word_surface.get_size()
            
            if x + word_width >= rect.right:
                x = rect.left
                y += word_height
                
            surface.blit(word_surface, (x, y))
            x += word_width + space_width
    
    def _render_options(self, surface):
        """Render dialog options"""
        if not self.current_options:
            return
        
        option_font = self.asset_manager.get_font("dialog_option")
        option_height = 25
        option_padding = 5
        
        # Calculate starting position
        start_y = self.rect.bottom - (len(self.current_options) * (option_height + option_padding)) - 10
        
        for i, option in enumerate(self.current_options):
            # Create option rectangle
            option_rect = pygame.Rect(
                self.rect.left + 20,
                start_y + i * (option_height + option_padding),
                self.rect.width - 40,
                option_height
            )
            
            # Draw option using theme if available
            option_text = option["text"]
            
            if self.theme:
                self.theme.draw_button(
                    surface,
                    option_rect,
                    option_text,
                    option_font,
                    is_hover=(i == self.selected_option),
                    is_selected=(i == self.selected_option)
                )
            else:
                # Fallback to original implementation
                if i == self.selected_option:
                    pygame.draw.rect(surface, (100, 100, 255), option_rect, 0)
                    text_color = (255, 255, 255)
                else:
                    pygame.draw.rect(surface, (50, 50, 80), option_rect, 0)
                    text_color = (200, 200, 200)
                
                # Draw option text
                option_text_surf = option_font.render(option_text, True, text_color)
                text_rect = option_text_surf.get_rect(midleft=(option_rect.left + 10, option_rect.centery))
                surface.blit(option_text_surf, text_rect)
    
    def handle_mouse_movement(self, event):
        """
        Handle mouse movement events.
        
        Args:
            event (pygame.event.Event): Mouse movement event
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        if not self.visible or not self.rect.collidepoint(event.pos):
            return False
        
        # Check if text is fully revealed
        if self.text_reveal_index < len(self.current_text):
            return False
        
        # Check for option hover
        if self.current_node_type == DialogNodeType.OPTIONS.value:
            option_height = 25
            option_padding =  5
            
            # Calculate starting position
            start_y = self.rect.bottom - (len(self.current_options) * (option_height + option_padding)) - 10
            
            # Check each option
            for i, _ in enumerate(self.current_options):
                option_rect = pygame.Rect(
                    self.rect.left + 20,
                    start_y + i * (option_height + option_padding),
                    self.rect.width - 40,
                    option_height
                )
                
                if option_rect.collidepoint(event.pos):
                    # Hover this option
                    self.selected_option = i
                    return True
        
        return False
    
    def handle_mouse_click(self, event):
        """
        Handle mouse click events.
        
        Args:
            event (pygame.event.Event): Mouse click event
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        if not self.visible or not self.rect.collidepoint(event.pos):
            return False
        
        # If text is still revealing, skip to end
        if self.text_reveal_index < len(self.current_text):
            self.text_reveal_index = len(self.current_text)
            return True
        
        # Check if click was on an option
        if self.current_node_type == DialogNodeType.OPTIONS.value:
            if self.selected_option >= 0 and self.selected_option < len(self.current_options):
                option = self.current_options[self.selected_option]
                option_id = option.get("id")
                
                # Forward to dialog manager
                dialog_manager = getattr(self.game_engine, "dialog_manager", None)
                if dialog_manager:
                    dialog_manager.select_option(option_id)
                
                return True
        else:
            # Non-option node, just advance
            self.game_engine.event_system.emit("dialog_request_advance", {})
            return True
        
        return False
    
    def handle_key_press(self, event):
        """
        Handle keyboard events.
        
        Args:
            event (pygame.event.Event): Key press event
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        if not self.visible:
            return False
        
        import pygame
        
        # Skip text reveal with any key
        if self.text_reveal_index < len(self.current_text):
            self.text_reveal_index = len(self.current_text)
            return True
        
        # Handle options navigation
        if self.current_node_type == DialogNodeType.OPTIONS.value:
            if event.key == pygame.K_UP:
                # Move to previous option
                if self.selected_option > 0:
                    self.selected_option -= 1
                else:
                    self.selected_option = len(self.current_options) - 1
                return True
                
            elif event.key == pygame.K_DOWN:
                # Move to next option
                if self.selected_option < len(self.current_options) - 1:
                    self.selected_option += 1
                else:
                    self.selected_option = 0
                return True
                
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                # Select option
                if self.selected_option >= 0 and self.selected_option < len(self.current_options):
                    option = self.current_options[self.selected_option]
                    option_id = option.get("id")
                    
                    # Forward to dialog manager
                    dialog_manager = getattr(self.game_engine, "dialog_manager", None)
                    if dialog_manager:
                        dialog_manager.select_option(option_id)
                    
                    return True
        else:
            # Advance dialog with Enter or Space
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.game_engine.event_system.emit("dialog_request_advance", {})
                return True
        
        return False