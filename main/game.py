# --- In main/game.py ---
import sys
import os
import copy
import logging
import textwrap # Using standard library textwrap

# Import your modules (adjust paths if needed)
from . import hero # Assuming hero.py is in the same directory
from . import inventory
from . import actions # Use the provided actions.py
from . import battle_system # Assuming it exists
from . import dialog_system # Import the new dialog system
from . import data_loader # Assuming it exists
from . import mechanics # Use the provided mechanics.py
# Add other necessary imports (e.g., NPC if needed directly)

# --- Global Data Variables (populated after loading) ---
game_locations_data = {}
game_items_data = {}
game_npc_data = {}

# --- Utility Function (if not in Util.py or imported) ---
def use_textwrap(text):
    """Wraps text for display."""
    # Dedent might be useful if descriptions have leading whitespace
    dedented_text = textwrap.dedent(str(text)).strip()
    print(textwrap.fill(dedented_text, width=70)) # Adjust width as needed

# --- Help Menu Function ---
def help_menu():
    """Displays help information."""
    print("\n--- Help Menu ---")
    print("Available commands depend on context.")
    print("Common commands: look, go [direction], examine [object/person], talk [person], take [item], inventory, help, quit")
    print("Other commands may become available based on objects or location.")
    print("Type the command and target (e.g., 'examine case', 'talk captain').")
    print("-----------------\n")

# --- Event Handler Function ---
# (Ensure the handle_game_event function from previous versions is here)
def handle_game_event(event_string, character, location_data, target_data):
    """
    Handles specific game events/actions triggered by action strings defined in JSON.
    Includes generic logic for 'loot_container' action type using 'contains_items'.
    """
    global game_items_data, game_locations_data # Ensure these are accessible

    logging.info(f"Handling action/event: {event_string} for target: {target_data.get('name', 'N/A')}")
    print("-" * 30)

    action_type = event_string
    action_payload = None
    if ":" in event_string:
        parts = event_string.split(":", 1)
        action_type = parts[0]
        action_payload = parts[1] if len(parts) > 1 else None

    # --- Handle Loot Container ---
    if action_type == "loot_container":
        target_id = target_data.get('id')
        target_name = target_data.get('name', 'container')

        # Find the actual interactable data in the main location dictionary to modify state
        live_target_data = None
        interactable_index = -1
        interactable_list = location_data.get('interactables', [])
        if isinstance(interactable_list, list): # Check if it's a list
            for index, data in enumerate(interactable_list):
                 # Check if data is a dictionary and has the matching id
                if isinstance(data, dict) and data.get('id') == target_id:
                    live_target_data = data
                    interactable_index = index
                    break
        else:
            logging.warning(f"Location '{location_data.get('location_id', 'Unknown')}' has malformed 'interactables' data: {interactable_list}")


        if live_target_data is None:
             print(f"Error: Could not find live data for interactable ID '{target_id}'.")
             logging.error("Could not find live data for interactable ID '%s' in location '%s'", target_id, location_data.get('location_id'))
             print("-" * 30) # Add separator on error exit
             return # Stop processing this event

        # Check the state from the *live* data
        current_state = live_target_data.get('state', 'closed') # Default to closed if no state

        if current_state != 'empty':
            print(f"You open the {target_name}.")
            # Get item list DIRECTLY from the object's data
            item_ids_in_container = live_target_data.get('contains_items', [])

            if not item_ids_in_container or not isinstance(item_ids_in_container, list):
                print("...but it's empty.")
                # Update state to empty and potentially remove the 'open' action
                location_data['interactables'][interactable_index]['state'] = 'empty'
                location_data['interactables'][interactable_index]['description'] = f"An empty {target_name}." # Update description
                # Optionally remove the action verb that triggered this
                verb_that_triggered = next((v for v, a in target_data.get('actions',{}).items() if a == event_string), None)
                # Check if 'actions' key exists before deleting
                if verb_that_triggered and 'actions' in location_data['interactables'][interactable_index] and verb_that_triggered in location_data['interactables'][interactable_index].get('actions',{}):
                     location_data['interactables'][interactable_index]['actions'].pop(verb_that_triggered, None)
                     logging.debug(f"Removed '{verb_that_triggered}' action for '{target_id}'.")

            else: # Container has items listed
                items_found_data = []
                items_found_names = []
                for item_id in item_ids_in_container:
                    if not isinstance(item_id, str): # Basic validation
                         logging.warning(f"Non-string item ID found in container '{target_id}': {item_id}")
                         continue
                    item_data = game_items_data.get(item_id)
                    if item_data and isinstance(item_data, dict):
                        items_found_data.append(item_data)
                        items_found_names.append(item_data.get('name', item_id))
                    else: logging.warning("Item definition missing or malformed for '%s' in container '%s'.", item_id, target_id)

                if items_found_names: # Check if any valid items were actually found
                    print("Inside you find:")
                    for name in items_found_names: print(f"- {name}")
                    while True:
                        choice = input("Take these items? (yes/no) > ").lower().strip()
                        if choice in ['yes', 'y']:
                            print("\nYou added:")
                            items_added_count = 0
                            for item_data_to_add in items_found_data:
                                # Use the character's add_inventory method
                                if character.add_inventory(copy.deepcopy(item_data_to_add)):
                                    item_name = item_data_to_add.get('name', item_data_to_add.get('id','unknown item'))
                                    print(f"- {item_name}")
                                    items_added_count += 1
                                else:
                                    print(f"Inventory full. Could not take {item_data_to_add.get('name', 'item')}.")
                                    # Decide if you break loop on full inventory or let user try again later
                                    # For now, we continue and update the state anyway

                            # Update State and remove action verb only if items were present
                            location_data['interactables'][interactable_index]['state'] = 'empty'
                            location_data['interactables'][interactable_index]['description'] = f"An empty {target_name}."
                            location_data['interactables'][interactable_index]['contains_items'] = [] # Clear items
                            verb_that_triggered = next((v for v, a in target_data.get('actions',{}).items() if a == event_string), None)
                            if verb_that_triggered and 'actions' in location_data['interactables'][interactable_index] and verb_that_triggered in location_data['interactables'][interactable_index]['actions']:
                                 location_data['interactables'][interactable_index]['actions'].pop(verb_that_triggered, None)
                                 logging.debug(f"Removed '{verb_that_triggered}' action for '{target_id}'.")
                            break
                        elif choice in ['no', 'n']:
                            print("You close it back up, leaving the items for now.")
                            break
                        else: print("Please answer yes or no.")
                else: # No valid items found
                    print("It seems to be empty.")
                    location_data['interactables'][interactable_index]['state'] = 'empty'
                    location_data['interactables'][interactable_index]['description'] = f"An empty {target_name}."
                    verb_that_triggered = next((v for v, a in target_data.get('actions',{}).items() if a == event_string), None)
                    if verb_that_triggered and 'actions' in location_data['interactables'][interactable_index] and verb_that_triggered in location_data['interactables'][interactable_index]['actions']:
                         location_data['interactables'][interactable_index]['actions'].pop(verb_that_triggered, None)

        elif current_state == 'empty':
             print(f"You check the {target_name} again, but it's already empty.")
        else:
             # Handle other potential states if needed
             print(f"The {target_name} is in an unusual state ('{current_state}') and cannot be interacted with like that right now.")

    # --- Handle Display Text ---
    elif action_type == "display_text":
        if action_payload:
            use_textwrap(action_payload)
        else:
            logging.warning("Action 'display_text' called without payload.")
            use_textwrap("You look, but learn nothing new.") # Default message

    # --- Handle other specific event types ---
    elif action_type == "event" and action_payload == "display_dossier_text":
        # Example specific event
        use_textwrap("Contains mission details. Target: Secure island facility. High risk, high reward. Communications are down. Investigate.")
        logging.info("Displayed dossier text event.")

    # --- Add more elif blocks for other event types ---
    # elif action_type == "unlock_door": ...
    # elif action_type == "trigger_trap": ...

    else:
        # Fallback for unhandled action types
        print(f"You try to interact using '{event_string}', but nothing specific happens yet.")
        logging.warning("Unhandled action/event type triggered: %s", event_string)

    print("-" * 30) # Separator after handling event


# --- Main Game Loop ---
def main_game_loop(character):
    """
    Main loop: Displays location, suggests actions, gets input, processes commands.
    Handles standard commands, movement, talk, and generic object actions.
    Tracks examined state per location visit.
    """
    global game_locations_data, game_items_data, game_npc_data # Access globals

    # Ensure logging is configured for this to appear if level is DEBUG
    logging.debug(f"Keys in game_npc_data: {list(game_npc_data.keys())}")

    # Initialize loop state variables BEFORE the loop
    game_is_running = True
    first_look = True # Force full description on first entry or after 'look'
    examined_this_visit = set() # Track examined IDs for the current location visit
    previous_location_id = None # Track location changes
    # End initialization

    while game_is_running:
        # --- 1. Get Current Location Info ---
        current_location_id = character.get_location()
        if not current_location_id or current_location_id not in game_locations_data:
            print(f"ERROR: Unknown or invalid location ID '{current_location_id}'. Ending game.")
            logging.critical("Player location '%s' invalid or not found in game_locations_data.", current_location_id)
            break # Exit loop
        # Get a reference to the current location's data dictionary
        current_location = game_locations_data[current_location_id]

        # --- Reset examined state if location changed ---
        if current_location_id != previous_location_id:
            logging.debug(f"Location changed from {previous_location_id} to {current_location_id}. Clearing examined set.")
            examined_this_visit.clear()
            previous_location_id = current_location_id
            first_look = True # Force look on location change

        # --- 2. Display Location Description ---
        print("-" * 30)
        print(f"Location: {current_location.get('name', 'Unknown Area')}")
        print("-" * 30)
        has_visited = character.has_visited(current_location_id)
        if not has_visited or first_look:
            description = current_location.get('description', 'You see nothing remarkable.')
            use_textwrap(description)
            if not has_visited: character.add_visited_location(current_location_id)
            # Handle entry events
            entry_events = current_location.get("events_on_entry", [])
            if entry_events and isinstance(entry_events, list):
                 logging.info(f"Location '{current_location_id}' has entry events: {entry_events}")
                 # TODO: Implement handling for entry events (e.g., call handle_game_event?)
                 # for event_str in entry_events:
                 #     handle_game_event(event_str, character, current_location, None) # Need target?
            elif entry_events: # Log if not a list
                 logging.warning(f"Location '{current_location_id}' has malformed 'events_on_entry': {entry_events}")
        else:
            # Use visited description if available, otherwise fallback to main description
            description = current_location.get('visited_description', current_location.get('description', 'You see nothing remarkable.'))
            use_textwrap(description)

        # --- 3. Display Contextual Information (NPCs, Items, Interactables) ---
        print("-" * 30) # Separator before context lists

        # Display NPCs
        npcs_here = current_location.get('npcs', [])
        if isinstance(npcs_here, list) and npcs_here: # Check if list and not empty
            print("You see:")
            for npc_id in npcs_here:
                if not isinstance(npc_id, str): continue # Skip non-string IDs
                npc_data = game_npc_data.get(npc_id) # Fetch data from global NPC dict
                npc_name = npc_data.get('name', npc_id) if npc_data and isinstance(npc_data, dict) else npc_id # Use name if found
                print(f"- {npc_name}")
        elif npcs_here: # Log if not a list but exists
             logging.warning(f"Location '{current_location_id}' has malformed 'npcs' data: {npcs_here}")


        # Display Interactables
        interactables_here = current_location.get('interactables', [])
        # Display Items (on the ground)
        items_here = current_location.get('items', [])

        # Check if there are any valid interactables or items to display
        valid_interactables = [i for i in interactables_here if isinstance(i, dict)] if isinstance(interactables_here, list) else []
        valid_items = [i for i in items_here if isinstance(i, dict)] if isinstance(items_here, list) else []

        if valid_interactables or valid_items:
             # Adjust header based on whether NPCs are present
             header = "You notice:" if not (isinstance(npcs_here, list) and npcs_here) else "Also here:"
             print(header)
             # Iterate through valid lists
             for interactable_data in valid_interactables:
                 # Display interactable name, possibly with state if relevant
                 i_name = interactable_data.get('name', 'an object')
                 i_state = interactable_data.get('state')
                 display_name = f"a {i_name}"
                 # Add state if it exists and isn't a common default like 'normal' or 'closed' (optional refinement)
                 if i_state and i_state not in ['normal', None]:
                     display_name += f" ({i_state})"
                 print(f"- {display_name}")
             for item_data in valid_items:
                  # Display item name
                  item_name = item_data.get('name', 'an item')
                  print(f"- a {item_name}")
        # Log warnings for malformed lists if they exist but aren't lists
        elif interactables_here: logging.warning(f"Location '{current_location_id}' has malformed 'interactables' data: {interactables_here}")
        elif items_here: logging.warning(f"Location '{current_location_id}' has malformed 'items' data: {items_here}")


        # Display Exits
        available_exits = current_location.get('exits', {})
        if isinstance(available_exits, dict) and available_exits: # Check if dict and not empty
            # Filter out potentially internal/hidden exits if needed later
            visible_exits = {cmd: dest for cmd, dest in available_exits.items() if isinstance(cmd, str) and not cmd.startswith("_")}
            if visible_exits:
                 print("\nPossible Exits:")
                 # Sort exits for consistent display order
                 for exit_cmd in sorted(visible_exits.keys()):
                      print(f"- {exit_cmd}")
        elif available_exits: # Log if not a dict but exists
             logging.warning(f"Location '{current_location_id}' has malformed 'exits' data: {available_exits}")


        first_look = False # Reset flag after displaying full context
        print("-" * 30) # Separator after context lists

        # --- 4. Display Suggested Actions ---
        # Use the function from actions.py, passing necessary context
        # <<< Ensure character and game_npc_data are passed >>>
        available_actions_list = actions.get_available_actions(current_location, character, game_npc_data)
        print("Suggested actions:")
        # Limit suggestions if list gets too long?
        max_suggestions = 15
        if isinstance(available_actions_list, list): # Check if it's a list
            for i, action in enumerate(available_actions_list):
                 if i >= max_suggestions:
                      print("- (more actions possible...)")
                      break
                 # Ensure action is displayable (e.g., a string)
                 if isinstance(action, str):
                      print(f"- {action}")
                 else:
                      logging.warning(f"Non-string action found in suggestions: {action}")
        else:
             logging.error(f"get_available_actions returned non-list: {available_actions_list}")

        print("-" * 20) # Separator after suggestions


        # --- 5. Get Player Input ---
        try:
            command = input("> ").lower().strip()
        except EOFError:
             logging.warning("EOFError received during input. Quitting.")
             command = "quit" # Treat EOF as quit command

        logging.debug("Player command: '%s'", command)
        if not command: continue # Ask again if empty input

        # --- 6. Parse Player Input ---
        parts = command.split(maxsplit=1)
        verb = parts[0] if parts else ""
        noun = parts[1] if len(parts) > 1 else ""
        logging.debug(f"Parsed command: verb='{verb}', noun='{noun}'")

        # --- 7. Execute Action ---
        action_executed = False # Flag to track if any action handler ran

        # --- Handle Standard Commands ---
        if verb == "quit":
            print("Quitting game.")
            # TODO: Add save prompt/logic here?
            game_is_running = False
            action_executed = True
        elif verb == "help":
            help_menu()
            action_executed = True
        elif verb == "inventory":
            # Ensure inventory module and function exist and handle character object
            try:
                inventory.inventory(character) # Call inventory function
            except AttributeError:
                 logging.error("inventory.inventory function not found or incompatible.")
                 print("Error accessing inventory system.")
            except Exception as e:
                 logging.exception("Error during inventory call:")
                 print("An error occurred accessing inventory.")
            action_executed = True
        elif verb == "look" and not noun: # Handle 'look' without a noun
            first_look = True # Set flag to redisplay full description
            print("\nLooking around again...")
            action_executed = True

        # --- Handle Movement ---
        elif verb == "go":
            available_exits = current_location.get('exits', {})
            if isinstance(available_exits, dict) and noun in available_exits: # Check type
                destination_id = available_exits[noun]
                if not isinstance(destination_id, str): # Check destination type
                     logging.error(f"Invalid destination ID type for exit '{noun}': {destination_id}")
                     print("There seems to be a problem with that exit.")
                elif destination_id not in game_locations_data:
                    print(f"Error: The way '{noun}' leads nowhere functional yet.")
                    logging.error("Movement failed: Dest ID '%s' not found in loaded locations.", destination_id)
                else:
                    print(f"\nYou go {noun}...")
                    # TODO: Trigger 'events_on_exit' for the *current* location if needed
                    character.set_location(destination_id)
                    logging.info("Player moved from %s to %s via 'go %s'", current_location_id, destination_id, noun)
                    # Location change handled at top of next loop iteration (clears examined, sets first_look)
            else:
                print(f"You can't go '{noun}' from here.")
            action_executed = True

        # --- Handle Talk/Speak ---
        elif verb == "talk" or verb == "speak":
            if not noun:
                print("Talk to who?")
            else:
                target_npc_data = None
                npc_list_ids = current_location.get('npcs', [])
                if isinstance(npc_list_ids, list): # Check type
                    for npc_id in npc_list_ids:
                        if not isinstance(npc_id, str): continue # Skip non-string IDs
                        npc_data = game_npc_data.get(npc_id)
                        if not npc_data or not isinstance(npc_data, dict): continue # Skip if data missing/malformed

                        npc_name_lower = npc_data.get('name', '').lower()
                        aliases = npc_data.get('aliases', [])
                        npc_aliases_lower = [alias.lower() for alias in aliases if isinstance(alias, str)] if isinstance(aliases, list) else []

                        if noun == npc_name_lower or noun in npc_aliases_lower:
                            target_npc_data = npc_data
                            logging.info(f"Matched input '{noun}' to NPC: {npc_id} ('{npc_data.get('name')}')")
                            break

                if target_npc_data:
                    # --- Call Dialog System ---
                    try:
                        dialog_result = dialog_system.run_conversation(character, target_npc_data)
                    except Exception as e:
                         logging.exception("Error during dialog_system.run_conversation call:")
                         print("An error occurred during the conversation.")
                         dialog_result = {"status": "error"} # Assume error if exception occurs
                    # --- End Call ---

                    # --- Handle Dialog Result ---
                    if dialog_result and isinstance(dialog_result, dict): # Check result type
                        status = dialog_result.get('status')
                        if status == 'start_combat':
                            combat_target_id = dialog_result.get('combat_target_id')
                            if combat_target_id and combat_target_id in game_npc_data:
                                print(f"\nDialogue breaks down! {target_npc_data.get('name')} attacks!")
                                enemy_data_for_combat = game_npc_data[combat_target_id]
                                # --- Call Battle System ---
                                try:
                                     # TODO: Confirm battle_system signature - does it need data or object?
                                     battle_system.battle_state(character, enemy_data_for_combat)
                                except AttributeError:
                                     logging.error("battle_system.battle_state function not found or incompatible.")
                                     print("Error initiating combat system.")
                                except Exception as e:
                                     logging.exception("Error during battle_system call:")
                                     print("An error occurred during combat.")
                                # --- End Battle Call ---
                                # Check if player died in combat
                                if character.get_health_points() <= 0:
                                     logging.info("Player defeated in combat initiated by dialog.")
                                     game_is_running = False # End game if player died
                            else:
                                logging.error(f"Dialog requested combat with invalid target ID: {combat_target_id}")
                        elif status == 'error':
                            # Message already printed by dialog system or exception handler
                            pass
                        # 'ended', 'no_dialog_first_attempt', 'no_dialog_already_attempted' require no special action here
                    else:
                         logging.error(f"Invalid result received from dialog_system: {dialog_result}")
                    # --- End Handle Dialog Result ---

                else: # No match found after checking all NPCs in the location
                    print(f"You don't see anyone called '{noun}' here to talk to.")

            action_executed = True


        # --- Handle Take ---
        elif verb == "take":
            if not noun:
                print("Take what?")
            else:
                item_taken = False
                items_in_location = list(current_location.get('items', [])) # Use list() for shallow copy
                item_index_to_remove = -1

                if isinstance(current_location.get('items'), list): # Check original list type
                    for i, item_data in enumerate(items_in_location):
                        if isinstance(item_data, dict):
                             item_name_lower = item_data.get('name', '').lower()
                             item_id = item_data.get('id')
                             if noun == item_name_lower:
                                if not item_id or not isinstance(item_id, str):
                                    logging.error(f"Item '{item_name_lower}' in location {current_location_id} has missing or invalid 'id': {item_id}. Cannot take.")
                                    print(f"There seems to be a problem with the {item_name_lower}.")
                                    item_taken = True # Mark as handled, even though failed
                                    break
                                # Fetch full item definition for adding to inventory
                                full_item_data = game_items_data.get(item_id)
                                if not full_item_data or not isinstance(full_item_data, dict):
                                     logging.error(f"Full item definition not found or malformed for ID '{item_id}' when taking.")
                                     print(f"There's a problem with the definition of the {item_name_lower}.")
                                     item_taken = True
                                     break
                                # Attempt to add item to player inventory
                                if character.add_inventory(copy.deepcopy(full_item_data)): # Use deepcopy
                                    print(f"You take the {item_name_lower}.")
                                    logging.info(f"Player took item '{item_id}' from location '{current_location_id}'")
                                    item_index_to_remove = i # Mark index for removal *after* iterating
                                    item_taken = True
                                else:
                                    print(f"Your inventory is full. You can't take the {item_name_lower}.")
                                    item_taken = True # Handled, but failed due to inventory limit
                                break # Item found (whether taken or not)
                        else:
                             logging.warning(f"Malformed item entry in location '{current_location_id}': {item_data}")

                    # Remove the item from the *original* list *after* the loop
                    if item_index_to_remove != -1:
                         try:
                              current_location['items'].pop(item_index_to_remove)
                         except IndexError:
                              logging.error(f"IndexError removing item at index {item_index_to_remove} from location {current_location_id}. List may have changed unexpectedly.")
                         except KeyError:
                              logging.error(f"KeyError: 'items' key missing from location {current_location_id} during removal.")


                # If not taken from ground, check if it's inside a container needing 'open'
                if not item_taken:
                    interactables_in_location = current_location.get('interactables', [])
                    is_unopened_container = False
                    if isinstance(interactables_in_location, list): # Check type
                        for interactable_data in interactables_in_location:
                             if isinstance(interactable_data, dict) and noun == interactable_data.get('name', '').lower():
                                 # Check if it's a container that needs opening first and isn't empty
                                 actions_dict = interactable_data.get('actions', {})
                                 is_container_action = isinstance(actions_dict, dict) and ('open' in actions_dict or 'loot_container' in actions_dict.values())
                                 is_not_empty = interactable_data.get('state') != 'empty'
                                 # Check if contains_items exists and is a non-empty list
                                 contains_items_list = interactable_data.get('contains_items')
                                 has_items = isinstance(contains_items_list, list) and bool(contains_items_list)

                                 if is_container_action and is_not_empty and has_items:
                                     print(f"You need to open the {noun} first to take things from it.")
                                     is_unopened_container = True
                                     break

                    # If not found in items list and not an unopened container
                    if not is_unopened_container:
                         print(f"You don't see any '{noun}' here to take.")

            action_executed = True


        # --- Handle Other Noun-Based Actions (Examine, Open, Read, etc.) ---
        elif noun: # Only process if a noun was provided
            target_found_and_action_valid = False

            # 1. Check NPCs first for 'examine'
            if verb == "examine":
                matched_npc_data = None
                npc_list_ids = current_location.get('npcs', [])
                if isinstance(npc_list_ids, list): # Check type
                    for npc_id in npc_list_ids:
                         if not isinstance(npc_id, str): continue
                         npc_data = game_npc_data.get(npc_id)
                         if npc_data and isinstance(npc_data, dict):
                              npc_name_lower = npc_data.get('name','').lower()
                              aliases = npc_data.get('aliases', [])
                              npc_aliases_lower = [a.lower() for a in aliases if isinstance(a, str)] if isinstance(aliases, list) else []
                              if noun == npc_name_lower or noun in npc_aliases_lower:
                                  matched_npc_data = npc_data
                                  break # Found matching NPC
                if matched_npc_data:
                     print("-" * 30)
                     # Use examined_description if available, otherwise default description
                     examine_desc = matched_npc_data.get("examined_description", matched_npc_data.get("description"))
                     if not examine_desc: examine_desc = f"You look closely at {matched_npc_data.get('name','them')}."
                     use_textwrap(examine_desc)
                     # Suggest talking if possible
                     if matched_npc_data.get("dialog_ref"):
                          print(f"\nYou could try: \n- talk {matched_npc_data.get('name').lower()}")
                     target_found_and_action_valid = True
                     action_executed = True # Mark as executed since we handled examine NPC

            # 2. If not examining an NPC, check Interactables and Items
            if not target_found_and_action_valid:
                potential_targets = (current_location.get('interactables', []) if isinstance(current_location.get('interactables'), list) else []) + \
                                    (current_location.get('items', []) if isinstance(current_location.get('items'), list) else [])
                matched_target_data = None
                for target_data in potential_targets:
                     if isinstance(target_data, dict):
                          object_name_lower = target_data.get('name', '').lower()
                          if noun == object_name_lower:
                              matched_target_data = target_data
                              break # Found matching object/item

                if matched_target_data:
                    # Use ID for tracking examined state, fallback to name if ID missing
                    object_id = matched_target_data.get('id', matched_target_data.get('name'))
                    available_object_actions = matched_target_data.get('actions', {})
                    if not isinstance(available_object_actions, dict): available_object_actions = {} # Handle malformed actions

                    if verb == "examine":
                        print("-" * 30)
                        if object_id in examined_this_visit:
                            # Use specific 'examined_description' if available and already examined this visit
                            examined_text = matched_target_data.get("examined_description")
                            use_textwrap(examined_text if examined_text else f"You find nothing new about the {noun}.")
                        else:
                            # First time examining this object *this visit*
                            # Check if 'examine' action maps to a specific display_text or event
                            action_string = available_object_actions.get(verb)
                            if action_string and isinstance(action_string, str): # Check action_string type
                                if action_string.startswith("display_text:"):
                                     use_textwrap(action_string.split(":", 1)[1].strip())
                                elif action_string.startswith("event:") or action_string.startswith("loot_container"):
                                     handle_game_event(action_string, character, current_location, matched_target_data)
                                else: # Default examine: use object's main description
                                     use_textwrap(matched_target_data.get('description', f"You look at the {noun}."))
                            else: # No specific examine action string, use default description
                                 use_textwrap(matched_target_data.get('description', f"You look at the {noun}."))
                            # Mark as examined *this visit* only if object_id is valid
                            if object_id: examined_this_visit.add(object_id)

                        # Suggest follow-up actions (excluding examine itself)
                        follow_up_verbs = [v for v in available_object_actions if v != "examine"]
                        if follow_up_verbs:
                            print("\nYou could also try:")
                            # Sort verbs for consistent order
                            for follow_up_verb in sorted(follow_up_verbs):
                                print(f"- {follow_up_verb} {noun}")
                        target_found_and_action_valid = True

                    elif verb in available_object_actions: # Handle verbs other than examine
                        action_string = available_object_actions[verb]
                        if isinstance(action_string, str): # Check type before using
                            logging.info("Executing action '%s' on object '%s' (%s) with string '%s'",
                                         verb, noun, object_id, action_string)
                            # Call event handler for actions defined in JSON
                            handle_game_event(action_string, character, current_location, matched_target_data)
                            target_found_and_action_valid = True
                        else:
                             logging.error(f"Invalid action string type for verb '{verb}' on object '{noun}': {action_string}")
                             print(f"There's a problem trying to '{verb}' the {noun}.")
                             target_found_and_action_valid = True # Handled by error message

                    else: # Verb is not 'examine' and not in the object's actions
                         print(f"You can't seem to '{verb}' the {noun}.")
                         target_found_and_action_valid = True # Handled by stating failure

                # 3. If noun was provided but didn't match any valid target
                elif not target_found_and_action_valid:
                    print(f"You don't see any '{noun}' here to {verb}.")
                    # No need to set target_found_and_action_valid = True here

            # Mark action as executed if any handler ran successfully or printed a failure message
            if target_found_and_action_valid:
                 action_executed = True

        # --- Handle Unknown Commands ---
        # This runs if no specific handler above set action_executed = True
        if not action_executed:
            # Provide slightly more specific feedback if possible
            if verb and noun: print(f"You can't '{verb}' the '{noun}' here, or you don't see a '{noun}'.")
            elif verb: print(f"You can't just '{verb}' here.")
            else: print(f"Unknown command: '{command}'")


        # --- Loop Continuation/End ---
        if game_is_running:
             # Add separator unless the last action was just 'look' (which adds its own separators)
             if not (verb == "look" and not noun):
                 print("-" * 30) # Separator before next prompt
             continue # Go to next iteration of the loop
        else:
            break # Exit loop if game_is_running became False (e.g., quit command or player death)

    # --- End of game loop ---
    print("\n--- Game Loop Ended ---") # Changed message slightly

# --- Title Screen / Game Start Function ---
def title_screen():
    """Handles the title screen, data loading, character creation, and starts the main game loop."""
    global game_data, game_items_data, game_locations_data, game_npc_data # Make sure globals are modified
    os.system('cls' if os.name == 'nt' else 'clear')
    print('------------------------------')
    print('- A Sound of Distant Thunder -')
    print('------------------------------')
    # Add other title elements...
    print('-          1. Play           -')
    print('-          2. Help           -')
    print('-          3. Quit           -')
    print('------------------------------')

    logging.info("--- Loading All Game Data ---")
    # Call the main data loader function
    try:
        game_data = data_loader.load_all_data() # Assumes base path is correct
    except Exception as e:
         logging.exception("CRITICAL ERROR during data loading!")
         print("\nFATAL ERROR: An unexpected error occurred during data loading.")
         print("Check game.log for details.")
         sys.exit(1)


    # Check if data loading failed critically
    if game_data is None or not game_data.get("locations") or not game_data.get("items"):
        print("\nFATAL ERROR: Failed to load essential game data (locations or items). Check paths and JSON files.")
        print("Check game.log for details.")
        logging.critical("Essential data loading failed. Exiting.")
        sys.exit(1)

    # Assign loaded data to global variables
    game_locations_data = game_data.get("locations", {})
    game_items_data = game_data.get("items", {})
    game_npc_data = game_data.get("npcs", {}) # Will be empty dict if loading failed or no NPCs

    logging.info("--- Data Load Complete ---")
    logging.info("Items: %d, Locations: %d, NPCs: %d",
                 len(game_items_data), len(game_locations_data), len(game_npc_data))

    while True:
        option = input("> ")
        if option.lower() == "play" or option == "1":
            # Pass game_items_data to class selection for starting inventory
            try:
                character = hero.class_selection(game_items_data=game_items_data)
            except Exception as e:
                 logging.exception("Error during character selection!")
                 print("An error occurred during character selection. Please check logs.")
                 character = None # Ensure character is None if creation fails

            if character is None:
                 print("Character creation failed or was cancelled.")
                 continue # Go back to title menu

            # --- Set Start Location ---
            start_location_id = "boat_deck" # Define your starting location ID
            if start_location_id in game_locations_data:
                character.set_location(start_location_id)
                logging.info("Set player start location to '%s'", start_location_id)
            else:
                # Attempt to find *any* valid location if start fails
                fallback_location = next(iter(game_locations_data), None)
                if fallback_location:
                    print(f"Warning: Start location '{start_location_id}' not found! Starting at '{fallback_location}' instead.")
                    logging.warning("Start location '%s' not found! Using fallback '%s'.", start_location_id, fallback_location)
                    character.set_location(fallback_location)
                else:
                     print(f"CRITICAL ERROR: Start location '{start_location_id}' not found and no other locations available!")
                     logging.critical("Start location '%s' not found and no fallback locations loaded!", start_location_id)
                     sys.exit(1) # Cannot proceed without a location

            # --- Display Initial Info ---
            print("-" * 30)
            print('--Your Character\'s Stats-----')
            # Use character object's getter methods
            print(f"- Health: {character.get_health_points()}/{character.get_hp_limit()}")
            print(f"- Defence: {character.get_defence_points()}")
            print(f"- Melee Attack: {character.get_strength_attribute()}")
            print(f"- Gun Skill: {character.get_gun_skill()}")
            print(f"- Luck: {character.get_luck()}")
            print(f"- Charm: {character.get_charm_attribute()}")
            print(f"- Stealth: {character.get_stealth_attribute()}")
            print("-" * 30)
            # Display intro text (Consider moving this to an event triggered by entering start location?)
            print('-         Chapter 1          -')
            print("-" * 30)
            # Consider loading intro text from a file or data structure?
            intro_text = """That sound of distant thunder was low and ominous. Like some kind of a warning...""" # Your full intro text
            use_textwrap(intro_text)
            print("-" * 30)

            # --- Start the Main Game Loop ---
            try:
                main_game_loop(character)
            except Exception as e:
                 logging.exception("CRITICAL ERROR occurred in main_game_loop!")
                 print("\n\nFATAL ERROR: An unexpected error occurred during gameplay.")
                 print("The game cannot continue. Please check game.log for details.")
                 # Optionally try to save score or state here before exiting
                 sys.exit(1)


            # After the loop ends (e.g., player quit or game over)
            print("\nReturning to Title Screen (or exiting).")
            # Decide if you want to loop back to title or exit here
            # For now, just ends the 'play' option loop
            break # Example: Exit title loop after game loop finishes

        elif option.lower() == "help" or option == "2":
            help_menu() # Use the defined help_menu function
        elif option.lower() == "quit" or option == "3":
            print("Exiting game. Goodbye!")
            sys.exit()
        else:
            print("Invalid option. Please enter 1, 2, or 3 (or Play, Help, Quit).")


# --- Main Execution Guard ---
if __name__ == "__main__":
    # --- Setup Logging ---
    log_filename = 'game.log'
    log_level = logging.INFO # Change to logging.DEBUG for more detail
    log_format = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s' # Added filename/lineno
    log_datefmt = '%Y-%m-%d %H:%M:%S'
    log_filemode = 'w' # 'w' overwrites log each run, 'a' appends

    # Basic configuration first
    logging.basicConfig(level=log_level,
                        format=log_format,
                        datefmt=log_datefmt,
                        filename=log_filename,
                        filemode=log_filemode)

    # Optional: Add a handler to also print logs to console (e.g., for warnings/errors)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING) # Show warnings and above on console
    formatter = logging.Formatter(log_format, datefmt=log_datefmt)
    console_handler.setFormatter(formatter)
    # Add handler to the root logger
    logging.getLogger('').addHandler(console_handler)

    logging.info("="*20 + " Game Started " + "="*20)
    # --- Start the Game ---
    try:
        title_screen()
    except Exception as e:
         # Catch potential errors during title screen/initialization
         logging.exception("CRITICAL ERROR during game initialization (title_screen)!")
         print("\n\nFATAL ERROR: An unexpected error occurred before gameplay could start.")
         print("Please check game.log for details.")
         sys.exit(1) # Exit if title screen fails critically

    logging.info("="*20 + " Game Ended " + "="*20)
