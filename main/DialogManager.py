"""
Dialog System for A Sound of Distant Thunder
Manages dialog flow, conditions, and effects in a data-driven way.
"""
import logging

# Configure logging
logger = logging.getLogger("DialogManager")

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
        
        # Register for events
        self.event_system.subscribe("auto_start_dialog", self._on_auto_start_dialog)
        
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
            
        # Set current dialog state
        self.current_dialog = dialog_data
        self.current_node = dialog_data.get("start_node")
        self.current_npc = npc_id
        self.dialog_history = []
        
        # Reset dialog variables
        self.dialog_variables = {
            "player_name": self.game_state.player.get_name()
        }
        
        # Add NPC-specific variables
        npc = self.game_state.get_npc(npc_id)
        if npc:
            self.dialog_variables["npc_name"] = getattr(npc, "name", "Unknown")
            self.dialog_variables["npc_suspicion"] = getattr(npc, "suspicion", 0)
            self.dialog_variables["npc_trust"] = getattr(npc, "trust_level", 0)
            self.dialog_variables["is_assimilated"] = getattr(npc, "is_assimilated", False)
        
        # Emit dialog started event
        self.event_system.emit("dialog_started", {
            "dialog_id": dialog_id,
            "npc_id": npc_id
        })
        
        # Process and return the first node
        return self.process_current_node()
    
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
        selected_option = None
        for option in node_data.get("options", []):
            if option["id"] == option_id:
                selected_option = option
                break
                
        if not selected_option:
            logger.error(f"Option not found: {option_id}")
            return None
        
        # Record this choice in history
        self.dialog_history.append({
            "node": self.current_node,
            "option": option_id,
            "text": selected_option.get("text", "")
        })
        
        # Apply effects from this option
        self._apply_option_effects(selected_option)
        
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
            
        node_data = self.current_dialog["nodes"].get(self.current_node)
        if not node_data:
            logger.error(f"Node not found: {self.current_node}")
            self.end_dialog()
            return None
        
        # Process node conditions if present
        if "condition" in node_data:
            condition_result = self._evaluate_condition(node_data["condition"])
            
            if not condition_result:
                # Condition failed, go to fallback node if available
                fallback = node_data.get("fallback")
                if fallback:
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
        
        # Process text with variable substitution
        text = node_data.get("text", "")
        processed_text = self._process_text_variables(text)
        
        # Prepare the response data
        response_data = {
            "id": self.current_node,
            "text": processed_text,
            "npc_id": self.current_npc
        }
        
        # Process options if present
        if "options" in node_data:
            options = []
            
            for option in node_data["options"]:
                # Check if this option has a condition
                if "condition" in option and not self._evaluate_condition(option["condition"]):
                    continue
                
                # Process option text with variables
                option_text = self._process_text_variables(option["text"])
                
                # Add processed option
                options.append({
                    "id": option["id"],
                    "text": option_text
                })
            
            response_data["options"] = options
            
            # Check if we have no valid options
            if not options and node_data.get("no_options_next"):
                # Auto-advance to the next node
                self.current_node = node_data["no_options_next"]
                return self.process_current_node()
        
        # Handle automatic progression
        elif "next" in node_data:
            response_data["auto_advance"] = True
            auto_delay = node_data.get("auto_delay", 0)
            
            if auto_delay > 0:
                response_data["auto_delay"] = auto_delay
            
            # Store next node for later
            response_data["next_node"] = node_data["next"]
        else:
            # No options or next, so this is an end node
            response_data["end_dialog"] = True
        
        # Emit dialog node updated event
        self.event_system.emit("dialog_node_updated", response_data)
        
        return response_data
    
    def advance_auto_node(self):
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
            "node": self.current_node,
            "auto": True
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
            return text
        except Exception as e:
            logger.error(f"Error processing text variables: {e}")
            return text
    
    def _apply_option_effects(self, option):
        """
        Apply effects from a dialog option.
        
        Args:
            option (dict): Option data with effects
        """
        # Apply suspicion effect
        if "suspicion_effect" in option and self.current_npc:
            amount = option["suspicion_effect"]
            self.game_state.update_npc_suspicion(self.current_npc, amount)
            logger.debug(f"Applied suspicion effect: {amount}")
            
        # Apply trust effect
        if "trust_effect" in option and self.current_npc:
            amount = option["trust_effect"]
            self.game_state.update_npc_trust(self.current_npc, amount)
            logger.debug(f"Applied trust effect: {amount}")
            
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
            for action in option["actions"]:
                self._execute_action(action)
    
    def _apply_node_effects(self, effects):
        """
        Apply effects from a dialog node.
        
        Args:
            effects (dict or list): Node effects to apply
        """
        if isinstance(effects, list):
            for effect in effects:
                self._apply_node_effects(effect)
            return
            
        # Apply individual effect
        if "set_variable" in effects:
            for var_name, var_value in effects["set_variable"].items():
                self.dialog_variables[var_name] = var_value
        
        if "set_global" in effects:
            for var_name, var_value in effects["set_global"].items():
                self.game_state.set_variable(var_name, var_value)
        
        if "action" in effects:
            self._execute_action(effects["action"])
    
    def _execute_action(self, action):
        """
        Execute a dialog action.
        
        Args:
            action (str or dict): Action to execute
        """
        if isinstance(action, str):
            # Simple action by name
            if action == "initiate_combat":
                self.event_system.emit("combat_initiated", {
                    "enemy_ids": [self.current_npc]
                })
                logger.info(f"Initiated combat with NPC: {self.current_npc}")
            
            elif action == "join_coalition":
                self.game_state.add_to_coalition(self.current_npc)
                logger.info(f"Added NPC to coalition: {self.current_npc}")
            
            elif action.startswith("give_item:"):
                item_id = action.split(":")[1]
                self.game_state.add_item_to_inventory(item_id)
                logger.info(f"Gave item to player: {item_id}")
            
            elif action == "end_dialog":
                self.end_dialog()
                logger.info("Dialog ended by action")
                
        elif isinstance(action, dict):
            # Complex action with parameters
            action_type = action.get("type")
            params = action.get("params", {})
            
            if action_type == "modify_variable":
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
            
            elif action_type == "give_item":
                item_id = params.get("item_id")
                if item_id:
                    self.game_state.add_item_to_inventory(item_id)
                    logger.info(f"Gave item to player: {item_id}")
            
            elif action_type == "remove_item":
                item_id = params.get("item_id")
                if item_id:
                    self.game_state.remove_item(item_id)
                    logger.info(f"Removed item from player: {item_id}")
            
            elif action_type == "assimilate_npc":
                npc_id = params.get("npc_id", self.current_npc)
                self.game_engine.assimilation_system.assimilate_npc(npc_id, "dialog")
                logger.info(f"Assimilated NPC via dialog: {npc_id}")
            
            elif action_type == "start_event":
                event_id = params.get("event_id")
                if event_id:
                    self.game_engine.handle_game_event(event_id)
                    logger.info(f"Started game event: {event_id}")
            
            elif action_type == "end_dialog":
                self.end_dialog()
                logger.info("Dialog ended by action")
    
    def _evaluate_condition(self, condition):
        """
        Evaluate a dialog condition.
        
        Args:
            condition (str or dict): Condition to evaluate
            
        Returns:
            bool: True if condition is met, False otherwise
        """
        if isinstance(condition, str):
            # Simple condition by name
            if condition == "is_assimilated":
                npc = self.game_state.get_npc(self.current_npc)
                return npc and getattr(npc, "is_assimilated", False)
            
            elif condition == "has_joined_coalition":
                return self.current_npc in self.game_state.coalition_members
            
            elif condition.startswith("has_item:"):
                item_id = condition.split(":")[1]
                return self.game_state.has_item(item_id)
            
            elif condition.startswith("has_flag:"):
                flag_name = condition.split(":")[1]
                return self.game_state.get_variable(flag_name, False)
                
        elif isinstance(condition, dict):
            # Complex condition with parameters
            condition_type = condition.get("type")
            params = condition.get("params", {})
            
            if condition_type == "has_item":
                item_id = params.get("item_id")
                return item_id and self.game_state.has_item(item_id)
            
            elif condition_type == "variable_check":
                var_name = params.get("variable")
                operation = params.get("operation", "equals")
                value = params.get("value")
                
                if not var_name:
                    return False
                    
                current = self.game_state.get_variable(var_name)
                
                if operation == "equals":
                    return current == value
                elif operation == "not_equals":
                    return current != value
                elif operation == "greater_than":
                    return current > value
                elif operation == "less_than":
                    return current < value
                elif operation == "greater_equal":
                    return current >= value
                elif operation == "less_equal":
                    return current <= value
                elif operation == "contains":
                    return value in current if isinstance(current, (list, str, dict)) else False
            
            elif condition_type == "dialog_variable":
                var_name = params.get("variable")
                operation = params.get("operation", "equals")
                value = params.get("value")
                
                if not var_name or var_name not in self.dialog_variables:
                    return False
                    
                current = self.dialog_variables[var_name]
                
                if operation == "equals":
                    return current == value
                elif operation == "not_equals":
                    return current != value
                elif operation == "greater_than":
                    return current > value
                elif operation == "less_than":
                    return current < value
            
            elif condition_type == "suspicion_level":
                npc = self.game_state.get_npc(self.current_npc)
                if not npc:
                    return False
                    
                suspicion = getattr(npc, "suspicion", 0)
                threshold = params.get("threshold", 50)
                operation = params.get("operation", "greater_equal")
                
                if operation == "greater_than":
                    return suspicion > threshold
                elif operation == "less_than":
                    return suspicion < threshold
                elif operation == "greater_equal":
                    return suspicion >= threshold
                elif operation == "less_equal":
                    return suspicion <= threshold
            
            elif condition_type == "trust_level":
                npc = self.game_state.get_npc(self.current_npc)
                if not npc:
                    return False
                    
                trust = getattr(npc, "trust_level", 0)
                threshold = params.get("threshold", 50)
                operation = params.get("operation", "greater_equal")
                
                if operation == "greater_than":
                    return trust > threshold
                elif operation == "less_than":
                    return trust < threshold
                elif operation == "greater_equal":
                    return trust >= threshold
                elif operation == "less_equal":
                    return trust <= threshold
            
            elif condition_type == "and":
                subconditions = params.get("conditions", [])
                return all(self._evaluate_condition(cond) for cond in subconditions)
            
            elif condition_type == "or":
                subconditions = params.get("conditions", [])
                return any(self._evaluate_condition(cond) for cond in subconditions)
            
            elif condition_type == "not":
                subcondition = params.get("condition")
                return not self._evaluate_condition(subcondition) if subcondition else True
        
        # Default to true for unknown conditions
        logger.warning(f"Unknown condition: {condition}")
        return True
    
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