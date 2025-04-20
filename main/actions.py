import textwrap 

def get_available_actions(location_data):
    """
    Determines available command strings based on location data.
    Checks standard commands, exits, actions for interactables/items,
    and adds 'talk' for NPCs.

    Args:
        location_data (dict): The data dictionary for the current location.

    Returns:
        list: A list of suggested command strings.
    """
    actions = ["look", "inventory", "help", "quit"] # Standard

    # Movement
    exits = location_data.get('exits', {})
    for direction in exits:
        actions.append(f"go {direction}")

    # Examine Interactables
    interactables_list = location_data.get('interactables', [])
    for interactable_data in interactables_list:
        name = interactable_data.get('name')
        if name:
            # Suggest examine first if available
            if 'examine' in interactable_data.get('actions', {}) or 'description' in interactable_data:
                 actions.append(f"examine {name}")
            # Suggest other actions (excluding examine which is covered)
            for verb in interactable_data.get('actions', {}):
                if verb != 'examine':
                    actions.append(f"{verb} {name}")

    # Examine Items
    items_list = location_data.get('items', [])
    for item_data in items_list:
        name = item_data.get('name', 'an unnamed item')
        if name != 'an unnamed item':
            # Suggest examine first if available
            if 'examine' in item_data.get('actions', {}) or 'description' in item_data:
                actions.append(f"examine {name}")
            # Suggest other actions
            for verb in item_data.get('actions', {}):
                if verb != 'examine':
                    actions.append(f"{verb} {name}")

    # --- VVV ADD THIS SECTION FOR NPCs VVV ---
    # Talk to NPCs
    npcs_list = location_data.get('npcs', [])
    for npc_id in npcs_list:
        # Generate a likely name for the suggestion.
        # TODO: Ideally, look up the actual NPC name from loaded NPC data if available
        npc_name = npc_id.replace("npc_", "").replace("_", " ").title()
        actions.append(f"talk {npc_name.lower()}") # Suggest lowercase name for easier matching
    # --- ^^^ END NPC SECTION ^^^ ---


    # Remove potential duplicates while preserving order reasonably
    actions = list(dict.fromkeys(actions))
    return actions