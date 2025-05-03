"""
Interaction System for A Sound of Distant Thunder
Handles player interactions with objects and NPCs in a data-driven way.
"""
import logging
from enum import Enum

# Configure logging
logger = logging.getLogger("InteractionSystem")

class InteractionResult(Enum):
    """Enumeration of possible interaction results for better code clarity"""
    SUCCESS = "success"
    FAILED = "failed" 
    NOT_SUPPORTED = "not_supported"
    NO_TARGET = "no_target"
    INVALID_ACTION = "invalid_action"

class InteractionSystem:
    """
    System for handling player interactions with objects and NPCs.
    Manages the verb-object interaction model typical of point-and-click adventures.
    """
    def __init__(self, game_engine):
        """
        Initialize the interaction system.
        
        Args:
            game_engine: GameEngine instance
        """
        self.game_engine = game_engine
        
        # Interaction state
        self.selected_verb = None
        self.selected_item = None
        
        # Get the condition evaluator
        self.condition_evaluator = self.game_engine.condition_evaluator
        
        # Register event listeners
        self.game_engine.event_system.subscribe("verb_selected", self._on_verb_selected)
        self.game_engine.event_system.subscribe("item_selected", self._on_item_selected)
        self.game_engine.event_system.subscribe("item_deselected", self._on_item_deselected)
        
        logger.info("Interaction System initialized")
    
    def _on_verb_selected(self, data):
        """
        Handle verb selection.
        
        Args:
            data (dict): Event data with selected verb
        """
        self.selected_verb = data.get("verb")
        
        # Keep item selection for "use" verb, reset otherwise
        if self.selected_verb != "use":
            self.selected_item = None
            
        logger.debug(f"Verb selected: {self.selected_verb}")
    
    def _on_item_selected(self, data):
        """
        Handle inventory item selection.
        
        Args:
            data (dict): Event data with selected item index
        """
        self.selected_item = data.get("item_index")
        
        # Auto-select "use" verb when item is selected
        if self.selected_item is not None:
            self.selected_verb = "use"
            
            # Update verb UI
            self.game_engine.event_system.emit("verb_selected", {
                "verb": "use"
            })
            
        logger.debug(f"Item selected: {self.selected_item}")
    
    def _on_item_deselected(self, data):
        """
        Handle inventory item deselection.
        
        Args:
            data (dict): Event data
        """
        self.selected_item = None
        logger.debug("Item deselected")
    
    # Updated method to use the condition evaluator
    def _evaluate_condition(self, condition):
        """
        Evaluate a condition using the central ConditionEvaluator.
        
        Args:
            condition (dict or str): Condition to evaluate
            
        Returns:
            bool: True if condition is met, False otherwise
        """
        return self.condition_evaluator.evaluate_condition(condition)
    
    def interact_with_object(self, object_id, verb=None):
        """
        Interact with a game object.
    
        Args:
        object_id (str): ID of the object to interact with
        verb (str, optional): Override the currently selected verb
        
        Returns:
        InteractionResult: Result of the interaction
        """
        # Get the object data
        current_location = self.game_engine.game_state.current_location
        if not current_location:
            self.game_engine.message_manager.show_error("No current location in game state")
            return InteractionResult.NO_TARGET
        
        location_data = self.game_engine.data_manager.get_data("locations", current_location)
        if not location_data:
            self.game_engine.message_manager.show_error(f"No location data for {current_location}")
            return InteractionResult.NO_TARGET
    
        # Find the object in location data
        object_data = self._find_object_data(location_data, object_id)
        if not object_data:
            self.game_engine.message_manager.show_error(f"Object not found: {object_id}")
            return InteractionResult.NO_TARGET
    
        # Use provided verb or fall back to selected verb
        use_verb = verb or self.selected_verb or "look"
    
        # Check if the action is allowed
        actions = object_data.get("actions", {})
        if not actions or use_verb not in actions:
            self.game_engine.message_manager.show_message(f"I can't {use_verb} that.")
            return InteractionResult.NOT_SUPPORTED
    
        # Get action data
        action_data = actions[use_verb]
    
        # Process the action
        if action_data:
            result = self._execute_action(use_verb, action_data, object_data)
            logger.info(f"Object interaction: {use_verb} {object_id} ({result.value})")
            return result
        else:
            self.game_engine.message_manager.show_message(f"Nothing happens.")
        return InteractionResult.FAILED
    
    def _find_object_data(self, location_data, object_id):
        """
        Find object data in location data.
        
        Args:
            location_data (dict): Location data to search
            object_id (str): ID of the object to find
            
        Returns:
            dict or None: Object data or None if not found
        """
        # Check in objects list
        for obj in location_data.get("objects", []):
            if obj.get("id") == object_id:
                return obj
        
        # Check in areas list
        for area in location_data.get("areas", []):
            if area.get("id") == object_id:
                return area
        
        return None
    
    def interact_with_npc(self, npc_id, verb=None):
        """
        Interact with an NPC.
        
        Args:
            npc_id (str): ID of the NPC to interact with
            verb (str, optional): Override the currently selected verb
            
        Returns:
            InteractionResult: Result of the interaction
        """
        # Get the NPC data
        npc_data = self.game_engine.data_manager.get_data("npcs", npc_id)
        if not npc_data:
            logger.error(f"NPC data not found: {npc_id}")
            return InteractionResult.NO_TARGET
        
        # Get NPC instance from game state
        npc = self.game_engine.game_state.get_npc(npc_id)
        if not npc:
            logger.error(f"NPC instance not found: {npc_id}")
            return InteractionResult.NO_TARGET
        
        # Use provided verb or fall back to selected verb
        use_verb = verb or self.selected_verb or "talk"
        
        # Process different verbs
        if use_verb == "look":
            return self._look_at_npc(npc_id, npc_data, npc)
        elif use_verb == "talk":
            return self._talk_to_npc(npc_id, npc_data, npc)
        elif use_verb == "use" and self.selected_item is not None:
            return self._use_item_with_npc(npc_id, npc_data, npc)
        elif use_verb == "attack":
            return self._attack_npc(npc_id, npc_data, npc)
        else:
            self._show_message(f"I can't {use_verb} that person.")
            return InteractionResult.NOT_SUPPORTED
    
    def _look_at_npc(self, npc_id, npc_data, npc):
        """
        Look at an NPC.
        
        Args:
            npc_id (str): ID of the NPC
            npc_data (dict): NPC data
            npc: NPC instance
            
        Returns:
            InteractionResult: Result of the interaction
        """
        # Check if NPC is defeated
        npc_defeated = self.game_engine.game_state.get_variable(f"npc_defeated_{npc_id}", False)
        
        if npc_defeated:
            # Look at defeated NPC
            description = npc_data.get("defeated_description", npc_data.get("description", ""))
        else:
            # Look at regular NPC
            description = npc_data.get("description", "")
        
        # Check for dynamic description based on NPC state
        if hasattr(npc, "is_assimilated") and npc.is_assimilated:
            # Add subtle hints for assimilated NPCs
            assimilation_evidence = getattr(npc, "get_assimilation_evidence", lambda: 0)()
            
            if assimilation_evidence > 0.7:
                # Obvious signs of assimilation
                description += " There's something off about them."
            elif assimilation_evidence > 0.3:
                # Subtle signs of assimilation
                description += " They seem different somehow."
        
        self._show_description(description)
        return InteractionResult.SUCCESS
    
    def _talk_to_npc(self, npc_id, npc_data, npc):
        """
        Talk to an NPC.
        
        Args:
            npc_id (str): ID of the NPC
            npc_data (dict): NPC data
            npc: NPC instance
            
        Returns:
            InteractionResult: Result of the interaction
        """
        # Check if NPC is defeated
        npc_defeated = self.game_engine.game_state.get_variable(f"npc_defeated_{npc_id}", False)
        
        if npc_defeated:
            self._show_message("They can't talk to you anymore.")
            return InteractionResult.FAILED
        
        # Check if NPC has a dialog
        dialog_refs = npc_data.get("dialog_trees", [])
        
        if not dialog_refs:
            self._show_message(f"{npc_data.get('name', 'They')} doesn't seem interested in talking.")
            
            # Mark as having attempted to talk to this NPC
            self.game_engine.game_state.set_variable(f"attempted_talk_{npc_id}", True)
            
            return InteractionResult.FAILED
        
        # Determine which dialog to use
        dialog_ref = self._select_dialog_for_npc(npc_id, dialog_refs)
        
        if not dialog_ref:
            self._show_message(f"{npc_data.get('name', 'They')} doesn't have anything to say right now.")
            return InteractionResult.FAILED
            
        # Start dialog
        self.game_engine.event_system.emit("dialog_started", {
            "npc_id": npc_id,
            "dialog_id": dialog_ref
        })
        
        return InteractionResult.SUCCESS
    
    def _select_dialog_for_npc(self, npc_id, dialog_refs):
        """
        Select appropriate dialog for an NPC based on game state.
        
        Args:
            npc_id (str): ID of the NPC
            dialog_refs (list): List of dialog IDs
            
        Returns:
            str or None: Selected dialog ID or None if none available
        """
        if not dialog_refs:
            return None
        
        # If only one dialog, use it
        if len(dialog_refs) == 1:
            return dialog_refs[0]
        
        # Check each dialog for conditions
        for dialog_id in dialog_refs:
            dialog_data = self.game_engine.data_manager.get_data("dialogs", dialog_id)
            if not dialog_data:
                continue
            
            # Check if there's a dialog condition
            if "condition" in dialog_data:
                condition = dialog_data["condition"]
                # Use the condition evaluator for consistency
                if self._evaluate_condition(condition):
                    return dialog_id
            else:
                # No condition, assume it's a default dialog
                # Store for fallback if no conditional dialogs match
                default_dialog = dialog_id
        
        # No conditional dialogs matched, use default if available
        if locals().get("default_dialog"):
            return default_dialog
        
        # No valid dialogs
        return dialog_refs[0]  # Fallback to first dialog
    
    def _use_item_with_npc(self, npc_id, npc_data, npc):
        """
        Use selected inventory item with NPC.
        
        Args:
            npc_id (str): ID of the NPC
            npc_data (dict): NPC data
            npc: NPC instance
            
        Returns:
            InteractionResult: Result of the interaction
        """
        # Get the selected item
        if self.selected_item is None:
            self._show_message("Select an item first.")
            return InteractionResult.NO_TARGET
            
        inventory = self.game_engine.game_state.player.get_inventory()
        if self.selected_item >= len(inventory):
            self._show_message("Invalid item selection.")
            return InteractionResult.NO_TARGET
            
        item = inventory[self.selected_item]
        item_id = item.get("id", "")
        item_type = item.get("item_type", "")
        item_name = item.get("name", "Unknown Item")
        
        # Check if NPC is defeated
        npc_defeated = self.game_engine.game_state.get_variable(f"npc_defeated_{npc_id}", False)
        if npc_defeated:
            self._show_message("They can't react to that anymore.")
            return InteractionResult.FAILED
            
        # Check if the NPC has a reaction to this item
        item_reactions = npc_data.get("item_reactions", {})
        
        if item_id in item_reactions:
            # Execute the reaction
            reaction = item_reactions[item_id]
            result = self._process_item_reaction(reaction, npc_id, npc, item_id, item_name)
            
            # Reset item selection
            self.selected_item = None
            self.game_engine.event_system.emit("item_deselected", {})
            
            return result
        elif item_type in item_reactions:
            # Generic reaction based on item type
            reaction = item_reactions[item_type]
            result = self._process_item_reaction(reaction, npc_id, npc, item_id, item_name)
            
            # Reset item selection
            self.selected_item = None
            self.game_engine.event_system.emit("item_deselected", {})
            
            return result
        else:
            # Generic response if no specific reaction
            self._show_message(f"{npc_data.get('name', 'They')} doesn't seem interested in that item.")
            
            # Reset item selection
            self.selected_item = None
            self.game_engine.event_system.emit("item_deselected", {})
            
            return InteractionResult.NOT_SUPPORTED
    
    def _process_item_reaction(self, reaction, npc_id, npc, item_id, item_name):
        """
        Process an NPC's reaction to an item.
        
        Args:
            reaction (dict or str): Reaction data
            npc_id (str): ID of the NPC
            npc: NPC instance
            item_id (str): ID of the item
            item_name (str): Name of the item
            
        Returns:
            InteractionResult: Result of the interaction
        """
        if isinstance(reaction, str):
            # Simple reaction is just a message
            self._show_message(reaction)
            return InteractionResult.SUCCESS
        elif isinstance(reaction, dict):
            # Complex reaction with action
            action_type = reaction.get("type", "display_text")
            
            if action_type == "display_text":
                self._show_message(reaction.get("text", ""))
                return InteractionResult.SUCCESS
                
            elif action_type == "start_dialog":
                dialog_id = reaction.get("dialog_id")
                if dialog_id:
                    self.game_engine.event_system.emit("dialog_started", {
                        "npc_id": npc_id,
                        "dialog_id": dialog_id
                    })
                    return InteractionResult.SUCCESS
                return InteractionResult.FAILED
                
            elif action_type == "take_item":
                # NPC takes the item
                if reaction.get("remove_item", True):
                    self.game_engine.game_state.remove_item(item_id)
                self._show_message(reaction.get("text", f"{npc.name} takes the {item_name}."))
                return InteractionResult.SUCCESS
                
            elif action_type == "give_item":
                # NPC gives an item to the player
                given_item_id = reaction.get("item_id")
                if given_item_id:
                    success = self.game_engine.game_state.add_item_to_inventory(given_item_id)
                    msg = reaction.get("text", f"{npc.name} gives you something.")
                    if not success:
                        msg += " But your inventory is full!"
                    self._show_message(msg)
                    return InteractionResult.SUCCESS if success else InteractionResult.FAILED
                return InteractionResult.FAILED
                
            elif action_type == "assimilate":
                # Use the goo to assimilate the NPC
                if hasattr(self.game_engine, "assimilation_system"):
                    success = self.game_engine.assimilation_system.assimilate_npc(npc_id, "goo_vial")
                    self._show_message(reaction.get("text", f"You used the goo on {npc.name}."))
                    return InteractionResult.SUCCESS if success else InteractionResult.FAILED
                else:
                    self._show_message("Nothing happens.")
                    return InteractionResult.FAILED
                    
            elif action_type == "event":
                # Trigger a game event
                event_id = reaction.get("event_id")
                if event_id:
                    self.game_engine.handle_game_event(event_id)
                    return InteractionResult.SUCCESS
                return InteractionResult.FAILED
                
            else:
                # Unknown action type
                self._show_message("Nothing happens.")
                logger.warning(f"Unknown item reaction action type: {action_type}")
                return InteractionResult.FAILED
        else:
            # Unknown reaction format
            self._show_message("Nothing happens.")
            logger.warning(f"Unknown item reaction format: {reaction}")
            return InteractionResult.FAILED
    
    def _attack_npc(self, npc_id, npc_data, npc):
        """
        Attack an NPC.
        
        Args:
            npc_id (str): ID of the NPC
            npc_data (dict): NPC data
            npc: NPC instance
            
        Returns:
            InteractionResult: Result of the interaction
        """
        # Check if NPC is already defeated
        npc_defeated = self.game_engine.game_state.get_variable(f"npc_defeated_{npc_id}", False)
        
        if npc_defeated:
            self._show_message("They're already defeated.")
            return InteractionResult.FAILED
            
        # Check if NPC has a special attack reaction dialog
        attack_dialog = npc_data.get("on_attack_dialog_ref")
        
        if attack_dialog:
            # Start the attack reaction dialog
            self.game_engine.event_system.emit("dialog_started", {
                "npc_id": npc_id,
                "dialog_id": attack_dialog
            })
            
            return InteractionResult.SUCCESS
            
        # Start combat
        self.game_engine.event_system.emit("combat_initiated", {
            "enemy_ids": [npc_id]
        })
        
        return InteractionResult.SUCCESS
    
    def _execute_action(self, verb, action_data, object_data):
        """
        Execute an action from an object interaction.
        
        Args:
            verb (str): Verb used for the action
            action_data: Action data (string or dict)
            object_data (dict): Data for the interacted object
            
        Returns:
            InteractionResult: Result of the action
        """
        # Process different action formats
        if isinstance(action_data, str):
            # Simple string format: just an action type or "action_type:parameter"
            if ":" in action_data:
                action_type, parameter = action_data.split(":", 1)
                return self._execute_simple_action(action_type, parameter, object_data)
            else:
                # No parameter
                return self._execute_simple_action(action_data, None, object_data)
                
        elif isinstance(action_data, dict):
            # Complex action format with explicit type and parameters
            action_type = action_data.get("type")
            params = action_data.get("params", {})
            
            if not action_type:
                logger.error("Action missing type")
                return InteractionResult.FAILED
                
            return self._execute_complex_action(action_type, params, object_data)
            
        else:
            # Invalid action data
            logger.error(f"Invalid action data format: {action_data}")
            self._show_message("Nothing happens.")
            return InteractionResult.FAILED
    
    def _execute_simple_action(self, action_type, parameter, object_data):
        """
        Execute a simple action with string parameter.
        
        Args:
            action_type (str): Type of action to execute
            parameter (str or None): Action parameter
            object_data (dict): Data for the interacted object
            
        Returns:
            InteractionResult: Result of the action
        """
        if action_type == "display_text":
            self._show_message(parameter or "You examine it closely.")
            return InteractionResult.SUCCESS
            
        elif action_type == "go":
            # Navigate to a location
            target_location = parameter
            if not target_location:
                self._show_message("You can't go there.")
                return InteractionResult.FAILED
                
            navigation_system = getattr(self.game_engine, "navigation_system", None)
            if navigation_system:
                success = navigation_system.navigate_to_location(target_location)
                return InteractionResult.SUCCESS if success else InteractionResult.FAILED
            else:
                logger.error("Navigation system not available")
                return InteractionResult.FAILED
                
        elif action_type == "take":
            # Add item to inventory
            item_id = parameter or object_data.get("gives_item")
            
            if not item_id:
                self._show_message(f"You can't take that.")
                return InteractionResult.FAILED
                
            success = self.game_engine.game_state.add_item_to_inventory(item_id)
            
            if success:
                self._show_message(f"You take the {object_data.get('name', 'item')}.")
                return InteractionResult.SUCCESS
            else:
                self._show_message("Your inventory is full.")
                return InteractionResult.FAILED
                
        elif action_type == "examine":
            # Show object description
            description = object_data.get("description", "Nothing special about it.")
            self._show_description(description)
            return InteractionResult.SUCCESS
            
        elif action_type == "event":
            # Trigger a game event
            event_id = parameter
            if not event_id:
                logger.error("No event ID provided")
                return InteractionResult.FAILED
                
            self.game_engine.event_system.emit("game_event_triggered", {
                "event_id": event_id
            })
            return InteractionResult.SUCCESS
            
        else:
            # Unknown action type
            logger.warning(f"Unknown simple action type: {action_type}")
            self._show_message("Nothing happens.")
            return InteractionResult.FAILED
    
    def _execute_complex_action(self, action_type, params, object_data):
        """
        Execute a complex action with parameter dictionary.
        
        Args:
            action_type (str): Type of action to execute
            params (dict): Action parameters
            object_data (dict): Data for the interacted object
            
        Returns:
            InteractionResult: Result of the action
        """
        if action_type == "display_text":
            text = params.get("text", "You examine it closely.")
            self._show_message(text)
            return InteractionResult.SUCCESS
            
        elif action_type == "multi_message":
            messages = params.get("messages", [])
            delay = params.get("delay", 0.5)
            
            if not messages:
                return InteractionResult.FAILED
                
            # Display the first message immediately
            self._show_message(messages[0])
            
            # Queue the rest with delays
            if len(messages) > 1:
                for i, msg in enumerate(messages[1:], 1):
                    self.game_engine.event_system.emit("queue_message", {
                        "text": msg,
                        "delay": delay * i
                    })
            
            return InteractionResult.SUCCESS
            
        elif action_type == "go":
            target_location = params.get("location")
            transition = params.get("transition")
            
            if not target_location:
                self._show_message("You can't go there.")
                return InteractionResult.FAILED
                
            navigation_system = getattr(self.game_engine, "navigation_system", None)
            if navigation_system:
                event_data = {"new_location": target_location}
                if transition:
                    event_data["transition"] = transition
                    
                self.game_engine.event_system.emit("location_changed", event_data)
                return InteractionResult.SUCCESS
            else:
                logger.error("Navigation system not available")
                return InteractionResult.FAILED
                
        elif action_type == "take":
            item_id = params.get("item_id") or object_data.get("gives_item")
            message = params.get("message")
            
            if not item_id:
                self._show_message(f"You can't take that.")
                return InteractionResult.FAILED
                
            success = self.game_engine.game_state.add_item_to_inventory(item_id)
            
            if success:
                self._show_message(message or f"You take the {object_data.get('name', 'item')}.")
                
                # Hide object if requested
                if params.get("hide_object", True):
                    # Object has been taken, should be hidden
                    self._hide_object(object_data.get("id"))
                
                return InteractionResult.SUCCESS
            else:
                self._show_message(params.get("inventory_full_message", "Your inventory is full."))
                return InteractionResult.FAILED
                
        elif action_type == "use":
            # Use the object
            effect_type = params.get("effect_type")
            
            if effect_type == "heal":
                amount = params.get("amount", 0)
                
                if amount <= 0:
                    return InteractionResult.FAILED
                    
                player = self.game_engine.game_state.player
                if not player:
                    return InteractionResult.FAILED
                    
                current_hp = player.get_health_points()
                max_hp = player.get_hp_limit()
                
                if current_hp < max_hp:
                    new_hp = min(current_hp + amount, max_hp)
                    player.set_health_points(new_hp)
                    self._show_message(params.get("success_message", f"You feel better. Health: {new_hp}/{max_hp}"))
                    
                    # Consume the object if it's a consumable
                    if params.get("consume", False):
                        self._hide_object(object_data.get("id"))
                    
                    return InteractionResult.SUCCESS
                else:
                    self._show_message(params.get("already_full_message", "You're already at full health."))
                    return InteractionResult.FAILED
                    
            elif effect_type == "modify_variable":
                var_name = params.get("variable")
                operation = params.get("operation", "set")
                value = params.get("value")
                
                if not var_name or value is None:
                    return InteractionResult.FAILED
                    
                current = self.game_engine.game_state.get_variable(var_name, 0)
                
                if operation == "set":
                    self.game_engine.game_state.set_variable(var_name, value)
                elif operation == "increment":
                    self.game_engine.game_state.set_variable(var_name, current + value)
                elif operation == "decrement":
                    self.game_engine.game_state.set_variable(var_name, current - value)
                elif operation == "multiply":
                    self.game_engine.game_state.set_variable(var_name, current * value)
                    
                self._show_message(params.get("message", f"You use the {object_data.get('name', 'object')}."))
                
                # Consume the object if requested
                if params.get("consume", False):
                    self._hide_object(object_data.get("id"))
                
                return InteractionResult.SUCCESS
                
            else:
                # Generic use
                self._show_message(params.get("message", f"You use the {object_data.get('name', 'object')}."))
                
                # Consume the object if requested
                if params.get("consume", False):
                    self._hide_object(object_data.get("id"))
                
                return InteractionResult.SUCCESS
                
        elif action_type == "examine":
            # Show object description
            description = params.get("description") or object_data.get("description", "Nothing special about it.")
            
            # Check for condition-based descriptions
            if "condition_descriptions" in params:
                for cond_desc in params["condition_descriptions"]:
                    condition = cond_desc.get("condition")
                    if self._evaluate_condition(condition):
                        description = cond_desc.get("description", description)
                        break
            
            self._show_description(description)
            return InteractionResult.SUCCESS
            
        elif action_type == "event":
            # Trigger a game event
            event_id = params.get("event_id")
            event_params = params.get("event_params", {})
            
            if not event_id:
                logger.error("No event ID provided")
                return InteractionResult.FAILED
                
            event_data = {"event_id": event_id}
            if event_params:
                event_data["params"] = event_params
                
            self.game_engine.event_system.emit("game_event_triggered", event_data)
            return InteractionResult.SUCCESS
            
        elif action_type == "open_container":
            # Open a container to show its contents
            items = params.get("items") or object_data.get("contains_items", [])
            
            if items:
                # Show container contents
                self.game_engine.event_system.emit("container_opened", {
                    "object_id": object_data.get("id"),
                    "items": items
                })
                
                return InteractionResult.SUCCESS
            else:
                self._show_message(params.get("empty_message", f"The {object_data.get('name', 'container')} is empty."))
                return InteractionResult.SUCCESS
                
        elif action_type == "multiple":
            # Execute multiple actions in sequence
            actions = params.get("actions", [])
            
            if not actions:
                return InteractionResult.FAILED
                
            # Execute each action in sequence
            for action in actions:
                action_type = action.get("type")
                action_params = action.get("params", {})
                
                if action_type:
                    self._execute_complex_action(action_type, action_params, object_data)
                    
            return InteractionResult.SUCCESS
            
        elif action_type == "conditional":
            # Execute action based on condition
            condition = params.get("condition")
            if_action = params.get("if_true")
            else_action = params.get("if_false")
            
            if self._evaluate_condition(condition):
                # Condition is true
                if if_action:
                    action_type = if_action.get("type")
                    action_params = if_action.get("params", {})
                    
                    if action_type:
                        return self._execute_complex_action(action_type, action_params, object_data)
            else:
                # Condition is false
                if else_action:
                    action_type = else_action.get("type")
                    action_params = else_action.get("params", {})
                    
                    if action_type:
                        return self._execute_complex_action(action_type, action_params, object_data)
            
            return InteractionResult.SUCCESS
            
        else:
            # Unknown action type
            logger.warning(f"Unknown complex action type: {action_type}")
            self._show_message("Nothing happens.")
            return InteractionResult.FAILED
    
    def _hide_object(self, object_id):
        """
        Hide an object from the current location.
        
        Args:
            object_id (str): ID of the object to hide
        """
        if not object_id:
            return
            
        # Set hidden flag for the object
        self.game_engine.game_state.set_variable(f"object_hidden_{object_id}", True)
    
    def _show_message(self, message):
        """
        Show a message to the player.
        
        Args:
            message (str): Message to show
        """
        if not message:
            return
            
        self.game_engine.event_system.emit("message_displayed", {
            "text": message
        })
        
        logger.debug(f"Message: {message}")
    
    def _show_description(self, description):
        """
        Show an object or NPC description.
        
        Args:
            description (str): Description to show
        """
        if not description:
            return
            
        self.game_engine.event_system.emit("description_displayed", {
            "text": description
        })
        
        logger.debug(f"Description displayed")
    
    def reset_state(self):
        """Reset interaction state"""
        self.selected_verb = None
        self.selected_item = None