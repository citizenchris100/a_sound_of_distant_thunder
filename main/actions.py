# main/actions.py

import logging

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
    Suggests 'examine' for defeated NPCs instead of 'talk' or 'attack'.

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
    if isinstance(exits, dict):
        for direction in exits:
            if not direction.startswith("_"):
                actions.append(f"go {direction}")
    else:
        logging.warning(f"Location '{location_data.get('location_id', 'Unknown')}' has malformed 'exits' data: {exits}")


    # --- Interactables and Items ---
    interactables_list = location_data.get('interactables', [])
    items_list = location_data.get('items', []) # Items on the ground
    all_targets = (interactables_list if isinstance(interactables_list, list) else []) + \
                  (items_list if isinstance(items_list, list) else [])

    for target_data in all_targets:
         if isinstance(target_data, dict):
            name = target_data.get('name')
            obj_id = target_data.get('id')
            if name:
                available_verbs = target_data.get('actions', {})
                if not isinstance(available_verbs, dict):
                    logging.warning(f"Target '{name}' in loc '{location_data.get('location_id', 'Unknown')}' malformed 'actions': {available_verbs}")
                    available_verbs = {}

                if 'examine' in available_verbs or 'description' in target_data:
                     actions.append(f"examine {name}")
                for verb in available_verbs:
                    if verb != 'examine':
                        actions.append(f"{verb} {name}")

                is_ground_item = any(item is target_data for item in items_list if isinstance(items_list, list))
                if is_ground_item:
                     if f"take {name}" not in actions:
                          actions.append(f"take {name}")
         else:
              logging.warning(f"Malformed target data in loc '{location_data.get('location_id', 'Unknown')}': {target_data}")


    # --- NPCs (Alive or Defeated) ---
    npcs_list = location_data.get('npcs', [])
    if isinstance(npcs_list, list):
        for npc_id in npcs_list:
            if not isinstance(npc_id, str):
                 logging.warning(f"Non-string NPC ID in loc '{location_data.get('location_id', 'Unknown')}': {npc_id}")
                 continue

            npc_data = game_npc_data.get(npc_id)
            if npc_data and isinstance(npc_data, dict):
                npc_name = npc_data.get('name', npc_id)
                has_dialog = bool(npc_data.get('dialog_ref'))
                aliases = npc_data.get('aliases', [])
                is_defeated = _get_flag(f"npc_defeated_{npc_id}", default=False)

                if is_defeated:
                    # --- Suggest actions for defeated NPC ---
                    actions.append(f"examine {npc_name.lower()}") # Examine suggests looting
                    # Optionally suggest examining by alias too?
                    # if aliases and isinstance(aliases, list) and aliases[0] and isinstance(aliases[0], str):
                    #      actions.append(f"examine {aliases[0].lower()}")
                else:
                    # --- Suggest actions for alive NPC ---
                    suggest_talk_name = f"talk {npc_name.lower()}"
                    suggest_talk_alias = None
                    if aliases and isinstance(aliases, list) and aliases[0] and isinstance(aliases[0], str):
                         suggest_talk_alias = f"talk {aliases[0].lower()}"

                    if has_dialog:
                        actions.append(suggest_talk_name)
                        if suggest_talk_alias: actions.append(suggest_talk_alias)
                    else:
                        # Only suggest talk for non-dialog NPC if not attempted
                        attempt_flag_name = f"attempted_talk_{npc_id}"
                        try:
                            already_attempted = _get_flag(attempt_flag_name, default=False)
                            if not already_attempted:
                                actions.append(suggest_talk_name)
                                if suggest_talk_alias: actions.append(suggest_talk_alias)
                        except NameError:
                             logging.error("Cannot check talk flag due to missing _get_flag.")
                             actions.append(suggest_talk_name) # Suggest anyway if check fails
                             if suggest_talk_alias: actions.append(suggest_talk_alias)

                    # Always suggest attack for alive NPCs (can be refined later)
                    actions.append(f"attack {npc_name.lower()}")
                    if suggest_talk_alias: # Reuse alias logic for attack suggestion
                         attack_alias = suggest_talk_alias.replace("talk", "attack")
                         actions.append(attack_alias)

            else:
                logging.warning(f"NPC data missing/malformed for ID '{npc_id}' in loc '{location_data.get('location_id', 'Unknown')}'.")
                # Suggest basic interactions even if data is missing?
                actions.append(f"examine {npc_id.lower()}")
                actions.append(f"talk {npc_id.lower()}")
                actions.append(f"attack {npc_id.lower()}")
    else:
         logging.warning(f"Location '{location_data.get('location_id', 'Unknown')}' has malformed 'npcs' data: {npcs_list}")


    # --- Remove potential duplicates ---
    try:
        actions = list(dict.fromkeys(actions))
    except TypeError:
         logging.error("Error removing duplicate actions.")
         cleaned_actions = []; seen = set()
         for item in actions:
             try:
                 if item not in seen: cleaned_actions.append(item); seen.add(item)
             except TypeError: cleaned_actions.append(item)
         actions = cleaned_actions

    return actions
