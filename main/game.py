from Util import use_textwrap
import sys
import os
import hero
import battle_system
import inventory
import NPC
import random
import dialog
import dialog_system
import data_loader
import copy 
import logging
from mechanics import check_player_surprise
import actions

game_data = None
game_items_data = {}
game_locations_data = {}
game_npc_data = {}

# TODO: add ability to save game

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    datefmt='%Y-%m-%d %H:%M:%S', 
    filename='game.log', 
    filemode='a' # 'a' for append (adds to file), 'w' for overwrite each run
)

def help_menu():
    """Displays help information."""
    # Define your actual help text here later
    print("\n--- Help Menu ---")
    print("Available commands depend on context.")
    print("Common commands: look, go [direction], examine [object], inventory, help, quit")
    print("Other commands may become available based on objects.")
    print("-----------------\n")

# --- Event Handler Function (incorporating loot_container logic) ---
def handle_game_event(event_string, character, location_data, target_data):
    """
    Handles specific game events/actions triggered by action strings defined in JSON.
    Includes generic logic for 'loot_container' action type using 'contains_items'.

    Args:
        event_string (str): The action string from JSON (e.g., "loot_container", "display_specific_text:dossier_briefing").
        character (Hero): The player character object.
        location_data (dict): The data for the current location (from game_locations_data).
        target_data (dict): The data dict for the interactable/item that triggered the event.
    """
    global game_items_data, game_locations_data, CONTAINER_CONTENTS # Ensure these are accessible

    logging.info(f"Handling action/event: {event_string} for target: {target_data.get('name', 'N/A')}")
    print("-" * 30)

    action_type = event_string
    action_payload = None
    if ":" in event_string:
        parts = event_string.split(":", 1)
        action_type = parts[0]
        action_payload = parts[1] if len(parts) > 1 else None

    if action_type == "loot_container":
        target_id = target_data.get('id')
        target_name = target_data.get('name', 'container')

        # Find the actual interactable data in the main location dictionary to modify state
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
        else:
            current_state = live_target_data.get('state', 'closed')

            if current_state != 'empty':
                print(f"You open the {target_name}.")
                # Get item list DIRECTLY from the object's data
                item_ids_in_container = live_target_data.get('contains_items', [])

                if not item_ids_in_container:
                    print("...but it's empty.")
                    # Update state to empty and remove the 'open' action
                    location_data['interactables'][interactable_index]['state'] = 'empty'
                    location_data['interactables'][interactable_index]['description'] = f"An empty {target_name}."
                    verb_that_triggered = next((v for v, a in target_data.get('actions',{}).items() if a == action_type), None)
                    if verb_that_triggered and verb_that_triggered in location_data['interactables'][interactable_index].get('actions',{}):
                         del location_data['interactables'][interactable_index]['actions'][verb_that_triggered]

                else: # Container has items listed
                    items_found_data = []
                    items_found_names = []
                    for item_id in item_ids_in_container:
                        item_data = game_items_data.get(item_id)
                        if item_data:
                            items_found_data.append(item_data)
                            items_found_names.append(item_data.get('name', item_id))
                        else: logging.warning("Item definition missing for '%s' in container '%s'.", item_id, target_id)

                    if items_found_names: # Check if any valid items were actually found
                        print("Inside you find:")
                        for name in items_found_names: print(f"- {name}")
                        while True:
                            choice = input("Take these items? (yes/no) > ").lower().strip()
                            if choice in ['yes', 'y']:
                                print("\nYou added:")
                                for item_data_to_add in items_found_data:
                                    character.add_inventory(copy.deepcopy(item_data_to_add))
                                    item_name = item_data_to_add.get('name', item_data_to_add.get('id','unknown item'))
                                    print(f"- {item_name}")
                                # Update State and remove action verb
                                location_data['interactables'][interactable_index]['state'] = 'empty'
                                location_data['interactables'][interactable_index]['description'] = f"An empty {target_name}."
                                location_data['interactables'][interactable_index]['contains_items'] = [] # Remove items
                                verb_that_triggered = next((v for v, a in target_data.get('actions',{}).items() if a == action_type), None)
                                if verb_that_triggered and verb_that_triggered in location_data['interactables'][interactable_index].get('actions',{}):
                                     del location_data['interactables'][interactable_index]['actions'][verb_that_triggered]
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
                        if verb_that_triggered and verb_that_triggered in location_data['interactables'][interactable_index].get('actions',{}):
                             del location_data['interactables'][interactable_index]['actions'][verb_that_triggered]

            elif current_state == 'empty':
                 print(f"You check the {target_name} again, but it's already empty.")
            else:
                 print(f"The {target_name} is in an unusual state ('{current_state}') and cannot be interacted with further.")

    # Example for display_text payload (if not handled directly by main loop)
    elif action_type == "display_text":
        if action_payload: use_textwrap(action_payload)
        else: logging.warning("Action 'display_text' called without payload.")

    # --- Add handlers for other action_types here ---
    # elif action_type == "toggle_switch": ...

    else:
        print(f"You try to interact, triggering '{event_string}', but nothing specific happens yet.")
        logging.warning("Unhandled action/event type triggered: %s", event_string)

    print("-" * 30)


# In main/game.py
# --- Make sure necessary imports and globals are defined above ---
# Imports: sys, os, hero, inventory, NPC, random, dialog, dialog_system,
#          data_loader, copy, logging, mechanics, actions
# Globals: game_locations_data, game_items_data, game_npc_data
# Functions: use_textwrap, help_menu, handle_game_event

def main_game_loop(character):
    """
    Main loop: Displays location, suggests actions, gets input, processes commands.
    Handles standard commands, movement, talk, and generic object actions.
    Tracks examined state per location visit.
    """
    global game_locations_data, game_items_data, game_npc_data # Access globals

    # --- Initialize loop state variables BEFORE the loop ---
    game_is_running = True
    first_look = True # Force full description on first entry or after 'look'
    examined_this_visit = set() # Track examined IDs for the current location visit
    previous_location_id = None # Track location changes
    # --- End initialization ---

    while game_is_running:
        # --- 1. Get Current Location Info ---
        current_location_id = character.get_location()
        if current_location_id not in game_locations_data:
            print(f"ERROR: Unknown location ID '{current_location_id}'. Ending game.")
            logging.critical("Player location '%s' not found in game_locations_data.", current_location_id)
            break # Exit loop
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
            # TODO: Trigger 'events_on_entry' from JSON data
        else:
            description = current_location.get('visited_description', current_location.get('description', 'You see nothing remarkable.'))
            use_textwrap(description)

        # --- 3. Display Contextual Information ---
        print("-" * 30)
        npcs_here = current_location.get('npcs', [])
        if npcs_here:
            print("You see:")
            for npc_id in npcs_here:
                # Use simple name derivation until NPC data loading is fully confirmed
                npc_data = game_npc_data.get(npc_id) if game_npc_data else None
                npc_name = npc_data.get('name') if npc_data else npc_id.replace("npc_", "").replace("_", " ").title()
                print(f"- {npc_name}")

        interactables_here = current_location.get('interactables', [])
        items_here = current_location.get('items', [])
        if interactables_here or items_here:
             if not npcs_here: print("You notice:")
             else: print("Also here:")
             for interactable_data in interactables_here: print(f"- a {interactable_data.get('name', 'an object')}")
             for item_data in items_here: print(f"- a {item_data.get('name', 'an item')}")

        available_exits = current_location.get('exits', {})
        if available_exits:
            print("\nPossible Exits:")
            for exit_cmd in available_exits.keys(): print(f"- {exit_cmd}")

        first_look = False # Reset flag after displaying context
        print("-" * 30)

        # --- Display Suggested Actions ---
        available_actions_list = actions.get_available_actions(current_location)
        print("Suggested actions:")
        for action in available_actions_list: print(f"- {action}")
        print("-" * 20)

        # --- 4. Get Player Input ---
        command = input("> ").lower().strip()
        logging.debug("Player command: '%s'", command)
        if not command: continue

        # --- 5. Parse Player Input ---
        parts = command.split(maxsplit=1)
        verb = parts[0] if parts else ""
        noun = parts[1] if len(parts) > 1 else ""
        logging.debug(f"Parsed command: verb='{verb}', noun='{noun}'")

        # --- 6. Execute Action ---
        action_executed = False

        # --- Handle Standard Commands (except 'look' without noun) ---
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

        # --- Handle Movement ---
        elif verb == "go":
            if noun in available_exits:
                destination_id = available_exits[noun]
                if destination_id not in game_locations_data:
                    print(f"Error: The way '{noun}' leads nowhere yet.")
                    logging.error("Movement failed: Dest ID '%s' not found.", destination_id)
                else:
                    print(f"\nYou go {noun}...")
                    character.set_location(destination_id)
                    logging.info("Player moved from %s to %s via 'go %s'", current_location_id, destination_id, noun)
                    # State reset happens at top of next loop
            else:
                print(f"You can't go '{noun}' from here.")
            action_executed = True

        # --- Handle Talk/Speak ---
        elif verb == "talk" or verb == "speak":
            if not noun:
                print("Talk to who?")
            else:
                npc_found = False
                target_npc_data = None
                npc_list_ids = current_location.get('npcs', [])
                for npc_id in npc_list_ids:
                    npc_data = game_npc_data.get(npc_id)
                    if not npc_data:
                        logging.warning(f"NPC data not found for ID: {npc_id} in location {current_location_id}")
                        continue
                    npc_actual_name = npc_data.get('name', '').lower()
                    if noun == npc_actual_name:
                        npc_found = True
                        target_npc_data = npc_data
                        logging.info(f"Matched input '{noun}' to NPC: {npc_id} ('{npc_data.get('name')}')")
                        break

                if npc_found and target_npc_data:
                    # TODO: Implement actual dialog system call here
                    npc_display_name = target_npc_data.get('name', 'them')
                    print(f"\nYou start talking to {npc_display_name}...")
                    logging.info(f"Initiating dialog with {target_npc_data.get('id')}")
                    print("(Dialog system interaction not implemented yet)")
                elif not npc_found:
                    print(f"You don't see anyone called '{noun}' here to talk to.")
            action_executed = True

        # --- Handle Generic Object Actions ---
        elif noun: # Check other verbs only if a noun was provided
            potential_targets = current_location.get('interactables', []) + current_location.get('items', [])
            target_found = False
            for target_data in potential_targets:
                object_name_lower = target_data.get('name', '').lower()
                if noun == object_name_lower:
                    target_found = True
                    target_id = target_data.get('id', object_name_lower)
                    available_object_actions = target_data.get('actions', {})

                    if verb == "examine": # Special handling for examine
                        if target_id in examined_this_visit:
                            examined_text = target_data.get("examined_description")
                            use_textwrap(examined_text if examined_text else f"You find nothing new about the {noun}.")
                        else: # First time examining
                            action_string = available_object_actions.get(verb)
                            if action_string:
                                if action_string.startswith("display_text:"): use_textwrap(action_string.split(":", 1)[1].strip())
                                elif action_string.startswith("event:") or action_string.startswith("loot_container"): handle_game_event(action_string, character, current_location, target_data)
                                else: use_textwrap(target_data.get('description', f"You examine the {noun} closely."))
                            else: use_textwrap(target_data.get('description', f"You look at the {noun}."))
                            examined_this_visit.add(target_id) # Mark as examined

                            # Check for and suggest FOLLOW-UP actions
                            follow_up_verbs = [v for v in available_object_actions if v != "examine"]
                            if follow_up_verbs:
                                print("\nYou could also try:")
                                for follow_up_verb in follow_up_verbs: print(f"- {follow_up_verb} {noun}")
                        action_executed = True
                        break # Examine handled

                    elif verb in available_object_actions: # Handle other verbs
                        action_string = available_object_actions[verb]
                        logging.info("Executing action '%s' on object '%s' with string '%s'", verb, noun, action_string)
                        if action_string.startswith("display_text:"): use_textwrap(action_string.split(":", 1)[1].strip())
                        elif action_string.startswith("event:") or action_string.startswith("loot_container"): handle_game_event(action_string, character, current_location, target_data)
                        else: print(f"You try to {verb} the {noun}, but aren't sure how.")
                        action_executed = True
                        break # Other action handled
                    else: # Verb not valid for this object
                        print(f"You can't {verb} the {noun}.")
                        action_executed = True
                        break # Interaction handled (by failing)

            if not target_found:
                # Noun provided but object not found - let fall through to Unknown Command
                 pass

        # --- Handle standard 'look' command (only if noun is empty) ---
        elif verb == "look" and not noun:
            first_look = True
            print("\nLooking around again...")
            action_executed = True

        # --- Handle Unknown Commands ---
        if not action_executed:
            print(f"Unknown command: '{command}'")

        # --- Loop Continuation ---
        if game_is_running:
            if verb != "look" or noun: print("-" * 30) # Separator unless just 'look'
            continue
        else:
            break

    # --- End of game loop ---
    print("\nLeaving game loop.")

def boat_zone(character):
    while True:
        print('------------------------------')
        prompt = input("1. Read Dossier\n2. Speak to the Captain\n3. Look Around the Ship\n4. Inventory\n5. Help\n> ")
        print('------------------------------')
        if "read" in prompt.lower() or prompt == "1":
            print('------------------------------')
            use_textwrap("""A brief Dossier put together by my boss.
The Client: Venture Capital Consortium. This is big money
for our agency Alex, don't fuck this up.
The Job: Our Client has put significant money into this
small upstart Pharma company. I couldn't get much info on the company. It all looks pretty hush
hush. What I could gather from the Client is that the company produces some kind of experimental
pharmaceutical. The production facility is on a small Caribbean island I'd never heard of.
Our client has lost contact with the island. Seems all communication has been cut off. Sounds like
before things went dark there had been some drama related to unauthorized use of the pharmaceutical.
Your mission if you choose to accept it. You'd better accept it. For this kind of money you'd be
crazy not to. In any case the ask is simple. Restore communications to the island and return with
information as to what the hell is going on.""")
            print('------------------------------')
        elif "speak" in prompt.lower() or prompt == "2":
            # TODO: add an are you sure before attacking the captain?
            speak_to_captain(character)
        elif "look" in prompt.lower() or prompt == "3":
            print('------------------------------')
            use_textwrap("""This boat or ship rather is pretty beat up. I'm guessing this was all we could get with
such short notice.""")
            print('------------------------------')
           
            has_ammo = any(item_dict.get("item_type") == "ammo" for item_dict in character.get_inventory())

            if not has_ammo: 
                use_textwrap("""There is a case near by. Probably the supplies prepared for me. Might
be a good idea to take a look. They could help""")
                print('------------------------------')
                boat_prompt = input("1. Look at the Case\n2. Return\n3. Help\n> ")
                if "look" in boat_prompt.lower() or boat_prompt == "1":
                    print('------------------------------')
                    print("As I approach the case one of the deck hands stops what he's doing to speak to me.")
                    print('------------------------------')
                    use_textwrap("""Deck Hand: Your agency had us prepare this for you. They weren't specific about what was
needed. So its just our general survival kit. Take a look.""")
                    print('------------------------------')
                    use_textwrap("""The deck hand opens the case. Inside there appears to be pretty much what he said. Standard
med kit and a 9mm pistol and hunting knife.""")
                    print('------------------------------')
                    option = input(
                        "Would you like to add the items from the case to your Inventory?\n1. Yes \n2. No\n> ")

                    if option.lower() == "yes" or option == "1":
                        items_to_add_ids = ["basic_pistol", "basic_knife", "basic_med_pack", "small_9mm_ammo_box"]
                        for item_id in items_to_add_ids:
                            item_data = game_items_data.get(item_id)
                            if item_data:
                                character.add_inventory(copy.deepcopy(item_data)) 
                            else:
                                print(f"Warning: '{item_id}' data not found.")

                        print('------------------------------')
                        use_textwrap("""The case items have been added to your inventory. You can view your inventory by
choosing the 'Inventory' prompt.""")
                        print('------------------------------')
                    elif option.lower() == "no" or option == "2":
                        print("Maybe I don't need this stuff")
                    else:
                        print('------------------------------')
                        use_textwrap("""Not a valid entry. Please choose from the following options by entering the command
or entering the corresponding number.""")
                        print('------------------------------')
                elif "return" in boat_prompt.lower() or boat_prompt == "2":
                    # Just return to the main boat zone loop
                    continue
                elif "help" in boat_prompt.lower() or boat_prompt == "3":
                    help_menu()
                else:
                    print('------------------------------')
                    use_textwrap("""Not a valid entry. Please choose from the following options by entering the command
or entering the corresponding number.""")
                    print('------------------------------')
            else:
                use_textwrap("""The deck hand has already given me the survival kit from the case.""")
        elif "inventory" in prompt.lower() or prompt == "4":
            # Pass character to inventory function (inventory.py needs update to handle dicts)
            inventory.inventory(character)
        elif "help" in prompt.lower() or prompt == "5":
            help_menu()
        else:
            print('------------------------------')
            use_textwrap("""Not a valid entry. Please choose from the following options by entering the command
or entering the corresponding number.""")
            print('------------------------------')


def speak_to_captain(character):
    hd1 = [dialog.HeroDialog(False,"Nearly there", """Looks like we\'re nearly there Captain""",None),
           dialog.HeroDialog(False,"The Storm","""Looks like we have a pretty bas system headed
our way.""",None),
           dialog.HeroDialog(False,"The Island?","""What can you tell me
about this island Captain?""",None),
           dialog.HeroDialog(False,"Attack","""I'm sorry to have to do this Captain.""",None),
           dialog.HeroDialog(False,"Disembark","""I think
I'm ready to head out Captain.""",None)]
    rsp1 = [dialog.HeroDialog(False,"Nearly there", """Indeed we are. That dock is in no condition for a
ship of this size. You\'ll have to disembark on one of our small inflatable crafts. Let me know when you\'re ready to
head out or if you have any other questions.""",None),
           dialog.HeroDialog(False,"The Storm","""This system has been heading our way from the east.
It's looking to be a bad one. Whatever you have to do on that Island. I'd suggest doing it fast. You won't want to be
out here once this torm hits.""",None),
            dialog.HeroDialog(False,"The Island?","""Don't know much about it. A buddy of mine was
making pretty good money ferrying people to and from the island.\nHe mentioned that he stopped getting ferry jobs
about a month ago.""",None),
            dialog.HeroDialog(False,"Attack","""What the hell do you think you're doing?""",None),
            dialog.HeroDialog(False,"Disembark","""You're ready? Ok. So we're going to get you onto one of our small inflatable crafts.
Don't worry it has a motor. I'd suggest you take care of it. We will be back to the precise coordinates we drop
you off at to pick you back up in aproximately 12 hours. We can wait for you, but not forever. You need to be
back here in 12 hours or find another ride home.""",None)]

    captain_npc = NPC.boat_captain(game_items_data)
    if captain_npc is None:
        print("Error: Could not create Boat Captain NPC.")
        return 

    dialog_system.conversation_system(character, captain_npc, hd1, rsp1, [
        {"label" : "Attack", "action": disembark, "op1": True,},
        {"label": "Disembark", "action": disembark, "op1": False,}
    ])


def disembark(character, attack):
    print('------------------------------')
    if attack:
        # Pass game_items_data when creating NPCs for battle (Unchanged from previous correct version)
        captain_npc = NPC.boat_captain(game_items_data)
        deck_hand1_npc = NPC.deck_hand01(game_items_data)
        deck_hand2_npc = NPC.deck_hand02(game_items_data)

        if captain_npc: battle_system.battle_state(character, captain_npc, False, False)
        if character.get_health_points() > 0 and deck_hand1_npc:
            print('------------------------------')
            battle_system.battle_state(character, deck_hand1_npc, True, False)
        if character.get_health_points() > 0 and deck_hand2_npc:
            print('------------------------------')
            battle_system.battle_state(character, deck_hand2_npc, True, False)

        if character.get_health_points() <= 0: return # Exit if player died

        print('------------------------------')
        use_textwrap("""Confidentiality is always of paramount concern on these assignments. Though The Captain seemed
to know very little about the client's facility. It was enough. He and the crew had to go.
I board the small inflatable craft the Captain prepared for me. It did in fact have a small 4
stroke motor. Which should be enough to get me to the Island dock from here. However in the distance I can see a light house.
Which had it been functioning would be useful on a pitch black night such as this.Sort of makes you wonder how bad
things could have gone on this island for the light house to just be sitting there like that. No light, no nothing.
In any case, I have a decision to make. Head to the dock or check out this ominous Light House.""")
    else:
        use_textwrap("""I board the small inflatable craft the Captain prepared for me. It did in fact have a small 4
stroke motor. Which should be enough to get me to the Island dock from here. However in the distance I can see a light house.
Which had it been functioning would be useful on a pitch black night such as this.Sort of makes you wonder how bad
things could have gone on this island for the light house to just be sitting there like that. No light, no nothing.
In any case, I have a decision to make. Head to the dock or check out this ominous Light House.""")

    # Disembark options logic remains unchanged
    while True: # Loop until valid choice is made
        print('------------------------------')
        option = input("Where to next?\n1. Light House\n2. Dock\n3. Help\n> ")
        destination_id = None
        move_location = False

        if "light" in option.lower() or option == "1":
            destination_id = "lighthouse_exterior" # Target location ID
            move_location = True
        elif "dock" in option.lower() or option == "2":
            destination_id = "dock" # Target location ID (ensure dock.json exists later)
            move_location = True
        # --- CORRECTED HELP CONDITION ---
        elif "help" in option.lower() or option == "3":
            help_menu()
            continue # Re-display prompt after help
        # --- END CORRECTION ---
        else:
            print("Invalid Option. Please choose 1, 2, or 3.")
            continue # Re-display prompt

        # If a valid destination was chosen (move_location is True)
        if move_location:
             # Check if destination exists before moving (optional but good)
             # NOTE: Need access to game_locations_data here, might need to be global or passed in
             global game_locations_data
             if destination_id not in game_locations_data:
                  print(f"Error: Location '{destination_id}' not implemented yet.")
                  logging.error("Attempted to move to non-existent location: %s", destination_id)
                  continue # Go back to prompt if destination invalid

             # Optional: Clear screen and show Chapter marker
             os.system('cls' if os.name == 'nt' else 'clear')
             print('------------------------------')
             print('-         Chapter 2          -')
             print('------------------------------')

             # Set the character's new location attribute
             character.set_location(destination_id)
             logging.info("Player location set to '%s' after disembarking.", destination_id)
             # Return control to the main_game_loop
             return # Exit the disembark function


boat_broke = """As I make my way ashore the boat engine starts to make a sound that can't be good.
I'm no mechanic but I'm guessing either I need to get this thing fixed or find another way back to the pickup point.
Wonderful. This gig is already starting off well."""


def lighthouse_exterior(character, first):
    global game_items_data, boat_broke 

    if first:
        print('------------------------------')
        use_textwrap(boat_broke)
        print('------------------------------')
        use_textwrap("""The light house was sitting atop a tiny peninsula about 100 feet or so above the shore.
I walked the shoreline around the peninsula until I found a stair case built into the side of the cliff wall. A couple
minutes later I'm up the stairs. Up close this place wasn't exactly the most inviting looking spot I've ever seen.
However that hasn't ever stopped me before.
The air is thick with humidity and a slight mist from the beach below. Moonlight is about all I have to light my way.
It suddenly occurred to me how oddly quiet it was. I seemed to be the only living thing out and about on this island.
Every step pierced the silence and I'd be lying if I said I didn't feel a little vulnerable out here. Everything about
this place screams spooky vibes.
As I near what appears to be the main entrance of The Lighthouse two figures approach from left. I ready my weapon.


Alex: Hello(?) Who goes there?


I got nothing in response and as they crept nearer I decided to raise my weapon.


Alex: I'm not looking for trouble ok. My boat engine is in need of repair and...


Just that moment I got a good look at these....things. They might have been human at one point however that seems to
have been a while ago. They were incredibly emaciated walked with a peculiar hunched posture.
I'm not sure if it was the moonlight or what but their skin was wrinkly and almost purple. No hair to speak of.
The most disturbing quality was what appeared to be an elongated snout or jaw. Though admittedly tt was hard to make out
before the attack came.""")
        print('------------------------------')

        # --- MODIFIED GOBLIN ENCOUNTER 1 (Scripted - Player Aware) ---
        logging.info("Triggering initial Lighthouse exterior encounter (Scripted, player aware).")
        goblin1 = NPC.basic_goblin(game_items_data)
        goblin2 = NPC.basic_goblin(game_items_data)

        # ** Override surprise check for this specific scripted encounter **
        # Player sees them coming and prepares, so player is not surprised.
        is_player_surprised1 = False
        print(f"DEBUG: Player surprised status vs Goblins: {is_player_surprised1} (Scripted - Player Aware)")

        # Call battle_state for each enemy, passing surprise=False
        if goblin1:
            battle_system.battle_state(character, goblin1, surprise=is_player_surprised1, range_attack=False) # Using False
        # Check health before fighting next enemy in sequence
        if character.get_health_points() > 0 and goblin2:
            print('------------------------------') # Separator between fights
            # Use the *same* initial surprise status for the second goblin in the group
            battle_system.battle_state(character, goblin2, surprise=is_player_surprised1, range_attack=False) # Using False
        # --- END MODIFIED GOBLIN ENCOUNTER 1 ---

        if character.get_health_points() <= 0:
            logging.warning("Player defeated in initial lighthouse exterior encounter.")
            return # Exit function if player died

        print('------------------------------')
        use_textwrap("""After I catch my breath and calm down a bit I'm able to get a better look at these...things.
Whatever they are they aren't human. Taking this job is starting to seem like a very bad idea. Regardless of how good
the money is. No amount of money is worth getting your head ripped off by some purple goblin. I continue around the
the Lighthouse until I come to what has to be the entrance.""")
        print('------------------------------')
    else:
        # Player returns to the exterior
        use_textwrap("""Outside the Lighthouse. Just as ominous and creepy as it ever was.""")
        print('------------------------------') # Added separator

    # Loop for exterior actions
    while True:
        option = input("1. Enter Lighthouse\n2. Explore Path to Dock\n3. Inventory\n4. Help\n> ")
        print('------------------------------') # Added separator after input

        if "enter" in option.lower() or option == "1":
            lighthouse_inside(character, True) # Assuming True resets the inside state?
            break # Exit exterior loop as we entered lighthouse
        elif "explore" in option.lower() or option == "2": # Explore Path
            use_textwrap("""There is a path nearby that most likely leads to the dock.""")
            print('------------------------------')
            option2 = input("1. Take Path to Dock\n2. Stay Here\n> ")
            print('------------------------------') # Added separator

            if "take" in option2.lower() or option2 == "1":
                use_textwrap("""The path to the dock is about as dark and dreary as the rest of this place.""")
                # --- GOBLIN ENCOUNTER 2 (Random Path Encounter - Uses Surprise Check) ---
                # Random chance check (Maybe base on Stealth vs generic area awareness later?)
                if random.randint(0, 12) < character.get_luck(): # TODO: Revisit encounter trigger logic later
                    logging.info("Triggering random path encounter.")
                    print("Something stirs on the path ahead!")
                    print('------------------------------')
                    goblin3 = NPC.basic_goblin(game_items_data)
                    goblin4 = NPC.basic_goblin(game_items_data)
                    enemies_in_group2 = [g for g in [goblin3, goblin4] if g]

                    is_player_surprised2 = False # Default
                    if enemies_in_group2:
                         # TODO: Get environment factors for path area
                         env_factors2 = {}
                         # Call the actual check function from mechanics.py
                         is_player_surprised2 = check_player_surprise(character, enemies_in_group2, environment_factors=env_factors2)

                    # Fight sequence using calculated surprise
                    if goblin3:
                         battle_system.battle_state(character, goblin3, surprise=is_player_surprised2, range_attack=False)
                    if character.get_health_points() > 0 and goblin4:
                         print('------------------------------') # Separator
                         battle_system.battle_state(character, goblin4, surprise=is_player_surprised2, range_attack=False)

                    if character.get_health_points() <= 0:
                        logging.warning("Player defeated in random path encounter.")
                        return # Exit function if player defeated
                    print('------------------------------') # Separator after combat finished
                # --- END GOBLIN ENCOUNTER 2 ---

                # Proceed to dock whether encounter happened or not (if player survived)
                dock(character, True) # Assuming True means arriving for first time via path
                break # Exit exterior loop as we moved to dock
            elif "stay" in option2.lower() or option2 == "2":
                continue # Go back to exterior options loop
            else:
                 use_textwrap("""Invalid input.""")
                 print('------------------------------') # Separator

        elif "inventory" in option.lower() or option == "3":
            inventory.inventory(character)
        elif "help" in option.lower() or option == "4":
            help_menu() # Assuming help_menu exists and returns
        else:
            use_textwrap("""Not a valid entry. Please choose from the following options.""")
            print('------------------------------') # Separator

def lighthouse_den(character, first):
    global game_items_data # Access global items data

    # --- Dialog definitions ---
    hd1 = [dialog.HeroDialog(False,"I need help.", """Like I said earlier I was just attacked by some
kind of ...thing. My boats motor is on the fritz. Maybe you have some parts that could help me fix it?""",0),
           dialog.HeroDialog(False, "Let me in now!", """Come on old timer let me in now!
This isn't a game I was just attacked and in need of some assistance.""", 1),
           dialog.HeroDialog(False, "Let me in or I'll bust this door down!",
                             """This is stupid. I just told you I was attacked. Open up now or I might just
have to bust this door down""", 2)
           ]
    res1 = dialog.responses(
        dialog.ResponseDialog(False, "Come on in", """Alright I'll let you in. But no funny business.""", None),
        dialog.ResponseDialog(False,"Fuck you", """Hah! Fuck you. I look out for one person. Me!. Also
let me tell you something right now. If you have any intentions of making it off this island alive you had
better work on your manners. Because you're not doing it without my help I'll tell you that.""",
                              [dialog.HeroDialog(False, "I'm sorry", """Look, you're right.
I do need you're help ok. I'm sorry. I've been through a lot. What with getting
attacked by that...purple goblin thing. I guess you could say I'm a tad rattled.""", 0),
                               dialog.HeroDialog(False, "Give me a break.", """Come on man. Look
I get it. You're in a position to fuck with me. I need you more than you need me
yadda yadda yadda. Would you just let me in for gods sakes.""", 1),
                               dialog.HeroDialog(False,"Fuck You!", """Fuck me? Fuck you Old Man!
You're dead.""",2)])
    )
    res2 = dialog.responses(
        dialog.ResponseDialog(False, "Come on in", """Alright I'll let you in. But no funny business.""", None),
        dialog.ResponseDialog(False, "Come on in", """Well Sonny Boy I guess I'm just going ot have to
come out there and kill you..""", None), # Should this response also trigger combat? Assumed yes below.
    )
    # --- End Dialog definitions ---

    lhk = NPC.light_house_keeper(game_items_data)
    if lhk is None:
        print("Error: Could not create Lighthouse Keeper NPC.")
        logging.error("Failed to create Lighthouse Keeper NPC instance.")
        return

    if first:
        explore = False # Reset explore flag for this area
        print('------------------------------')
        use_textwrap("""With each step up that creaky old spiral stair case the smell gets worse. It smells like a combination
of stale beer, body odor and maybe...death? Definitely something dead up here. I reach the top landing which has a single
heavy wooden door. This must be the Lighthouse Keeper's den.""")
        while True:
            print('------------------------------')
            option = input("1. Knock on door\n2. Explore Landing\n3. Inventory\n4. Go Back Downstairs\n5. Help\n> ")
            if "knock" in option.lower() or option == "1":
                print('------------------------------')
                use_textwrap("""I approach cautiously and lightly knock on the door.""")
                # Run first dialog sequence
                s1 = dialog_system.persuasion_system(character, lhk, hd1, res1, 6) # Check persuasion skill value needed

                if s1 is None:
                    logging.info("Dialog with Lighthouse Keeper ended prematurely (s1).")
                    break # Exit knock sequence

                # Outcome 1: Keeper lets player in peacefully
                elif s1.get("succeed"):
                    print('------------------------------')
                    print("The heavy door creaks open...")
                    logging.info("Player peacefully enters Lighthouse Keeper's den.")
                    # TODO: Add function call or logic for inside the Keeper's room
                    print("(Placeholder: Entering Keeper's room peacefully)")
                    # Need logic here to actually move player state or call next function

                # Outcome 2: First dialog failed, potentially leading to second chance or fight
                else:
                    print('------------------------------')
                    # Check if response has further hero options (indicating second chance)
                    if s1.get("hero_responses"):
                         s2 = dialog_system.persuasion_system(character, lhk, s1["hero_responses"], res2, s1.get("score", 0))
                         if s2 is None:
                             logging.info("Second dialog with Lighthouse Keeper ended prematurely (s2).")
                             break
                         # Outcome 2a: Second chance succeeded
                         elif s2.get("succeed"):
                            print('------------------------------')
                            print("The heavy door creaks open...")
                            logging.info("Player peacefully enters Lighthouse Keeper's den after second chance.")
                            # TODO: Add function call or logic for inside the Keeper's room
                            print("(Placeholder: Entering Keeper's room peacefully)")
                            # Need logic here to actually move player state or call next function
                         # Outcome 2b: Second chance failed -> FIGHT!
                         else:
                            print('------------------------------')
                            # Check which response led to combat - maybe only "Fuck You!"/"Come on out.." triggers it?
                            # Assuming any failure from res2 triggers combat for now
                            use_textwrap("The old man bursts through the door, enraged!") # Or use s2 response text?
                            logging.warning("Dialogue failed, triggering Lighthouse Keeper fight.")
                            # --- KEEPER ENCOUNTER (Using hardcoded surprise) ---
                            is_player_surprised_keeper = True # Keeper bursting out always surprises player
                            print(f"DEBUG: Player surprised status vs Keeper: {is_player_surprised_keeper} (Scripted)")
                            # Pass hardcoded True for surprise
                            battle_system.battle_state(character, lhk, surprise=is_player_surprised_keeper, range_attack=False)
                            # --- END KEEPER ENCOUNTER ---

                            if character.get_health_points() <= 0:
                                logging.warning("Player defeated by Lighthouse Keeper.")
                                return # Exit function if player died
                            print('------------------------------')
                            print("The Lighthouse Keeper lies defeated.")
                            # TODO: What happens after defeating the keeper? Loot his body? Enter room?
                            print("(Placeholder: Keeper defeated. What next?)")
                            # Need logic here after winning fight

                    # Outcome 3: First dialog failed directly to combat (e.g., maybe res1 only had one path?)
                    # This might occur if the structure of res1 response doesn't include 'hero_responses' on failure
                    elif "Attack" in s1.get("label", ""): # Example check if direct attack was chosen in first dialog
                         use_textwrap("What the hell do you think you're doing?") # Keeper response text
                         logging.warning("Direct attack chosen, triggering Lighthouse Keeper fight.")
                         # --- KEEPER ENCOUNTER (Using hardcoded surprise - player initiates?) ---
                         # If player attacks first, should they be surprised? Maybe False here?
                         is_player_surprised_keeper = False # Player initiated the attack
                         print(f"DEBUG: Player surprised status vs Keeper: {is_player_surprised_keeper} (Player Attack)")
                         battle_system.battle_state(character, lhk, surprise=is_player_surprised_keeper, range_attack=False)
                         # --- END KEEPER ENCOUNTER ---
                         if character.get_health_points() <= 0: return # Exit if player died
                         print('------------------------------')
                         print("The Lighthouse Keeper lies defeated.")
                         print("(Placeholder: Keeper defeated. What next?)")

                    else:
                         # Handle other potential failure paths from the first dialog if needed
                         logging.error("Unhandled dialog failure path from s1 for Lighthouse Keeper: %s", s1)
                         print("An unexpected dialogue outcome occurred.")

                break # Exit den options loop after knock sequence resolves

            elif "explore" in option.lower() or option == "2": # Explore Landing
                 print('------------------------------')
                 if not explore:
                    use_textwrap("""You scan the landing. It's small, dusty, and smells just as bad as the foyer. Doesn't look like much of interest here.""")
                    if random.randint(0, 20) < character.get_luck(): # Harder to find things
                        use_textwrap("""Against the odds, you spot something wedged in a crack near the wall!""")
                        found_item_id = "charm1" # Example item ID
                        found_item_data = game_items_data.get(found_item_id)
                        if found_item_data:
                             character.add_inventory(copy.deepcopy(found_item_data))
                        else:
                             print(f"Warning: Could not find item data for '{found_item_id}'.")
                             logging.warning("Item data missing for '%s' found on den landing.", found_item_id)
                    else:
                         use_textwrap("""Nothing but dust bunnies and grime.""")
                    explore = True # Mark landing as explored
                 else:
                     use_textwrap("You've already checked the landing thoroughly.")

            elif "inventory" in option.lower() or option == "3":
                inventory.inventory(character) # Assuming inventory module handles dicts now

            elif "back" in option.lower() or "downstairs" in option.lower() or option == "4": # Go Back Downstairs
                lighthouse_inside(character, False) # Return to foyer logic
                break # Exit this loop

            elif "help" in option.lower() or option == "5":
                help_menu() # Assuming help_menu exists

            else:
                use_textwrap("""Not a valid entry. Please choose from the following options.""")
    else:
        # This is called when returning to the den area after being inside the keeper's room or going downstairs
        # Should likely show different options or just route back to the foyer/exterior?
        # For now, just prints a message and implicitly returns (or should call another state).
        print('------------------------------')
        use_textwrap("You are back on the landing outside the Lighthouse Keeper's door.")
        # Let's assume returning here means going back downstairs by default for now
        lighthouse_inside(character, False) # Calls the foyer function again

# --- Make sure help_menu() and use_textwrap() are defined or imported ---
# Placeholder for help_menu if needed
def help_menu():
     print("\n[Help Menu Placeholder]\n")

# Placeholder for use_textwrap if needed
def use_textwrap(text):
     import textwrap
     print(textwrap.fill(text, width=60)) # Example width

# Placeholder for boat_broke if needed
boat_broke = "The boat broke."


def lighthouse_inside(character, first):
    if first:
        explore = False
        print('------------------------------')
        use_textwrap("""I attempt to turn the handle to the lighthouse door. It's locked. Of course it is.
I'm a crafty sort so picking this lock shouldn't be an issue. However I do not have anything to pick it with. So that's
not really an option. Just left of the door is a small intercom box. I press the button which makes a kind of buzzing
sound as I press it.
Lighthouse Keeper: Who is it? What do you want? Go away!
Alex: Look I just got here. My name is Alex. I was sent by the people
that fund this facility. I'm kind of in need of some assistance.
Lighthouse Keeper: A company man eh?
Alex: Not exactly. They hired me to...see what was happening here. Or rather they opened a contract with my
agency and my agency gave me the gig. Could you let me in. I was just attacked by some...I don't know what...a couple
things and...
Lighthouse Keeper: Attacked? Oh why didn't you say so. Come on in.
The door buzzes. I open it and enter into the foyer. Whoever the voice was on the other end of that intercom wasn't
the tidiest of fellows. It's a mess in here. Junk is everywhere. Though some of it does appear like it could be useful.
The rest is just trash. In the center of the foyer is a spiral staircase. That must be where he's lurking. From the
looks of it he just discards his trash down here. One giant trash can.""")
        while True:
            print('------------------------------')
            option = input("1. Ascend Staircase\n2. Explore\n3. Inventory\n4. Return\n5. Help\n> ")
            if "ascend" in option.lower() or option == "1":
                print('------------------------------')
                lighthouse_den(character,True)
                break
            elif "explore" in option.lower() or option == "2":
                print('------------------------------')
                if not explore:
                    use_textwrap("""In hopes of finding something useful amongst all this junk I begin to dig around. I
carefully sift through the trash that seems to cover the entire floor of the foyer.""")
                    if random.randint(0, 12) < character.get_luck():
                        use_textwrap("""Wouldn't you know it. This wasn't such a bad idea after all. I found
something.""")
                        
                        found_item_id = "cologne1" 
                        found_item_data = game_items_data.get(found_item_id)
                        if found_item_data:
                             
                             character.add_inventory(copy.deepcopy(found_item_data))
                        else:
                             print(f"Warning: Could not find item data for '{found_item_id}'.")
                       
                    else:
                        use_textwrap("""Of course there isn't anything to be found in this garbage. Normally I'd
console myself by saying 'It can't hurt to look'. However in this case I'm pretty certain I could have caught a
disease from that crap. Probably a good idea to just move on.""")
                    explore = True
                else:
                    use_textwrap("I've already rummaged through this crap enough. Doubtful I'll find anything.")
            elif "inventory" in option.lower() or option == "3":
                inventory.inventory(character)
            elif "help" in option.lower() or option == "5":
                help_menu()
            elif "return" in option.lower() or option == "4":
                lighthouse_exterior(character, False)
                break
            else:
                use_textwrap("""Not a valid entry. Please choose from the following options by entering the command
                            or entering the corresponding number.""")
    else:
        print("You are back in the messy foyer of the lighthouse.")
        lighthouse_exterior(character, False) # Simple return for now


def dock(character, first):
    # Dock logic remains unchanged from previous version
    if first:
        use_textwrap(boat_broke)
        use_textwrap("You arrive at the dilapidated dock. Planks are missing, and the whole structure groans under your weight.")
        # TODO: Add more description and interaction logic for the dock
        print('------------------------------')
        print("What do you want to do at the dock?")
        # Example options
        option = input("1. Look for boat parts\n2. Look for people\n3. Go back towards lighthouse\n> ")
        if option == "1": print("You search around the dock debris but find no usable parts for your boat engine.")
        elif option == "2": print("The dock seems deserted. No sign of life here.")
        elif option == "3": lighthouse_exterior(character, False) # Go back
        else:
            print("Invalid choice.")
            dock(character, False) # Loop back
    else:
         print("You are back at the dock.")
         lighthouse_exterior(character, False) # Simple return for now


def title_screen():
    global game_data, game_items_data, game_locations_data
    os.system('cls' if os.name == 'nt' else 'clear')
    print('------------------------------') 
    print('- A Sound of Distant Thunder -')
    print('------------------------------')
    print('-   by Christopher Manning   -')
    print('------------------------------')
    print('-          1. Play           -')
    print('-          2. Help           -')
    print('-          3. Quit           -')
    print('------------------------------')

    logging.info("Loading all game data...")
    game_data = data_loader.load_all_data() 
    game_npc_data = game_data.get("npcs") or {} 

    if game_data is None:
        logging.critical("load_all_data returned None. Exiting.")
        sys.exit(1) 
    game_items_data = game_data.get("items", {})
    game_locations_data = game_data.get("locations", {})
    game_npc_data = game_data.get("npcs", {})

    logging.info("Data load complete. Items loaded: %d, Locations loaded: %d",
                 len(game_items_data), len(game_locations_data))

    while True:
        option = input("> ")
        if option.lower() == "play" or option == "1":
            character = hero.class_selection(game_items_data=game_items_data)
            if character is None:
                 print("Error during character creation.")
                 continue
            start_location_id = "boat_deck"
            if start_location_id in game_locations_data:
                character.set_location(start_location_id) 
                logging.info("Set player start location to '%s'", start_location_id)
                print(f"DEBUG [title_screen]: Location just set to: {character.get_location()}")
            else:
               
                print(f"CRITICAL ERROR: Start location '{start_location_id}' not found in loaded data!")
                logging.critical("Start location '%s' not found!", start_location_id)
                sys.exit(1)
            print('------------------------------')
            print('--Your Character\'s Stats-----')
            print(f"- Health: {character.get_health_points()}/{character.get_hp_limit()}")
            print(f"- Defence: {character.get_defence_points()}")
            print(f"- Melee Attack: {character.get_strength_attribute()}")
            print(f"- Gun Skill: {character.get_gun_skill()}")
            print(f"- Luck: {character.get_luck()}")
            print(f"- Charm: {character.get_charm_attribute()}")
            print(f"- Stealth: {character.get_stealth_attribute()}")
            print('------------------------------')
            print('-         Chapter 1          -')
            print('------------------------------')
            use_textwrap("""That sound of distant thunder was low and ominous. Like some kind of a warning. It was clearly
telling me to turn back. Was I going to listen? Hell no. The money was speaking louder than the thunder. Money
can make you do stupid things. Like board a creaky dirty old ship at 9pm on a Thursday evening. A Thursday
evening that seemed intent on levying some kind of storm upon all of us. I should be home drinking. Instead I’m
here on the deck of a ship heading toward the thunder. Suffice is to say this gig came up last minute and the
paycheck is insane. Some money people want me to get control of this  island. Some kind of manufacturing
facility. The dossier here has the details. For this kind of money, I'm more than willing to oblige. Seems easy
enough. However I'm a firm believer that  if its too good to be true it probably is. It's looking like  we're
getting pretty close. The captain is approaching. Looks like its time to disembark.""")
            print('------------------------------')
            main_game_loop(character)
            print("\nEnd of Chapter 1 (or current demo). Thank you for playing!")
            break 
        elif option.lower() == "help" or option == "2":
            help_menu()
        elif option.lower() == "quit" or option == "3":
            print("Exiting game. Goodbye!")
            sys.exit()
        else:
            print("Invalid option. Please enter 1, 2, or 3 (or Play, Help, Quit).")


def help_menu():
    # Help menu content remains unchanged
    print('------------------------------')
    print('-         How to Play        -')
    print('------------------------------')
    print('------------------------------')
    print('- Type either the Number or  -')
    print('- the command next to the    -')
    print('- corresponding prompt.      -')
    print('------------------------------')
    print('------------------------------')
    print('- Common prompts             -')
    print('------------------------------')
    print('------------------------------')
    print('- "Go to <location>":        -')
    print('-  this will move you to a   -')
    print('-  new location              -')
    print('------------------------------')
    print('- "Look at <something>":     -')
    print('-  this will give you        -')
    print('-  details                   -')
    print('------------------------------')
    print('- "Take <something>":        -')
    print('-  this will add the item    -')
    print('-  o your inventory          -')
    print('------------------------------')
    print('- "Speak to <someone>":      -')
    print('-  enter into a              -')
    print('-  conversation with         -')
    print('-  an NPC                    -')
    print('------------------------------')
    print('- "(Weapon) Attack":         -')
    print('-  Attack a person or thing  -')
    print('-  with the corresponding    -')
    print('-  weapon                    -')
    print('------------------------------')
    print('- "Inventory":               -')
    print('-  view your current         -')
    print('-  inventory to either use or-')
    print('-  equip items               -')
    print('------------------------------')
    print('- "Flee":                    -')
    print('-   Attempt to retreat       -')
    print('-   from battle / attack     -')
    print('------------------------------')
    print('- "Return":                  -')
    print('-   Go back to the previous  -')
    print('-   set of prompts           -')
    print('------------------------------')
    print('------------------------------')


if __name__ == "__main__": 
    title_screen()