# main/dialog_system.py

import json
import os
import logging
import textwrap # Using standard library textwrap
import copy # For potential use with give_item effect later

# Assuming hero.py defines the Hero class and has methods for stats, items, flags, fondness
# Need to ensure Hero class has methods like get_charm_attribute(), get_luck(), get_inventory() etc.
# And potentially methods for managing flags and fondness, or we use a global state.
from . import hero # Use relative import

# Assuming game.py sets up logging
logger = logging.getLogger(__name__)

# --- Placeholder for Game State (Flags, etc.) ---
# This needs a more robust implementation later. It could be a class,
# part of the main game state, or managed on the character object.
# For now, a simple global dictionary to demonstrate flag checking/setting.
DIALOG_GAME_STATE = {
    "flags": {}
}

def _get_flag(flag_name, default=False):
    """Gets a flag value from the temporary game state."""
    # Ensure default matches expected type if flag exists but is None
    val = DIALOG_GAME_STATE["flags"].get(flag_name)
    if val is None:
        return default
    return val


def _set_flag(flag_name, value):
    """Sets a flag value in the temporary game state."""
    logger.debug(f"Setting flag: {flag_name} = {value}")
    DIALOG_GAME_STATE["flags"][flag_name] = value

# --- Utility Function ---
def use_textwrap(text):
    """Wraps text for display."""
    # Dedent might be useful if descriptions have leading whitespace
    dedented_text = textwrap.dedent(str(text)).strip()
    print(textwrap.fill(dedented_text, width=70)) # Adjust width as needed


# --- Condition Checking Logic ---
def _check_condition(condition, character, target_npc_data):
    """
    Checks if a single dialog condition object is met.

    Args:
        condition (dict): The condition object from the JSON.
        character (hero.Hero): The player character object.
        target_npc_data (dict): The data dictionary for the NPC in conversation.

    Returns:
        bool: True if the condition is met, False otherwise.
    """
    condition_type = condition.get("condition_type")

    # --- Check Flag ---
    if condition_type == "check_flag":
        flag_name = condition.get("flag_name")
        # Default required value depends on type: check for presence (true) or absence (false)
        required_value = condition.get("flag_value", True)
        if not flag_name:
            logging.warning("check_flag condition missing 'flag_name'")
            return False # Invalid condition definition

        current_value = _get_flag(flag_name, None) # Get current value, default to None if not set

        # How we compare depends on the required value
        met = False
        if isinstance(required_value, bool):
            # If checking for True, flag must exist and be truthy.
            # If checking for False, flag must not exist or be falsy.
            current_truthy = bool(current_value) # Evaluate current flag's truthiness
            met = (current_truthy == required_value)
        else:
            # For non-boolean, check for exact equality
            met = (current_value == required_value)

        logger.debug(f"Condition Check: Flag '{flag_name}' == {required_value}? Current: {current_value}. Met: {met}")
        return met

    # --- Check Stat ---
    elif condition_type == "check_stat":
        stat_name = condition.get("stat")
        min_val = condition.get("min")
        max_val = condition.get("max") # Optional max value
        if not stat_name or min_val is None:
             logging.warning("check_stat condition missing 'stat' or 'min'")
             return False

        # Dynamically construct the getter method name based on common patterns
        # Assumes methods like get_charm_attribute(), get_luck(), get_strength_attribute() etc. exist
        getter_method_name = f"get_{stat_name}"
        if not hasattr(character, getter_method_name):
             # Try alternative common pattern if first fails (e.g., get_defence_points)
             getter_method_name = f"get_{stat_name}_attribute"
             if not hasattr(character, getter_method_name):
                  getter_method_name = f"get_{stat_name}_points" # Another common pattern
                  if not hasattr(character, getter_method_name):
                       logging.warning(f"Player object missing stat getter method for: {stat_name}")
                       return False

        # Call the found getter method
        try:
            player_stat = getattr(character, getter_method_name)()
            met = (player_stat >= min_val)
            if max_val is not None: # Check max value if provided
                met = met and (player_stat <= max_val)
            logger.debug(f"Condition Check: Stat '{stat_name}' >= {min_val}" + (f" <= {max_val}" if max_val is not None else "") + f"? Player has: {player_stat}. Met: {met}")
            return met
        except Exception as e:
             logging.error(f"Error getting player stat '{stat_name}' using {getter_method_name}: {e}")
             return False


    # --- Check Item ---
    elif condition_type == "check_item":
        item_id = condition.get("item_id")
        quantity = condition.get("quantity", 1)
        if not item_id:
            logging.warning("check_item condition missing 'item_id'")
            return False

        # Assumes character has get_inventory() returning list of item dicts
        count = 0
        try:
            for item_dict in character.get_inventory():
                if isinstance(item_dict, dict) and item_dict.get("item_id") == item_id:
                    # TODO: Handle quantity if items stack within a single dict later
                    count += 1
        except Exception as e:
             logging.error(f"Error accessing player inventory for item check: {e}")
             return False

        met = (count >= quantity)
        logger.debug(f"Condition Check: Has item '{item_id}' x{quantity}? Player has: {count}. Met: {met}")
        return met

    # --- Check Fondness (Placeholder) ---
    elif condition_type == "check_fondness":
        # Requires fondness tracking implementation (e.g., on character)
        target_npc_id = target_npc_data.get('id') # Get ID of the NPC we are talking to
        min_val = condition.get("min")
        max_val = condition.get("max")
        if min_val is None:
             logging.warning("check_fondness condition missing 'min'")
             return False

        # Placeholder: Assume a get_fondness(npc_id) method exists on character
        # current_fondness = character.get_fondness(target_npc_id)
        current_fondness = 0 # Replace with actual call
        met = (current_fondness >= min_val)
        if max_val is not None:
            met = met and (current_fondness <= max_val)
        logging.warning(f"Condition Check: 'check_fondness' not fully implemented. Assumed fondness: {current_fondness}. Met: {met}")
        return met # Return based on placeholder

    # --- Check NPC State (Placeholder) ---
    elif condition_type == "check_npc_state":
        # Requires NPC state tracking (e.g., on NPC runtime object or global state)
        target_npc_id = target_npc_data.get('id')
        required_state = condition.get("required_state")
        if not required_state:
             logging.warning("check_npc_state condition missing 'required_state'")
             return False
        # Placeholder: Assume a function get_npc_state(npc_id) exists
        # current_state = get_npc_state(target_npc_id)
        current_state = "neutral" # Replace with actual call
        met = (current_state == required_state)
        logging.warning(f"Condition Check: 'check_npc_state' not fully implemented. Assumed state: '{current_state}'. Met: {met}")
        return met # Return based on placeholder

    # --- Unknown Condition Type ---
    else:
        logging.warning(f"Unsupported condition type: {condition_type}")
        return False # Default to false for unknown conditions

def _are_conditions_met(conditions, character, target_npc_data):
    """Checks if ALL conditions in a list are met."""
    if not conditions:
        return True # No conditions means the choice is always available
    for condition in conditions:
        if not _check_condition(condition, character, target_npc_data):
            # Log which condition failed (optional)
            # logging.debug(f"Condition failed: {condition}")
            return False # If any condition fails, the choice is unavailable
    return True # All conditions passed


# --- Effect Application Logic ---
def _apply_effect(effect, character, target_npc_data):
    """
    Applies a single dialog effect object.

    Args:
        effect (dict): The effect object from the JSON.
        character (hero.Hero): The player character object.
        target_npc_data (dict): The data dictionary for the NPC in conversation.

    Returns:
        dict or None: Returns a dictionary describing a special action required
                      by the runner (e.g., start combat, perform check),
                      otherwise returns None.
    """
    effect_type = effect.get("effect_type")
    global game_items_data # Needed for give_item

    # --- Set Flag ---
    if effect_type == "set_flag":
        flag_name = effect.get("flag_name")
        flag_value = effect.get("flag_value", True) # Default to setting True
        if flag_name:
            _set_flag(flag_name, flag_value)
        else:
            logging.warning("set_flag effect missing 'flag_name'")

    # --- Change Fondness (Placeholder) ---
    elif effect_type == "change_fondness":
        target_npc_id = target_npc_data.get('id')
        amount = effect.get("amount")
        if amount is None:
             logging.warning("change_fondness effect missing 'amount'")
        else:
             # Placeholder: Assume a change_fondness(npc_id, amount) method exists
             # character.change_fondness(target_npc_id, amount)
             logging.warning(f"Effect Apply: 'change_fondness' by {amount} for {target_npc_id} not implemented.")
             pass

    # --- Give Item (Placeholder) ---
    elif effect_type == "give_item":
        item_id = effect.get("item_id")
        quantity = effect.get("quantity", 1)
        if not item_id:
             logging.warning("give_item effect missing 'item_id'")
        else:
            # Requires access to the master item definitions (game_items_data)
            # This assumes game_items_data is accessible (e.g., global or passed in)
            # from game import game_items_data # Avoid top-level import if possible

            # item_data = game_items_data.get(item_id)
            # if item_data:
            #    item_name = item_data.get('name', item_id)
            #    print(f"You receive {item_name}" + (f" x{quantity}" if quantity > 1 else "") + ".")
            #    for _ in range(quantity):
            #        if not character.add_inventory(copy.deepcopy(item_data)):
            #            print("Your inventory is full!")
            #            break # Stop trying to add if full
            # else:
            #    logging.error(f"Item data not found for give_item effect: {item_id}")
            logging.warning(f"Effect Apply: 'give_item' ({item_id} x{quantity}) not implemented.")
            pass

    # --- Take Item (Placeholder) ---
    elif effect_type == "take_item":
        item_id = effect.get("item_id")
        quantity = effect.get("quantity", 1)
        if not item_id:
             logging.warning("take_item effect missing 'item_id'")
        else:
             # Placeholder: Assume character.remove_item(item_id, quantity) exists
             # if character.remove_item(item_id, quantity):
             #    print(f"You hand over {item_id}.") # Get proper name later
             # else:
             #    print(f"You don't have {item_id} to give.") # Should be caught by condition ideally
             logging.warning(f"Effect Apply: 'take_item' ({item_id} x{quantity}) not implemented.")
             pass

    # --- Perform Check (Signal Runner) ---
    elif effect_type == "perform_check":
        # This effect signals the main runner to handle the check and branching
        logging.debug(f"Effect signals 'perform_check': {effect}")
        return {"perform_check_details": effect}

    # --- Set NPC State (Placeholder) ---
    elif effect_type == "set_npc_state":
        target_npc_id = target_npc_data.get('id')
        new_state = effect.get("new_state")
        if not new_state:
             logging.warning("set_npc_state effect missing 'new_state'")
        else:
             # Placeholder: Assume set_npc_state(npc_id, state) exists
             # set_npc_state(target_npc_id, new_state)
             logging.warning(f"Effect Apply: 'set_npc_state' for {target_npc_id} to '{new_state}' not implemented.")
             pass

    # --- Start Combat (Signal Runner) ---
    elif effect_type == "start_combat":
        # This effect signals the main runner to end dialog and start combat
        target = effect.get("target_npc", "CURRENT")
        target_id = target_npc_data.get('id') if target == "CURRENT" else target
        logging.debug(f"Effect signals 'start_combat' against {target_id}")
        return {"start_combat_target_id": target_id}

    # --- Unknown Effect Type ---
    else:
        logging.warning(f"Unsupported effect type: {effect_type}")

    return None # Indicate no special action needed by the runner

def _apply_effects(effects, character, target_npc_data):
    """
    Applies all effects in a list.

    Returns:
        dict or None: Returns the first special action dict encountered (if any),
                      otherwise None.
    """
    special_runner_action = None
    if not effects:
        return None
    for effect in effects:
        result = _apply_effect(effect, character, target_npc_data)
        if result and not special_runner_action: # Store the first special action needed
             special_runner_action = result
    return special_runner_action


# --- Dialog File Loading ---
def _load_dialog_data(dialog_ref):
    """Loads and returns dialog nodes data from a JSON file."""
    # Construct path relative to this script's assumed location within 'main'
    try:
        # Assumes dialog_system.py is in 'main', data is in 'main/data/dialogs'
        script_dir = os.path.dirname(__file__) # Directory of dialog_system.py ('main')
        dialog_dir = os.path.join(script_dir, 'data', 'dialogs')
        file_path = os.path.join(dialog_dir, f"{dialog_ref}.json")
        logger.info(f"Attempting to load dialog file: {file_path}")

        if not os.path.exists(file_path):
            logging.error(f"Dialog file not found: {file_path}")
            print(f"DEBUG: Dialog file missing at {file_path}") # User feedback
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # TODO: Add JSON schema validation here using dialog_schema.json
            # Example:
            # from jsonschema import validate
            # try:
            #     with open(os.path.join(script_dir, 'data', 'schemas', 'dialog_schema.json'), 'r') as sf:
            #         schema = json.load(sf)
            #     validate(instance=data, schema=schema)
            # except Exception as schema_error:
            #     logging.error(f"Schema validation failed for {file_path}: {schema_error}")
            #     return None # Fail if schema validation fails

            return data.get("dialog_nodes", {}) # Return only the nodes dictionary

    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON in dialog file {dialog_ref}.json: {e}")
        print(f"DEBUG: Error reading dialog file {dialog_ref}.json")
        return None
    except Exception as e:
        logging.exception(f"Unexpected error loading dialog file {dialog_ref}.json:")
        print(f"DEBUG: Unexpected error loading dialog file {dialog_ref}.json")
        return None


# --- Main Conversation Runner ---
def run_conversation(character, target_npc_data):
    """
    Runs a dialog conversation based on JSON data.

    Args:
        character (hero.Hero): The player character object.
        target_npc_data (dict): The data dictionary for the NPC being spoken to.

    Returns:
        dict: A dictionary containing the status of how the conversation ended.
              Keys:
                'status': (str) 'ended', 'combat', 'error', 'no_dialog'
                'combat_target_id': (str, optional) NPC ID if status is 'combat'
    """
    dialog_ref = target_npc_data.get("dialog_ref")
    npc_name = target_npc_data.get("name", "Someone")
    npc_id = target_npc_data.get("id", "unknown_npc")

    # --- Initial Check ---
    if not dialog_ref:
        logging.warning(f"NPC {npc_name} ({npc_id}) has no 'dialog_ref'.")
        use_textwrap(f"{npc_name} doesn't seem interested in talking right now.")
        return {"status": "no_dialog"}

    # --- Load Dialog Data ---
    dialog_nodes = _load_dialog_data(dialog_ref)
    if dialog_nodes is None:
        use_textwrap("Sorry, there seems to be a problem with the conversation data.")
        return {"status": "error"}

    # --- Conversation State ---
    # Assume the dialog_ref is the ID of the starting node
    current_node_id = dialog_ref
    # Track choices made *within this specific conversation instance* to handle non-repeatable options
    session_choices_made = set() # Stores choice_id or node_id+choice_index

    print("-" * 30) # Separator at start of conversation

    # --- Main Dialog Loop ---
    while True:
        # Get data for the current node
        current_node = dialog_nodes.get(current_node_id)
        if not current_node:
            logging.error(f"Dialog Error: Node ID '{current_node_id}' not found in {dialog_ref}.json")
            use_textwrap("The conversation trails off unexpectedly...")
            return {"status": "error"}

        # 1. Display NPC text
        npc_text = current_node.get("npc_text")
        if npc_text:
            use_textwrap(f"{npc_name}: {npc_text}")
        else:
            logging.warning(f"Node '{current_node_id}' has no npc_text.")

        # 2. Prepare and display available player choices
        player_choices_data = current_node.get("player_choices", [])
        available_choices = [] # List to store the actual choice dicts that are valid
        display_choices = [] # List to store text for display

        if not player_choices_data:
            logging.debug(f"Node '{current_node_id}' has no player choices. Ending conversation.")
            print("-" * 30) # Separator at end
            return {"status": "ended"}

        for index, choice_data in enumerate(player_choices_data):
            # Check conditions first
            conditions = choice_data.get("conditions", [])
            if not _are_conditions_met(conditions, character, target_npc_data):
                continue # Skip this choice if conditions aren't met

            # Check if repeatable=false and already chosen this session
            is_repeatable = choice_data.get("repeatable", False)
            choice_key = choice_data.get("choice_id", f"{current_node_id}_{index}") # Unique key
            if not is_repeatable and choice_key in session_choices_made:
                continue # Skip non-repeatable choices already made

            # If conditions met and choice is available, add for display
            choice_text = choice_data.get("choice_text", "...")
            display_choices.append(choice_text)
            available_choices.append(choice_data) # Store the full dict

        # Display the filtered choices
        if not available_choices:
            logging.info(f"No available choices for player at node '{current_node_id}' (all conditions failed or repeated). Ending conversation.")
            use_textwrap("(You have nothing more to say right now.)")
            print("-" * 30) # Separator at end
            return {"status": "ended"}

        print("\nYour response:")
        for i, text in enumerate(display_choices):
            print(f"  {i + 1}. {text}")

        # 3. Get Player Input
        while True:
            try:
                player_input = input("> ")
                if not player_input: continue # Handle empty input
                selected_index = int(player_input) - 1
                if 0 <= selected_index < len(available_choices):
                    chosen_option = available_choices[selected_index]
                    break # Valid choice selected
                else:
                    print(f"Invalid choice number (enter 1-{len(available_choices)}).")
            except ValueError:
                print("Please enter the number of your choice.")
            except EOFError: # Handle Ctrl+D or unexpected end of input
                 logging.warning("EOFError received during dialog input. Ending conversation.")
                 return {"status": "error"}

        # 4. Process Chosen Option
        logging.debug(f"Player chose index {selected_index}: '{chosen_option.get('choice_text')}'")

        # Mark as chosen this session if not repeatable
        is_repeatable = chosen_option.get("repeatable", False)
        if not is_repeatable:
             choice_key = chosen_option.get("choice_id", f"{current_node_id}_{selected_index}") # Use index if no ID
             session_choices_made.add(choice_key)

        # Apply effects and check for special runner actions
        effects = chosen_option.get("effects", [])
        special_action = _apply_effects(effects, character, target_npc_data)

        # Handle special actions signaled by effects
        if special_action:
             if "start_combat_target_id" in special_action:
                 combat_target_id = special_action["start_combat_target_id"]
                 logging.info(f"Dialog ending to trigger combat with {combat_target_id}.")
                 print("-" * 30)
                 return {"status": "start_combat", "combat_target_id": combat_target_id}
             elif "perform_check_details" in special_action:
                 # TODO: Implement skill check logic here
                 check_details = special_action["perform_check_details"]
                 check_type = check_details.get("check_type")
                 success_node = check_details.get("success_node")
                 failure_node = check_details.get("failure_node")
                 # success = perform_skill_check(character, target_npc_data, check_details) # Call actual check
                 success = False # Placeholder - Assume failure for now
                 logging.warning(f"'perform_check' ({check_type}) effect not fully implemented. Result: {'Success' if success else 'Failure'}")
                 next_node_id = success_node if success else failure_node
                 if not next_node_id:
                      logging.error(f"Perform_check effect for {check_type} missing success or failure node!")
                      return {"status": "error"}
             else:
                 # Handle other potential special actions?
                 logging.warning(f"Unhandled special action from effects: {special_action}")
                 next_node_id = chosen_option.get("destination_node") # Default to choice destination
        else:
            # Determine next node normally
            next_node_id = chosen_option.get("destination_node")

        # 5. Move to Next Node or End Conversation
        if not next_node_id:
            logging.error(f"Chosen option '{chosen_option.get('choice_text')}' has no destination_node!")
            return {"status": "error"}

        if next_node_id == "[END_CONVERSATION]":
            logging.debug("Destination node is END_CONVERSATION. Ending dialog normally.")
            print("-" * 30) # Separator at end
            return {"status": "ended"}
        elif next_node_id == "[END_CONVERSATION_AND_ATTACK]":
             logging.info("Dialog ending to trigger combat via destination node.")
             print("-" * 30)
             # We need the ID of the NPC we are talking to
             return {"status": "start_combat", "combat_target_id": npc_id}
        else:
            # Loop continues with the new node ID
            current_node_id = next_node_id
            print("-" * 20) # Separator between turns
