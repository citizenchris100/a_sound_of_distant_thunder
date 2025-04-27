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
# <<< Import flag functions from dialog_system >>>
# Note: This creates a dependency. Ideally, flag/state management
# would be in a separate, shared module later.
from .dialog_system import _set_flag, _get_flag
import logging

# Get logger instance
logger = logging.getLogger(__name__)

# TODO: critical hit concept
# TODO: add a view stats options durring battle
# TODO: gun damage should be based soley on range/surprise and gun skill
# TODO: Combat difficulty balancing
# TODO: More sophisticated multi-enemy turn management (initiative?)

def write_score(score, name):
    """Appends the player's name, score, and current date to the score file using a robust relative path."""
    try:
        script_dir = os.path.dirname(__file__)
        score_file_path = os.path.abspath(os.path.join(script_dir, "..", "score.txt"))
    except NameError:
        score_file_path = "../score.txt"
        logger.warning("__file__ not found, falling back to relative path '%s' for score file.", score_file_path)
    try:
        now = datetime.datetime.now(); date_str = now.strftime("%m/%d/%y")
        line_to_write = f"{name},{score},{date_str}\n"
        logger.info("Attempting to write score to: %s", score_file_path)
        with open(score_file_path, "a") as file: file.write(line_to_write)
        logger.info("Successfully wrote score for %s to %s", name, score_file_path)
    except IOError as e: logger.error("IOError writing score file '%s': %s", score_file_path, e); print(f"Error writing score file: {e}")
    except Exception as e: logger.exception("Unexpected error writing score file '%s':", score_file_path); print(f"Unexpected error saving score.")

def display_score():
    """Reads scores from file, sorts them, and displays a ranked list."""
    scores = []
    try:
        script_dir = os.path.dirname(__file__); score_file_path = os.path.abspath(os.path.join(script_dir, "..", "score.txt"))
    except NameError: score_file_path = "../score.txt"; logger.warning("__file__ not found, fallback path '%s'.", score_file_path)
    try:
        logger.info("Attempting to read scores from: %s", score_file_path)
        with open(score_file_path, "r") as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip();
                if not line: continue
                try:
                    parts = line.split(',');
                    if len(parts) == 3: name = parts[0].strip(); score_str = parts[1].strip(); date_str = parts[2].strip(); score_int = int(score_str); scores.append({'name': name, 'score': score_int, 'date': date_str})
                    else: logger.warning("Skipping malformed score line #%d: %s", line_num, line)
                except ValueError: logger.warning("Skipping score line #%d invalid score: %s", line_num, line)
                except Exception as e: logger.error("Error processing score line #%d '%s': %s", line_num, line, e)
    except FileNotFoundError: logger.info("Score file not found: %s.", score_file_path); print("No scores recorded yet."); return
    except Exception as e: logger.exception("Unexpected error reading score file '%s':", score_file_path); print(f"Error reading score file."); return
    scores.sort(key=lambda item: item['score'], reverse=True)
    print("\n--- HIGH SCORES ---"); print(f"{'Rank':>4} | {'Score':>6} | {'Name':<12} | {'Date':<8}"); print("-" * 37)
    for i, entry in enumerate(scores[:10]): rank = i + 1; print(f"{rank:>4} | {entry['score']:>6} | {entry['name']:<12} | {entry['date']:<8}")
    print("-" * 37)

def game_over(character_var):
    """Handles the game over sequence when player health reaches 0."""
    score = character_var.get_exp()
    if character_var.get_health_points() <= 0:
        print("\nYou have been defeated."); print(f"Your Final score is {score}")
        try: name = input("Enter your Name: ")
        except EOFError: name = "Player" # Handle potential EOF on input
        try: write_score(score, name); print(f"Score for {name} saved.")
        except Exception as e: print("Could not save score."); logger.error("Failed to write score for %s: %s", name, e)
        display_score(); print("\nGame Over sequence complete."); return True
    else: logger.warning("game_over() called but player HP > 0."); return False

def character_defence(character_var):
    """Calculates character's total defense including equipped armor."""
    base_defence = character_var.get_defence_points(); equipped_armour_dict = character_var.get_equipped_armour(); armour_defence = 0
    if equipped_armour_dict and not is_item_broken(equipped_armour_dict): armour_defence = get_item_attribute(equipped_armour_dict, 'defense', default=0)
    return base_defence + armour_defence

def npc_defence(enemy_var):
    """Calculates NPC's total defense including equipped armor."""
    base_defence = enemy_var.get_defence() if hasattr(enemy_var, 'get_defence') else 0; equipped_armour_dict = None
    if hasattr(enemy_var, 'get_equipped_armour'): equipped_armour_dict = enemy_var.get_equipped_armour()
    armour_defence = 0
    if equipped_armour_dict and not is_item_broken(equipped_armour_dict): armour_defence = get_item_attribute(equipped_armour_dict, 'defense', default=0)
    return base_defence + armour_defence

def calculate_melee_hit(attacker, weapon_dict):
    """Calculates melee hit damage based on strength and weapon, decreases weapon durability."""
    strength = 0
    if hasattr(attacker, 'get_strength_attribute'): strength = attacker.get_strength_attribute()
    elif hasattr(attacker, 'get_strength'): strength = attacker.get_strength()
    else: logger.warning(f"Cannot get strength for attacker {getattr(attacker, 'get_name', lambda: 'Unknown')()}")
    weapon_damage = 0
    if weapon_dict and not is_item_broken(weapon_dict):
        weapon_damage = get_item_attribute(weapon_dict, 'damage', default=0)
        loss = get_item_property(weapon_dict, 'durability_loss_per_use', default=1)
        if decrease_item_durability(weapon_dict, loss) and is_item_broken(weapon_dict):
             attacker_name = getattr(attacker, 'get_name', lambda: 'Attacker')(); weapon_name = get_item_property(weapon_dict, 'name', 'Melee Weapon')
             msg = f"Your {weapon_name} broke!" if hasattr(attacker, 'get_strength_attribute') else f"{attacker_name}'s {weapon_name} broke!"
             print(f"   {msg}")
    elif weapon_dict and is_item_broken(weapon_dict):
         attacker_name = getattr(attacker, 'get_name', lambda: 'Attacker')(); weapon_name = get_item_property(weapon_dict, 'name', 'Melee Weapon')
         msg = f"Your {weapon_name} is broken!" if hasattr(attacker, 'get_strength_attribute') else f"{attacker_name}'s {weapon_name} is broken!"
         print(f"   {msg}"); weapon_damage = 0
    if weapon_dict is None or is_item_broken(weapon_dict): return math.ceil(strength / 2)
    else: return strength + weapon_damage

def calculate_gun_hit(attacker, weapon_dict, shots=1):
    """Calculates gun hit damage based on skill and weapon, decreases ammo and durability."""
    gun_skill = attacker.get_gun_skill() if hasattr(attacker, 'get_gun_skill') else 0; weapon_damage = 0
    current_ammo = get_gun_ammo(weapon_dict); actual_shots = min(shots, current_ammo)
    if weapon_dict and not is_item_broken(weapon_dict) and actual_shots > 0:
        weapon_damage = get_item_attribute(weapon_dict, 'damage', default=0)
        set_gun_ammo(weapon_dict, current_ammo - actual_shots)
        print(f"   ({get_gun_ammo(weapon_dict)} shots remaining in {get_item_property(weapon_dict, 'name', 'Gun')})")
        loss = get_item_property(weapon_dict, 'durability_loss_per_use', default=1)
        if decrease_item_durability(weapon_dict, loss * actual_shots) and is_item_broken(weapon_dict):
             attacker_name = getattr(attacker, 'get_name', lambda: 'Attacker')(); weapon_name = get_item_property(weapon_dict, 'name', 'Gun')
             msg = f"Your {weapon_name} broke!" if hasattr(attacker, 'get_gun_skill') else f"{attacker_name}'s {weapon_name} broke!"
             print(f"   {msg}")
        return (gun_skill + weapon_damage) * actual_shots
    elif weapon_dict and actual_shots <= 0: print(f"   *Click* Out of ammo in {get_item_property(weapon_dict, 'name', 'Gun')}!"); return 0
    elif weapon_dict and is_item_broken(weapon_dict):
        attacker_name = getattr(attacker, 'get_name', lambda: 'Attacker')(); weapon_name = get_item_property(weapon_dict, 'name', 'Gun')
        msg = f"Your {weapon_name} is broken!" if hasattr(attacker, 'get_gun_skill') else f"{attacker_name}'s {weapon_name} is broken!"
        print(f"   {msg}"); return 0
    else: return 0

def apply_damage_to_target(target, hit_damage, attacker_name="Attacker"):
    """Applies damage from a hit to a target, considering defense and armor durability."""
    if hit_damage <= 0: print(f"   {attacker_name}'s attack glances off harmlessly."); return
    defence = 0
    if hasattr(target, 'get_defence_points'): defence = character_defence(target)
    elif hasattr(target, 'get_defence'): defence = npc_defence(target)
    damage_after_defence = max(0, math.floor(hit_damage - defence))
    equipped_armour_dict = None
    if hasattr(target, 'get_equipped_armour'): equipped_armour_dict = target.get_equipped_armour()
    if equipped_armour_dict and not is_item_broken(equipped_armour_dict):
        durability_damage = damage_after_defence
        if durability_damage > 0 and decrease_item_durability(equipped_armour_dict, durability_damage):
            armor_name = get_item_property(equipped_armour_dict,'name','Armor'); target_name = getattr(target, 'get_name', lambda: 'Target')()
            print(f"   {target_name}'s {armor_name} absorbs {durability_damage} impact.")
            if is_item_broken(equipped_armour_dict): print(f"   {target_name}'s {armor_name} broke!")
    final_damage_to_health = damage_after_defence
    current_hp = 0
    if hasattr(target, 'get_health_points'): current_hp = target.get_health_points()
    elif hasattr(target, 'get_health'): current_hp = target.get_health()
    new_hp = current_hp - final_damage_to_health
    set_hp_success = False
    if hasattr(target, 'set_health_points'): target.set_health_points(new_hp); set_hp_success = True
    elif hasattr(target, 'set_health'): target.set_health(new_hp); set_hp_success = True
    if set_hp_success:
        target_name = getattr(target, 'get_name', lambda: 'Target')()
        if final_damage_to_health > 0: print(f"   {target_name} takes {final_damage_to_health} damage to health.")
        elif hit_damage > 0: print(f"   {target_name}'s defense blocked all health damage!")

def enemy_attack(character_var, enemy_var):
    """Handles a single enemy's attack turn."""
    if not hasattr(enemy_var, 'get_health') or enemy_var.get_health() <= 0: return
    print('------------------------------')
    enemy_name = getattr(enemy_var, 'get_name', lambda: 'Enemy')(); print(f"{enemy_name} attacks!")
    use_gun = False; equipped_gun_dict = None
    if hasattr(enemy_var, 'get_equipped_gun'):
        equipped_gun_dict = enemy_var.get_equipped_gun()
        if equipped_gun_dict and get_gun_ammo(equipped_gun_dict) > 0 and not is_item_broken(equipped_gun_dict) and hasattr(enemy_var, 'get_gun_skill'): use_gun = True
    if use_gun and equipped_gun_dict:
        gun_name = get_item_property(equipped_gun_dict, 'name', 'Gun'); print(f"   {enemy_name} fires their {gun_name}!")
        attacker_skill = enemy_var.get_gun_skill() if hasattr(enemy_var, 'get_gun_skill') else 0
        attacker_luck = enemy_var.get_luck() if hasattr(enemy_var, 'get_luck') else 0
        target_defense = character_defence(character_var)
        base_chance = 75; skill_bonus = attacker_skill * 2; defense_penalty = target_defense * 3; luck_mod = attacker_luck
        final_hit_chance = max(5, min(95, base_chance + skill_bonus - defense_penalty + luck_mod))
        hit_roll = random.randint(1, 100); logger.debug(f"ENEMY Roll={hit_roll} vs Chance={final_hit_chance}% (B:{base_chance} S:{skill_bonus} D:{defense_penalty} L:{luck_mod})")
        if hit_roll <= final_hit_chance: hit_damage = calculate_gun_hit(enemy_var, equipped_gun_dict); apply_damage_to_target(character_var, hit_damage, enemy_name)
        else: print("   Fortunately, they missed!"); calculate_gun_hit(enemy_var, equipped_gun_dict)
    else:
        equipped_melee_dict = None
        if hasattr(enemy_var, 'get_equipped_melee'): equipped_melee_dict = enemy_var.get_equipped_melee()
        hit_damage = 0
        if equipped_melee_dict and not is_item_broken(equipped_melee_dict): print(f"   {enemy_name} strikes with their {get_item_property(equipped_melee_dict, 'name', 'Weapon')}!"); hit_damage = calculate_melee_hit(enemy_var, equipped_melee_dict)
        elif equipped_melee_dict and is_item_broken(equipped_melee_dict): print(f"   {enemy_name}'s {get_item_property(equipped_melee_dict, 'name', 'Weapon')} is broken!"); hit_damage = calculate_melee_hit(enemy_var, None)
        else: print(f"   {enemy_name} attacks with brute force!"); hit_damage = calculate_melee_hit(enemy_var, None)
        apply_damage_to_target(character_var, hit_damage, enemy_name)
    print('------------------------------')
    if character_var.get_health_points() > 0: print(f"Your current Health is now {character_var.get_health_points()}/{character_var.get_hp_limit()}")

def enemy_defeat(character_var, enemy_var):
    """Handles logic when a single enemy is defeated."""
    enemy_name = getattr(enemy_var, 'get_name', lambda: 'Enemy')()
    print('------------------------------'); print(f"You defeated {enemy_name}!")
    base_exp = (getattr(enemy_var, 'get_strength', lambda: 0)() + getattr(enemy_var, 'get_defence', lambda: 0)())
    if hasattr(enemy_var, 'get_gun_skill'): base_exp += enemy_var.get_gun_skill()
    luck_bonus = random.randint(0, 10) if random.randint(0, 10) < character_var.get_luck() else 0
    exp_gained = math.ceil(base_exp + luck_bonus)
    print(f"You gained {exp_gained} experience points.")
    character_var.set_exp(character_var.get_exp() + exp_gained)
    lvl_system.level_up(character_var)

    # <<< Set defeated flag here >>>
    defeated_npc_id = getattr(enemy_var, 'original_id', None)
    if defeated_npc_id:
        logging.info(f"Setting defeat flag for NPC {defeated_npc_id} inside enemy_defeat")
        _set_flag(f"npc_defeated_{defeated_npc_id}", True)
        # Do NOT set looted flag here, only upon examine
    else:
        logger.error("Could not get original_id from defeated enemy object in enemy_defeat.")
    # <<< End flag setting >>>

    inventory.loot_add(character_var, enemy_var) # Present loot immediately


# <<< Updated battle_state function >>>
def battle_state(character_var, initial_combatants, surprise=False):
    """
    Manages the main battle loop against one or more enemies.
    """
    if not initial_combatants:
        logger.error("battle_state called with no combatants.")
        return {"status": "error"}

    active_combatants = list(initial_combatants)
    # <<< Removed defeated_this_fight list, flags are set in enemy_defeat >>>
    enemy_names = ", ".join([getattr(e, 'get_name', lambda: 'Unknown')() for e in active_combatants])

    print("\n===== BATTLE START =====")
    print(f"You encounter: {enemy_names}!")
    print(f"Your Health: {character_var.get_health_points()}/{character_var.get_hp_limit()}")
    for enemy in active_combatants:
        print(f"{getattr(enemy, 'get_name', lambda: 'Enemy')()}'s Health: {getattr(enemy, 'get_health', lambda: 0)()}")
    print("========================")

    battle_outcome = {"status": "error"} # Default outcome

    if surprise:
        print("\nYou were surprised!")
        for enemy_var in active_combatants:
             if character_var.get_health_points() <= 0: break
             enemy_attack(character_var, enemy_var)
        if character_var.get_health_points() <= 0:
            print("===== BATTLE END =====")
            if game_over(character_var): battle_outcome = {"status": "player_defeated"}
            return battle_outcome

    while active_combatants and character_var.get_health_points() > 0:
        print('------------------------------')
        print("Choose your action:")
        general_options = ["Inventory", "Flee"]

        # --- Display Targets ---
        print("Targets:")
        for i, enemy in enumerate(active_combatants):
            enemy_name = getattr(enemy, 'get_name', lambda: f'Enemy {i+1}')()
            enemy_hp = getattr(enemy, 'get_health', lambda: '?')()
            print(f"  {i+1}. Attack {enemy_name} (HP: {enemy_hp})")
        print("-" * 10)
        num_targets = len(active_combatants)
        for i, opt in enumerate(general_options): print(f"{i+1+num_targets}. {opt}")

        action_taken = False
        target_enemy = None
        player_action = None

        # --- Player Turn Input Loop ---
        while True:
            action_choice_input = input("> ")
            try:
                action_choice_num = int(action_choice_input)
                num_targets = len(active_combatants) # Recalculate

                if 1 <= action_choice_num <= num_targets:
                    target_index = action_choice_num - 1
                    target_enemy = active_combatants[target_index]
                    target_name = getattr(target_enemy, 'get_name', lambda: f'Target {action_choice_num}')()
                    print(f"Attack {target_name} with:")
                    print("  1. Melee Attack")
                    print("  2. Gun Attack")
                    print("  3. Back")
                    while True:
                        sub_action_input = input(">> ")
                        try:
                            sub_action_num = int(sub_action_input)
                            if sub_action_num == 1: player_action = "melee"; break
                            elif sub_action_num == 2: player_action = "gun"; break
                            elif sub_action_num == 3: target_enemy = None; break # Go back
                            else: print("Invalid action number (1-3).")
                        except ValueError: print("Please enter a number (1-3).")
                        except EOFError: logging.warning("EOF during sub-action."); return {"status": "error"}
                    if player_action: break

                elif num_targets < action_choice_num <= num_targets + len(general_options):
                    action_index = action_choice_num - num_targets - 1
                    player_action = general_options[action_index].lower()
                    break
                else:
                    print("Invalid choice number.")
            except ValueError:
                print("Invalid input. Please enter a number.")
            except EOFError:
                 logging.warning("EOF during action selection."); return {"status": "error"}

        # --- Process Player Action ---
        if player_action == "melee":
            if target_enemy:
                action_taken = True; print(f"\n>> Player Turn: Melee Attack on {target_enemy.get_name()} <<")
                equipped_melee_dict = character_var.get_equipped_melee()
                hit_damage = 0
                if equipped_melee_dict is None: print("   You attack unarmed!"); hit_damage = calculate_melee_hit(character_var, None)
                elif is_item_broken(equipped_melee_dict): print(f"   Your {get_item_property(equipped_melee_dict, 'name', 'Weapon')} is broken!"); hit_damage = calculate_melee_hit(character_var, None)
                else: print(f"   You attack with {get_item_property(equipped_melee_dict, 'name', 'Weapon')}!"); logger.debug(f"Melee: {get_item_property(equipped_melee_dict, 'name', 'N/A')}, Dmg: {get_item_attribute(equipped_melee_dict, 'damage', 'N/A')}, Dur: {get_item_property(equipped_melee_dict, 'current_durability', 'N/A')}"); hit_damage = calculate_melee_hit(character_var, equipped_melee_dict)
                apply_damage_to_target(target_enemy, hit_damage, character_var.get_name())
            else: logger.error("Melee action chosen but target_enemy is None."); continue

        elif player_action == "gun":
            if target_enemy:
                action_taken = True; print(f"\n>> Player Turn: Gun Attack on {target_enemy.get_name()} <<")
                equipped_gun_dict = character_var.get_equipped_gun()
                if equipped_gun_dict is None: print("   You don't have a gun equipped!")
                elif is_item_broken(equipped_gun_dict): print(f"   Your {get_item_property(equipped_gun_dict, 'name', 'Gun')} is broken!")
                elif get_gun_ammo(equipped_gun_dict) <= 0: print(f"   Your {get_item_property(equipped_gun_dict, 'name', 'Gun')} is out of ammo!")
                else:
                     gun_name = get_item_property(equipped_gun_dict, 'name', 'Gun'); print(f"   You fire your {gun_name}!")
                     logger.debug(f"Gun: {gun_name}, Dmg: {get_item_attribute(equipped_gun_dict, 'damage', 'N/A')}, Dur: {get_item_property(equipped_gun_dict, 'current_durability', 'N/A')}, Ammo: {get_gun_ammo(equipped_gun_dict)}")
                     attacker_skill = character_var.get_gun_skill(); attacker_luck = character_var.get_luck(); target_defense = npc_defence(target_enemy)
                     base_chance = 75; skill_bonus = attacker_skill * 2; defense_penalty = target_defense * 3; luck_mod = attacker_luck
                     final_hit_chance = max(5, min(95, base_chance + skill_bonus - defense_penalty + luck_mod))
                     hit_roll = random.randint(1, 100); logger.debug(f"Hit Roll={hit_roll} vs Chance={final_hit_chance}% (B:{base_chance} S:{skill_bonus} D:{defense_penalty} L:{luck_mod})")
                     if hit_roll <= final_hit_chance: print("   Your shot hit!"); hit_damage = calculate_gun_hit(character_var, equipped_gun_dict, shots=1); apply_damage_to_target(target_enemy, hit_damage, character_var.get_name())
                     else: print("   Your shot missed!"); calculate_gun_hit(character_var, equipped_gun_dict, shots=1)
            else: logger.error("Gun action chosen but target_enemy is None."); continue

        elif player_action == "inventory":
            print("\n>> Player Turn: Access Inventory <<"); inventory.inventory(character_var); action_taken = False

        elif player_action == "flee":
            action_taken = True; print("\n>> Player Turn: Attempt to Flee <<")
            if random.randint(0, 10) + character_var.get_luck() > 8:
                print("   You successfully escaped!"); print("===== BATTLE END =====")
                battle_outcome = {"status": "fled"}; return battle_outcome
            else: print("   You couldn't escape!")

        # --- Check if Targeted Enemy Defeated ---
        if target_enemy and getattr(target_enemy, 'get_health', lambda: 0)() <= 0:
            if target_enemy in active_combatants:
                 enemy_defeat(character_var, target_enemy) # This now sets the flag
                 # defeated_this_fight.append(target_enemy) # No longer needed to return list
                 active_combatants.remove(target_enemy)

        # --- Check if ALL Enemies Defeated ---
        if not active_combatants:
            print("===== BATTLE END =====")
            # <<< Simplified return status >>>
            battle_outcome = {"status": "all_enemies_defeated"}
            return battle_outcome

        # --- Enemy Turn(s) ---
        if action_taken and character_var.get_health_points() > 0:
             print("\n>> Enemy Turn(s) <<")
             for enemy_var in list(active_combatants):
                  if enemy_var in active_combatants and getattr(enemy_var, 'get_health', lambda: 0)() > 0:
                       enemy_attack(character_var, enemy_var)
                       if character_var.get_health_points() <= 0: break

        # --- Check if Player Defeated ---
        if character_var.get_health_points() <= 0:
            print("===== BATTLE END =====")
            if game_over(character_var): battle_outcome = {"status": "player_defeated"}
            return battle_outcome

    # --- Loop Exit ---
    logger.error("Battle loop exited unexpectedly.")
    print('------------------------------')
    print(f"End of battle. Your health: {character_var.get_health_points()}/{character_var.get_hp_limit()}")
    print(f"Your current Score is {character_var.get_exp()}")
    return battle_outcome
