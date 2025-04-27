# Filename: main/event_system.py

import logging
import textwrap
from typing import Dict, List, Optional, Callable, Any, Union
from . import dialog_system
from . import inventory
from .ItemUtil import get_item_property

logger = logging.getLogger(__name__)

class EventManager:
    """Central event management system for the game."""
    
    def __init__(self, game_data: Dict[str, Any]):
        self.game_data = game_data
        self.active_events: List[Event] = []
        self.delayed_events: List[Event] = []
        self.event_registry: Dict[str, Event] = {}
        self.event_handlers: Dict[str, Callable] = {}
        self.turn_counter = 0
        
        # Register default event handlers
        self._register_default_handlers()
        
        # Load events from data
        self._load_events_from_data()
    
    def _register_default_handlers(self):
        """Register built-in event handlers."""
        self.event_handlers["display_text"] = self._handle_display_text
        self.event_handlers["loot_container"] = self._handle_loot_container
        self.event_handlers["trigger_dialog"] = self._handle_trigger_dialog
        self.event_handlers["set_flag"] = self._handle_set_flag
        self.event_handlers["check_flag"] = self._handle_check_flag
        self.event_handlers["give_item"] = self._handle_give_item
        self.event_handlers["teleport"] = self._handle_teleport
        self.event_handlers["display_chapter"] = self._handle_display_chapter
        self.event_handlers["modify_location"] = self._handle_modify_location
        self.event_handlers["custom"] = self._handle_custom
        self.event_handlers["trigger_combat"] = self._handle_trigger_combat
    
    def _load_events_from_data(self):
        """Load events from the game data structure."""
        event_data = self.game_data.get('events', {})
        
        for event_id, event_dict in event_data.items():
            try:
                event = Event(
                    event_id=event_dict.get('event_id', event_id),
                    event_type=event_dict.get('event_type'),
                    payload=event_dict.get('payload', {}),
                    conditions=event_dict.get('conditions', []),
                    chain_events=event_dict.get('chain_events', []),
                    priority=event_dict.get('priority', 0),
                    repeatable=event_dict.get('repeatable', False)
                )
                
                self.register_event(event)
                
                # Handle delayed events from data
                delay_turns = event_dict.get('delay_turns')
                if delay_turns is not None and delay_turns > 0:
                    self.schedule_delayed_event(event.event_id, delay_turns)
                    
            except Exception as e:
                logger.error(f"Error creating event from data {event_id}: {e}")
    
    def register_event(self, event: 'Event'):
        """Register an event for later use."""
        self.event_registry[event.event_id] = event
    
    def register_handler(self, event_type: str, handler: Callable):
        """Register a custom event handler."""
        self.event_handlers[event_type] = handler
    
    def trigger_event(self, event_id: str, character: Any, location_data: Dict, 
                     target_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Trigger an event by ID."""
        if event_id not in self.event_registry:
            logger.error(f"Event not found: {event_id}")
            return {"status": "error", "message": f"Event {event_id} not found"}
        
        event = self.event_registry[event_id]
        return self.process_event(event, character, location_data, target_data, **kwargs)
    
    def process_event(self, event: 'Event', character: Any, location_data: Dict,
                     target_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Process a single event."""
        # Check conditions
        if not event.check_conditions(character, location_data, target_data):
            logger.debug(f"Event conditions not met: {event.event_id}")
            return {"status": "conditions_not_met"}
        
        # Execute the event
        result = event.execute(self, character, location_data, target_data, **kwargs)
        
        # Handle chained events
        if event.chain_events:
            for chain_event_id in event.chain_events:
                self.trigger_event(chain_event_id, character, location_data, target_data, **kwargs)
        
        return result
    
    def schedule_delayed_event(self, event_id: str, delay_turns: int):
        """Schedule an event to fire after a certain number of turns."""
        if event_id not in self.event_registry:
            logger.error(f"Cannot schedule unknown event: {event_id}")
            return
        
        event = self.event_registry[event_id]
        event.scheduled_turn = self.turn_counter + delay_turns
        self.delayed_events.append(event)
    
    def advance_turn(self, character: Any, location_data: Dict):
        """Advance the turn counter and check for delayed events."""
        self.turn_counter += 1
        
        # Process delayed events
        events_to_trigger = []
        remaining_events = []
        
        for event in self.delayed_events:
            if event.scheduled_turn <= self.turn_counter:
                events_to_trigger.append(event)
            else:
                remaining_events.append(event)
        
        self.delayed_events = remaining_events
        
        # Trigger the ready events
        for event in events_to_trigger:
            self.process_event(event, character, location_data)
    
    # Default Event Handlers
    def _handle_display_text(self, event: 'Event', character: Any, location_data: Dict,
                           target_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Display text to the player."""
        text = event.payload.get("text", "")
        
        # If no text in payload but we have a display_text:message format in the event_id
        if not text and ":" in event.event_id:
            parts = event.event_id.split(":", 1)
            if parts[0] == "display_text" and len(parts) > 1:
                text = parts[1]
        
        if text:
            use_textwrap(text)
        else:
            use_textwrap("You learn nothing new.")
        
        return {"status": "success"}
    
    def _handle_loot_container(self, event: 'Event', character: Any, location_data: Dict,
                             target_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Handle looting a container."""
        if not target_data:
            return {"status": "error", "message": "No target for loot container"}
        
        target_id = target_data.get('id')
        target_name = target_data.get('name', 'container')
        
        # Find the live target data
        live_target_data = None
        interactable_index = -1
        interactable_list = location_data.get('interactables', [])
        
        for index, data in enumerate(interactable_list):
            if isinstance(data, dict) and data.get('id') == target_id:
                live_target_data = data
                interactable_index = index
                break
        
        if live_target_data is None:
            return {"status": "error", "message": f"Cannot find live data for '{target_id}'"}
        
        current_state = live_target_data.get('state', 'closed')
        if current_state == 'empty':
            print(f"You check the {target_name} again, but it's empty.")
            return {"status": "already_looted"}
        
        print(f"You open the {target_name}.")
        item_ids_in_container = live_target_data.get('contains_items', [])
        
        if not item_ids_in_container:
            print("...but it's empty.")
            location_data['interactables'][interactable_index]['state'] = 'empty'
            location_data['interactables'][interactable_index]['description'] = f"An empty {target_name}."
            return {"status": "empty"}
        
        # Process items
        items_found_data = []
        items_found_names = []
        
        for item_id in item_ids_in_container:
            item_data = self.game_data['items'].get(item_id)
            if item_data:
                items_found_data.append(item_data)
                items_found_names.append(item_data.get('name', item_id))
        
        if items_found_names:
            print("Inside you find:")
            for name in items_found_names:
                print(f"- {name}")
            
            while True:
                choice = input("Take these items? (yes/no) > ").lower().strip()
                if choice in ['yes', 'y']:
                    print("\nYou added:")
                    for item_data_to_add in items_found_data:
                        if character.add_inventory(item_data_to_add.copy()):
                            print(f"- {item_data_to_add.get('name', 'item')}")
                        else:
                            print(f"Inventory full. Could not take {item_data_to_add.get('name', 'item')}.")
                    
                    location_data['interactables'][interactable_index]['state'] = 'empty'
                    location_data['interactables'][interactable_index]['description'] = f"An empty {target_name}."
                    location_data['interactables'][interactable_index]['contains_items'] = []
                    break
                elif choice in ['no', 'n']:
                    print("You close it back up.")
                    break
                else:
                    print("Please answer yes or no.")
        
        return {"status": "success"}
    
    def _handle_trigger_dialog(self, event: 'Event', character: Any, location_data: Dict,
                             target_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Trigger a dialog sequence."""
        dialog_ref = event.payload.get("dialog_ref")
        npc_id = event.payload.get("npc_id")
        
        if not dialog_ref or not npc_id:
            return {"status": "error", "message": "Missing dialog_ref or npc_id"}
        
        npc_data = self.game_data['npcs'].get(npc_id)
        if not npc_data:
            return {"status": "error", "message": f"NPC {npc_id} not found"}
        
        result = dialog_system.run_conversation(character, npc_data, override_dialog_ref=dialog_ref)
        return {"status": "success", "dialog_result": result}
    
    def _handle_set_flag(self, event: 'Event', character: Any, location_data: Dict,
                        target_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Set a game flag."""
        flag_name = event.payload.get("flag_name")
        flag_value = event.payload.get("flag_value", True)
        
        if not flag_name:
            return {"status": "error", "message": "Missing flag_name"}
        
        dialog_system._set_flag(flag_name, flag_value)
        return {"status": "success"}
    
    def _handle_check_flag(self, event: 'Event', character: Any, location_data: Dict,
                          target_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Check a game flag."""
        flag_name = event.payload.get("flag_name")
        expected_value = event.payload.get("expected_value", True)
        
        if not flag_name:
            return {"status": "error", "message": "Missing flag_name"}
        
        actual_value = dialog_system._get_flag(flag_name)
        return {"status": "success", "flag_match": actual_value == expected_value}
    
    def _handle_give_item(self, event: 'Event', character: Any, location_data: Dict,
                         target_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Give an item to the player."""
        item_id = event.payload.get("item_id")
        quantity = event.payload.get("quantity", 1)
        
        if not item_id:
            return {"status": "error", "message": "Missing item_id"}
        
        item_data = self.game_data['items'].get(item_id)
        if not item_data:
            return {"status": "error", "message": f"Item {item_id} not found"}
        
        success_count = 0
        for _ in range(quantity):
            if character.add_inventory(item_data.copy()):
                success_count += 1
            else:
                print(f"Inventory full. Could only take {success_count} {item_data.get('name', 'item')}(s).")
                break
        
        if success_count > 0:
            item_name = item_data.get('name', 'item')
            print(f"You received {success_count} {item_name}{'s' if success_count > 1 else ''}.")
        
        return {"status": "success", "items_added": success_count}
    
    def _handle_teleport(self, event: 'Event', character: Any, location_data: Dict,
                        target_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Teleport the player to a new location."""
        destination_id = event.payload.get("destination_id")
        
        if not destination_id:
            return {"status": "error", "message": "Missing destination_id"}
        
        if destination_id not in self.game_data['locations']:
            return {"status": "error", "message": f"Location {destination_id} not found"}
        
        character.set_location(destination_id)
        print(f"\nYou are transported to a new location...")
        
        return {"status": "success", "new_location": destination_id}
    
    def _handle_display_chapter(self, event: 'Event', character: Any, location_data: Dict,
                              target_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Display chapter text."""
        chapter_num = event.payload.get("chapter_number", 1)
        chapter_text = event.payload.get("chapter_text", "")
        
        print("-" * 30)
        print(f"-         Chapter {chapter_num}          -")
        print("-" * 30)
        if chapter_text:
            use_textwrap(chapter_text)
        
        return {"status": "success"}
    
    def _handle_modify_location(self, event: 'Event', character: Any, location_data: Dict,
                              target_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Modify a location's data."""
        modifications = event.payload.get("modifications", {})
        
        for key, value in modifications.items():
            if key in location_data:
                location_data[key] = value
        
        return {"status": "success"}
    
    def _handle_custom(self, event: 'Event', character: Any, location_data: Dict,
                      target_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Handle custom events that require specific logic."""
        handler_type = event.payload.get("handler_type")
        
        # Map of handler types to methods
        custom_handlers = {
            "npc_dialog": self._custom_npc_dialog,
            "check_and_trigger": self._custom_check_and_trigger,
            "conditional_unlock": self._custom_conditional_unlock
        }
        
        handler_method = custom_handlers.get(handler_type)
        if handler_method:
            return handler_method(event, character, location_data, target_data, **kwargs)
        
        logger.warning(f"Unknown custom handler type: {handler_type}")
        return {"status": "error", "message": f"Unknown custom handler type: {handler_type}"}
    
    def _custom_npc_dialog(self, event: 'Event', character: Any, location_data: Dict,
                          target_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Handle NPC dialog events."""
        npc_id = event.payload.get("npc_id")
        dialog_ref = event.payload.get("dialog_ref")
        
        if not npc_id or not dialog_ref:
            return {"status": "error", "message": "Missing npc_id or dialog_ref"}
        
        npc_data = self.game_data['npcs'].get(npc_id)
        if not npc_data:
            return {"status": "error", "message": f"NPC {npc_id} not found"}
        
        dialog_result = dialog_system.run_conversation(
            character, npc_data, override_dialog_ref=dialog_ref
        )
        
        # Handle post-dialog events
        post_dialog_events = event.payload.get("post_dialog_events", [])
        for event_id in post_dialog_events:
            self.trigger_event(event_id, character, location_data)
        
        return {"status": "success", "dialog_result": dialog_result}
    
    def _custom_check_and_trigger(self, event: 'Event', character: Any, location_data: Dict,
                                 target_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Check conditions and trigger different events based on result."""
        conditions = event.payload.get("condition_checks", [])
        true_events = event.payload.get("on_true", [])
        false_events = event.payload.get("on_false", [])
        
        all_conditions_met = True
        for condition in conditions:
            if condition["type"] == "check_flag":
                if dialog_system._get_flag(condition["flag_name"]) != condition.get("expected_value", True):
                    all_conditions_met = False
                    break
        
        events_to_trigger = true_events if all_conditions_met else false_events
        
        for event_id in events_to_trigger:
            self.trigger_event(event_id, character, location_data)
        
        return {"status": "success", "conditions_met": all_conditions_met}
    
    def _custom_conditional_unlock(self, event: 'Event', character: Any, location_data: Dict,
                                  target_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Check condition and unlock something if true."""
        # Placeholder for future implementation
        return {"status": "success"}
    
    def _handle_trigger_combat(self, event: 'Event', character: Any, location_data: Dict,
                              target_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Trigger combat with specified NPCs."""
        import copy
        from .battle_system import battle_state
        from .dialog_system import _set_flag
        
        # Get combat parameters
        spawn_npcs = event.payload.get("spawn_npcs", [])
        surprise = event.payload.get("surprise", False)
        text = event.payload.get("text")
        location_npc_list_key = event.payload.get("location_npc_list", "npcs")
        
        if text:
            print(text)
        
        # Spawn NPCs into location if needed
        location_npcs = location_data.get(location_npc_list_key, [])
        for npc_id in spawn_npcs:
            if npc_id not in location_npcs:
                location_npcs.append(npc_id)
        location_data[location_npc_list_key] = location_npcs
        
        # Create NPC instances for combat
        combatants = []
        for npc_id in spawn_npcs:
            npc_data = self.game_data['npcs'].get(npc_id)
            if npc_data:
                # Import create_npc_instance from game.py
                try:
                    from .game import create_npc_instance
                    npc_instance = create_npc_instance(npc_data)
                    if npc_instance:
                        combatants.append(npc_instance)
                except ImportError:
                    logger.error("Could not import create_npc_instance from game.py")
                    return {"status": "error", "message": "NPC instantiation failed"}
        
        if not combatants:
            return {"status": "error", "message": "No valid combatants found"}
        
        # Start combat
        battle_result = battle_state(character, combatants, surprise=surprise)
        
        # Handle battle results
        if battle_result.get("status") == "all_enemies_defeated":
            # Mark NPCs as defeated
            for npc_id in spawn_npcs:
                _set_flag(f"npc_defeated_{npc_id}", True)
        
        return {"status": "success", "battle_result": battle_result}


class Event:
    """Represents a game event."""
    
    def __init__(self, event_id: str, event_type: str, payload: Dict[str, Any],
                 conditions: Optional[List[Dict[str, Any]]] = None,
                 chain_events: Optional[List[str]] = None,
                 priority: int = 0, repeatable: bool = False):
        self.event_id = event_id
        self.event_type = event_type
        self.payload = payload
        self.conditions = conditions or []
        self.chain_events = chain_events or []
        self.priority = priority
        self.repeatable = repeatable
        self.scheduled_turn = None
        self.executed_count = 0
    
    def check_conditions(self, character: Any, location_data: Dict,
                        target_data: Optional[Dict] = None) -> bool:
        """Check if all conditions for this event are met."""
        if not self.conditions:
            return True
        
        for condition in self.conditions:
            condition_type = condition.get("type")
            
            if condition_type == "check_flag":
                flag_name = condition.get("flag_name")
                expected_value = condition.get("expected_value", True)
                if dialog_system._get_flag(flag_name) != expected_value:
                    return False
            
            elif condition_type == "check_stat":
                stat_name = condition.get("stat_name")
                min_value = condition.get("min_value")
                max_value = condition.get("max_value")
                
                getter_method = getattr(character, f"get_{stat_name}", None)
                if not getter_method:
                    return False
                
                stat_value = getter_method()
                if min_value is not None and stat_value < min_value:
                    return False
                if max_value is not None and stat_value > max_value:
                    return False
            
            elif condition_type == "check_item":
                item_id = condition.get("item_id")
                min_quantity = condition.get("min_quantity", 1)
                
                count = 0
                for item in character.get_inventory():
                    if item.get("item_id") == item_id:
                        count += 1
                
                if count < min_quantity:
                    return False
            
            elif condition_type == "check_location":
                location_id = condition.get("location_id")
                if character.get_location() != location_id:
                    return False
            
            elif condition_type == "check_npc_state":
                npc_id = condition.get("npc_id")
                required_state = condition.get("required_state")
                # This would need to be implemented based on your NPC state system
                # For now, returning True as placeholder
                return True
        
        return True
    
    def execute(self, event_manager: EventManager, character: Any, location_data: Dict,
               target_data: Optional[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Execute the event."""
        if not self.repeatable and self.executed_count > 0:
            return {"status": "already_executed"}
        
        handler = event_manager.event_handlers.get(self.event_type)
        if not handler:
            logger.error(f"No handler for event type: {self.event_type}")
            return {"status": "error", "message": f"No handler for event type: {self.event_type}"}
        
        result = handler(self, character, location_data, target_data, **kwargs)
        self.executed_count += 1
        
        return result


def use_textwrap(text):
    """Utility function to wrap text for display."""
    if not isinstance(text, str):
        text = str(text)
    dedented_text = textwrap.dedent(text).strip()
    print(textwrap.fill(dedented_text, width=70))