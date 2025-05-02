"""
Interaction System for A Sound of Distant Thunder
Handles player interactions with objects and NPCs.
"""
import logging

# Configure logging
logger = logging.getLogger("InteractionSystem")

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
        
        # Register event listeners
        self.game_engine.event_system.subscribe("verb_selected", self._on_verb_selected)
        self.game_engine.event_system.subscribe("item_selected", self._on_item_selected)
        
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
    
    def interact_with_object(self, object_id, verb=None):
        """
        Interact with a game object.
        
        Args:
            object_id (str): ID of the object to interact with
            verb (str, optional): Override the currently selected verb
            
        Returns:
            bool: True if interaction was successful, False otherwise
        """
        # Get the object data
        current_location = self.game_engine.game_state.current_location
        location_data = self.game_engine.data_manager.get_data("locations", current_location)
        
        if not location_data:
            logger.error(f"No location data for {current_location}")
            return False
            
        # Find the object in location data
        object_data = None
        for obj in location_data.get("objects", []):
            if obj.get("id") == object_id:
                object_data = obj
                break
                
        if not object_data:
            logger.error(f"Object not found: {object_id}")
            return False
            
        # Use provided verb or fall back to selected verb
        use_verb = verb or self.selected_verb or "look"
        
        # Check if the action is allowed
        actions = object_data.get("actions", {})
        if use_verb not in actions:
            self._show_message(f"I can't {use_verb} that.")
            return False
            
        # Get action data
        action = actions[use_verb]
        
        # Process the action
        if isinstance(action, str):
            # Simple action format: "action_type:parameter"
            if ":" in action:
                action_type, parameter = action.split(":", 1)
                self._execute_action(action_type, parameter, object_data)
            else:
                # No parameter
                self._execute_action(action, None, object_data)
        elif isinstance(action, dict):
            # Complex action format with explicit type and parameters
            self._execute_action(
                action.get("type"),
                action.get("parameters"),
                object_data
            )
            
        logger.info(f"Object interaction: {use_verb} {object_id}")
        return True
    
    def interact_with_npc(self, npc_id, verb=None):
        """
        Interact with an NPC.
        
        Args:
            npc_id (str): ID of the NPC to interact with
            verb (str, optional): Override the currently selected verb
            
        Returns:
            bool: True if interaction was successful, False otherwise
        """
        # Get the NPC data
        npc_data = self.game_engine.data_manager.get_data("npcs", npc_id)
        
        if not npc_data:
            logger.error(f"NPC data not found: {npc_id}")
            return False
            
        # Use provided verb or fall back to selected verb
        use_verb = verb or self.selected_verb or "talk"
        
        # Process different verbs
        if use_verb == "look":
            self._look_at_npc(npc_id, npc_data)
        elif use_verb == "talk":
            self._talk_to_npc(npc_id, npc_data)
        elif use_verb == "use" and self.selected_item is not None:
            self._use_item_with_npc(npc_id, npc_data)
        elif use_verb == "attack":
            self._attack_npc(npc_id, npc_data)
        else:
            self._show_message(f"I can't {use_verb} that person.")
            return False
            
        logger.info(f"NPC interaction: {use_verb} {npc_id}")
        return True
    
    def _look_at_npc(self, npc_id, npc_data):
        """
        Look at an NPC.
        
        Args:
            npc_id (str): ID of the NPC
            npc_data (dict): NPC data
        """
        # Check if NPC is defeated
        npc_defeated = self.game_engine.game_state.get_variable(f"npc_defeated_{npc_id}", False)
        
        if npc_defeated:
            # Look at defeated NPC
            description = npc_data.get("defeated_description", npc_data.get("description", ""))
        else:
            # Look at regular NPC
            description = npc_data.get("description", "")
            
        self._show_description(description)
    
    def _talk_to_npc(self, npc_id, npc_data):
        """
        Talk to an NPC.
        
        Args:
            npc_id (str): ID of the NPC
            npc_data (dict): NPC data
        """
        # Check if NPC is defeated
        npc_defeated = self.game_engine.game_state.get_variable(f"npc_defeated_{npc_id}", False)
        
        if npc_defeated:
            self._show_message("They can't talk to you anymore.")
            return
            
        # Check if NPC has a dialog
        dialog_ref = npc_data.get("dialog_ref")
        
        if not dialog_ref:
            self._show_message(f"{npc_data.get('name', 'They')} doesn't seem interested in talking.")
            return
            
        # Start dialog
        self.game_engine.event_system.emit("dialog_started", {
            "npc_id": npc_id,
            "dialog_id": dialog_ref
        })
    
    def _use_item_with_npc(self, npc_id, npc_data):
        """
        Use selected inventory item with NPC.
        
        Args:
            npc_id (str): ID of the NPC
            npc_data (dict): NPC data
        """
        # Get the selected item
        if self.selected_item is None:
            self._show_message("Select an item first.")
            return
            
        inventory = self.game_engine.game_state.player.get_inventory()
        if self.selected_item >= len(inventory):
            self._show_message("Invalid item selection.")
            return
            
        item = inventory[self.selected_item]
        item_id = item.get("id", "")
        item_name = item.get("name", "Unknown Item")
        
        # Check if NPC is defeated
        npc_defeated = self.game_engine.game_state.get_variable(f"npc_defeated_{npc_id}", False)
        if npc_defeated:
            self._show_message("They can't react to that anymore.")
            return
            
        # Check if the NPC has a reaction to this item
        item_reactions = npc_data.get("item_reactions", {})
        
        if item_id in item_reactions:
            # Execute the reaction
            reaction = item_reactions[item_id]
            
            if isinstance(reaction, str):
                # Simple reaction is just a message
                self._show_message(reaction)
            elif isinstance(reaction, dict):
                # Complex reaction with action
                action_type = reaction.get("type", "display_text")
                
                if action_type == "display_text":
                    self._show_message(reaction.get("text", ""))
                elif action_type == "start_dialog":
                    dialog_id = reaction.get("dialog_id")
                    if dialog_id:
                        self.game_engine.event_system.emit("dialog_started", {
                            "npc_id": npc_id,
                            "dialog_id": dialog_id
                        })
                elif action_type == "take_item":
                    # NPC takes the item
                    if reaction.get("remove_item", True):
                        self.game_engine.game_state.remove_item(item_id)
                    self._show_message(reaction.get("text", f"{npc_data.get('name', 'They')} takes the {item_name}."))
                elif action_type == "give_item":
                    # NPC gives an item to the player
                    given_item_id = reaction.get("item_id")
                    if given_item_id:
                        self.game_engine.game_state.add_item_to_inventory(given_item_id)
                    self._show_message(reaction.get("text", f"{npc_data.get('name', 'They')} gives you something."))
                elif action_type == "assimilate":
                    # Use the goo to assimilate the NPC
                    self.game_engine.assimilation_system.assimilate_npc(npc_id, "goo_vial")
                    self._show_message(reaction.get("text", f"You used the goo on {npc_data.get('name', 'them')}."))
        else:
            # Generic response if no specific reaction
            self._show_message(f"{npc_data.get('name', 'They')} doesn't seem interested in that item.")
            
        # Reset item selection
        self.selected_item = None
        self.game_engine.event_system.emit("item_deselected", {})
        
    def _attack_npc(self, npc_id, npc_data):
        """
        Attack an NPC.
        
        Args:
            npc_id (str): ID of the NPC
            npc_data (dict): NPC data
        """
        # Check if NPC is already defeated
        npc_defeated = self.game_engine.game_state.get_variable(f"npc_defeated_{npc_id}", False)
        
        if npc_defeated:
            self._show_message("They're already defeated.")
            return
            
        # Check if NPC has a special attack reaction dialog
        attack_dialog = npc_data.get("on_attack_dialog_ref")
        
        if attack_dialog:
            # Start the attack reaction dialog
            self.game_engine.event_system.emit("dialog_started", {
                "npc_id": npc_id,
                "dialog_id": attack_dialog
            })
            
        # Start combat
        self.game_engine.event_system.emit("combat_initiated", {
            "enemy_ids": [npc_id]
        })
    
    def _execute_action(self, action_type, parameter, object_data):
        """
        Execute an action from an object interaction.
        
        Args:
            action_type (str): Type of action to execute
            parameter: Action parameter data
            object_data (dict): Data for the interacted object
        """
        if action_type == "display_text":
            self._show_message(parameter)
        elif action_type == "go":
            # Navigate to a location
            self.game_engine.navigation_system.navigate_to_location(parameter)
        elif action_type == "take":
            # Add item to inventory
            item_id = parameter if isinstance(parameter, str) else object_data.get("gives_item")
            
            if item_id:
                success = self.game_engine.game_state.add_item_to_inventory(item_id)
                
                if success:
                    self._show_message(f"You take the {object_data.get('name', 'item')}.")
                else:
                    self._show_message("Your inventory is full.")
            else:
                self._show_message(f"You can't take that.")
        elif action_type == "use":
            # Use the object
            if "effect" in object_data:
                effect = object_data["effect"]
                
                if effect["type"] == "heal":
                    amount = effect.get("amount", 0)
                    current_hp = self.game_engine.game_state.player.get_health_points()
                    max_hp = self.game_engine.game_state.player.get_hp_limit()
                    
                    if current_hp < max_hp:
                        new_hp = min(current_hp + amount, max_hp)
                        self.game_engine.game_state.player.set_health_points(new_hp)
                        self._show_message(f"You feel better. Health: {new_hp}/{max_hp}")
                    else:
                        self._show_message("You're already at full health.")
            else:
                self._show_message(f"You use the {object_data.get('name', 'object')}.")
        elif action_type == "examine":
            # Show object description
            self._show_description(object_data.get("description", "Nothing special about it."))
        elif action_type == "event":
            # Trigger a game event
            event_id = parameter
            self.game_engine.event_system.emit("game_event_triggered", {
                "event_id": event_id
            })
        elif action_type == "open_container":
            # Open a container to show its contents
            items = object_data.get("contains_items", [])
            
            if items:
                # Show container contents
                self.game_engine.event_system.emit("container_opened", {
                    "object_id": object_data.get("id"),
                    "items": items
                })
            else:
                self._show_message(f"The {object_data.get('name', 'container')} is empty.")
        else:
            # Unknown action type
            logger.warning(f"Unknown action type: {action_type}")
            self._show_message("Nothing happens.")
    
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