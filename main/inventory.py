from .Util import vowel_start
import copy 
from ItemUtil import is_item_broken, get_gun_ammo, set_gun_ammo, get_item_attribute
try:

    from ItemUtil import is_item_broken
except ImportError:
    print("ERROR in inventory.py: Could not import 'is_item_broken' from ItemUtil. Weapon loot check will fail.")
    # Define a dummy function to avoid immediate crashes later
    def is_item_broken(item_dict):
        return False # Default to not broken if import fails


# TODO: is full inventory working? what to do if tries to add more items to inventory than slots available?
# TODO: consolodate multiple items in list ex: med pack x2 etc...

def inventory(character_var):
    """Displays inventory and handles using/equipping/discarding items (dictionaries)."""
    print('------------------------------')
    print('-         Inventory          -')
    print('------------------------------')

    inv = character_var.get_inventory() # Get the list of item dictionaries

    if not inv: # Check if inventory is empty
        print('------------------------------')
        print('-           Empty            -')
        print('------------------------------')
        print('------------------------------')
        return # Exit if inventory is empty

    while True:
        print('------------------------------')
        print('--- Your Inventory Items ---')
        for i, item_dict in enumerate(inv):
            # Access item name from dictionary
            item_name = item_dict.get("name", "Unknown Item")
            print(f"{i + 1}: {item_name}")
        print('------------------------------')
        print("Currently Equipped:")
        # Access equipped item names from dictionaries (if equipped)
        melee_name = character_var.get_equipped_melee().get("name", "None") if character_var.get_equipped_melee() else "None"
        gun_name = character_var.get_equipped_gun().get("name", "None") if character_var.get_equipped_gun() else "None"
        armor_name = character_var.get_equipped_armour().get("name", "None") if character_var.get_equipped_armour() else "None"
        print(f" Melee: {melee_name}")
        print(f" Gun:   {gun_name}")
        print(f" Armor: {armor_name}")
        print('------------------------------')

        n = input(
            "Enter the number of the item to Use/Equip/Discard.\n"
            "Type 'Exit' to return.\n> "
        )

        if "exit" in n.lower():
            break

        if n.isdigit():
            try:
                index = int(n) - 1
                if 0 <= index < len(inv):
                    selected_item_dict = inv[index] # Get the selected item dictionary
                    item_name = selected_item_dict.get("name", "Unknown Item")
                    item_type = selected_item_dict.get("item_type")

                    print('------------------------------')
                    print(f"Selected: {item_name}")
                    # Display item description and durability
                    print(f"Desc: {selected_item_dict.get('description', 'No description.')}")
                    if "max_durability" in selected_item_dict:
                         print(f"Durability: {selected_item_dict.get('current_durability', 'N/A')} / {selected_item_dict.get('max_durability', 'N/A')}")

                    options = []
                    if item_type == "consumable": options.append("Use")
                    if item_type in ["weapon", "armor"]: options.append("Equip")
                    if item_type == "ammo": options.append("Reload") # Changed 'ammo' action to 'Reload'
                    options.append("Discard")
                    options.append("Back")

                    print("Actions:")
                    for i, opt in enumerate(options):
                        print(f" {i + 1}. {opt}")

                    action_choice = input("> ")
                    action_choice_num = -1
                    if action_choice.isdigit():
                        action_choice_num = int(action_choice) -1

                    selected_action = None
                    if 0 <= action_choice_num < len(options):
                        selected_action = options[action_choice_num].lower()

                    # --- Handle Actions ---
                    if selected_action == "use" and item_type == "consumable":
                        # --- Using Consumables ---
                        # Get effect attributes from the dictionary
                        attributes = selected_item_dict.get("attributes", {})
                        heal_amount = attributes.get("heal_amount", 0)
                        effect_type = attributes.get("effect_type", "")

                        if effect_type == "heal":
                            if character_var.get_health_points() < character_var.get_hp_limit():
                                character_var.set_health_points(character_var.get_health_points() + heal_amount)
                                print('------------------------------')
                                start = vowel_start(item_name)
                                print(f"You used {start}{item_name}.")
                                print(f"{heal_amount} health restored.")
                                print(f"Your Health is now {character_var.get_health_points()}/{character_var.get_hp_limit()}")
                                print('------------------------------')
                                character_var.del_inventory(index) # Remove item by index after use
                                # Loop continues implicitly, showing updated inventory
                            else:
                                print('------------------------------')
                                print("Your Health is already Max.")
                        elif effect_type == "multi": # Example for Night Shade
                            mutate_level = attributes.get("mutate_level", 0)
                            intoxicate_level = attributes.get("intoxicate_level", 0)
                            print('------------------------------')
                            print(f"You consumed the {item_name}. You feel strange...")
                            # TODO: Implement actual mutation/intoxication effects
                            print(f" (Mutation: {mutate_level}, Intoxication: {intoxicate_level})")
                            print('------------------------------')
                            character_var.del_inventory(index)
                        # Add more consumable effect types here...
                        else:
                            print("You can't use this item in that way right now.")

                    elif selected_action == "equip" and item_type in ["weapon", "armor"]:
                        # --- Equipping Items ---
                        item_to_equip = selected_item_dict # The dictionary itself
                        current_equipped = None
                        equip_success = False

                        # Determine weapon type from attributes
                        weapon_type = item_to_equip.get("attributes", {}).get("weapon_type")

                        if item_type == "weapon" and weapon_type == "gun":
                            current_equipped = character_var.get_equipped_gun()
                            character_var.set_equipped_gun(item_to_equip)
                            equip_success = True
                        elif item_type == "weapon" and weapon_type == "melee":
                            current_equipped = character_var.get_equipped_melee()
                            character_var.set_equipped_melee(item_to_equip)
                            equip_success = True
                        elif item_type == "armor":
                            current_equipped = character_var.get_equipped_armour()
                            character_var.set_equipped_armour(item_to_equip)
                            equip_success = True

                        if equip_success:
                            print('------------------------------')
                            print(f"{item_name} is now equipped.")
                            # Remove the equipped item from main inventory list
                            inv.pop(index)
                            # Add the previously equipped item back to inventory (if any)
                            # Use deepcopy to prevent state sharing if the same item was equipped before
                            if current_equipped:
                                character_var.add_inventory(copy.deepcopy(current_equipped))
                            print('------------------------------')
                            # No break here, show updated inventory/equipped status

                    elif selected_action == "reload" and item_type == "ammo":
                        # --- Reloading Ammo ---
                        equipped_gun_dict = character_var.get_equipped_gun()
                        ammo_box_dict = selected_item_dict
                        ammo_box_type = ammo_box_dict.get("attributes", {}).get("ammo_type")
                        ammo_box_quantity = ammo_box_dict.get("attributes", {}).get("quantity", 0)

                        if not equipped_gun_dict:
                            print("You need to equip a gun first to reload!")
                        elif is_item_broken(equipped_gun_dict):
                             print(f"Your {equipped_gun_dict.get('name','Gun')} is broken and cannot be reloaded.")
                        else:
                            gun_ammo_type = equipped_gun_dict.get("attributes", {}).get("ammo_type")
                            if gun_ammo_type != ammo_box_type:
                                print(f"This gun uses {gun_ammo_type}, but this is {ammo_box_type} ammo.")
                            elif ammo_box_quantity <= 0:
                                print(f"This {ammo_box_dict.get('name', 'Ammo Box')} is empty.")
                            else:
                                # --- Placeholder for ammo state ---
                                # Get current ammo and clip size from the equipped gun dict
                                clip_size = equipped_gun_dict.get("attributes", {}).get("clip_size", 0)
                                # Assume 'current_ammo' key exists (NEEDS BETTER SOLUTION LATER)
                                current_ammo = equipped_gun_dict.get('current_ammo', 0)
                                # --- End Placeholder ---

                                if current_ammo >= clip_size:
                                    print("Your weapon's clip is already full.")
                                else:
                                    ammo_needed = clip_size - current_ammo
                                    ammo_to_transfer = min(ammo_needed, ammo_box_quantity)

                                    # --- Placeholder for ammo state update ---
                                    equipped_gun_dict['current_ammo'] = current_ammo + ammo_to_transfer
                                    # --- End Placeholder ---

                                    # Update ammo box quantity (modify the dictionary in inventory)
                                    # Note: Modifying dict directly might be okay for ammo boxes as they are consumable
                                    ammo_box_dict["attributes"]["quantity"] = ammo_box_quantity - ammo_to_transfer
                                    print('------------------------------')
                                    print(f"Reloaded {ammo_to_transfer} rounds of {ammo_box_type}.")
                                    print(f"Gun now has {equipped_gun_dict['current_ammo']}/{clip_size} ammo.")
                                    if ammo_box_dict["attributes"]["quantity"] <= 0:
                                        print(f"The {ammo_box_dict.get('name')} is now empty and removed.")
                                        character_var.del_inventory(index) # Remove empty ammo box
                                    else:
                                         print(f"{ammo_box_dict['attributes']['quantity']} rounds left in the box.")
                                    print('------------------------------')
                                    # No break, show updated inventory

                    elif selected_action == "discard":
                        # --- Discarding Items ---
                        print(f"Are you sure you want to discard {item_name}?")
                        confirm = input(" (yes/no): ")
                        if confirm.lower() == "yes":
                            character_var.del_inventory(index) # Use updated del_inventory by index
                            print(f"{item_name} discarded.")
                            # No break, show updated inventory
                        else:
                            print("Discard cancelled.")

                    elif selected_action == "back":
                        # Do nothing, loop will continue showing inventory
                        pass
                    else:
                        print("Invalid action for this item type.")

                else: # Input was not a valid number or out of range
                    print("Invalid item number. Please try again.")
            except ValueError: # Handle cases where input is not a digit
                print("Invalid input. Please enter a number or 'Exit'.")

        elif "exit" in n.lower(): # Redundant check, handled above, but safe
             break
        else: # Handle non-numeric input that isn't 'exit'
             print("Invalid input. Please enter the number of the item or type 'Exit'.")


def loot_add(character_var, enemy_var):
    """Handles looting items (dictionaries) from a defeated enemy, including their equipped weapon."""

    enemy_inv = enemy_var.get_inventory() 
    equipped_weapon = enemy_var.get_equipped_melee()
    eligible_weapon = None

    if equipped_weapon and not is_item_broken(equipped_weapon):
        eligible_weapon = equipped_weapon 

    combined_loot = list(enemy_inv) 
    if eligible_weapon:
        combined_loot.append(eligible_weapon) 

    if not combined_loot: 
        print(f"{enemy_var.get_name()} had no loot.")
        return

    while combined_loot:
        print('------------------------------')
        print(f'--- {enemy_var.get_name()}\'s Remaining Items ---')
      
        for i, item_dict in enumerate(combined_loot):
            item_name = item_dict.get("name", "Unknown Item")
            print(f"{i + 1}: {item_name}") 
        print('------------------------------')
        n = input("Enter item number to take, 'All', 'Inv' for your inventory, or 'Exit'.\n> ")
        if "exit" in n.lower():
            print("Stopped looting.")
            break
        elif "inv" in n.lower():
            inventory(character_var) 
            continue
        elif "all" in n.lower():
            items_taken_count = 0
            items_could_not_take = []
            for item_dict in list(combined_loot):
                if len(character_var.get_inventory()) < character_var.get_inventory_limit():
                    character_var.add_inventory(copy.deepcopy(item_dict))
                    combined_loot.remove(item_dict) 
                    items_taken_count += 1
                else:
                    items_could_not_take.append(item_dict.get("name", "Unknown Item"))

            if items_taken_count > 0:
                 print(f"Took {items_taken_count} item(s).")
            if items_could_not_take:
                 print("Inventory full. Could not take:", ", ".join(items_could_not_take))
            break 

        elif n.isdigit():
            try:
                index = int(n) - 1
                if 0 <= index < len(combined_loot):
                    item_to_take = combined_loot[index]
                    if len(character_var.get_inventory()) < character_var.get_inventory_limit():
                        character_var.add_inventory(copy.deepcopy(item_to_take))
                        combined_loot.pop(index)
                    else:
                        print("Your inventory is full. Cannot take this item.")
                else:
                    print("Invalid item number.")
            except ValueError:
                print("Invalid input.")
        else:
            print("Invalid input. Enter a number, 'All', 'Inv', or 'Exit'.")
    if not combined_loot:
        print("Looted all items.")