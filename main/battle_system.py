import random
import math
import sys
import datetime
# Use relative imports for modules within the 'main' package
from . import inventory
from . import lvl_system
from . import hero # Assuming hero class is needed for type hints maybe?
import os
from .NPC import Enemy # Assuming Enemy class is in NPC.py
from .ItemUtil import (
    get_item_attribute, get_item_property,
    decrease_item_durability, is_item_broken,
    get_gun_ammo, set_gun_ammo
)
import logging

# Get logger instance
logger = logging.getLogger(__name__)

# TODO: critical hit concept
# TODO: add a view stats options durring battle
# TODO: gun damage should be based soley on range/surprise and gun skill
# TODO: Combat difficulty balancing

def write_score(score, name):
    """Appends the player's name, score, and current date to the score file using a robust relative path."""
    try:
        # Try to determine the script's directory and go up one level for the score file
        script_dir = os.path.dirname(__file__)
        score_file_path = os.path.abspath(os.path.join(script_dir, "..", "score.txt"))
    except NameError:
        # Fallback if __file__ is not defined (e.g., in interactive mode)
        score_file_path = "../score.txt" # Assumes running from main directory relative to score.txt
        logger.warning("__file__ not found, falling back to relative path '%s' for score file.", score_file_path)

    try:
        now = datetime.datetime.now()
        date_str = now.strftime("%m/%d/%y") # Format date as MM/DD/YY
        line_to_write = f"{name},{score},{date_str}\n" # CSV format: Name,Score,Date
        logger.info("Attempting to write score to calculated path: %s", score_file_path)
        # Open file in append mode ('a')
        with open(score_file_path, "a") as file:
             file.write(line_to_write)
        logger.info("Successfully wrote score for %s to %s", name, score_file_path)

    except IOError as e:
        # Handle file system errors (permissions, disk full, etc.)
        logger.error("IOError writing score file '%s': %s", score_file_path, e)
        print(f"Error writing to score file: {e}")
    except Exception as e:
        # Catch any other unexpected errors during file writing
        logger.exception("Unexpected error writing score file '%s':", score_file_path)
        print(f"An unexpected error occurred saving the score.")


def display_score():
    """Reads scores from file using robust relative path, sorts them, and displays a ranked list."""
    scores = []
    try:
        # Determine score file path robustly
        script_dir = os.path.dirname(__file__)
        score_file_path = os.path.abspath(os.path.join(script_dir, "..", "score.txt"))
    except NameError:
        score_file_path = "../score.txt"
        logger.warning("__file__ not found, falling back to relative path '%s' for score file.", score_file_path)

    try:
        logger.info("Attempting to read scores from: %s", score_file_path)
        # Open file for reading ('r')
        with open(score_file_path, "r") as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip() # Remove leading/trailing whitespace
                if not line: # Skip empty lines
                    continue
                try:
                    # Split line by comma (assuming CSV format)
                    parts = line.split(',')
                    if len(parts) == 3: # Expect Name, Score, Date
                        name = parts[0].strip()
                        score_str = parts[1].strip()
                        date_str = parts[2].strip()
                        # Convert score to integer
                        score_int = int(score_str)
                        # Append data as a dictionary
                        scores.append({'name': name, 'score': score_int, 'date': date_str})
                    else:
                        # Log warning for lines that don't have exactly 3 parts
                        logger.warning("Skipping malformed score line #%d (expected 3 parts, found %d): %s",
                                     line_num, len(parts), line)

                except ValueError:
                    # Handle cases where score part is not a valid integer
                    logger.warning("Skipping score line #%d with invalid score value: %s", line_num, line)
                except Exception as e:
                    # Catch other potential errors during line processing
                    logger.error("Error processing score line #%d '%s': %s", line_num, line, e)

    except FileNotFoundError:
        # Handle case where score file doesn't exist yet
        logger.info("Score file not found at %s. No scores to display.", score_file_path)
        print("No scores recorded yet.")
        return # Exit function early if no file
    except Exception as e:
         # Catch other errors during file reading (permissions, etc.)
         logger.exception("Unexpected error reading score file '%s':", score_file_path)
         print(f"Error reading score file.")
         return # Exit function on error

    # Sort scores in descending order based on the 'score' value
    scores.sort(key=lambda item: item['score'], reverse=True)

    # Display the formatted high scores
    print("\n--- HIGH SCORES ---")
    print(f"{'Rank':>4} | {'Score':>6} | {'Name':<12} | {'Date':<8}") # Header
    print("-" * 37) # Separator line
    max_scores_to_show = 10 # Limit number of scores shown
    for i, entry in enumerate(scores[:max_scores_to_show]):
        rank = i + 1
        # Format each score entry
        print(f"{rank:>4} | {entry['score']:>6} | {entry['name']:<12} | {entry['date']:<8}")
    print("-" * 37) # Footer separator

def game_over(character_var):
    """Handles the game over sequence when player health reaches 0."""
    score = character_var.get_exp() # Get player's final score (experience)
    # Check if player health is actually zero or less
    if character_var.get_health_points() <= 0:
        print("\nYou have been defeated.")
        print(f"Your Final score is {score}")
        name = input("Enter your Name: ") # Prompt for player name
        try:
            write_score(score, name) # Attempt to save the score
            print(f"Score for {name} saved.")
        except Exception as e:
            # Inform user if score saving fails
            print("Could not save score.")
            # Log the error for debugging
            logger.error("Failed to write score for %s: %s", name, e)

        display_score() # Show the high scores table
        print("\nGame Over sequence complete.")
        return True # Indicate game over occurred
    else:
        # This function shouldn't be called if player isn't dead
        logger.warning("game_over() called but player HP > 0.")
        return False # Indicate game over did not occur

def character_defence(character_var):
    """Calculates character's total defense including equipped armor."""
    base_defence = character_var.get_defence_points() # Base stat
    equipped_armour_dict = character_var.get_equipped_armour() # Get equipped armor item dict
    armour_defence = 0
    # Check if armor is equipped and not broken
    if equipped_armour_dict and not is_item_broken(equipped_armour_dict):
        # Get 'defense' attribute from the armor's data
        armour_defence = get_item_attribute(equipped_armour_dict, 'defense', default=0)
    return base_defence + armour_defence # Return total defense

def npc_defence(enemy_var):
    """Calculates NPC's total defense including equipped armor."""
    # Ensure enemy_var has the get_defence method
    base_defence = enemy_var.get_defence() if hasattr(enemy_var, 'get_defence') else 0
    equipped_armour_dict = None
    # Check if the NPC object has the method to get equipped armor
    if hasattr(enemy_var, 'get_equipped_armour'):
        equipped_armour_dict = enemy_var.get_equipped_armour()
    armour_defence = 0
    # Check if armor is equipped and not broken
    if equipped_armour_dict and not is_item_broken(equipped_armour_dict):
        # Get 'defense' attribute from the armor's data
        armour_defence = get_item_attribute(equipped_armour_dict, 'defense', default=0)
    return base_defence + armour_defence # Return total defense


def calculate_melee_hit(attacker, weapon_dict):
    """Calculates melee hit damage based on strength and weapon, decreases weapon durability."""
    # Get attacker strength using appropriate method
    strength = 0
    if hasattr(attacker, 'get_strength_attribute'): strength = attacker.get_strength_attribute() # Player method
    elif hasattr(attacker, 'get_strength'): strength = attacker.get_strength() # NPC method
    else: logger.warning(f"Cannot get strength for attacker {getattr(attacker, 'get_name', lambda: 'Unknown')()}")

    weapon_damage = 0
    # Check if a weapon is equipped and not broken
    if weapon_dict and not is_item_broken(weapon_dict):
        weapon_damage = get_item_attribute(weapon_dict, 'damage', default=0) # Get weapon base damage
        # Decrease durability
        loss = get_item_property(weapon_dict, 'durability_loss_per_use', default=1)
        if decrease_item_durability(weapon_dict, loss):
             # Check if the weapon broke *after* this use
             if is_item_broken(weapon_dict):
                  # Use attacker's name if possible
                  attacker_name = getattr(attacker, 'get_name', lambda: 'Attacker')()
                  weapon_name = get_item_property(weapon_dict, 'name', 'Melee Weapon')
                  # Distinguish between player and NPC weapon breaking
                  if hasattr(attacker, 'get_strength_attribute'): # Is it the player?
                       print(f"   Your {weapon_name} broke!")
                  else:
                       print(f"   {attacker_name}'s {weapon_name} broke!")

    elif weapon_dict and is_item_broken(weapon_dict):
         # Inform if weapon is already broken
         attacker_name = getattr(attacker, 'get_name', lambda: 'Attacker')()
         weapon_name = get_item_property(weapon_dict, 'name', 'Melee Weapon')
         if hasattr(attacker, 'get_strength_attribute'):
              print(f"   Your {weapon_name} is broken!")
         else:
              print(f"   {attacker_name}'s {weapon_name} is broken!")
         weapon_damage = 0 # Broken weapon deals no damage

    # If no weapon or weapon broke, calculate unarmed damage
    if weapon_dict is None or is_item_broken(weapon_dict):
        unarmed_damage = math.ceil(strength / 2) # Unarmed damage based on strength
        return unarmed_damage
    else:
        # Total damage is strength + weapon damage
        return strength + weapon_damage

def calculate_gun_hit(attacker, weapon_dict, shots=1):
    """Calculates gun hit damage based on skill and weapon, decreases ammo and durability."""
    # Get attacker's gun skill (default to 0 if not applicable)
    gun_skill = attacker.get_gun_skill() if hasattr(attacker, 'get_gun_skill') else 0
    weapon_damage = 0
    current_ammo = get_gun_ammo(weapon_dict) # Get current ammo in the weapon
    # Determine actual shots fired (cannot exceed available ammo)
    actual_shots = min(shots, current_ammo)

    # Check if weapon exists, is not broken, and has ammo
    if weapon_dict and not is_item_broken(weapon_dict) and actual_shots > 0:
        weapon_damage = get_item_attribute(weapon_dict, 'damage', default=0) # Get weapon base damage

        # Decrease ammo and durability
        set_gun_ammo(weapon_dict, current_ammo - actual_shots) # Update ammo count
        print(f"   ({get_gun_ammo(weapon_dict)} shots remaining in {get_item_property(weapon_dict, 'name', 'Gun')})")
        loss = get_item_property(weapon_dict, 'durability_loss_per_use', default=1)
        if decrease_item_durability(weapon_dict, loss * actual_shots): # Decrease durability per shot
             if is_item_broken(weapon_dict): # Check if it broke
                  attacker_name = getattr(attacker, 'get_name', lambda: 'Attacker')()
                  weapon_name = get_item_property(weapon_dict, 'name', 'Gun')
                  if hasattr(attacker, 'get_gun_skill'): # Is it the player?
                       print(f"   Your {weapon_name} broke!")
                  else:
                       print(f"   {attacker_name}'s {weapon_name} broke!")


        # Total damage is (skill + weapon damage) multiplied by number of shots
        return (gun_skill + weapon_damage) * actual_shots
    elif weapon_dict and actual_shots <= 0:
        # Out of ammo message
        print(f"   *Click* Out of ammo in {get_item_property(weapon_dict, 'name', 'Gun')}!")
        return 0
    elif weapon_dict and is_item_broken(weapon_dict):
        # Broken gun message
        attacker_name = getattr(attacker, 'get_name', lambda: 'Attacker')()
        weapon_name = get_item_property(weapon_dict, 'name', 'Gun')
        if hasattr(attacker, 'get_gun_skill'):
             print(f"   Your {weapon_name} is broken!")
        else:
             print(f"   {attacker_name}'s {weapon_name} is broken!")
        return 0
    else:
        # Should not happen if checks are done before calling, but safety return
        return 0

def apply_damage_to_target(target, hit_damage, attacker_name="Attacker"):
    """Applies damage from a hit to a target, considering defense and armor durability."""
    if hit_damage <= 0:
        # No damage dealt
        print(f"   {attacker_name}'s attack glances off harmlessly.")
        return

    # Calculate target's total defense
    defence = 0
    if hasattr(target, 'get_defence_points'): defence = character_defence(target) # Player defense
    elif hasattr(target, 'get_defence'): defence = npc_defence(target) # NPC defense

    # Damage reduced by defense (minimum 0)
    damage_after_defence = max(0, math.floor(hit_damage - defence))

    # Apply damage to armor durability if armor is equipped and not broken
    equipped_armour_dict = None
    if hasattr(target, 'get_equipped_armour'):
        equipped_armour_dict = target.get_equipped_armour()

    if equipped_armour_dict and not is_item_broken(equipped_armour_dict):
        # Damage to armor is based on damage that got through base defense
        durability_damage = damage_after_defence # Apply full damage that gets through defense to armor
        if durability_damage > 0 and decrease_item_durability(equipped_armour_dict, durability_damage):
            armor_name = get_item_property(equipped_armour_dict,'name','Armor')
            target_name = getattr(target, 'get_name', lambda: 'Target')()
            print(f"   {target_name}'s {armor_name} absorbs {durability_damage} impact.") # Changed phrasing
            # Check if armor broke after taking damage
            if is_item_broken(equipped_armour_dict):
                 print(f"   {target_name}'s {armor_name} broke!")

    # Final damage to health is the damage after defense reduction
    final_damage_to_health = damage_after_defence

    # Get target's current health
    current_hp = 0
    if hasattr(target, 'get_health_points'): current_hp = target.get_health_points() # Player HP
    elif hasattr(target, 'get_health'): current_hp = target.get_health() # NPC HP

    # Calculate new health
    new_hp = current_hp - final_damage_to_health

    # Set target's new health using appropriate method
    set_hp_success = False
    if hasattr(target, 'set_health_points'): target.set_health_points(new_hp); set_hp_success = True # Player
    elif hasattr(target, 'set_health'): target.set_health(new_hp); set_hp_success = True # NPC

    # Print damage message
    if set_hp_success:
        target_name = getattr(target, 'get_name', lambda: 'Target')()
        if final_damage_to_health > 0:
             print(f"   {target_name} takes {final_damage_to_health} damage to health.")
        elif hit_damage > 0: # Only print 'blocked' if there was potential damage
             print(f"   {target_name}'s defense blocked all health damage!")


def enemy_attack(character_var, enemy_var):
    """Handles the enemy's attack turn, choosing between gun and melee."""
    print('------------------------------')
    enemy_name = getattr(enemy_var, 'get_name', lambda: 'Enemy')()
    print(f"{enemy_name} attacks!")

    # Determine if enemy should use gun
    use_gun = False
    equipped_gun_dict = None
    if hasattr(enemy_var, 'get_equipped_gun'):
        equipped_gun_dict = enemy_var.get_equipped_gun()
        # Check if gun equipped, has ammo, not broken, and enemy has gun skill
        if equipped_gun_dict and get_gun_ammo(equipped_gun_dict) > 0 and not is_item_broken(equipped_gun_dict):
            if hasattr(enemy_var, 'get_gun_skill'):
                 use_gun = True

    # --- Gun Attack Logic ---
    if use_gun and equipped_gun_dict:
        gun_name = get_item_property(equipped_gun_dict, 'name', 'Gun')
        print(f"   {enemy_name} fires their {gun_name}!")

        # Get relevant stats for hit calculation
        attacker_skill = enemy_var.get_gun_skill() if hasattr(enemy_var, 'get_gun_skill') else 0
        attacker_luck = enemy_var.get_luck() if hasattr(enemy_var, 'get_luck') else 0
        target_defense = character_defence(character_var) # Player's defense

        # --- Hit Chance Calculation (Example) ---
        base_chance = 75; skill_bonus = attacker_skill * 2; defense_penalty = target_defense * 3; luck_mod = attacker_luck
        final_hit_chance = max(5, min(95, base_chance + skill_bonus - defense_penalty + luck_mod))
        hit_roll = random.randint(1, 100)
        logger.debug(f"ENEMY Roll={hit_roll} vs Chance={final_hit_chance}% (Base:{base_chance} Skill:{skill_bonus} DefPen:{defense_penalty} Luck:{luck_mod})")

        if hit_roll <= final_hit_chance:
            hit_damage = calculate_gun_hit(enemy_var, equipped_gun_dict)
            apply_damage_to_target(character_var, hit_damage, enemy_name)
        else:
            print("   Fortunately, they missed!")
            calculate_gun_hit(enemy_var, equipped_gun_dict) # Still consumes ammo/durability on miss

    # --- Melee Attack Logic (if not using gun) ---
    else:
        equipped_melee_dict = None
        if hasattr(enemy_var, 'get_equipped_melee'):
            equipped_melee_dict = enemy_var.get_equipped_melee()

        hit_damage = 0
        if equipped_melee_dict and not is_item_broken(equipped_melee_dict):
             print(f"   {enemy_name} strikes with their {get_item_property(equipped_melee_dict, 'name', 'Weapon')}!")
             hit_damage = calculate_melee_hit(enemy_var, equipped_melee_dict)
        elif equipped_melee_dict and is_item_broken(equipped_melee_dict):
             print(f"   {enemy_name}'s {get_item_property(equipped_melee_dict, 'name', 'Weapon')} is broken!")
             hit_damage = calculate_melee_hit(enemy_var, None) # Attack unarmed
        else:
             print(f"   {enemy_name} attacks with brute force!")
             hit_damage = calculate_melee_hit(enemy_var, None)

        apply_damage_to_target(character_var, hit_damage, enemy_name)

    # Display player's current health after the attack
    print('------------------------------')
    if character_var.get_health_points() > 0:
        print(f"Your current Health is now {character_var.get_health_points()}/{character_var.get_hp_limit()}")


def enemy_defeat(character_var, enemy_var):
    """Handles logic when an enemy is defeated: EXP gain, level up, looting."""
    enemy_name = getattr(enemy_var, 'get_name', lambda: 'Enemy')()
    print('------------------------------')
    print(f"You defeated {enemy_name}!")

    # --- Calculate Experience Points ---
    base_exp = (getattr(enemy_var, 'get_strength', lambda: 0)() +
                getattr(enemy_var, 'get_defence', lambda: 0)())
    if hasattr(enemy_var, 'get_gun_skill'): base_exp += enemy_var.get_gun_skill()
    luck_bonus = random.randint(0, 10) if random.randint(0, 10) < character_var.get_luck() else 0
    exp_gained = math.ceil(base_exp + luck_bonus)

    print(f"You gained {exp_gained} experience points.")
    character_var.set_exp(character_var.get_exp() + exp_gained)
    lvl_system.level_up(character_var)

    # --- Handle Looting ---
    inventory.loot_add(character_var, enemy_var)


def battle_state(character_var, enemy_var, surprise=False, range_attack=True):
    """
    Manages the main battle loop.

    Args:
        character_var: The player character object.
        enemy_var: The enemy NPC object.
        surprise (bool): If True, the enemy gets the first attack.
        range_attack (bool): Placeholder, might influence starting distance/options later.

    Returns:
        dict: A dictionary indicating the battle outcome.
              Keys: 'status' ('enemy_defeated', 'player_defeated', 'fled', 'error')
                    'defeated_npc_object' (optional, the enemy object if defeated)
    """
    enemy_name = getattr(enemy_var, 'get_name', lambda: 'Enemy')() # Get name safely
    print("\n===== BATTLE START =====")
    print(f"You encounter {enemy_name}!")
    print(f"Your Health: {character_var.get_health_points()}/{character_var.get_hp_limit()}")
    # Ensure enemy_var has get_health method
    enemy_hp = getattr(enemy_var, 'get_health', lambda: 0)()
    print(f"{enemy_name}'s Health: {enemy_hp}")
    print("========================")

    battle_outcome = {"status": "error"} # Default outcome status

    # --- Handle Surprise Attack ---
    if surprise:
        print("\nYou were surprised!")
        enemy_attack(character_var, enemy_var) # Enemy attacks first
        if character_var.get_health_points() <= 0:
            print("===== BATTLE END =====")
            if game_over(character_var): battle_outcome = {"status": "player_defeated"}
            return battle_outcome # Return immediately

    # --- Main Battle Loop ---
    while getattr(enemy_var, 'get_health', lambda: 0)() > 0 and character_var.get_health_points() > 0:
        print('------------------------------')
        print("Choose your action:")
        options = ["Melee Attack", "Gun Attack", "Inventory", "Flee"]
        for i, opt in enumerate(options): print(f"{i+1}. {opt}")
        action_choice = input("> ")

        action_taken = False

        # --- Player Action: Melee Attack ---
        if action_choice == "1" or "melee" in action_choice.lower():
            action_taken = True; print("\n>> Player Turn: Melee Attack <<")
            equipped_melee_dict = character_var.get_equipped_melee()
            hit_damage = 0
            if equipped_melee_dict is None: print("   You attack unarmed!"); hit_damage = calculate_melee_hit(character_var, None)
            elif is_item_broken(equipped_melee_dict): print(f"   Your {get_item_property(equipped_melee_dict, 'name', 'Weapon')} is broken!"); hit_damage = calculate_melee_hit(character_var, None)
            else: print(f"   You attack with {get_item_property(equipped_melee_dict, 'name', 'Weapon')}!"); logger.debug(f"Melee: {get_item_property(equipped_melee_dict, 'name', 'N/A')}, Dmg: {get_item_attribute(equipped_melee_dict, 'damage', 'N/A')}, Dur: {get_item_property(equipped_melee_dict, 'current_durability', 'N/A')}"); hit_damage = calculate_melee_hit(character_var, equipped_melee_dict)
            apply_damage_to_target(enemy_var, hit_damage, character_var.get_name())

        # --- Player Action: Gun Attack ---
        elif action_choice == "2" or "gun" in action_choice.lower():
            action_taken = True; print("\n>> Player Turn: Gun Attack <<")
            equipped_gun_dict = character_var.get_equipped_gun()
            if equipped_gun_dict is None: print("   You don't have a gun equipped!")
            elif is_item_broken(equipped_gun_dict): print(f"   Your {get_item_property(equipped_gun_dict, 'name', 'Gun')} is broken!")
            elif get_gun_ammo(equipped_gun_dict) <= 0: print(f"   Your {get_item_property(equipped_gun_dict, 'name', 'Gun')} is out of ammo!")
            else:
                 gun_name = get_item_property(equipped_gun_dict, 'name', 'Gun'); print(f"   You fire your {gun_name}!")
                 logger.debug(f"Gun: {gun_name}, Dmg: {get_item_attribute(equipped_gun_dict, 'damage', 'N/A')}, Dur: {get_item_property(equipped_gun_dict, 'current_durability', 'N/A')}, Ammo: {get_gun_ammo(equipped_gun_dict)}")
                 attacker_skill = character_var.get_gun_skill(); attacker_luck = character_var.get_luck(); target_defense = npc_defence(enemy_var)
                 base_chance = 75; skill_bonus = attacker_skill * 2; defense_penalty = target_defense * 3; luck_mod = attacker_luck
                 final_hit_chance = max(5, min(95, base_chance + skill_bonus - defense_penalty + luck_mod))
                 hit_roll = random.randint(1, 100); logger.debug(f"Hit Roll={hit_roll} vs Chance={final_hit_chance}% (B:{base_chance} S:{skill_bonus} D:{defense_penalty} L:{luck_mod})")
                 if hit_roll <= final_hit_chance: print("   Your shot hit!"); hit_damage = calculate_gun_hit(character_var, equipped_gun_dict, shots=1); apply_damage_to_target(enemy_var, hit_damage, character_var.get_name())
                 else: print("   Your shot missed!"); calculate_gun_hit(character_var, equipped_gun_dict, shots=1)

        # --- Player Action: Inventory ---
        elif action_choice == "3" or "inventory" in action_choice.lower():
            print("\n>> Player Turn: Access Inventory <<"); inventory.inventory(character_var); action_taken = False

        # --- Player Action: Flee ---
        elif action_choice == "4" or "flee" in action_choice.lower():
            action_taken = True; print("\n>> Player Turn: Attempt to Flee <<")
            if random.randint(0, 10) + character_var.get_luck() > 8: # Adjust flee logic as needed
                print("   You successfully escaped!"); print("===== BATTLE END =====")
                battle_outcome = {"status": "fled"}; return battle_outcome # <<< RETURN: Player fled
            else: print("   You couldn't escape!")

        # --- Invalid Action ---
        else: print("Invalid action choice."); continue

        # --- Check if Enemy Defeated ---
        if getattr(enemy_var, 'get_health', lambda: 0)() <= 0:
            enemy_defeat(character_var, enemy_var)
            print("===== BATTLE END =====")
            battle_outcome = {"status": "enemy_defeated", "defeated_npc_object": enemy_var}
            return battle_outcome # <<< RETURN: Enemy defeated

        # --- Enemy Turn ---
        if action_taken and character_var.get_health_points() > 0:
             print("\n>> Enemy Turn <<"); enemy_attack(character_var, enemy_var)

        # --- Check if Player Defeated ---
        if character_var.get_health_points() <= 0:
            print("===== BATTLE END =====")
            if game_over(character_var): battle_outcome = {"status": "player_defeated"}
            return battle_outcome # <<< RETURN: Player defeated

    # --- Loop Exit ---
    logger.error("Battle loop exited unexpectedly.")
    print('------------------------------')
    print(f"End of battle. Your health: {character_var.get_health_points()}/{character_var.get_hp_limit()}")
    print(f"Your current Score is {character_var.get_exp()}")
    return battle_outcome # <<< RETURN: Default error status
