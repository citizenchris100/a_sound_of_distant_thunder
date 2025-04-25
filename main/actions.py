# main/actions.py

import logging # Added logging

# Need access to flag checking logic from dialog_system
# This dependency suggests that flag management should ideally be moved
# to a more central location (e.g., a game state manager or the character class)
# accessible by both modules without circular imports.
try:
    # Attempt relative import assuming dialog_system is in the same package
    from .dialog_system import _get_flag
except ImportError:
    # Fallback if direct import fails (e.g., during testing or restructuring)
    logging.error("actions.py: Could not import _get_flag from dialog_system. Talk suggestions for non-dialog NPCs might be incorrect.")
    # Define a dummy function to prevent crashes if _get_flag is critical elsewhere
    def _get_flag(flag_name, default=False):
        """Dummy fallback for _get_flag if import fails."""
        logging.warning("Using dummy _get_flag function.")
        return False # Assume flag is not set if function unavailable

# Set up logger for this module
logger = logging.getLogger(__name__)

def get_available_actions(location_data, character, game_npc_data):
    """
    Determines available command strings based on location data,
    character state (for flags), and NPC data.

    Args:
        location_data (dict): The data dictionary for the current location.
        character (hero.Hero): The player character object.
        game_npc_data (dict): The global dictionary of loaded NPC data.

    Returns:
        list: A list of suggested command strings.
    """
    # Start with standard, always available commands
    actions = ["look", "inventory", "help", "quit"]

    # --- Movement ---
    exits = location_data.get('exits', {})
    # Ensure exits is a dictionary before iterating
    if isinstance(exits, dict):
        for direction in exits:
            # Filter out potentially internal/hidden exits if needed later
            if not direction.startswith("_"):
                actions.append(f"go {direction}")
    else:
        logging.warning(f"Location '{location_data.get('location_id', 'Unknown')}' has malformed 'exits' data: {exits}")


    # --- Interactables and Items ---
    interactables_list = location_data.get('interactables', [])
    items_list = location_data.get('items', []) # Items on the ground

    # Ensure lists are actually lists before combining
    all_targets = (interactables_list if isinstance(interactables_list, list) else []) + \
                  (items_list if isinstance(items_list, list) else [])

    for target_data in all_targets:
         # Ensure each target is a dictionary
         if isinstance(target_data, dict):
            name = target_data.get('name')
            obj_id = target_data.get('id') # For potential future use (e.g., checking state)
            if name: # Only process if the target has a name
                available_verbs = target_data.get('actions', {})
                # Ensure available_verbs is a dictionary
                if not isinstance(available_verbs, dict):
                    logging.warning(f"Target '{name}' in location '{location_data.get('location_id', 'Unknown')}' has malformed 'actions': {available_verbs}")
                    available_verbs = {} # Treat as having no actions

                # Suggest examine first if possible
                # Check if 'examine' is an explicit action OR if there's a description
                if 'examine' in available_verbs or 'description' in target_data:
                     actions.append(f"examine {name}")

                # Suggest other defined actions
                for verb in available_verbs:
                    # Avoid suggesting 'examine' again if it was already added
                    if verb != 'examine':
                        actions.append(f"{verb} {name}")

                # Suggest 'take' specifically for items defined in the location's 'items' list
                # Check if the current target_data originated from items_list
                is_ground_item = any(item is target_data for item in items_list if isinstance(items_list, list))
                if is_ground_item:
                     # Check if 'take' is already suggested by 'actions', avoid adding twice
                     # Also check if 'take' is even a valid action defined for the item (optional but good)
                     if f"take {name}" not in actions: # and 'take' in available_verbs: # Uncomment second part if needed
                          actions.append(f"take {name}")
         else:
              # Log if a target in the list is not a dictionary or lacks a name
              logging.warning(f"Malformed target data found in location '{location_data.get('location_id', 'Unknown')}': {target_data}")


    # --- Talk to NPCs ---
    npcs_list = location_data.get('npcs', [])
    if isinstance(npcs_list, list): # Ensure npcs_list is actually a list
        for npc_id in npcs_list:
            # Ensure npc_id is a string before proceeding
            if not isinstance(npc_id, str):
                 logging.warning(f"Non-string NPC ID found in location '{location_data.get('location_id', 'Unknown')}': {npc_id}")
                 continue

            npc_data = game_npc_data.get(npc_id)
            if npc_data and isinstance(npc_data, dict): # Check if data exists and is a dict
                npc_name = npc_data.get('name', npc_id) # Use name, fallback to ID
                has_dialog = bool(npc_data.get('dialog_ref')) # Check if dialog_ref exists and is not empty/null
                aliases = npc_data.get('aliases', []) # Get aliases list

                # Suggest talking by primary name
                suggest_talk_name = f"talk {npc_name.lower()}"
                # Suggest talking by first alias (if exists and is valid)
                suggest_talk_alias = None
                if aliases and isinstance(aliases, list) and aliases[0] and isinstance(aliases[0], str):
                     suggest_talk_alias = f"talk {aliases[0].lower()}"

                if has_dialog:
                    # Always suggest talking if they have dialog
                    actions.append(suggest_talk_name)
                    if suggest_talk_alias:
                         actions.append(suggest_talk_alias)
                else:
                    # If no dialog, only suggest talking if player hasn't attempted it yet
                    attempt_flag_name = f"attempted_talk_{npc_id}"
                    try:
                        # Use the imported _get_flag (or its dummy fallback)
                        already_attempted = _get_flag(attempt_flag_name, default=False)
                        if not already_attempted:
                            # Only suggest talk if not already attempted
                            actions.append(suggest_talk_name)
                            if suggest_talk_alias:
                                 actions.append(suggest_talk_alias)
                    except NameError:
                         # This block should ideally not be reached if the dummy func is defined
                         logging.error("Cannot check talk flag due to missing _get_flag import/definition.")
                         # Fallback: Suggest talking anyway if the check fails catastrophically
                         actions.append(suggest_talk_name)
                         if suggest_talk_alias: actions.append(suggest_talk_alias)

            else:
                # Fallback if NPC data is somehow missing or malformed
                logging.warning(f"NPC data missing or malformed for ID '{npc_id}' referenced in location '{location_data.get('location_id', 'Unknown')}'.")
                # Suggest talking by ID as last resort if data is missing
                actions.append(f"talk {npc_id.lower()}")
    else:
         # Log if the 'npcs' key contains something other than a list
         logging.warning(f"Location '{location_data.get('location_id', 'Unknown')}' has malformed 'npcs' data (expected list): {npcs_list}")


    # --- Remove potential duplicates while preserving order reasonably ---
    # Using dict.fromkeys for Python 3.7+ preserves order
    # Fallback for older Python might be needed if compatibility is required
    try:
        actions = list(dict.fromkeys(actions))
    except TypeError: # Handle potential unhashable items if data is malformed
         logging.error("Error removing duplicate actions, potential unhashable type in list.")
         # Simple list conversion as fallback (loses order guarantee)
         # This might happen if, e.g., a list was accidentally put in the actions list
         cleaned_actions = []
         seen = set()
         for item in actions:
             # Only add hashable items to avoid errors with set operations
             try:
                 if item not in seen:
                     cleaned_actions.append(item)
                     seen.add(item)
             except TypeError:
                 # Keep unhashable items but don't try to deduplicate them based on content
                 cleaned_actions.append(item)
         actions = cleaned_actions


    return actions
