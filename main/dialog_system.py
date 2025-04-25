# main/dialog_system.py

import json
import os
import logging
import textwrap
import copy
from . import hero # Use relative import

logger = logging.getLogger(__name__)

# Temporary Game State (Replace with proper state management)
# TODO: Move flag management to a dedicated state manager or character class
DIALOG_GAME_STATE = {
    "flags": {}
}

def _get_flag(flag_name, default=False):
    """Gets a flag value from the temporary game state."""
    val = DIALOG_GAME_STATE["flags"].get(flag_name)
    return default if val is None else val

def _set_flag(flag_name, value):
    """Sets a flag value in the temporary game state."""
    logger.debug(f"Setting flag: {flag_name} = {value}")
    DIALOG_GAME_STATE["flags"][flag_name] = value

def use_textwrap(text):
    """Wraps text for display."""
    dedented_text = textwrap.dedent(str(text)).strip()
    print(textwrap.fill(dedented_text, width=70))

# --- Condition Checking Logic ---
def _check_condition(condition, character, target_npc_data):
    """Checks if a single dialog condition object is met."""
    condition_type = condition.get("condition_type")

    if condition_type == "check_flag":
        flag_name = condition.get("flag_name")
        required_value = condition.get("flag_value", True)
        if not flag_name: return False
        current_value = _get_flag(flag_name, None)
        met = (bool(current_value) == required_value) if isinstance(required_value, bool) else (current_value == required_value)
        logger.debug(f"Cond Check: Flag '{flag_name}' == {required_value}? Current: {current_value}. Met: {met}")
        return met

    elif condition_type == "check_stat":
        stat_name = condition.get("stat")
        min_val = condition.get("min")
        max_val = condition.get("max")
        if not stat_name or min_val is None: return False
        getter_method_name = f"get_{stat_name}"
        alt_getter1 = f"get_{stat_name}_attribute"
        alt_getter2 = f"get_{stat_name}_points"
        if hasattr(character, getter_method_name): getter = getattr(character, getter_method_name)
        elif hasattr(character, alt_getter1): getter = getattr(character, alt_getter1)
        elif hasattr(character, alt_getter2): getter = getattr(character, alt_getter2)
        else: logging.warning(f"Player missing stat getter for: {stat_name}"); return False
        try:
            player_stat = getter()
            met = (player_stat >= min_val)
            if max_val is not None: met = met and (player_stat <= max_val)
            logger.debug(f"Cond Check: Stat '{stat_name}' >= {min_val}" + (f" <= {max_val}" if max_val is not None else "") + f"? Player: {player_stat}. Met: {met}")
            return met
        except Exception as e: logging.error(f"Error getting stat '{stat_name}': {e}"); return False

    elif condition_type == "check_item":
        item_id = condition.get("item_id")
        quantity = condition.get("quantity", 1)
        if not item_id: return False
        count = 0
        try:
            # Assumes character.get_inventory() returns list of item dicts
            for item_dict in character.get_inventory():
                if isinstance(item_dict, dict) and item_dict.get("item_id") == item_id:
                    # TODO: Handle quantity if items stack within a single dict later
                    count += 1
        except Exception as e: logging.error(f"Error checking inventory: {e}"); return False
        met = (count >= quantity)
        logger.debug(f"Cond Check: Item '{item_id}' x{quantity}? Player has: {count}. Met: {met}")
        return met

    elif condition_type == "check_fondness":
        target_npc_id = target_npc_data.get('id')
        min_val = condition.get("min")
        max_val = condition.get("max")
        if min_val is None: return False
        # Placeholder - Requires implementation of fondness tracking
        # current_fondness = character.get_fondness(target_npc_id)
        current_fondness = 0 # Replace with actual call
        met = (current_fondness >= min_val)
        if max_val is not None: met = met and (current_fondness <= max_val)
        logging.warning(f"Cond Check: 'check_fondness' NI. Assumed: {current_fondness}. Met: {met}")
        return met

    elif condition_type == "check_npc_state":
        target_npc_id = target_npc_data.get('id')
        required_state = condition.get("required_state")
        if not required_state: return False
        # Placeholder - Requires implementation of NPC state tracking
        # current_state = get_npc_state(target_npc_id)
        current_state = "neutral" # Replace with actual call
        met = (current_state == required_state)
        logging.warning(f"Cond Check: 'check_npc_state' NI. Assumed: '{current_state}'. Met: {met}")
        return met

    else:
        logging.warning(f"Unsupported condition type: {condition_type}")
        return False

def _are_conditions_met(conditions, character, target_npc_data):
    """Checks if ALL conditions in a list are met."""
    if not conditions: return True
    return all(_check_condition(cond, character, target_npc_data) for cond in conditions)

# --- Effect Application Logic ---
def _apply_effect(effect, character, target_npc_data):
    """Applies a single dialog effect. Returns special action dict if needed by runner."""
    effect_type = effect.get("effect_type")
    # global game_items_data # Avoid global if possible, pass if needed for give_item

    if effect_type == "set_flag":
        flag_name = effect.get("flag_name")
        flag_value = effect.get("flag_value", True)
        if flag_name: _set_flag(flag_name, flag_value)
        else: logging.warning("set_flag effect missing 'flag_name'")

    elif effect_type == "change_fondness":
        target_npc_id = target_npc_data.get('id')
        amount = effect.get("amount")
        if amount is not None:
            # Placeholder: character.change_fondness(target_npc_id, amount)
            logging.warning(f"Effect Apply: 'change_fondness' by {amount} for {target_npc_id} NI.")
        else: logging.warning("change_fondness effect missing 'amount'")

    elif effect_type == "give_item":
        item_id = effect.get("item_id")
        quantity = effect.get("quantity", 1)
        if item_id:
            # Placeholder: Needs access to game_items_data and character.add_inventory
            logging.warning(f"Effect Apply: 'give_item' ({item_id} x{quantity}) NI.")
        else: logging.warning("give_item effect missing 'item_id'")

    elif effect_type == "take_item":
        item_id = effect.get("item_id")
        quantity = effect.get("quantity", 1)
        if item_id:
            # Placeholder: character.remove_item(item_id, quantity)
            logging.warning(f"Effect Apply: 'take_item' ({item_id} x{quantity}) NI.")
        else: logging.warning("take_item effect missing 'item_id'")

    elif effect_type == "perform_check":
        logging.debug(f"Effect signals 'perform_check': {effect}")
        return {"perform_check_details": effect}

    elif effect_type == "set_npc_state":
        target_npc_id = target_npc_data.get('id')
        new_state = effect.get("new_state")
        if new_state:
            # Placeholder: set_npc_state(target_npc_id, new_state)
            logging.warning(f"Effect Apply: 'set_npc_state' for {target_npc_id} to '{new_state}' NI.")
        else: logging.warning("set_npc_state effect missing 'new_state'")

    elif effect_type == "start_combat":
        target = effect.get("target_npc", "CURRENT")
        target_id = target_npc_data.get('id') if target == "CURRENT" else target
        logging.debug(f"Effect signals 'start_combat' against {target_id}")
        return {"start_combat_target_id": target_id}

    else:
        logging.warning(f"Unsupported effect type: {effect_type}")

    return None # No special runner action needed

def _apply_effects(effects, character, target_npc_data):
    """Applies all effects in a list. Returns first special action dict encountered."""
    special_runner_action = None
    if not effects: return None
    for effect in effects:
        result = _apply_effect(effect, character, target_npc_data)
        if result and not special_runner_action: special_runner_action = result
    return special_runner_action

# --- Dialog File Loading ---
def _load_dialog_data(dialog_ref):
    """Loads and returns dialog nodes data from a JSON file."""
    if not dialog_ref or not isinstance(dialog_ref, str):
        logging.error(f"Invalid dialog_ref provided for loading: {dialog_ref}")
        return None
    try:
        script_dir = os.path.dirname(__file__)
        dialog_dir = os.path.join(script_dir, 'data', 'dialogs')
        # Ensure filename ends with .json, even if ref doesn't include it
        filename = f"{dialog_ref}.json" if not dialog_ref.endswith(".json") else dialog_ref
        file_path = os.path.join(dialog_dir, filename)
        logger.info(f"Attempting to load dialog file: {file_path}")

        if not os.path.exists(file_path):
            logging.error(f"Dialog file not found: {file_path}")
            print(f"DEBUG: Dialog file missing at {file_path}")
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # TODO: Add JSON schema validation here
            dialog_nodes = data.get("dialog_nodes", {})
            if not isinstance(dialog_nodes, dict):
                 logging.error(f"Dialog file {filename} has malformed 'dialog_nodes' (not a dictionary).")
                 return None
            return dialog_nodes

    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON in dialog file {dialog_ref}.json: {e}")
        print(f"DEBUG: Error reading dialog file {dialog_ref}.json")
        return None
    except Exception as e:
        logging.exception(f"Unexpected error loading dialog file {dialog_ref}.json:")
        print(f"DEBUG: Unexpected error loading dialog file {dialog_ref}.json")
        return None

# --- Main Conversation Runner ---
def run_conversation(character, target_npc_data, override_dialog_ref=None): # <<< Added override_dialog_ref
    """
    Runs a dialog conversation based on JSON data.
    Handles initial attempts to talk to NPCs without dialog.
    Can run a specific dialog sequence via override_dialog_ref.

    Args:
        character (hero.Hero): The player character object.
        target_npc_data (dict): The data dictionary for the NPC being spoken to.
        override_dialog_ref (str, optional): If provided, load and run this dialog
                                             instead of the NPC's main dialog_ref.

    Returns:
        dict: A dictionary containing the status of how the conversation ended.
              Keys:
                'status': (str) 'ended', 'combat', 'error', 'no_dialog_first_attempt', etc.
                'combat_target_id': (str, optional) NPC ID if status is 'combat'
    """
    # Determine which dialog reference to use
    dialog_ref_to_use = override_dialog_ref if override_dialog_ref else target_npc_data.get("dialog_ref")

    npc_name = target_npc_data.get("name", "Someone")
    npc_id = target_npc_data.get("id", "unknown_npc")

    # --- Handle NPCs without Dialog (or if override ref wasn't provided for non-dialog NPC) ---
    if not dialog_ref_to_use:
        # Only show description/generic message if we weren't trying to run a specific override (like a reaction)
        if not override_dialog_ref:
            attempt_flag_name = f"attempted_talk_{npc_id}"
            already_attempted = _get_flag(attempt_flag_name, default=False)
            print("-" * 30)
            if not already_attempted:
                description_to_show = target_npc_data.get("examined_description", target_npc_data.get("description"))
                if not description_to_show: description_to_show = f"{npc_name} doesn't seem interested in talking right now."
                use_textwrap(description_to_show)
                _set_flag(attempt_flag_name, True)
                logging.info(f"First talk attempt to non-dialog NPC: {npc_id}.")
                print("-" * 30)
                return {"status": "no_dialog_first_attempt"}
            else:
                use_textwrap(f"{npc_name} still doesn't seem interested in talking.")
                logging.info(f"Subsequent talk attempt to non-dialog NPC: {npc_id}.")
                print("-" * 30)
                return {"status": "no_dialog_already_attempted"}
        else:
            # This case shouldn't normally happen if override is used correctly (e.g., for reactions)
            logging.error(f"run_conversation called with override_dialog_ref for NPC {npc_id} who also lacks a main dialog_ref.")
            return {"status": "error"}


    # --- Load Dialog Data ---
    dialog_nodes = _load_dialog_data(dialog_ref_to_use)
    if dialog_nodes is None or not dialog_nodes: # Check if empty after loading
        use_textwrap("Sorry, there seems to be a problem with the conversation data.")
        logging.error(f"Failed to load or found no nodes in dialog: {dialog_ref_to_use}")
        return {"status": "error"}

    # --- Determine Start Node ---
    # Assume the dialog_ref itself is the starting node ID,
    # OR look for a specific key like "start" if the ref is just the filename.
    # Let's stick with dialog_ref == start_node_id for now.
    current_node_id = dialog_ref_to_use
    # Check if the specific start node exists
    if current_node_id not in dialog_nodes:
         # Fallback: Try to find a node named "start" or take the first node found
         fallback_start_node = dialog_nodes.get("start", next(iter(dialog_nodes), None))
         if fallback_start_node:
              logging.warning(f"Start node '{current_node_id}' not found in {dialog_ref_to_use}. Falling back to '{fallback_start_node}'.")
              current_node_id = fallback_start_node
         else: # Should not happen if dialog_nodes is not empty, but safety check
              logging.error(f"Cannot find starting node '{current_node_id}' or any fallback node in {dialog_ref_to_use}.")
              return {"status": "error"}


    # --- Conversation State ---
    session_choices_made = set() # Tracks choices made this session

    print("-" * 30) # Separator at start of actual dialog

    # --- Main Dialog Loop ---
    while True:
        current_node = dialog_nodes.get(current_node_id)
        if not current_node:
            logging.error(f"Dialog Error: Node ID '{current_node_id}' not found in {dialog_ref_to_use}.json")
            use_textwrap("The conversation trails off unexpectedly...")
            return {"status": "error"}

        # 1. Display NPC text (if any)
        npc_text = current_node.get("npc_text")
        if npc_text:
            use_textwrap(f"{npc_name}: {npc_text}")

        # 2. Prepare available player choices
        player_choices_data = current_node.get("player_choices", [])
        available_choices = []
        if not player_choices_data or not isinstance(player_choices_data, list): # Handle nodes with no/bad choices
             logging.debug(f"Node '{current_node_id}' has no valid player choices. Ending branch.")
             print("-" * 30)
             return {"status": "ended"}

        for index, choice_data in enumerate(player_choices_data):
            if not isinstance(choice_data, dict): # Skip malformed choices
                 logging.warning(f"Skipping malformed choice data in node '{current_node_id}': {choice_data}")
                 continue
            if not _are_conditions_met(choice_data.get("conditions", []), character, target_npc_data):
                continue
            is_repeatable = choice_data.get("repeatable", False)
            choice_key = choice_data.get("choice_id", f"{current_node_id}_{index}")
            if not is_repeatable and choice_key in session_choices_made:
                continue
            available_choices.append(choice_data)

        # --- Check for Auto-Continue ---
        chosen_option = None
        if len(available_choices) == 1 and available_choices[0].get("choice_text") == "[CONTINUE]":
            logging.debug(f"Node '{current_node_id}' has single auto-continue choice. Transitioning...")
            chosen_option = available_choices[0]
        else:
            # 3. Display available choices (if not auto-continuing)
            if not available_choices:
                logging.info(f"No available choices for player at node '{current_node_id}'. Ending.")
                use_textwrap("(You have nothing more to say right now.)")
                print("-" * 30)
                return {"status": "ended"}

            print("\nYour response:")
            display_choices_text = [ch.get("choice_text", "...") for ch in available_choices]
            for i, text in enumerate(display_choices_text):
                print(f"  {i + 1}. {text}")

            # 4. Get Player Input (if not auto-continuing)
            while True:
                try:
                    player_input = input("> ")
                    if not player_input: continue
                    selected_index = int(player_input) - 1
                    if 0 <= selected_index < len(available_choices):
                        chosen_option = available_choices[selected_index]
                        break
                    else: print(f"Invalid choice number (enter 1-{len(available_choices)}).")
                except ValueError: print("Please enter the number of your choice.")
                except EOFError: logging.warning("EOFError during dialog. Ending."); return {"status": "error"}

        # 5. Process Chosen Option
        if chosen_option is None:
             logging.error("Error: chosen_option is None after choice selection/auto-continue.")
             return {"status": "error"}

        logging.debug(f"Processing choice: '{chosen_option.get('choice_text')}'")

        # Mark as chosen if not repeatable
        is_repeatable = chosen_option.get("repeatable", False)
        if not is_repeatable:
             original_index = -1
             try: # Find original index safely
                  original_index = player_choices_data.index(chosen_option)
             except ValueError:
                  logging.warning("Could not find chosen_option in original list for key generation.")
             choice_key = chosen_option.get("choice_id", f"{current_node_id}_{original_index}")
             if original_index != -1: session_choices_made.add(choice_key)

        # Apply effects and check for special actions
        effects = chosen_option.get("effects", [])
        special_action = _apply_effects(effects, character, target_npc_data)

        next_node_id = None
        if special_action:
             if "start_combat_target_id" in special_action:
                 combat_target_id = special_action["start_combat_target_id"]
                 logging.info(f"Dialog ending to trigger combat with {combat_target_id}.")
                 print("-" * 30)
                 return {"status": "start_combat", "combat_target_id": combat_target_id}
             elif "perform_check_details" in special_action:
                 check_details = special_action["perform_check_details"]
                 check_type = check_details.get("check_type")
                 success_node = check_details.get("success_node")
                 failure_node = check_details.get("failure_node")
                 # Placeholder
                 success = False # Replace with: perform_skill_check(character, target_npc_data, check_details)
                 logging.warning(f"'perform_check' ({check_type}) NI. Result: {'Success' if success else 'Failure'}")
                 next_node_id = success_node if success else failure_node
                 if not next_node_id:
                      logging.error(f"Perform_check for {check_type} missing success/failure node!")
                      return {"status": "error"}
             else:
                 logging.warning(f"Unhandled special action: {special_action}")
                 next_node_id = chosen_option.get("destination_node") # Fallback
        else:
            next_node_id = chosen_option.get("destination_node")

        # 6. Move to Next Node or End
        if not next_node_id or not isinstance(next_node_id, str): # Check type
            logging.error(f"Chosen option '{chosen_option.get('choice_text')}' has invalid destination_node: {next_node_id}")
            return {"status": "error"}

        if next_node_id == "[END_CONVERSATION]":
            logging.debug("Destination node is END_CONVERSATION. Ending dialog.")
            print("-" * 30)
            return {"status": "ended"}
        elif next_node_id == "[END_CONVERSATION_AND_ATTACK]":
             logging.info("Dialog ending to trigger combat via destination node.")
             print("-" * 30)
             return {"status": "start_combat", "combat_target_id": npc_id}
        else:
            current_node_id = next_node_id
            if chosen_option.get("choice_text") != "[CONTINUE]":
                 print("-" * 20) # Separator between turns
