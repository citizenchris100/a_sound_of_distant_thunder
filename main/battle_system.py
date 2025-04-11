# main/battle_system.py (Refactored for PURE Data-Driven Approach using Dictionaries)

import random
import math
import sys # Import sys for sys.exit() in game_over
# We still need inventory functions for now
import inventory
# We still need level system for now
import lvl_system
# We will NOT import items anymore as we use dictionaries directly
# import items - REMOVE THIS IMPORT

# --- Score Functions (unchanged) ---
def display_score():
    try:
        with open("../score.txt", "r") as file:
            for line in file:
                xline = line.split(",")
                if len(xline) >= 2:
                    print(xline[0], xline[1].strip())
    except FileNotFoundError:
        print("Score file not found.")

def write_score(score, name):
    try:
        with open("../score.txt", "a") as file:
            file.write(f"{name},{score}\n")
    except IOError:
        print("Error writing to score file.")

def game_over(character_var):
    # Assuming character_var has get_exp() and get_health_points() methods
    score = character_var.get_exp()
    if character_var.get_health_points() <= 0:
        print("\nYou have been defeated.")
        print(f"Your Final score is {score}")
        name = input("Enter your Name: ")
        write_score(score, name)
        display_score()
        print("\nExiting game...")
        sys.exit() # Exit the game cleanly

# --- Helper Functions for Dictionary Access ---

def get_item_attribute(item_dict, attribute_name, default=0):
    """Safely gets a numeric attribute from an item's 'attributes' dictionary."""
    if isinstance(item_dict, dict) and isinstance(item_dict.get("attributes"), dict):
        return item_dict["attributes"].get(attribute_name, default)
    return default

def get_item_property(item_dict, property_name, default=None):
    """Safely gets a top-level property from an item dictionary."""
    if isinstance(item_dict, dict):
        return item_dict.get(property_name, default)
    return default

def decrease_item_durability(item_dict, loss_amount):
    """Decreases item durability (stored in 'current_durability') safely."""
    if not isinstance(item_dict, dict) or loss_amount <= 0:
        return False # Indicate durability was not changed
    current_dur = item_dict.get("current_durability", 0)
    new_dur = max(0, current_dur - loss_amount)
    item_dict["current_durability"] = new_dur # Update the dictionary directly
    # Optional: Add print message about durability loss
    # print(f"   {item_dict.get('name', 'Item')}'s durability decreased to {new_dur}")
    return True # Indicate durability was changed

def is_item_broken(item_dict):
    """Checks if an item's 'current_durability' is 0 or less."""
    if isinstance(item_dict, dict):
        return item_dict.get("current_durability", 0) <= 0
    return True # Assume broken if not a valid item dict

# --- Refactored Combat Functions ---

def character_defence(character_var):
    """Calculates character's total defense."""
    # Assuming character_var has get_defence_points() and get_equipped_armour() methods
    base_defence = character_var.get_defence_points()
    equipped_armour_dict = character_var.get_equipped_armour() # This should now return a dictionary or None
    armour_defence = 0

    if equipped_armour_dict and not is_item_broken(equipped_armour_dict):
        # Access defense directly from the armor dictionary's attributes
        armour_defence = get_item_attribute(equipped_armour_dict, 'defense', default=0)

    return base_defence + armour_defence

def npc_defence(enemy_var):
    """Calculates NPC's total defense."""
    # Assuming enemy_var has get_defence() method
    base_defence = enemy_var.get_defence()
    equipped_armour_dict = None
    # Check if enemy has get_equipped_armour method (for Human NPCs)
    if hasattr(enemy_var, 'get_equipped_armour'):
        equipped_armour_dict = enemy_var.get_equipped_armour() # Should return a dictionary or None

    armour_defence = 0
    if equipped_armour_dict and not is_item_broken(equipped_armour_dict):
        armour_defence = get_item_attribute(equipped_armour_dict, 'defense', default=0)

    return base_defence + armour_defence


def calculate_melee_hit(attacker, weapon_dict):
    """Calculates melee hit damage based on strength and weapon dictionary."""
    # Assuming attacker has get_strength_attribute() method
    strength = attacker.get_strength_attribute()
    weapon_damage = 0

    if weapon_dict and not is_item_broken(weapon_dict):
        weapon_damage = get_item_attribute(weapon_dict, 'damage', default=0)
        # Decrease weapon durability
        loss = get_item_property(weapon_dict, 'durability_loss_per_use', default=1)
        if decrease_item_durability(weapon_dict, loss):
             if is_item_broken(weapon_dict):
                  print(f"   {get_item_property(weapon_dict, 'name', 'Melee Weapon')} broke!")
             # else:
                  # Optional: print durability loss message
                  # print(f"   {get_item_property(weapon_dict, 'name', 'Melee Weapon')} durability decreased.")

    return strength + weapon_damage

def calculate_gun_hit(attacker, weapon_dict, shots=1):
    """Calculates gun hit damage based on gun skill and weapon dictionary."""
    # Assuming attacker has get_gun_skill() method
    gun_skill = attacker.get_gun_skill() if hasattr(attacker, 'get_gun_skill') else 0
    weapon_damage = 0
    ammo_in_clip = 0

    # Guns need special handling for ammo count stored within the *instance* of the item
    # This is tricky if we only store the base item dictionary.
    # We'll need to adjust how equipped items store state like ammo count.
    # --- TEMPORARY PLACEHOLDER for ammo ---
    # Let's assume for now the weapon_dict *might* have a temporary 'current_ammo' key.
    # This needs a better solution later (e.g., wrapping item dicts in a class instance
    # when equipped, or storing ammo count separately on the character).
    if isinstance(weapon_dict, dict):
        # Check for a temporary 'current_ammo' key; fallback to 'clip_size' if not found
        ammo_in_clip = weapon_dict.get('current_ammo', get_item_attribute(weapon_dict, 'clip_size', 0))
    # --- END PLACEHOLDER ---

    actual_shots = min(shots, ammo_in_clip)

    if weapon_dict and not is_item_broken(weapon_dict) and actual_shots > 0:
        weapon_damage = get_item_attribute(weapon_dict, 'damage', default=0)

        # --- TEMPORARY PLACEHOLDER for ammo update ---
        if isinstance(weapon_dict, dict):
            weapon_dict['current_ammo'] = ammo_in_clip - actual_shots
            print(f"   ({weapon_dict.get('current_ammo', 0)} shots remaining in {get_item_property(weapon_dict, 'name', 'Gun')})")
        # --- END PLACEHOLDER ---

        # Decrease weapon durability
        loss = get_item_property(weapon_dict, 'durability_loss_per_use', default=1)
        if decrease_item_durability(weapon_dict, loss * actual_shots):
             if is_item_broken(weapon_dict):
                  print(f"   {get_item_property(weapon_dict, 'name', 'Gun')} broke!")

        return (gun_skill + weapon_damage) * actual_shots
    elif isinstance(weapon_dict, dict) and actual_shots <= 0:
        print(f"   *Click* Out of ammo in {get_item_property(weapon_dict, 'name', 'Gun')}!")
        return 0
    else: # Weapon broken or invalid
        return 0

def apply_damage_to_target(target, damage, attacker_name="Attacker"):
    """Applies damage to a target, considering defense."""
    if damage <= 0:
        print(f"   {attacker_name}'s attack has no effect.")
        return

    # Calculate target defense
    # Assuming target has get_health(), set_health(), get_equipped_armour() methods
    if hasattr(target, 'get_defence_points'): # Check if Hero-like
        defence = character_defence(target)
    elif hasattr(target, 'get_defence'): # Check if Enemy-like
        defence = npc_defence(target)
    else:
        defence = 0

    total_damage_taken = max(0, math.floor(damage - defence))

    # Apply damage to armor first if applicable
    equipped_armour_dict = None
    if hasattr(target, 'get_equipped_armour'):
        equipped_armour_dict = target.get_equipped_armour()

    if equipped_armour_dict and not is_item_broken(equipped_armour_dict):
        # Decrease armor durability when damage is taken
        # Using total_damage_taken as durability loss for simplicity
        if decrease_item_durability(equipped_armour_dict, total_damage_taken):
            print(f"   {get_item_property(equipped_armour_dict, 'name', 'Armor')} absorbs some damage.")
            if is_item_broken(equipped_armour_dict):
                 print(f"   {get_item_property(equipped_armour_dict, 'name', 'Armor')} is now broken!")

    # Apply damage to health
    # Assuming target has get_health() and set_health() methods
    current_hp = target.get_health()
    new_hp = current_hp - total_damage_taken
    target.set_health(new_hp)

    print(f"   {target.get_name()} takes {total_damage_taken} damage.")
    if new_hp <= 0:
        print(f"   {target.get_name()} has been defeated!")


def enemy_attack(character_var, enemy_var):
    """Handles the enemy's attack turn."""
    print('------------------------------')
    print(f"{enemy_var.get_name()} attacks!")

    # Determine attack type (basic logic)
    use_gun = False
    equipped_gun_dict = None
    if hasattr(enemy_var, 'get_equipped_gun'):
        equipped_gun_dict = enemy_var.get_equipped_gun()
        # --- TEMPORARY PLACEHOLDER for ammo check ---
        if equipped_gun_dict and equipped_gun_dict.get('current_ammo', get_item_attribute(equipped_gun_dict, 'clip_size', 0)) > 0:
            if hasattr(enemy_var, 'get_gun_skill') and enemy_var.get_gun_skill() > enemy_var.get_strength():
                use_gun = True
        # --- END PLACEHOLDER ---

    if use_gun and equipped_gun_dict:
        print(f"   {enemy_var.get_name()} fires their {get_item_property(equipped_gun_dict, 'name', 'Gun')}!")
        if random.randint(0, 6) < enemy_var.get_luck():
            hit_damage = calculate_gun_hit(enemy_var, equipped_gun_dict)
            apply_damage_to_target(character_var, hit_damage, enemy_var.get_name())
        else:
            print("   Fortunately, they missed!")
            calculate_gun_hit(enemy_var, equipped_gun_dict) # Consume ammo/durability on miss
    else:
        # Melee attack
        equipped_melee_dict = None
        if hasattr(enemy_var, 'get_equipped_melee'):
            equipped_melee_dict = enemy_var.get_equipped_melee()

        if equipped_melee_dict:
             print(f"   {enemy_var.get_name()} strikes with their {get_item_property(equipped_melee_dict, 'name', 'Weapon')}!")
        else:
             print(f"   {enemy_var.get_name()} attacks with brute force!")

        hit_damage = calculate_melee_hit(enemy_var, equipped_melee_dict)
        apply_damage_to_target(character_var, hit_damage, enemy_var.get_name())

    # Display character's current health
    print('------------------------------')
    # Assuming character_var has get_health_points() and get_hp_limit()
    if character_var.get_health_points() > 0:
        print(f"Your current Health is now {character_var.get_health_points()}/{character_var.get_hp_limit()}")
    else:
        game_over(character_var)


def enemy_defeat(character_var, enemy_var):
    """Handles logic when an enemy is defeated."""
    print('------------------------------')
    print(f"You defeated {enemy_var.get_name()}!")

    # Calculate EXP gain
    base_exp = enemy_var.get_strength() + enemy_var.get_defence()
    if hasattr(enemy_var, 'get_gun_skill'):
        base_exp += enemy_var.get_gun_skill()
    luck_bonus = random.randint(0, 10) if random.randint(0, 10) < character_var.get_luck() else 0
    exp_gained = math.ceil(base_exp + luck_bonus)

    print(f"You gained {exp_gained} experience points.")
    # Assuming character_var has get_exp() and set_exp()
    character_var.set_exp(character_var.get_exp() + exp_gained)
    lvl_system.level_up(character_var)

    # Handle Loot
    # Placeholder: Call old loot function for now
    # This needs updating to handle item dictionaries
    # add_loot(enemy_var)
    inventory.loot_add(character_var, enemy_var)


def battle_state(character_var, enemy_var, surprise=False, range_attack=True):
    """Manages the main battle loop."""
    print("\n===== BATTLE START =====")
    print(f"You encounter {enemy_var.get_name()}!")
    print(f"Your Health: {character_var.get_health_points()}/{character_var.get_hp_limit()}")
    print(f"{enemy_var.get_name()}'s Health: {enemy_var.get_health()}")
    print("========================")

    if surprise:
        print("\nYou were surprised!")
        enemy_attack(character_var, enemy_var)
        if character_var.get_health_points() <= 0: return

    while enemy_var.get_health() > 0 and character_var.get_health_points() > 0:
        print('------------------------------')
        print("Choose your action:")
        options = ["Melee Attack", "Gun Attack", "Inventory", "Flee"]
        for i, opt in enumerate(options):
            print(f"{i+1}. {opt}")
        action_choice = input("> ")

        # --- Player Turn ---
        action_taken = False

        if action_choice == "1" or "melee" in action_choice.lower():
            action_taken = True
            print("\n>> Player Turn: Melee Attack <<")
            equipped_melee_dict = character_var.get_equipped_melee() # Should return dict or None

            if equipped_melee_dict is None:
                 print("   You attack unarmed!")
                 hit_damage = calculate_melee_hit(character_var, None) # Pass None for unarmed
            elif is_item_broken(equipped_melee_dict):
                print(f"   Your {get_item_property(equipped_melee_dict, 'name', 'Weapon')} is broken!")
                hit_damage = 0 # No damage if broken
            else:
                print(f"   You attack with {get_item_property(equipped_melee_dict, 'name', 'Weapon')}!")
                # --- DEBUG PRINT ---
                print(f"DEBUG: Melee Weapon: {get_item_property(equipped_melee_dict, 'name', 'N/A')}, "
                      f"Damage Attr: {get_item_attribute(equipped_melee_dict, 'damage', 'N/A')}, "
                      f"Current Dur: {get_item_property(equipped_melee_dict, 'current_durability', 'N/A')}")
                # ------------------
                hit_damage = calculate_melee_hit(character_var, equipped_melee_dict)

            apply_damage_to_target(enemy_var, hit_damage, character_var.get_name())


        elif action_choice == "2" or "gun" in action_choice.lower():
            action_taken = True
            print("\n>> Player Turn: Gun Attack <<")
            equipped_gun_dict = character_var.get_equipped_gun() # Should return dict or None

            if equipped_gun_dict is None:
                print("   You don't have a gun equipped!")
            elif is_item_broken(equipped_gun_dict):
                print(f"   Your {get_item_property(equipped_gun_dict, 'name', 'Gun')} is broken!")
            # --- TEMPORARY PLACEHOLDER for ammo check ---
            elif equipped_gun_dict.get('current_ammo', get_item_attribute(equipped_gun_dict, 'clip_size', 0)) <= 0:
                 print(f"   Your {get_item_property(equipped_gun_dict, 'name', 'Gun')} is out of ammo!")
            # --- END PLACEHOLDER ---
            else:
                 print(f"   You fire your {get_item_property(equipped_gun_dict, 'name', 'Gun')}!")
                 # --- DEBUG PRINT ---
                 print(f"DEBUG: Gun: {get_item_property(equipped_gun_dict, 'name', 'N/A')}, "
                       f"Damage Attr: {get_item_attribute(equipped_gun_dict, 'damage', 'N/A')}, "
                       f"Current Dur: {get_item_property(equipped_gun_dict, 'current_durability', 'N/A')}, "
                       f"Ammo: {equipped_gun_dict.get('current_ammo', 'N/A')}") # Placeholder ammo
                 # ------------------
                 if random.randint(0, 6) < character_var.get_luck():
                     hit_damage = calculate_gun_hit(character_var, equipped_gun_dict, shots=1)
                     apply_damage_to_target(enemy_var, hit_damage, character_var.get_name())
                 else:
                     print("   Your shot missed!")
                     calculate_gun_hit(character_var, equipped_gun_dict, shots=1) # Consume ammo/durability

        elif action_choice == "3" or "inventory" in action_choice.lower():
            action_taken = True
            print("\n>> Player Turn: Access Inventory <<")
            inventory.inventory(character_var)

        elif action_choice == "4" or "flee" in action_choice.lower():
            action_taken = True
            print("\n>> Player Turn: Attempt to Flee <<")
            if random.randint(0, 10) + character_var.get_luck() > 8:
                print("   You successfully escaped the battle!")
                print("===== BATTLE END =====")
                return
            else:
                print("   You couldn't escape!")
                print("   The enemy attacks as you try to run!")
                enemy_attack(character_var, enemy_var)

        else:
            print("Invalid action choice. Please try again.")

        # Check if Enemy Defeated
        if enemy_var.get_health() <= 0:
            enemy_defeat(character_var, enemy_var)
            print("===== BATTLE END =====")
            break

        # Enemy Turn (if player didn't flee or use inventory)
        if action_taken and not (action_choice == "3" or "inventory" in action_choice.lower()):
             if character_var.get_health_points() > 0:
                print("\n>> Enemy Turn <<")
                enemy_attack(character_var, enemy_var)

        # Check if Player Defeated
        if character_var.get_health_points() <= 0:
            print("===== BATTLE END =====")
            # game_over handling is tricky here, might be called inside enemy_attack
            # Or we can call it explicitly after the loop if player health <= 0
            break

    # After battle loop ends
    print('------------------------------')
    if character_var.get_health_points() > 0 and enemy_var.get_health() <= 0:
         print("You are victorious!")
    elif character_var.get_health_points() <= 0:
         print("You have fallen in battle.")
         game_over(character_var) # Call game_over if player was defeated
    print(f"Your final health: {character_var.get_health_points()}/{character_var.get_hp_limit()}")
    print(f"Your current Score is {character_var.get_exp()}")