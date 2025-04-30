class DialogManager:
    """
    Manages dialog flow, conditions, and effects.
    """
    def __init__(self, data_manager, game_state, event_system):
        self.data_manager = data_manager
        self.game_state = game_state
        self.event_system = event_system
        self.current_dialog = None
        self.current_node = None
        self.current_npc = None
        self.history = []
        
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
            return None
            
        # Set current dialog state
        self.current_dialog = dialog_data
        self.current_node = dialog_data.get("start_node")
        self.current_npc = npc_id
        self.history = []
        
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
            return None
            
        # Find the option in the current node
        current_node_data = self.current_dialog["nodes"][self.current_node]
        
        # Find the selected option
        selected_option = None
        for option in current_node_data.get("options", []):
            if option["id"] == option_id:
                selected_option = option
                break
                
        if not selected_option:
            return None
            
        # Record this choice in history
        self.history.append({
            "node": self.current_node,
            "option": option_id
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
            dict: Processed node data, or None if node doesn't exist
        """
        if not self.current_node or self.current_node not in self.current_dialog["nodes"]:
            return None
            
        node_data = self.current_dialog["nodes"][self.current_node]
        
        # Check conditions if present
        if "condition" in node_data:
            condition = node_data["condition"]
            if not self._evaluate_condition(condition):
                # Condition failed, go to fallback node if available
                fallback = node_data.get("fallback")
                if fallback:
                    self.current_node = fallback
                    return self.process_current_node()
                else:
                    # No fallback, end dialog
                    self.end_dialog()
                    return None
        
        # Prepare the response data
        response_data = {
            "id": self.current_node,
            "text": node_data.get("text", ""),
        }
        
        # Add options if present
        if "options" in node_data:
            options = []
            for option in node_data["options"]:
                # Check if this option has a condition
                if "condition" in option and not self._evaluate_condition(option["condition"]):
                    continue
                    
                options.append({
                    "id": option["id"],
                    "text": option["text"]
                })
            response_data["options"] = options
        
        # Handle automatic progression
        if "next" in node_data and "options" not in node_data:
            response_data["auto_advance"] = True
            self.current_node = node_data["next"]
        
        return response_data
    
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
            
        # Apply trust effect
        if "trust_effect" in option and self.current_npc:
            amount = option["trust_effect"]
            self.game_state.update_npc_trust(self.current_npc, amount)
            
        # Execute action if present
        if "action" in option:
            self._execute_action(option["action"])
    
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
                    "npc_id": self.current_npc
                })
            elif action == "join_coalition":
                self.game_state.add_to_coalition(self.current_npc)
            elif action.startswith("give_item:"):
                item_id = action.split(":")[1]
                self.game_state.add_item_to_inventory(item_id)
        elif isinstance(action, dict):
            # Complex action with parameters
            action_type = action.get("type")
            params = action.get("params", {})
            
            if action_type == "modify_variable":
                var_name = params.get("variable")
                operation = params.get("operation")
                value = params.get("value")
                
                if operation == "set":
                    self.game_state.set_variable(var_name, value)
                elif operation == "increment":
                    current = self.game_state.get_variable(var_name, 0)
                    self.game_state.set_variable(var_name, current + value)
    
    def _evaluate_condition(self, condition):
        """
        Evaluate a dialog condition.
        
        Args:
            condition (dict): Condition to evaluate
            
        Returns:
            bool: True if condition is met, False otherwise
        """
        if isinstance(condition, str):
            # Simple condition by name
            if condition == "is_assimilated":
                npc = self.game_state.get_npc(self.current_npc)
                return npc and npc.is_assimilated
            elif condition == "has_joined_coalition":
                return self.current_npc in self.game_state.coalition_members
        elif isinstance(condition, dict):
            # Complex condition with parameters
            condition_type = condition.get("type")
            params = condition.get("params", {})
            
            if condition_type == "has_item":
                item_id = params.get("item_id")
                return self.game_state.has_item(item_id)
            elif condition_type == "variable_check":
                var_name = params.get("variable")
                operation = params.get("operation")
                value = params.get("value")
                
                if not var_name:
                    return False
                    
                current = self.game_state.get_variable(var_name)
                
                if operation == "equals":
                    return current == value
                elif operation == "greater_than":
                    return current > value
                elif operation == "less_than":
                    return current < value
                
        return True  # Default to true if condition type is unknown
    
    def end_dialog(self):
        """End the current dialog"""
        if self.current_dialog:
            self.event_system.emit("dialog_ended", {
                "npc_id": self.current_npc
            })
            
        self.current_dialog = None
        self.current_node = None
        self.current_npc = None