# main/dialog_system.py

import json
import os
import logging
import textwrap
import copy
from . import hero # Use relative import

logger = logging.getLogger(__name__)

# Temporary Game State (Replace with proper state management)
DIALOG_GAME_STATE = {
    "flags": {}
}

def _get_flag(flag_name, default=False):
    val = DIALOG_GAME_STATE["flags"].get(flag_name)
    return default if val is None else val

def _set_flag(flag_name, value):
    logger.debug(f"Setting flag: {flag_name} = {value}")
    DIALOG_GAME_STATE["flags"][flag_name] = value

def use_textwrap(text):
    dedented_text = textwrap.dedent(str(text)).strip()
    print(textwrap.fill(dedented_text, width=70))

# --- Condition Checking Logic ---
def _check_condition(condition, character, target_npc_data):
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
            for item_dict in character.get_inventory():
                if isinstance(item_dict, dict) and item_dict.get("item_id") == item_id: count += 1
        except Exception as e: logging.error(f"Error checking inventory: {e}"); return False
        met = (count >= quantity)
        logger.debug(f"Cond Check: Item '{item_id}' x{quantity}? Player has: {count}. Met: {met}")
        return met

    elif condition_type == "check_fondness":
        target_npc_id = target_npc_data.get('id')
        min_val = condition.get("min")
        max_val = condition.get("max")
        if min_val is None: return False
        # Placeholder
        current_fondness = 0 # Replace with actual: character.get_fondness(target_npc_id)
        met = (current_fondness >= min_val)
        if max_val is not None: met = met and (current_fondness <= max_val)
        logging.warning(f"Cond Check: 'check_fondness' NI. Assumed: {current_fondness}. Met: {met}")
        return met

    elif condition_type == "check_npc_state":
        target_npc_id = target_npc_data.get('id')
        required_state = condition.get("required_state")
        if not required_state: return False
        # Placeholder
        current_state = "neutral" # Replace with actual: get_npc_state(target_npc_id)
        met = (current_state == required_state)
        logging.warning(f"Cond Check: 'check_npc_state' NI. Assumed: '{current_state}'. Met: {met}")
        return met

    else:
        logging.warning(f"Unsupported condition type: {condition_type}")
        return False

def _are_conditions_met(conditions, character, target_npc_data):
    if not conditions: return True
    return all(_check_condition(cond, character, target_npc_data) for cond in conditions)

# --- Effect Application Logic ---
def _apply_effect(effect, character, target_npc_data):
    effect_type = effect.get("effect_type")
    global game_items_data # Needed for give_item

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

    return None

def _apply_effects(effects, character, target_npc_data):
    special_runner_action = None
    if not effects: return None
    for effect in effects:
        result = _apply_effect(effect, character, target_npc_data)
        if result and not special_runner_action: special_runner_action = result
    return special_runner_action

# --- Dialog File Loading ---
def _load_dialog_data(dialog_ref):
    try:
        script_dir = os.path.dirname(__file__)
        dialog_dir = os.path.join(script_dir, 'data', 'dialogs')
        file_path = os.path.join(dialog_dir, f"{dialog_ref}.json")
        logger.info(f"Attempting to load dialog file: {file_path}")

        if not os.path.exists(file_path):
            logging.error(f"Dialog file not found: {file_path}")
            print(f"DEBUG: Dialog file missing at {file_path}")
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # TODO: Add JSON schema validation here
            return data.get("dialog_nodes", {})

    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON in {dialog_ref}.json: {e}")
        print(f"DEBUG: Error reading dialog file {dialog_ref}.json")
        return None
    except Exception as e:
        logging.exception(f"Unexpected error loading {dialog_ref}.json:")
        print(f"DEBUG: Unexpected error loading dialog file {dialog_ref}.json")
        return None

# --- Main Conversation Runner ---
def run_conversation(character, target_npc_data):
    dialog_ref = target_npc_data.get("dialog_ref")
    npc_name = target_npc_data.get("name", "Someone")
    npc_id = target_npc_data.get("id", "unknown_npc")

    if not dialog_ref:
        logging.warning(f"NPC {npc_name} ({npc_id}) has no 'dialog_ref'.")
        use_textwrap(f"{npc_name} doesn't seem interested in talking right now.")
        return {"status": "no_dialog"}

    dialog_nodes = _load_dialog_data(dialog_ref)
    if dialog_nodes is None:
        use_textwrap("Sorry, there seems to be a problem with the conversation data.")
        return {"status": "error"}

    current_node_id = dialog_ref # Start at the node specified by dialog_ref
    session_choices_made = set()

    print("-" * 30) # Separator at start

    while True:
        current_node = dialog_nodes.get(current_node_id)
        if not current_node:
            logging.error(f"Dialog Error: Node ID '{current_node_id}' not found in {dialog_ref}.json")
            use_textwrap("The conversation trails off unexpectedly...")
            return {"status": "error"}

        # 1. Display NPC text (if any)
        npc_text = current_node.get("npc_text")
        if npc_text: # Only print if text is not null or empty
            use_textwrap(f"{npc_name}: {npc_text}")

        # 2. Prepare available player choices
        player_choices_data = current_node.get("player_choices", [])
        available_choices = []
        if not player_choices_data: # Handle nodes with no choices (end of branch)
             logging.debug(f"Node '{current_node_id}' has no player choices. Ending conversation.")
             print("-" * 30)
             return {"status": "ended"}

        for index, choice_data in enumerate(player_choices_data):
            if not _are_conditions_met(choice_data.get("conditions", []), character, target_npc_data):
                continue
            is_repeatable = choice_data.get("repeatable", False)
            choice_key = choice_data.get("choice_id", f"{current_node_id}_{index}")
            if not is_repeatable and choice_key in session_choices_made:
                continue
            available_choices.append(choice_data) # Store the full dict

        # --- Check for Auto-Continue ---
        chosen_option = None
        if len(available_choices) == 1 and available_choices[0].get("choice_text") == "[CONTINUE]":
            logging.debug(f"Node '{current_node_id}' has single auto-continue choice. Transitioning...")
            chosen_option = available_choices[0]
            # Skip display and input
        # --- End Auto-Continue Check ---
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

        # 5. Process Chosen Option (either selected or auto-continued)
        if chosen_option is None: # Should not happen if logic is correct, but safety check
             logging.error("Error: chosen_option is None after choice selection/auto-continue.")
             return {"status": "error"}

        logging.debug(f"Processing choice: '{chosen_option.get('choice_text')}'")

        # Mark as chosen if not repeatable
        is_repeatable = chosen_option.get("repeatable", False)
        if not is_repeatable:
             # Use original index to generate key if choice_id is missing
             original_index = player_choices_data.index(chosen_option) if chosen_option in player_choices_data else -1
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
                 # Placeholder for actual check logic
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
        if not next_node_id:
            logging.error(f"Chosen option '{chosen_option.get('choice_text')}' has no destination_node!")
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
            # Add separator only if we didn't just auto-continue (which feels abrupt otherwise)
            if chosen_option.get("choice_text") != "[CONTINUE]":
                 print("-" * 20) # Separator between turns
