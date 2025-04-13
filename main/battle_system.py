import random
import math
import sys
import datetime
import inventory 
import lvl_system
import hero 
import os 
from NPC import Enemy 
from ItemUtil import (
    get_item_attribute, get_item_property,
    decrease_item_durability, is_item_broken,
    get_gun_ammo, set_gun_ammo
)
import logging
logger = logging.getLogger(__name__)

# TODO: critical hit concept
# TODO: add a view stats options durring battle
# TODO: gun damage should be based soley on range/surprise and gun skill

def write_score(score, name):
    """Appends the player's name, score, and current date to the score file using a robust relative path."""
    try:
        script_dir = os.path.dirname(__file__) 
        score_file_path = os.path.abspath(os.path.join(script_dir, "..", "score.txt"))
    except NameError:
        score_file_path = "../score.txt"
        logger.warning("__file__ not found, falling back to relative path '%s' for score file.", score_file_path)

    try:
        now = datetime.datetime.now()
        date_str = now.strftime("%m/%d/%y")
        line_to_write = f"{name},{score},{date_str}\n"
        logger.info("Attempting to write score to calculated path: %s", score_file_path)
        with open(score_file_path, "a") as file:
             file.write(line_to_write)
        logger.info("Successfully wrote score for %s to %s", name, score_file_path)

    except IOError as e:
        logger.error("IOError writing score file '%s': %s", score_file_path, e)
        print(f"Error writing to score file: {e}") 
    except Exception as e:
        logger.exception("Unexpected error writing score file '%s':", score_file_path) 
        print(f"An unexpected error occurred saving the score.") 


def display_score():
    """Reads scores from file using robust relative path, sorts them, and displays a ranked list."""
    scores = []
    try:
        script_dir = os.path.dirname(__file__)
        score_file_path = os.path.abspath(os.path.join(script_dir, "..", "score.txt"))
    except NameError:
        score_file_path = "../score.txt"
        logger.warning("__file__ not found, falling back to relative path '%s' for score file.", score_file_path)

    try:
        logger.info("Attempting to read scores from: %s", score_file_path)
        with open(score_file_path, "r") as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line: 
                    continue
                try:
                    parts = line.split(',')
                    if len(parts) == 3:
                        name = parts[0].strip() 
                        score_str = parts[1].strip()
                        date_str = parts[2].strip()
                        score_int = int(score_str)
                        scores.append({'name': name, 'score': score_int, 'date': date_str})
                    else:
                        logger.warning("Skipping malformed score line #%d (expected 3 parts, found %d): %s",
                                     line_num, len(parts), line)

                except ValueError:
                    logger.warning("Skipping score line #%d with invalid score value: %s", line_num, line)
                except Exception as e:
                    logger.error("Error processing score line #%d '%s': %s", line_num, line, e)

    except FileNotFoundError:
        logger.info("Score file not found at %s. No scores to display.", score_file_path)
        print("No scores recorded yet.")
        return 
    except Exception as e:
         logger.exception("Unexpected error reading score file '%s':", score_file_path)
         print(f"Error reading score file.") 
         return

    scores.sort(key=lambda item: item['score'], reverse=True)

    print("\n--- HIGH SCORES ---")
    print(f"{'Rank':>4} | {'Score':>6} | {'Name':<12} | {'Date':<8}")
    print("-" * 37) 
    max_scores_to_show = 10 
    for i, entry in enumerate(scores[:max_scores_to_show]):
        rank = i + 1
        print(f"{rank:>4} | {entry['score']:>6} | {entry['name']:<12} | {entry['date']:<8}")
    print("-" * 37) 

def game_over(character_var):
    score = character_var.get_exp()
    if character_var.get_health_points() <= 0:
        print("\nYou have been defeated.")
        print(f"Your Final score is {score}")
        name = input("Enter your Name: ")
        try:
            write_score(score, name)
            print(f"Score for {name} saved.")
        except Exception as e:
            print("Could not save score.")
        display_score()
        print("\nGame Over sequence complete.")
        return True
    else:
        logger.warning("game_over() called but player HP > 0.")
        return False 

def character_defence(character_var):
    """Calculates character's total defense."""
    base_defence = character_var.get_defence_points()
    equipped_armour_dict = character_var.get_equipped_armour()
    armour_defence = 0
    if equipped_armour_dict and not is_item_broken(equipped_armour_dict):  
        armour_defence = get_item_attribute(equipped_armour_dict, 'defense', default=0)  
    return base_defence + armour_defence

def npc_defence(enemy_var):
    """Calculates NPC's total defense."""
    base_defence = enemy_var.get_defence()
    equipped_armour_dict = None
    if hasattr(enemy_var, 'get_equipped_armour'):
        equipped_armour_dict = enemy_var.get_equipped_armour()
    armour_defence = 0
    if equipped_armour_dict and not is_item_broken(equipped_armour_dict):  
        armour_defence = get_item_attribute(equipped_armour_dict, 'defense', default=0)  
    return base_defence + armour_defence


def calculate_melee_hit(attacker, weapon_dict):
    """Calculates melee hit damage, decreases durability."""
    # Get attacker strength using the correct method
    strength = 0
    if hasattr(attacker, 'get_strength_attribute'): strength = attacker.get_strength_attribute()
    elif hasattr(attacker, 'get_strength'): strength = attacker.get_strength()
    else: print(f"Warning: Cannot get strength for attacker {attacker.get_name()}")

    weapon_damage = 0
    if weapon_dict and not is_item_broken(weapon_dict):  
        weapon_damage = get_item_attribute(weapon_dict, 'damage', default=0)  
        loss = get_item_property(weapon_dict, 'durability_loss_per_use', default=1)  
        if decrease_item_durability(weapon_dict, loss):  
             if is_item_broken(weapon_dict):  
                  print(f"   Your {get_item_property(weapon_dict, 'name', 'Melee Weapon')} broke!")  
    elif weapon_dict and is_item_broken(weapon_dict):  
         print(f"   Your {get_item_property(weapon_dict, 'name', 'Melee Weapon')} is broken!")  
         weapon_damage = 0

    if weapon_dict is None or is_item_broken(weapon_dict):  
        unarmed_damage = math.ceil(strength / 2)
        return unarmed_damage
    else:
        return strength + weapon_damage

def calculate_gun_hit(attacker, weapon_dict, shots=1):
    """Calculates gun hit damage, decreases ammo and durability."""
    gun_skill = attacker.get_gun_skill() if hasattr(attacker, 'get_gun_skill') else 0
    weapon_damage = 0
    current_ammo = get_gun_ammo(weapon_dict) 
    actual_shots = min(shots, current_ammo)

    if weapon_dict and not is_item_broken(weapon_dict) and actual_shots > 0:  
        weapon_damage = get_item_attribute(weapon_dict, 'damage', default=0)  

        set_gun_ammo(weapon_dict, current_ammo - actual_shots)  
        print(f"   ({get_gun_ammo(weapon_dict)} shots remaining in {get_item_property(weapon_dict, 'name', 'Gun')})")  

        loss = get_item_property(weapon_dict, 'durability_loss_per_use', default=1)  
        if decrease_item_durability(weapon_dict, loss * actual_shots):  
             if is_item_broken(weapon_dict):  
                  print(f"   Your {get_item_property(weapon_dict, 'name', 'Gun')} broke!")  

        return (gun_skill + weapon_damage) * actual_shots
    elif weapon_dict and actual_shots <= 0:
        print(f"   *Click* Out of ammo in {get_item_property(weapon_dict, 'name', 'Gun')}!")  
        return 0
    elif weapon_dict and is_item_broken(weapon_dict):  
        print(f"   Your {get_item_property(weapon_dict, 'name', 'Gun')} is broken!")  
        return 0
    else:
        return 0

def apply_damage_to_target(target, hit_damage, attacker_name="Attacker"):
    """Applies damage from a hit to a target, considering defense and armor."""
    if hit_damage <= 0:
        print(f"   {attacker_name}'s attack glances off harmlessly.")
        return

    defence = 0
    if hasattr(target, 'get_defence_points'): defence = character_defence(target)
    elif hasattr(target, 'get_defence'): defence = npc_defence(target)

    damage_after_defence = max(0, math.floor(hit_damage - defence))

    equipped_armour_dict = None
    if hasattr(target, 'get_equipped_armour'):
        equipped_armour_dict = target.get_equipped_armour()

    if equipped_armour_dict and not is_item_broken(equipped_armour_dict):  
        durability_damage = damage_after_defence
        if decrease_item_durability(equipped_armour_dict, durability_damage):  
            armor_name = get_item_property(equipped_armour_dict,'name','Armor')  
            print(f"   {target.get_name()}'s {armor_name} takes {durability_damage} impact damage.") # Adjusted message
            if is_item_broken(equipped_armour_dict):  
                 print(f"   {target.get_name()}'s {armor_name} broke!")

    final_damage_to_health = damage_after_defence

    current_hp = 0
    if hasattr(target, 'get_health_points'): current_hp = target.get_health_points()
    elif hasattr(target, 'get_health'): current_hp = target.get_health()

    new_hp = current_hp - final_damage_to_health

    set_hp_success = False
    if hasattr(target, 'set_health_points'):
        target.set_health_points(new_hp)
        set_hp_success = True
    elif hasattr(target, 'set_health'):
        target.set_health(new_hp)
        set_hp_success = True

    if set_hp_success:
        if final_damage_to_health > 0:
             print(f"   {target.get_name()} takes {final_damage_to_health} damage to health.")
        elif hit_damage > 0: # Only print 'no damage' if there was an actual hit attempt
             print(f"   {target.get_name()}'s defense blocked all health damage!")


def enemy_attack(character_var, enemy_var):
    """Handles the enemy's attack turn, using updated helpers."""
    print('------------------------------')
    print(f"{enemy_var.get_name()} attacks!")

    use_gun = False
    equipped_gun_dict = None
    if hasattr(enemy_var, 'get_equipped_gun'):
        equipped_gun_dict = enemy_var.get_equipped_gun()
        if equipped_gun_dict and get_gun_ammo(equipped_gun_dict) > 0 and not is_item_broken(equipped_gun_dict): 
            if hasattr(enemy_var, 'get_gun_skill'):
                 use_gun = True

    if use_gun and equipped_gun_dict:
        gun_name = get_item_property(equipped_gun_dict, 'name', 'Gun') 
        print(f"   {enemy_var.get_name()} fires their {gun_name}!")

        attacker_skill = enemy_var.get_gun_skill() if hasattr(enemy_var, 'get_gun_skill') else 0
        attacker_luck = enemy_var.get_luck() if hasattr(enemy_var, 'get_luck') else 0
        target_defense = character_defence(character_var)
        # TODO: Consider adding weapon accuracy later

        base_chance = 75  
        skill_bonus = attacker_skill * 2  
        defense_penalty = target_defense * 3 #
        luck_mod = attacker_luck 

        final_hit_chance = base_chance + skill_bonus - defense_penalty + luck_mod

        final_hit_chance = max(5, min(95, final_hit_chance))

        hit_roll = random.randint(1, 100)

        print(f"DEBUG: ENEMY Roll={hit_roll} vs Chance={final_hit_chance}% "
              f"(Base:{base_chance} Skill:{skill_bonus} DefPen:{defense_penalty} Luck:{luck_mod})")
      
        if hit_roll <= final_hit_chance:
            hit_damage = calculate_gun_hit(enemy_var, equipped_gun_dict)
            apply_damage_to_target(character_var, hit_damage, enemy_var.get_name())
        else:
            print("   Fortunately, they missed!")
            calculate_gun_hit(enemy_var, equipped_gun_dict)
    else:
        equipped_melee_dict = None
        if hasattr(enemy_var, 'get_equipped_melee'):
            equipped_melee_dict = enemy_var.get_equipped_melee()

        hit_damage = 0 
        if equipped_melee_dict and not is_item_broken(equipped_melee_dict):  
             print(f"   {enemy_var.get_name()} strikes with their {get_item_property(equipped_melee_dict, 'name', 'Weapon')}!")  
             hit_damage = calculate_melee_hit(enemy_var, equipped_melee_dict)
        elif equipped_melee_dict and is_item_broken(equipped_melee_dict):  
             print(f"   {enemy_var.get_name()}'s {get_item_property(equipped_melee_dict, 'name', 'Weapon')} is broken!")  
             hit_damage = calculate_melee_hit(enemy_var, None) # Attack unarmed if weapon broken
        else:
             print(f"   {enemy_var.get_name()} attacks with brute force!")
             hit_damage = calculate_melee_hit(enemy_var, None) # Unarmed attack

        apply_damage_to_target(character_var, hit_damage, enemy_var.get_name())

    print('------------------------------')
    if character_var.get_health_points() > 0:
        print(f"Your current Health is now {character_var.get_health_points()}/{character_var.get_hp_limit()}")
    # Game over check is primarily handled within the battle_state loop

def enemy_defeat(character_var, enemy_var):
    """Handles logic when an enemy is defeated."""
    print('------------------------------')
    print(f"You defeated {enemy_var.get_name()}!")

    base_exp = enemy_var.get_strength() + enemy_var.get_defence()
    if hasattr(enemy_var, 'get_gun_skill'): base_exp += enemy_var.get_gun_skill()
    luck_bonus = random.randint(0, 10) if random.randint(0, 10) < character_var.get_luck() else 0
    exp_gained = math.ceil(base_exp + luck_bonus)

    print(f"You gained {exp_gained} experience points.")
    character_var.set_exp(character_var.get_exp() + exp_gained)
    lvl_system.level_up(character_var)

    inventory.loot_add(character_var, enemy_var) # Assumes inventory.py is updated


def battle_state(character_var, enemy_var, surprise=False, range_attack=True):
    """Manages the main battle loop using data-driven items."""
    print("\n===== BATTLE START =====")
    print(f"You encounter {enemy_var.get_name()}!")
    print(f"Your Health: {character_var.get_health_points()}/{character_var.get_hp_limit()}")
    print(f"{enemy_var.get_name()}'s Health: {enemy_var.get_health()}")
    print("========================")

    if surprise:
        print("\nYou were surprised!")
        enemy_attack(character_var, enemy_var)
        if character_var.get_health_points() <= 0:
            print("===== BATTLE END =====")
            game_over(character_var)
            return

    while enemy_var.get_health() > 0 and character_var.get_health_points() > 0:
        print('------------------------------')
        print("Choose your action:")
        options = ["Melee Attack", "Gun Attack", "Inventory", "Flee"]
        for i, opt in enumerate(options): print(f"{i+1}. {opt}")
        action_choice = input("> ")

        action_taken = False

        if action_choice == "1" or "melee" in action_choice.lower():
            action_taken = True
            print("\n>> Player Turn: Melee Attack <<")
            equipped_melee_dict = character_var.get_equipped_melee()
            hit_damage = 0
            if equipped_melee_dict is None:
                 print("   You attack unarmed!")
                 hit_damage = calculate_melee_hit(character_var, None)
            elif is_item_broken(equipped_melee_dict):  
                print(f"   Your {get_item_property(equipped_melee_dict, 'name', 'Weapon')} is broken!")  
                hit_damage = calculate_melee_hit(character_var, None) # Attack unarmed if weapon broken
            else:
                print(f"   You attack with {get_item_property(equipped_melee_dict, 'name', 'Weapon')}!")  
                print(f"DEBUG: Melee Weapon: {get_item_property(equipped_melee_dict, 'name', 'N/A')}, "  
                      f"Damage Attr: {get_item_attribute(equipped_melee_dict, 'damage', 'N/A')}, "  
                      f"Current Dur: {get_item_property(equipped_melee_dict, 'current_durability', 'N/A')}")  
                hit_damage = calculate_melee_hit(character_var, equipped_melee_dict)

            apply_damage_to_target(enemy_var, hit_damage, character_var.get_name())

        elif action_choice == "2" or "gun" in action_choice.lower():
            action_taken = True
            print("\n>> Player Turn: Gun Attack <<")
            equipped_gun_dict = character_var.get_equipped_gun()

            if equipped_gun_dict is None:
                print("   You don't have a gun equipped!")
            elif is_item_broken(equipped_gun_dict): 
                print(f"   Your {get_item_property(equipped_gun_dict, 'name', 'Gun')} is broken!") 
            elif get_gun_ammo(equipped_gun_dict) <= 0:  
                print(f"   Your {get_item_property(equipped_gun_dict, 'name', 'Gun')} is out of ammo!")  
            else:
                 gun_name = get_item_property(equipped_gun_dict, 'name', 'Gun')  
                 print(f"   You fire your {gun_name}!")  
                 print(f"DEBUG: Gun: {gun_name}, "
                       f"Damage Attr: {get_item_attribute(equipped_gun_dict, 'damage', 'N/A')}, "  
                       f"Current Dur: {get_item_property(equipped_gun_dict, 'current_durability', 'N/A')}, "  
                       f"Ammo: {get_gun_ammo(equipped_gun_dict)}")  

                 attacker_skill = character_var.get_gun_skill()
                 attacker_luck = character_var.get_luck()
                 target_defense = npc_defence(enemy_var)
                 # TODO: Consider adding weapon accuracy attribute later if desired

                 base_chance = 75  
                 skill_bonus = attacker_skill * 2  
                 defense_penalty = target_defense * 3 
                 luck_mod = attacker_luck 

                 final_hit_chance = base_chance + skill_bonus - defense_penalty + luck_mod

                 final_hit_chance = max(5, min(95, final_hit_chance))

                 hit_roll = random.randint(1, 100)

                 print(f"DEBUG: Hit Chance Roll={hit_roll} vs Chance={final_hit_chance}% "
                       f"(Base:{base_chance} Skill:{skill_bonus} DefPen:{defense_penalty} Luck:{luck_mod})")
               
                 if hit_roll <= final_hit_chance:
                     print("   Your shot hit!")
                     hit_damage = calculate_gun_hit(character_var, equipped_gun_dict, shots=1)
                     apply_damage_to_target(enemy_var, hit_damage, character_var.get_name())
                 else:
                     print("   Your shot missed!")
                     calculate_gun_hit(character_var, equipped_gun_dict, shots=1)

        elif action_choice == "3" or "inventory" in action_choice.lower():
            print("\n>> Player Turn: Access Inventory <<")
            inventory.inventory(character_var)
            action_taken = False # Accessing inventory usually doesn't provoke enemy attack

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
                # Enemy attacks immediately after failed flee

        else:
            print("Invalid action choice. Please try again.")
            continue # Skip enemy turn

        # Check if Enemy Defeated
        if enemy_var.get_health() <= 0:
            enemy_defeat(character_var, enemy_var)
            print("===== BATTLE END =====")
            break

        # Enemy Turn (if player didn't flee, didn't use inventory, and is alive)
        if action_taken and character_var.get_health_points() > 0:
             print("\n>> Enemy Turn <<")
             enemy_attack(character_var, enemy_var)

        # Check if Player Defeated
        if character_var.get_health_points() <= 0:
            print("===== BATTLE END =====")
            game_over(character_var)
            break

    # After battle loop finishes
    print('------------------------------')
    # Final status print (can be refined)
    print(f"End of battle. Your health: {character_var.get_health_points()}/{character_var.get_hp_limit()}")
    print(f"Your current Score is {character_var.get_exp()}")