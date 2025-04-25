# --- In main/game.py ---
import sys
import os
import copy
import logging
import textwrap # If Util.py doesn't have use_textwrap or you prefer it here

# Import your modules (adjust paths if needed)
from . import hero # Assuming hero.py is in the same directory
from . import inventory
from . import actions # Use the provided actions.py
from . import battle_system # Assuming it exists
from . import dialog_system # <<< Import the new dialog system
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
# (Ensure the handle_game_event function from the previous version is here)
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

        live_target_data = None
        interactable_index = -1
        interactable_list = location_data.get('interactables', [])
        for index, data in enumerate(interactable_list):
            if data.get('id') == target_id:
                live_target_data = data
                interactable_index = index
                break

        if live_target_data is None:
             print(f"Error: Could not find live data for interactable ID '{target_id}'.")
             logging.error("Could not find live data for interactable ID '%s'", target_id)
             print("-" * 30)
             return

        current_state = live_target_data.get('state', 'closed')

        if current_state != 'empty':
            print(f"You open the {target_name}.")
            item_ids_in_container = live_target_data.get('contains_items', [])

            if not item_ids_in_container:
                print("...but it's empty.")
                location_data['interactables'][interactable_index]['state'] = 'empty'
                location_data['interactables'][interactable_index]['description'] = f"An empty {target_name}."
                verb_that_triggered = next((v for v, a in target_data.get('actions',{}).items() if a == event_string), None)
                if verb_that_triggered and 'actions' in location_data['interactables'][interactable_index] and verb_that_triggered in location_data['interactables'][interactable_index].get('actions',{}):
                     if 'actions' in location_data['interactables'][interactable_index]:
                          location_data['interactables'][interactable_index]['actions'].pop(verb_that_triggered, None)
                          logging.debug(f"Removed '{verb_that_triggered}' action for '{target_id}'.")

            else: # Container has items listed
                items_found_data = []
                items_found_names = []
                for item_id in item_ids_in_container:
                    item_data = game_items_data.get(item_id)
                    if item_data:
                        items_found_data.append(item_data)
                        items_found_names.append(item_data.get('name', item_id))
                    else: logging.warning("Item definition missing for '%s' in container '%s'.", item_id, target_id)

                if items_found_names:
                    print("Inside you find:")
                    for name in items_found_names: print(f"- {name}")
                    while True:
                        choice = input("Take these items? (yes/no) > ").lower().strip()
                        if choice in ['yes', 'y']:
                            print("\nYou added:")
                            items_added_count = 0
                            for item_data_to_add in items_found_data:
                                if character.add_inventory(copy.deepcopy(item_data_to_add)):
                                    item_name = item_data_to_add.get('name', item_data_to_add.get('id','unknown item'))
                                    print(f"- {item_name}")
                                    items_added_count += 1
                                else:
                                    print(f"Inventory full. Could not take {item_data_to_add.get('name', 'item')}.")

                            location_data['interactables'][interactable_index]['state'] = 'empty'
                            location_data['interactables'][interactable_index]['description'] = f"An empty {target_name}."
                            location_data['interactables'][interactable_index]['contains_items'] = []
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
             print(f"The {target_name} is in an unusual state ('{current_state}') and cannot be interacted with like that right now.")

    # --- Handle Display Text ---
    elif action_type == "display_text":
        if action_payload:
            use_textwrap(action_payload)
        else:
            logging.warning("Action 'display_text' called without payload.")
            use_textwrap("You look, but learn nothing new.")

    # --- Handle other specific event types ---
    elif action_type == "event" and action_payload == "display_dossier_text":
        use_textwrap("Contains mission details. Target: Secure island facility. High risk, high reward. Communications are down. Investigate.")
        logging.info("Displayed dossier text event.")

    else:
        print(f"You try to interact using '{event_string}', but nothing specific happens yet.")
        logging.warning("Unhandled action/event type triggered: %s", event_string)

    print("-" * 30)


# --- Main Game Loop ---
def main_game_loop(character):
    """
    Main loop: Displays location, suggests actions, gets input, processes commands.
    Handles standard commands, movement, talk, and generic object actions.
    Tracks examined state per location visit.
    """
    global game_locations_data, game_items_data, game_npc_data # Access globals

    logging.debug(f"Keys in game_npc_data: {list(game_npc_data.keys())}")

    game_is_running = True
    first_look = True
    examined_this_visit = set()
    previous_location_id = None

    while game_is_running:
        current_location_id = character.get_location()
        if not current_location_id or current_location_id not in game_locations_data:
            print(f"ERROR: Unknown or invalid location ID '{current_location_id}'. Ending game.")
            logging.critical("Player location '%s' invalid or not found in game_locations_data.", current_location_id)
            break
        current_location = game_locations_data[current_location_id]

        if current_location_id != previous_location_id:
            logging.debug(f"Location changed from {previous_location_id} to {current_location_id}. Clearing examined set.")
            examined_this_visit.clear()
            previous_location_id = current_location_id
            first_look = True

        print("-" * 30)
        print(f"Location: {current_location.get('name', 'Unknown Area')}")
        print("-" * 30)
        has_visited = character.has_visited(current_location_id)
        if not has_visited or first_look:
            description = current_location.get('description', 'You see nothing remarkable.')
            use_textwrap(description)
            if not has_visited: character.add_visited_location(current_location_id)
            entry_events = current_location.get("events_on_entry", [])
            if entry_events:
                 logging.info(f"Location '{current_location_id}' has entry events: {entry_events}")
                 # TODO: Implement handling for entry events
        else:
            description = current_location.get('visited_description', current_location.get('description', 'You see nothing remarkable.'))
            use_textwrap(description)

        print("-" * 30) # Separator before context lists
        npcs_here = current_location.get('npcs', [])
        if npcs_here:
            print("You see:")
            for npc_id in npcs_here:
                npc_data = game_npc_data.get(npc_id)
                npc_name = npc_data.get('name', npc_id) if npc_data else npc_id
                print(f"- {npc_name}")

        interactables_here = current_location.get('interactables', [])
        items_here = current_location.get('items', [])
        if interactables_here or items_here:
             if not npcs_here: print("You notice:")
             else: print("Also here:")
             for interactable_data in interactables_here if isinstance(interactables_here, list) else []:
                 i_name = interactable_data.get('name', 'an object')
                 i_state = interactable_data.get('state')
                 display_name = f"a {i_name}"
                 if i_state and i_state != 'normal': display_name += f" ({i_state})"
                 print(f"- {display_name}")
             for item_data in items_here if isinstance(items_here, list) else []:
                  item_name = item_data.get('name', 'an item')
                  print(f"- a {item_name}")

        available_exits = current_location.get('exits', {})
        if available_exits:
            visible_exits = {cmd: dest for cmd, dest in available_exits.items() if not cmd.startswith("_")}
            if visible_exits:
                 print("\nPossible Exits:")
                 for exit_cmd in sorted(visible_exits.keys()): print(f"- {exit_cmd}")

        first_look = False
        print("-" * 30)

        available_actions_list = actions.get_available_actions(current_location)
        print("Suggested actions:")
        max_suggestions = 15
        for i, action in enumerate(available_actions_list):
             if i >= max_suggestions:
                  print("- (more actions possible...)")
                  break
             print(f"- {action}")
        print("-" * 20)

        command = input("> ").lower().strip()
        logging.debug("Player command: '%s'", command)
        if not command: continue

        parts = command.split(maxsplit=1)
        verb = parts[0] if parts else ""
        noun = parts[1] if len(parts) > 1 else ""
        logging.debug(f"Parsed command: verb='{verb}', noun='{noun}'")

        action_executed = False

        if verb == "quit":
            print("Quitting game.")
            game_is_running = False
            action_executed = True
        elif verb == "help":
            help_menu()
            action_executed = True
        elif verb == "inventory":
            inventory.inventory(character)
            action_executed = True
        elif verb == "look" and not noun:
            first_look = True
            print("\nLooking around again...")
            action_executed = True

        elif verb == "go":
            available_exits = current_location.get('exits', {})
            if noun in available_exits:
                destination_id = available_exits[noun]
                if destination_id not in game_locations_data:
                    print(f"Error: The way '{noun}' leads nowhere functional yet.")
                    logging.error("Movement failed: Dest ID '%s' not found in loaded locations.", destination_id)
                else:
                    print(f"\nYou go {noun}...")
                    character.set_location(destination_id)
                    logging.info("Player moved from %s to %s via 'go %s'", current_location_id, destination_id, noun)
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
                for npc_id in npc_list_ids:
                    npc_data = game_npc_data.get(npc_id)
                    if not npc_data: continue # Skip if data missing

                    npc_name_lower = npc_data.get('name', '').lower()
                    aliases = npc_data.get('aliases', [])
                    npc_aliases_lower = [alias.lower() for alias in aliases] if isinstance(aliases, list) else []

                    if noun == npc_name_lower or noun in npc_aliases_lower:
                        target_npc_data = npc_data
                        logging.info(f"Matched input '{noun}' to NPC: {npc_id} ('{npc_data.get('name')}')")
                        break

                if target_npc_data:
                    # --- <<< Integration Point >>> ---
                    # Call the dialog system runner
                    dialog_result = dialog_system.run_conversation(character, target_npc_data)
                    # --- <<< End Integration Point >>> ---

                    # --- Handle Dialog Result ---
                    if dialog_result:
                        status = dialog_result.get('status')
                        if status == 'start_combat':
                            combat_target_id = dialog_result.get('combat_target_id')
                            if combat_target_id and combat_target_id in game_npc_data:
                                print(f"\nDialogue breaks down! {target_npc_data.get('name')} attacks!")
                                # TODO: Need to handle how battle_system gets enemy data/object
                                # Assuming battle_system can handle the NPC data dict for now
                                enemy_data_for_combat = game_npc_data[combat_target_id]
                                battle_system.battle_state(character, enemy_data_for_combat)
                                # Check if player died in combat
                                if character.get_health_points() <= 0:
                                     game_is_running = False # End game if player died
                            else:
                                logging.error(f"Dialog requested combat with invalid target ID: {combat_target_id}")
                        elif status == 'error':
                            print("An error occurred during the conversation.")
                        # 'ended' or 'no_dialog' statuses require no special action here
                    # --- End Handle Dialog Result ---

                else: # No match found after checking all NPCs in the location
                    print(f"You don't see anyone called '{noun}' here to talk to.")

            action_executed = True


        elif verb == "take":
            if not noun:
                print("Take what?")
            else:
                item_taken = False
                items_in_location = list(current_location.get('items', []))
                item_index_to_remove = -1

                for i, item_data in enumerate(items_in_location):
                    if isinstance(item_data, dict):
                         item_name_lower = item_data.get('name', '').lower()
                         item_id = item_data.get('id')
                         if noun == item_name_lower:
                            if not item_id:
                                logging.error(f"Item '{item_name_lower}' in location {current_location_id} is missing an 'id'. Cannot take.")
                                print(f"There seems to be a problem with the {item_name_lower}.")
                                item_taken = True
                                break
                            full_item_data = game_items_data.get(item_id)
                            if not full_item_data:
                                 logging.error(f"Full item definition not found for ID '{item_id}' when taking.")
                                 print(f"There's a problem with the definition of the {item_name_lower}.")
                                 item_taken = True
                                 break
                            if character.add_inventory(copy.deepcopy(full_item_data)):
                                print(f"You take the {item_name_lower}.")
                                logging.info(f"Player took item '{item_id}' from location '{current_location_id}'")
                                item_index_to_remove = i
                                item_taken = True
                            else:
                                print(f"Your inventory is full. You can't take the {item_name_lower}.")
                                item_taken = True
                            break
                    else:
                         logging.warning(f"Malformed item entry in location '{current_location_id}': {item_data}")

                if item_index_to_remove != -1:
                     current_location['items'].pop(item_index_to_remove)

                if not item_taken:
                    interactables_in_location = current_location.get('interactables', [])
                    is_unopened_container = False
                    for interactable_data in interactables_in_location:
                         if isinstance(interactable_data, dict) and noun == interactable_data.get('name', '').lower():
                             is_container_action = 'open' in interactable_data.get('actions', {}) or 'loot_container' in interactable_data.get('actions', {}).values()
                             is_not_empty = interactable_data.get('state') != 'empty'
                             if is_container_action and is_not_empty and interactable_data.get('contains_items'):
                                 print(f"You need to open the {noun} first to take things from it.")
                                 is_unopened_container = True
                                 break
                    if not is_unopened_container:
                         print(f"You don't see any '{noun}' here to take.")
            action_executed = True

        elif noun: # Handle other noun-based actions
            target_found_and_action_valid = False
            if verb == "examine":
                matched_npc_data = None
                npc_list_ids = current_location.get('npcs', [])
                for npc_id in npc_list_ids:
                     npc_data = game_npc_data.get(npc_id)
                     if npc_data:
                          npc_name_lower = npc_data.get('name','').lower()
                          aliases = npc_data.get('aliases', [])
                          npc_aliases_lower = [a.lower() for a in aliases] if isinstance(aliases, list) else []
                          if noun == npc_name_lower or noun in npc_aliases_lower:
                              matched_npc_data = npc_data
                              break
                if matched_npc_data:
                     print("-" * 30)
                     examine_desc = matched_npc_data.get("examined_description", matched_npc_data.get("description"))
                     if not examine_desc: examine_desc = f"You look closely at {matched_npc_data.get('name','them')}."
                     use_textwrap(examine_desc)
                     if matched_npc_data.get("dialog_ref"):
                          print(f"\nYou could try: \n- talk {matched_npc_data.get('name').lower()}")
                     target_found_and_action_valid = True
                     action_executed = True

            if not target_found_and_action_valid:
                potential_targets = current_location.get('interactables', []) + current_location.get('items', [])
                matched_target_data = None
                for target_data in potential_targets:
                     if isinstance(target_data, dict):
                          object_name_lower = target_data.get('name', '').lower()
                          if noun == object_name_lower:
                              matched_target_data = target_data
                              break

                if matched_target_data:
                    object_id = matched_target_data.get('id', matched_target_data.get('name'))
                    available_object_actions = matched_target_data.get('actions', {})

                    if verb == "examine":
                        print("-" * 30)
                        if object_id in examined_this_visit:
                            examined_text = matched_target_data.get("examined_description")
                            use_textwrap(examined_text if examined_text else f"You find nothing new about the {noun}.")
                        else:
                            action_string = available_object_actions.get(verb)
                            if action_string and action_string.startswith("display_text:"):
                                 use_textwrap(action_string.split(":", 1)[1].strip())
                            elif action_string and (action_string.startswith("event:") or action_string.startswith("loot_container")):
                                 handle_game_event(action_string, character, current_location, matched_target_data)
                            else:
                                 use_textwrap(matched_target_data.get('description', f"You look at the {noun}."))
                            examined_this_visit.add(object_id)

                        follow_up_verbs = [v for v in available_object_actions if v != "examine"]
                        if follow_up_verbs:
                            print("\nYou could also try:")
                            for follow_up_verb in sorted(follow_up_verbs): print(f"- {follow_up_verb} {noun}")
                        target_found_and_action_valid = True

                    elif verb in available_object_actions:
                        action_string = available_object_actions[verb]
                        logging.info("Executing action '%s' on object '%s' (%s) with string '%s'", verb, noun, object_id, action_string)
                        handle_game_event(action_string, character, current_location, matched_target_data)
                        target_found_and_action_valid = True
                    else:
                         print(f"You can't seem to '{verb}' the {noun}.")
                         target_found_and_action_valid = True

                if not target_found_and_action_valid:
                    print(f"You don't see any '{noun}' here to {verb}.")

            if target_found_and_action_valid:
                 action_executed = True

        if not action_executed:
            if verb and noun: print(f"You can't '{verb}' the '{noun}' here, or you don't see a '{noun}'.")
            elif verb: print(f"You can't just '{verb}' here.")
            else: print(f"Unknown command: '{command}'")

        if game_is_running:
             if not (verb == "look" and not noun):
                 print("-" * 30)
             continue
        else:
            break

    print("\n--- Game Loop Ended ---")

# --- Title Screen / Game Start Function ---
def title_screen():
    global game_data, game_items_data, game_locations_data, game_npc_data
    os.system('cls' if os.name == 'nt' else 'clear')
    print('------------------------------')
    print('- A Sound of Distant Thunder -')
    print('------------------------------')
    print('-          1. Play           -')
    print('-          2. Help           -')
    print('-          3. Quit           -')
    print('------------------------------')

    logging.info("--- Loading All Game Data ---")
    game_data = data_loader.load_all_data()

    if game_data is None or not game_data.get("locations") or not game_data.get("items"):
        print("\nFATAL ERROR: Failed to load essential game data (locations or items). Check paths and JSON files.")
        print("Check game.log for details.")
        logging.critical("Essential data loading failed. Exiting.")
        sys.exit(1)

    game_locations_data = game_data.get("locations", {})
    game_items_data = game_data.get("items", {})
    game_npc_data = game_data.get("npcs", {})

    logging.info("--- Data Load Complete ---")
    logging.info("Items: %d, Locations: %d, NPCs: %d",
                 len(game_items_data), len(game_locations_data), len(game_npc_data))

    while True:
        option = input("> ")
        if option.lower() == "play" or option == "1":
            character = hero.class_selection(game_items_data=game_items_data)
            if character is None:
                 print("Character creation failed or was cancelled.")
                 continue

            start_location_id = "boat_deck"
            if start_location_id in game_locations_data:
                character.set_location(start_location_id)
                logging.info("Set player start location to '%s'", start_location_id)
            else:
                fallback_location = next(iter(game_locations_data), None)
                if fallback_location:
                    print(f"Warning: Start location '{start_location_id}' not found! Starting at '{fallback_location}' instead.")
                    logging.warning("Start location '%s' not found! Using fallback '%s'.", start_location_id, fallback_location)
                    character.set_location(fallback_location)
                else:
                     print(f"CRITICAL ERROR: Start location '{start_location_id}' not found and no other locations available!")
                     logging.critical("Start location '%s' not found and no fallback locations loaded!", start_location_id)
                     sys.exit(1)

            print("-" * 30)
            print('--Your Character\'s Stats-----')
            print(f"- Health: {character.get_health_points()}/{character.get_hp_limit()}")
            print(f"- Defence: {character.get_defence_points()}")
            print(f"- Melee Attack: {character.get_strength_attribute()}")
            print(f"- Gun Skill: {character.get_gun_skill()}")
            print(f"- Luck: {character.get_luck()}")
            print(f"- Charm: {character.get_charm_attribute()}")
            print(f"- Stealth: {character.get_stealth_attribute()}")
            print("-" * 30)
            print('-         Chapter 1          -')
            print("-" * 30)
            intro_text = """That sound of distant thunder was low and ominous. Like some kind of a warning...""" # Your full intro text
            use_textwrap(intro_text)
            print("-" * 30)

            main_game_loop(character)

            print("\nReturning to Title Screen (or exiting).")
            break

        elif option.lower() == "help" or option == "2":
            help_menu()
        elif option.lower() == "quit" or option == "3":
            print("Exiting game. Goodbye!")
            sys.exit()
        else:
            print("Invalid option. Please enter 1, 2, or 3 (or Play, Help, Quit).")

# --- Main Execution Guard ---
if __name__ == "__main__":
    log_filename = 'game.log'
    log_level = logging.INFO
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_datefmt = '%Y-%m-%d %H:%M:%S'
    log_filemode = 'w'

    logging.basicConfig(level=log_level,
                        format=log_format,
                        datefmt=log_datefmt,
                        filename=log_filename,
                        filemode=log_filemode)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    formatter = logging.Formatter(log_format, datefmt=log_datefmt)
    console_handler.setFormatter(formatter)
    logging.getLogger('').addHandler(console_handler)

    logging.info("===== Game Started =====")
    title_screen()
    logging.info("===== Game Ended =====")

