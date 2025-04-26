# --- In main/game.py ---
import sys
import os
import copy
import logging
import textwrap

# Import your modules
from . import hero
from . import inventory # Assuming inventory.loot_add exists
from . import actions
from . import battle_system
from . import dialog_system
from . import data_loader
from . import mechanics
from .NPC import Enemy, Human # Import NPC classes

# --- Global Data Variables ---
game_locations_data = {}
game_items_data = {}
game_npc_data = {}

# --- Utility Function ---
def use_textwrap(text):
    """Wraps text for display."""
    dedented_text = textwrap.dedent(str(text)).strip()
    print(textwrap.fill(dedented_text, width=70))

# --- Help Menu Function ---
def help_menu():
    """Displays help information."""
    print("\n--- Help Menu ---")
    print("Common: look, go [dir], examine [target], talk [person], take [item], inventory, help, quit")
    print("Combat: attack [person]")
    print("-----------------\n")

# --- Event Handler Function ---
# (handle_game_event function remains the same as previous version)
def handle_game_event(event_string, character, location_data, target_data):
    """Handles specific game events/actions triggered by action strings."""
    global game_items_data, game_locations_data
    logging.info(f"Handling event: {event_string} for target: {target_data.get('name', 'N/A')}")
    print("-" * 30)
    action_type = event_string; action_payload = None
    if ":" in event_string: parts = event_string.split(":", 1); action_type = parts[0]; action_payload = parts[1] if len(parts) > 1 else None

    if action_type == "loot_container":
        target_id = target_data.get('id'); target_name = target_data.get('name', 'container')
        live_target_data = None; interactable_index = -1; interactable_list = location_data.get('interactables', [])
        if isinstance(interactable_list, list):
            for index, data in enumerate(interactable_list):
                if isinstance(data, dict) and data.get('id') == target_id: live_target_data = data; interactable_index = index; break
        else: logging.warning(f"Loc '{location_data.get('location_id', 'Unknown')}' malformed 'interactables': {interactable_list}")
        if live_target_data is None: print(f"Error: Cannot find live data for '{target_id}'."); logging.error("Cannot find live data for '%s'", target_id); print("-" * 30); return
        current_state = live_target_data.get('state', 'closed')
        if current_state != 'empty':
            print(f"You open the {target_name}.")
            item_ids_in_container = live_target_data.get('contains_items', [])
            if not item_ids_in_container or not isinstance(item_ids_in_container, list):
                print("...but it's empty."); location_data['interactables'][interactable_index]['state'] = 'empty'; location_data['interactables'][interactable_index]['description'] = f"An empty {target_name}."
                verb_that_triggered = next((v for v, a in target_data.get('actions',{}).items() if a == event_string), None)
                if verb_that_triggered and 'actions' in location_data['interactables'][interactable_index] and verb_that_triggered in location_data['interactables'][interactable_index].get('actions',{}):
                     if 'actions' in location_data['interactables'][interactable_index]: location_data['interactables'][interactable_index]['actions'].pop(verb_that_triggered, None)
            else:
                items_found_data = []; items_found_names = []
                for item_id in item_ids_in_container:
                    if not isinstance(item_id, str): logging.warning(f"Non-string ID in container '{target_id}': {item_id}"); continue
                    item_data = game_items_data.get(item_id)
                    if item_data and isinstance(item_data, dict): items_found_data.append(item_data); items_found_names.append(item_data.get('name', item_id))
                    else: logging.warning("Item def missing/malformed '%s' in container '%s'.", item_id, target_id)
                if items_found_names:
                    print("Inside you find:"); [print(f"- {name}") for name in items_found_names]
                    while True:
                        choice = input("Take these items? (yes/no) > ").lower().strip()
                        if choice in ['yes', 'y']:
                            print("\nYou added:"); items_added_count = 0
                            for item_data_to_add in items_found_data:
                                if character.add_inventory(copy.deepcopy(item_data_to_add)): print(f"- {item_data_to_add.get('name', 'item')}"); items_added_count += 1
                                else: print(f"Inventory full. Could not take {item_data_to_add.get('name', 'item')}.")
                            location_data['interactables'][interactable_index]['state'] = 'empty'; location_data['interactables'][interactable_index]['description'] = f"An empty {target_name}."
                            location_data['interactables'][interactable_index]['contains_items'] = []
                            verb_that_triggered = next((v for v, a in target_data.get('actions',{}).items() if a == event_string), None)
                            if verb_that_triggered and 'actions' in location_data['interactables'][interactable_index] and verb_that_triggered in location_data['interactables'][interactable_index]['actions']: location_data['interactables'][interactable_index]['actions'].pop(verb_that_triggered, None)
                            break
                        elif choice in ['no', 'n']: print("You close it back up."); break
                        else: print("Please answer yes or no.")
                else:
                    print("It seems to be empty."); location_data['interactables'][interactable_index]['state'] = 'empty'; location_data['interactables'][interactable_index]['description'] = f"An empty {target_name}."
                    verb_that_triggered = next((v for v, a in target_data.get('actions',{}).items() if a == event_string), None)
                    if verb_that_triggered and 'actions' in location_data['interactables'][interactable_index] and verb_that_triggered in location_data['interactables'][interactable_index]['actions']: location_data['interactables'][interactable_index]['actions'].pop(verb_that_triggered, None)
        elif current_state == 'empty': print(f"You check the {target_name} again, but it's empty.")
        else: print(f"The {target_name} state ('{current_state}') prevents interaction.")
    elif action_type == "display_text":
        if action_payload: use_textwrap(action_payload)
        else: logging.warning("display_text missing payload."); use_textwrap("You learn nothing new.")
    elif action_type == "event" and action_payload == "display_dossier_text":
        use_textwrap("Mission details: Secure island facility. High risk/reward. Comms down. Investigate."); logging.info("Displayed dossier.")
    else: print(f"Action '{event_string}' does nothing yet."); logging.warning("Unhandled action type: %s", event_string)
    print("-" * 30)


# --- NPC Instantiation Helper Function ---
def create_npc_instance(npc_data):
    """
    Creates an instance of an Enemy or Human class from NPC data dictionary.
    Also handles setting inventory and equipped items.
    """
    global game_items_data # Access global item definitions

    if not npc_data or not isinstance(npc_data, dict): logging.error("Invalid npc_data for instantiation."); return None
    npc_id = npc_data.get('id', 'unknown_npc'); name = npc_data.get('name', 'Unknown'); stats = npc_data.get('stats', {})
    if not isinstance(stats, dict): logging.warning(f"NPC '{npc_id}' has malformed 'stats'. Using defaults."); stats = {}
    health = stats.get('current_health', stats.get('max_health', 10)); max_health = stats.get('max_health', health)
    defence = stats.get('defense', 0); strength = stats.get('strength', 1); luck = stats.get('luck', 0); awareness = stats.get('awareness', 1)

    npc_instance = None # Initialize instance variable

    # --- Determine Class and Instantiate ---
    if 'gun_skill' in stats: # Check if it's a Human type
        gun_skill = stats.get('gun_skill', 0)
        try: npc_instance = Human(en_name=name, health=health, defence=defence, strength=strength, luck=luck, awareness=awareness, gun_skill=gun_skill)
        except Exception as e: logging.exception(f"Error creating Human instance {npc_id}:"); return None
    else: # Assume basic Enemy type
        try: npc_instance = Enemy(en_name=name, health=health, defence=defence, strength=strength, luck=luck, awareness=awareness)
        except Exception as e: logging.exception(f"Error creating Enemy instance {npc_id}:"); return None

    # --- Set Common Attributes (Post-Instantiation) ---
    npc_instance.set_hp_limit(max_health) # Ensure max HP is set
    npc_instance.set_description(npc_data.get('description'))
    npc_instance.original_id = npc_id # Store original ID

    # --- Set Inventory ---
    inventory_ids = npc_data.get('inventory', [])
    if isinstance(inventory_ids, list):
        npc_inventory_list = []
        for item_id in inventory_ids:
            if isinstance(item_id, str):
                item_definition = game_items_data.get(item_id)
                if item_definition and isinstance(item_definition, dict): npc_inventory_list.append(copy.deepcopy(item_definition))
                else: logging.warning(f"Item def missing/malformed for '{item_id}' in {npc_id}'s inventory.")
            else: logging.warning(f"Non-string item ID '{item_id}' found in {npc_id}'s inventory.")
        if hasattr(npc_instance, 'set_inventory'): npc_instance.set_inventory(npc_inventory_list)
        else: npc_instance.inventory = npc_inventory_list
    elif inventory_ids: logging.warning(f"NPC '{npc_id}' has malformed 'inventory' data: {inventory_ids}")

    # --- Set Equipped Items ---
    equipped_items_dict = npc_data.get('equipped_items', {})
    if isinstance(equipped_items_dict, dict):
        for slot, item_id in equipped_items_dict.items():
            if not isinstance(item_id, str): logging.warning(f"Invalid item ID '{item_id}' in slot '{slot}' for NPC '{npc_id}'."); continue
            item_definition = game_items_data.get(item_id)
            if item_definition and isinstance(item_definition, dict):
                item_copy = copy.deepcopy(item_definition); setter_method_name = None
                if slot == "gun" and hasattr(npc_instance, 'set_equipped_gun'): setter_method_name = 'set_equipped_gun'
                elif slot == "melee" and hasattr(npc_instance, 'set_equipped_melee'): setter_method_name = 'set_equipped_melee'
                elif slot == "armor_body" and hasattr(npc_instance, 'set_equipped_armour'): setter_method_name = 'set_equipped_armour'
                # Add more slots here if needed
                if setter_method_name:
                    try: getattr(npc_instance, setter_method_name)(item_copy); logging.debug(f"Equipped '{item_id}' to '{slot}' for '{npc_id}'.")
                    except AttributeError: logging.error(f"Missing setter '{setter_method_name}' for '{npc_id}'.")
                    except Exception as e: logging.exception(f"Error calling setter '{setter_method_name}' for '{npc_id}':")
                else: logging.warning(f"No setter method for slot '{slot}' on '{npc_id}'.")
            else: logging.warning(f"Item def missing/malformed for equipped '{item_id}' (slot: {slot}) for '{npc_id}'.")
    elif equipped_items_dict: logging.warning(f"NPC '{npc_id}' has malformed 'equipped_items' data: {equipped_items_dict}")

    logging.debug(f"Finished creating instance for {npc_id} (Class: {type(npc_instance).__name__})")
    return npc_instance


# --- Main Game Loop ---
def main_game_loop(character):
    """Main game loop."""
    # <<< Added Debug Print >>>
    print("DEBUG: >>> ENTERING main_game_loop <<<")
    global game_locations_data, game_items_data, game_npc_data
    logging.debug(f"NPC Data Keys: {list(game_npc_data.keys())}")
    game_is_running = True; first_look = True; examined_this_visit = set(); previous_location_id = None

    while game_is_running:
        current_location_id = character.get_location()
        if not current_location_id or current_location_id not in game_locations_data: print(f"ERROR: Invalid location ID '{current_location_id}'."); logging.critical("Invalid location '%s'.", current_location_id); break
        current_location = game_locations_data[current_location_id]

        if current_location_id != previous_location_id: logging.debug(f"Loc changed: {previous_location_id} -> {current_location_id}."); examined_this_visit.clear(); previous_location_id = current_location_id; first_look = True

        # --- Check for Hostile NPCs on Entry ---
        combat_started_on_entry = False
        entry_npcs = current_location.get('npcs', [])
        if first_look and isinstance(entry_npcs, list):
            for npc_id in list(entry_npcs): # Iterate copy
                if not isinstance(npc_id, str): continue
                npc_data = game_npc_data.get(npc_id)
                is_defeated = dialog_system._get_flag(f"npc_defeated_{npc_id}", default=False)
                if npc_data and isinstance(npc_data, dict) and npc_data.get("hostile") is True and not is_defeated:
                    npc_name = npc_data.get('name', npc_id)
                    logging.info(f"Hostile NPC '{npc_name}' ({npc_id}) found on entry.")
                    print(f"\nWARNING: {npc_name} looks hostile!")
                    reaction_dialog_ref = npc_data.get("on_attack_dialog_ref")
                    if reaction_dialog_ref:
                        logging.info(f"Running hostile reaction: {reaction_dialog_ref}")
                        try: dialog_system.run_conversation(character, npc_data, override_dialog_ref=reaction_dialog_ref)
                        except Exception as e: logging.exception("Error running hostile reaction:")
                    enemy_object = create_npc_instance(npc_data)
                    if enemy_object:
                        battle_result = None
                        try: battle_result = battle_system.battle_state(character, enemy_object, surprise=True)
                        except Exception as e: logging.exception("Battle error on entry:"); print("Combat error!")
                        if character.get_health_points() <= 0: logging.info("Player defeated on entry."); game_is_running = False; break
                        if battle_result and battle_result.get("status") == "enemy_defeated":
                            defeated_npc_obj = battle_result.get("defeated_npc_object")
                            defeated_npc_id_entry = getattr(defeated_npc_obj, 'original_id', None)
                            if defeated_npc_id_entry:
                                logging.info(f"Setting defeat flag for NPC {defeated_npc_id_entry}"); dialog_system._set_flag(f"npc_defeated_{defeated_npc_id_entry}", True)
                                dialog_system._set_flag(f"npc_looted_{defeated_npc_id_entry}", True) # Assume looted after battle
                                logging.info(f"Setting looted flag for NPC {defeated_npc_id_entry} after battle.")
                            else: logging.error("Could not get original_id from defeated NPC object on entry.")
                        combat_started_on_entry = True; break
                    else: logging.error(f"Failed instantiate hostile NPC {npc_id}")
        if not game_is_running: break
        if combat_started_on_entry: continue

        # --- Display Location ---
        print("-" * 30); print(f"Location: {current_location.get('name', '?Area?')}"); print("-" * 30)
        has_visited = character.has_visited(current_location_id)
        if not has_visited or first_look:
            description = current_location.get('description', 'No description.'); use_textwrap(description)
            if not has_visited: character.add_visited_location(current_location_id)
            entry_events = current_location.get("events_on_entry", [])
            if entry_events and isinstance(entry_events, list): logging.info(f"Entry events: {entry_events}") # TODO: Handle
            elif entry_events: logging.warning(f"Malformed 'events_on_entry': {entry_events}")
        else: use_textwrap(current_location.get('visited_description', current_location.get('description', 'No description.')))

        # --- Display Context ---
        print("-" * 30); npcs_here = current_location.get('npcs', [])
        if isinstance(npcs_here, list) and npcs_here:
            print("You see:")
            for npc_id in npcs_here:
                if not isinstance(npc_id, str): continue
                npc_data = game_npc_data.get(npc_id)
                npc_name = npc_data.get('name', npc_id) if npc_data and isinstance(npc_data, dict) else npc_id
                is_defeated = dialog_system._get_flag(f"npc_defeated_{npc_id}", default=False)
                if is_defeated: print(f"- Body of {npc_name}")
                else: print(f"- {npc_name}")
        elif npcs_here: logging.warning(f"Malformed 'npcs': {npcs_here}")
        interactables_here = current_location.get('interactables', []); items_here = current_location.get('items', [])
        valid_interactables = [i for i in interactables_here if isinstance(i, dict)] if isinstance(interactables_here, list) else []
        valid_items = [i for i in items_here if isinstance(i, dict)] if isinstance(items_here, list) else []
        if valid_interactables or valid_items:
             header = "You notice:" if not (isinstance(npcs_here, list) and npcs_here) else "Also here:"; print(header)
             for i_data in valid_interactables: i_name = i_data.get('name', '?'); i_state = i_data.get('state'); print(f"- a {i_name}" + (f" ({i_state})" if i_state and i_state not in ['normal', None] else ""))
             for i_data in valid_items: print(f"- a {i_data.get('name', '?')}")
        elif interactables_here: logging.warning(f"Malformed 'interactables': {interactables_here}")
        elif items_here: logging.warning(f"Malformed 'items': {items_here}")
        available_exits = current_location.get('exits', {})
        if isinstance(available_exits, dict) and available_exits:
            visible_exits = {cmd: dest for cmd, dest in available_exits.items() if isinstance(cmd, str) and not cmd.startswith("_")}
            if visible_exits: print("\nPossible Exits:"); [print(f"- {cmd}") for cmd in sorted(visible_exits.keys())]
        elif available_exits: logging.warning(f"Malformed 'exits': {available_exits}")
        first_look = False; print("-" * 30)

        # --- Display Actions ---
        available_actions_list = actions.get_available_actions(current_location, character, game_npc_data)
        print("Suggested actions:")
        if isinstance(available_actions_list, list):
            suggested_attacks = []
            if isinstance(npcs_here, list):
                 for npc_id in npcs_here:
                      is_defeated = dialog_system._get_flag(f"npc_defeated_{npc_id}", default=False)
                      if not is_defeated:
                          npc_data = game_npc_data.get(npc_id)
                          if npc_data and isinstance(npc_data, dict):
                               npc_name = npc_data.get('name');
                               if npc_name: suggested_attacks.append(f"attack {npc_name.lower()}")
            combined_suggestions = available_actions_list + suggested_attacks
            final_suggestions = list(dict.fromkeys(combined_suggestions))
            for i, action in enumerate(final_suggestions):
                 if isinstance(action, str): print(f"- {action}")
                 else: logging.warning(f"Non-string action: {action}")
        else: logging.error(f"Bad suggestions list: {available_actions_list}")
        print("-" * 20)

        # --- Input & Parse ---
        try: command = input("> ").lower().strip()
        except EOFError: logging.warning("EOF received."); command = "quit"
        logging.debug("Input: '%s'", command)
        if not command: continue
        parts = command.split(maxsplit=1); verb = parts[0] if parts else ""; noun = parts[1] if len(parts) > 1 else ""; action_executed = False
        logging.debug(f"Parsed: V='{verb}', N='{noun}'")

        # --- Execute Actions ---
        battle_result = None # Initialize battle result for this turn

        if verb == "quit": print("Quitting."); game_is_running = False; action_executed = True
        elif verb == "help": help_menu(); action_executed = True
        elif verb == "inventory":
            try: inventory.inventory(character)
            except Exception as e: logging.exception("Inv error:"); print("Inv error.")
            action_executed = True
        elif verb == "look" and not noun: first_look = True; print("\nLooking..."); action_executed = True
        elif verb == "go":
            available_exits = current_location.get('exits', {});
            if isinstance(available_exits, dict) and noun in available_exits:
                dest_id = available_exits[noun]
                if not isinstance(dest_id, str): logging.error(f"Bad exit dest: {dest_id}"); print("Exit problem.")
                elif dest_id not in game_locations_data: print(f"Error: Way '{noun}' leads nowhere."); logging.error("Move fail: Dest '%s' missing.", dest_id)
                else: print(f"\nYou go {noun}..."); character.set_location(dest_id); logging.info("Moved: %s->%s via %s", current_location_id, dest_id, noun)
            else: print(f"Can't go '{noun}'.")
            action_executed = True
        # <<< Added Debug Print >>>
        elif verb == "talk" or verb == "speak":
            print(f"DEBUG: Entered 'talk' handler with noun: '{noun}'")
            if not noun: print("Talk who?")
            else:
                target_npc_data = None; npc_list_ids = current_location.get('npcs', [])
                # <<< Added Debug Print >>>
                print(f"DEBUG: NPC list for talk check: {npc_list_ids}")
                if isinstance(npc_list_ids, list):
                    for npc_id in npc_list_ids:
                        if not isinstance(npc_id, str): continue
                        npc_data = game_npc_data.get(npc_id)
                        print(f"DEBUG [Talk]: Checking ID '{npc_id}'. Data fetched: {'Yes' if npc_data else 'No'}")
                        if not npc_data or not isinstance(npc_data, dict): continue
                        npc_name_lower = npc_data.get('name', '').lower(); aliases = npc_data.get('aliases', []); npc_aliases_lower = [a.lower() for a in aliases if isinstance(a, str)] if isinstance(aliases, list) else []
                        print(f"DEBUG [Talk]: Comparing '{noun}' to '{npc_name_lower}' and {npc_aliases_lower}")
                        if noun == npc_name_lower or noun in npc_aliases_lower:
                            is_defeated = dialog_system._get_flag(f"npc_defeated_{npc_id}", default=False)
                            if is_defeated: print(f"No response from the body of {npc_data.get('name', 'the figure')}."); target_npc_data = None; action_executed = True; break
                            else: target_npc_data = npc_data; logging.info(f"Match talk: {npc_id}"); print(f"DEBUG [Talk]: Match found for {npc_id}"); break
                if target_npc_data:
                    dialog_result = None
                    try: dialog_result = dialog_system.run_conversation(character, target_npc_data)
                    except Exception as e: logging.exception("Dialog error:"); print("Conv error."); dialog_result = {"status": "error"}
                    if dialog_result and isinstance(dialog_result, dict):
                        status = dialog_result.get('status')
                        if status == 'start_combat':
                            combat_target_id = dialog_result.get('combat_target_id')
                            if combat_target_id and combat_target_id in game_npc_data:
                                print(f"\nDialogue breaks down! {target_npc_data.get('name')} attacks!")
                                enemy_data = game_npc_data[combat_target_id]; enemy_object = create_npc_instance(enemy_data)
                                if enemy_object:
                                    try: battle_result = battle_system.battle_state(character, enemy_object)
                                    except Exception as e: logging.exception("Battle error:"); print("Combat error.")
                                    if character.get_health_points() <= 0: logging.info("Player defeated."); game_is_running = False
                                else: logging.error(f"Failed instantiate {combat_target_id}")
                            else: logging.error(f"Dialog combat invalid target: {combat_target_id}")
                        elif status == 'error': pass
                    else: logging.error(f"Invalid dialog result: {dialog_result}")
                elif not action_executed: print(f"See no '{noun}' here.")
            action_executed = True
        # <<< Added Debug Print >>>
        elif verb == "attack":
            print(f"DEBUG: Entered 'attack' handler with noun: '{noun}'")
            if not noun: print("Attack who?")
            else:
                target_npc_data = None; npc_list_ids = current_location.get('npcs', [])
                 # <<< Added Debug Print >>>
                print(f"DEBUG: NPC list for attack check: {npc_list_ids}")
                if isinstance(npc_list_ids, list):
                    for npc_id in npc_list_ids:
                        if not isinstance(npc_id, str): continue
                        npc_data = game_npc_data.get(npc_id)
                        print(f"DEBUG [Attack]: Checking ID '{npc_id}'. Data fetched: {'Yes' if npc_data else 'No'}")
                        if not npc_data or not isinstance(npc_data, dict): continue
                        npc_name_lower = npc_data.get('name', '').lower(); aliases = npc_data.get('aliases', []); npc_aliases_lower = [a.lower() for a in aliases if isinstance(a, str)] if isinstance(aliases, list) else []
                        print(f"DEBUG [Attack]: Comparing '{noun}' to '{npc_name_lower}' and {npc_aliases_lower}")
                        if noun == npc_name_lower or noun in npc_aliases_lower:
                            is_defeated = dialog_system._get_flag(f"npc_defeated_{npc_id}", default=False)
                            if is_defeated: print(f"No point attacking the body of {npc_data.get('name', 'the figure')}."); target_npc_data = None; action_executed = True; break
                            else: target_npc_data = npc_data; logging.info(f"Player targets attack: {npc_id}"); print(f"DEBUG [Attack]: Match found for {npc_id}"); break
                if target_npc_data:
                    npc_id_attacked = target_npc_data.get('id'); npc_name_attacked = target_npc_data.get('name', 'them')
                    print(f"\nYou move to attack {npc_name_attacked}!")
                    reaction_dialog_ref = target_npc_data.get("on_attack_dialog_ref"); is_already_hostile = target_npc_data.get("hostile") is True
                    if reaction_dialog_ref and not is_already_hostile:
                        logging.info(f"Running attack reaction: {reaction_dialog_ref}")
                        try: dialog_system.run_conversation(character, target_npc_data, override_dialog_ref=reaction_dialog_ref)
                        except Exception as e: logging.exception("Error running reaction dialog:")
                    enemy_object = create_npc_instance(target_npc_data)
                    if enemy_object:
                        try: battle_result = battle_system.battle_state(character, enemy_object, surprise=False)
                        except Exception as e: logging.exception("Battle error:"); print("Combat error.")
                        if character.get_health_points() <= 0: logging.info("Player defeated."); game_is_running = False
                        # TODO: Handle allies joining fight
                    else: logging.error(f"Failed instantiate NPC {npc_id_attacked}"); print("Combat prep error.")
                elif not action_executed: print(f"See no '{noun}' here to attack.")
            action_executed = True
        elif verb == "take":
            if not noun: print("Take what?")
            else:
                item_taken = False; items_in_location = list(current_location.get('items', [])); item_index_to_remove = -1
                if isinstance(current_location.get('items'), list):
                    for i, item_data in enumerate(items_in_location):
                        if isinstance(item_data, dict):
                             item_name_lower = item_data.get('name', '').lower(); item_id = item_data.get('id')
                             if noun == item_name_lower:
                                if not item_id or not isinstance(item_id, str): logging.error(f"Item '{item_name_lower}' invalid id."); print(f"Problem with {item_name_lower}."); item_taken = True; break
                                full_item_data = game_items_data.get(item_id)
                                if not full_item_data or not isinstance(full_item_data, dict): logging.error(f"Item def missing: {item_id}"); print(f"Problem with def of {item_name_lower}."); item_taken = True; break
                                if character.add_inventory(copy.deepcopy(full_item_data)): print(f"Took {item_name_lower}."); logging.info(f"Took item '{item_id}'"); item_index_to_remove = i; item_taken = True
                                else: print(f"Inventory full."); item_taken = True
                                break
                        else: logging.warning(f"Malformed item entry: {item_data}")
                    if item_index_to_remove != -1:
                         try: current_location['items'].pop(item_index_to_remove)
                         except Exception as e: logging.error(f"Error removing item: {e}")
                if not item_taken:
                    interactables_in_location = current_location.get('interactables', [])
                    is_unopened_container = False
                    if isinstance(interactables_in_location, list):
                        for interactable_data in interactables_in_location:
                             if isinstance(interactable_data, dict) and noun == interactable_data.get('name', '').lower():
                                 actions_dict = interactable_data.get('actions', {}); is_container_action = isinstance(actions_dict, dict) and ('open' in actions_dict or 'loot_container' in actions_dict.values())
                                 is_not_empty = interactable_data.get('state') != 'empty'; contains_items_list = interactable_data.get('contains_items'); has_items = isinstance(contains_items_list, list) and bool(contains_items_list)
                                 if is_container_action and is_not_empty and has_items: print(f"Need to open {noun} first."); is_unopened_container = True; break
                    if not is_unopened_container: print(f"See no '{noun}' here to take.")
            action_executed = True
        elif noun: # Other Noun Actions
            target_found_and_action_valid = False # Reset flag for this action attempt
            if verb == "examine": # Check NPCs first
                matched_npc_data = None; npc_list_ids = current_location.get('npcs', [])
                if isinstance(npc_list_ids, list):
                    print(f"DEBUG: Checking examine target '{noun}' against NPCs: {npc_list_ids}") # DEBUG
                    for npc_id in npc_list_ids:
                         if not isinstance(npc_id, str): continue
                         npc_data = game_npc_data.get(npc_id)
                         print(f"DEBUG [Examine]: Checking ID '{npc_id}'. Data fetched: {'Yes' if npc_data else 'No'}") # DEBUG
                         if npc_data and isinstance(npc_data, dict):
                              npc_name_lower = npc_data.get('name','').lower(); aliases = npc_data.get('aliases', []); npc_aliases_lower = [a.lower() for a in aliases if isinstance(a, str)] if isinstance(aliases, list) else []
                              body_name = f"body of {npc_name_lower}"
                              print(f"DEBUG [Examine]: Comparing '{noun}' to name='{npc_name_lower}', aliases={npc_aliases_lower}, body='{body_name}'") # DEBUG
                              if noun == npc_name_lower or noun in npc_aliases_lower or noun == body_name:
                                  matched_npc_data = npc_data; print(f"DEBUG [Examine]: Match found for {npc_id}"); break # DEBUG
                if matched_npc_data:
                    npc_id = matched_npc_data.get('id'); is_defeated = dialog_system._get_flag(f"npc_defeated_{npc_id}", default=False)
                    print("-" * 30)
                    print(f"DEBUG [Examine]: Matched NPC {npc_id}. Defeated: {is_defeated}") # DEBUG
                    if is_defeated:
                        is_looted = dialog_system._get_flag(f"npc_looted_{npc_id}", default=False)
                        print(f"DEBUG [Examine]: Body is defeated. Looted: {is_looted}") # DEBUG
                        if is_looted: print(f"You search the body of {matched_npc_data.get('name')} again, but find nothing more.")
                        else:
                            print(f"You search the body of {matched_npc_data.get('name')}...")
                            enemy_object = create_npc_instance(matched_npc_data)
                            if enemy_object:
                                try:
                                     print(f"DEBUG [Examine]: Calling inventory.loot_add for {npc_id}") # DEBUG
                                     inventory.loot_add(character, enemy_object)
                                except AttributeError: logging.error("inventory.loot_add missing/incompatible."); print("Error looting.")
                                except Exception as e: logging.exception("Error during body loot:"); print("Error looting.")
                                print(f"DEBUG [Examine]: Setting looted flag for {npc_id}") # DEBUG
                                dialog_system._set_flag(f"npc_looted_{npc_id}", True)
                            else: logging.error(f"Could not instantiate NPC {npc_id} to loot body."); print("Could not examine body.")
                    else: # Original examine logic for live NPCs
                        print(f"DEBUG [Examine]: NPC {npc_id} is alive. Showing description.") # DEBUG
                        examine_desc = matched_npc_data.get("examined_description", matched_npc_data.get("description")); use_textwrap(examine_desc if examine_desc else f"Look closely at {matched_npc_data.get('name','them')}.")
                        if matched_npc_data.get("dialog_ref"): print(f"\nCould try: \n- talk {matched_npc_data.get('name').lower()}")
                    target_found_and_action_valid = True; action_executed = True

            if not action_executed: # Check objects/items only if NPC examine didn't handle it
                potential_targets = (current_location.get('interactables', []) if isinstance(current_location.get('interactables'), list) else []) + (current_location.get('items', []) if isinstance(current_location.get('items'), list) else [])
                matched_target_data = None
                print(f"DEBUG [Examine]: Checking objects/items for '{noun}'") # DEBUG
                for target_data in potential_targets:
                     if isinstance(target_data, dict):
                          object_name_lower = target_data.get('name', '').lower()
                          if noun == object_name_lower: matched_target_data = target_data; print(f"DEBUG [Examine]: Matched object/item: {object_name_lower}"); break
                if matched_target_data:
                    object_id = matched_target_data.get('id', matched_target_data.get('name')); available_object_actions = matched_target_data.get('actions', {});
                    if not isinstance(available_object_actions, dict): available_object_actions = {}
                    if verb == "examine":
                        print("-" * 30); print(f"DEBUG [Examine]: Examining object/item '{noun}'") # DEBUG
                        if object_id in examined_this_visit: use_textwrap(matched_target_data.get("examined_description", f"Nothing new about {noun}."))
                        else:
                            action_string = available_object_actions.get(verb)
                            if action_string and isinstance(action_string, str):
                                if action_string.startswith("display_text:"): use_textwrap(action_string.split(":", 1)[1].strip())
                                elif action_string.startswith("event:") or action_string.startswith("loot_container"): handle_game_event(action_string, character, current_location, matched_target_data)
                                else: use_textwrap(matched_target_data.get('description', f"Look at {noun}."))
                            else: use_textwrap(matched_target_data.get('description', f"Look at {noun}."))
                            if object_id: examined_this_visit.add(object_id)
                        follow_up_verbs = [v for v in available_object_actions if v != "examine"]
                        if follow_up_verbs: print("\nCould also try:"); [print(f"- {v} {noun}") for v in sorted(follow_up_verbs)]
                        target_found_and_action_valid = True
                    elif verb in available_object_actions:
                        action_string = available_object_actions[verb]
                        if isinstance(action_string, str): logging.info("Exec action '%s' on '%s': '%s'", verb, noun, action_string); handle_game_event(action_string, character, current_location, matched_target_data); target_found_and_action_valid = True
                        else: logging.error(f"Invalid action string for '{verb}' on '{noun}': {action_string}"); print(f"Problem trying '{verb}' on {noun}."); target_found_and_action_valid = True
                    else: print(f"Can't '{verb}' the {noun}."); target_found_and_action_valid = True
                elif not target_found_and_action_valid:
                    print(f"You don't see '{noun}' here to examine.")
                    target_found_and_action_valid = True # Mark as handled (by failing)

            if target_found_and_action_valid: action_executed = True
        # --- Handle Unknown ---
        if not action_executed:
            if verb and noun: print(f"Can't '{verb}' '{noun}'.")
            elif verb: print(f"Can't just '{verb}'.")
            else: print(f"Unknown command: '{command}'")

        # --- Process Battle Result (Set Defeat Flag) ---
        if battle_result and isinstance(battle_result, dict):
            if battle_result.get("status") == "enemy_defeated":
                defeated_npc_obj = battle_result.get("defeated_npc_object")
                defeated_npc_id = getattr(defeated_npc_obj, 'original_id', None)
                if defeated_npc_id:
                    logging.info(f"Setting defeat flag for NPC {defeated_npc_id}")
                    dialog_system._set_flag(f"npc_defeated_{defeated_npc_id}", True)
                    # <<< REMOVED automatic setting of looted flag here >>>
                    # dialog_system._set_flag(f"npc_looted_{defeated_npc_id}", True)
                    # logging.info(f"Setting looted flag for NPC {defeated_npc_id} after battle.")
                else: logging.error("Could not get original_id from defeated_npc_object.")
            battle_result = None
        # --- End Process Battle Result ---

        # --- Loop Continue ---
        if game_is_running:
             if not (verb == "look" and not noun): print("-" * 30)
             continue
        else: break
    print("\n--- Game Loop Ended ---")

# --- Title Screen ---
def title_screen():
    """Handles title, data loading, char creation, starts game loop."""
    # (Function remains the same as previous version)
    global game_data, game_items_data, game_locations_data, game_npc_data
    os.system('cls' if os.name == 'nt' else 'clear')
    print('------------------------------'); print('- A Sound of Distant Thunder -'); print('------------------------------')
    print('-          1. Play           -'); print('-          2. Help           -'); print('-          3. Quit           -'); print('------------------------------')
    logging.info("--- Loading All Game Data ---")
    try: game_data = data_loader.load_all_data()
    except Exception as e: logging.exception("CRITICAL ERROR during data loading!"); print("\nFATAL ERROR: Data loading failed."); sys.exit(1)
    if game_data is None or not game_data.get("locations") or not game_data.get("items"): print("\nFATAL ERROR: Failed to load essential game data."); logging.critical("Essential data loading failed."); sys.exit(1)
    game_locations_data = game_data.get("locations", {}); game_items_data = game_data.get("items", {}); game_npc_data = game_data.get("npcs", {})
    logging.info("--- Data Load Complete ---"); logging.info("Items: %d, Locations: %d, NPCs: %d", len(game_items_data), len(game_locations_data), len(game_npc_data))
    while True:
        option = input("> ")
        if option.lower() == "play" or option == "1":
            try: character = hero.class_selection(game_items_data=game_items_data)
            except Exception as e: logging.exception("Char selection error!"); print("Error during char selection."); character = None
            if character is None: print("Char creation failed/cancelled."); continue
            start_location_id = "boat_deck"
            if start_location_id in game_locations_data: character.set_location(start_location_id); logging.info("Set start location: %s", start_location_id)
            else:
                fallback_location = next(iter(game_locations_data), None)
                if fallback_location: print(f"Warning: Start loc '{start_location_id}' not found! Starting at '{fallback_location}'."); logging.warning("Start loc '%s' not found! Using fallback '%s'.", start_location_id, fallback_location); character.set_location(fallback_location)
                else: print(f"CRITICAL: Start loc '{start_location_id}' not found & no fallback!"); logging.critical("No start/fallback location!"); sys.exit(1)
            print("-" * 30); print('--Your Character\'s Stats-----')
            print(f"- Health: {character.get_health_points()}/{character.get_hp_limit()}"); print(f"- Defence: {character.get_defence_points()}"); print(f"- Melee Attack: {character.get_strength_attribute()}"); print(f"- Gun Skill: {character.get_gun_skill()}"); print(f"- Luck: {character.get_luck()}"); print(f"- Charm: {character.get_charm_attribute()}"); print(f"- Stealth: {character.get_stealth_attribute()}")
            print("-" * 30); print('-         Chapter 1          -'); print("-" * 30)
            intro_text = """That sound of distant thunder was low and ominous. Like some kind of a warning..."""
            use_textwrap(intro_text); print("-" * 30)
            try: main_game_loop(character)
            except Exception as e: logging.exception("CRITICAL ERROR in main_game_loop!"); print("\n\nFATAL ERROR: Gameplay error. Check logs."); sys.exit(1)
            print("\nReturning to Title Screen."); break
        elif option.lower() == "help" or option == "2": help_menu()
        elif option.lower() == "quit" or option == "3": print("Exiting game. Goodbye!"); sys.exit()
        else: print("Invalid option.")

# --- Main Execution Guard ---
if __name__ == "__main__":
    log_filename = 'game.log'; log_level = logging.INFO; log_format = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'; log_datefmt = '%Y-%m-%d %H:%M:%S'; log_filemode = 'w'
    logging.basicConfig(level=log_level, format=log_format, datefmt=log_datefmt, filename=log_filename, filemode=log_filemode)
    console_handler = logging.StreamHandler(sys.stdout); console_handler.setLevel(logging.WARNING); formatter = logging.Formatter(log_format, datefmt=log_datefmt); console_handler.setFormatter(formatter); logging.getLogger('').addHandler(console_handler)
    logging.info("="*20 + " Game Started " + "="*20)
    try: title_screen()
    except Exception as e: logging.exception("CRITICAL ERROR during initialization!"); print("\n\nFATAL ERROR: Initialization failed. Check logs."); sys.exit(1)
    logging.info("="*20 + " Game Ended " + "="*20)
