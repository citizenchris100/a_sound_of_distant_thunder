import random
import math
import sys
import inventory 
import lvl_system
import hero 
from NPC import Enemy 
from ItemUtil import (
    get_item_attribute, get_item_property,
    decrease_item_durability, is_item_broken,
    get_gun_ammo, set_gun_ammo
)

def display_score():
    try:
        with open("../score.txt", "r") as file:
            for line in file:
                xline = line.split(",")
                if len(xline) >= 2: print(xline[0], xline[1].strip())
    except FileNotFoundError: print("Score file not found.")
    
def write_score(score, name):
    try:
        with open("../score.txt", "a") as file: file.write(f"{name},{score}\n")
    except IOError: print("Error writing to score file.")
    
def game_over(character_var):
    score = character_var.get_exp()
    if character_var.get_health_points() <= 0:
        print("\nYou have been defeated.")
        print(f"Your Final score is {score}")
        name = input("Enter your Name: ")
        write_score(score, name)
        display_score()
        print("\nExiting game...")
        sys.exit()

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
    strength = attacker.get_strength_attribute()
    weapon_damage = 0
    if weapon_dict and not is_item_broken(weapon_dict):
        weapon_damage = get_item_attribute(weapon_dict, 'damage', default=0)
        loss = get_item_property(weapon_dict, 'durability_loss_per_use', default=1)
        if decrease_item_durability(weapon_dict, loss):
             if is_item_broken(weapon_dict):
                  print(f"   Your {get_item_property(weapon_dict, 'name', 'Melee Weapon')} broke!")
    elif weapon_dict and is_item_broken(weapon_dict):
         print(f"   Your {get_item_property(weapon_dict, 'name', 'Melee Weapon')} is broken!")
    
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

def apply_damage_to_target(target, damage, attacker_name="Attacker"):
    """Applies damage to a target, considering defense and armor durability."""
    if damage <= 0:
        print(f"   {attacker_name}'s attack has no effect.")
        return

    defence = 0
    if hasattr(target, 'get_defence_points'): defence = character_defence(target)
    elif hasattr(target, 'get_defence'): defence = npc_defence(target)

    total_damage_taken = max(0, math.floor(damage - defence))

    equipped_armour_dict = None
    if hasattr(target, 'get_equipped_armour'):
        equipped_armour_dict = target.get_equipped_armour()

    if equipped_armour_dict and not is_item_broken(equipped_armour_dict):
        if decrease_item_durability(equipped_armour_dict, total_damage_taken):
            print(f"   {target.get_name()}'s {get_item_property(equipped_armour_dict,'name','Armor')} takes {total_damage_taken} damage.")
            if is_item_broken(equipped_armour_dict):
                 print(f"   {target.get_name()}'s {get_item_property(equipped_armour_dict,'name','Armor')} broke!")
   
    current_hp = target.get_health()
    new_hp = current_hp - total_damage_taken
    target.set_health(new_hp)

    print(f"   {target.get_name()} takes {total_damage_taken} damage to health.")
    if new_hp <= 0:
        print(f"   {target.get_name()} has been defeated!")


def enemy_attack(character_var, enemy_var):
    """Handles the enemy's attack turn, using updated helpers."""
    print('------------------------------')
    print(f"{enemy_var.get_name()} attacks!")

    use_gun = False
    equipped_gun_dict = None
    if hasattr(enemy_var, 'get_equipped_gun'):
        equipped_gun_dict = enemy_var.get_equipped_gun()
        if equipped_gun_dict and get_gun_ammo(equipped_gun_dict) > 0 and not is_item_broken(equipped_gun_dict):
            if hasattr(enemy_var, 'get_gun_skill') and enemy_var.get_gun_skill() > enemy_var.get_strength():
                use_gun = True

    if use_gun and equipped_gun_dict:
        print(f"   {enemy_var.get_name()} fires their {get_item_property(equipped_gun_dict, 'name', 'Gun')}!")
        if random.randint(0, 6) < enemy_var.get_luck():
            hit_damage = calculate_gun_hit(enemy_var, equipped_gun_dict)
            apply_damage_to_target(character_var, hit_damage, enemy_var.get_name())
        else:
            print("   Fortunately, they missed!")
            calculate_gun_hit(enemy_var, equipped_gun_dict) 
    else:
        equipped_melee_dict = None
        if hasattr(enemy_var, 'get_equipped_melee'):
            equipped_melee_dict = enemy_var.get_equipped_melee()

        if equipped_melee_dict and not is_item_broken(equipped_melee_dict):
             print(f"   {enemy_var.get_name()} strikes with their {get_item_property(equipped_melee_dict, 'name', 'Weapon')}!")
             hit_damage = calculate_melee_hit(enemy_var, equipped_melee_dict)
        elif equipped_melee_dict and is_item_broken(equipped_melee_dict):
             print(f"   {enemy_var.get_name()}'s {get_item_property(equipped_melee_dict, 'name', 'Weapon')} is broken!")
             hit_damage = calculate_melee_hit(enemy_var, None) 
        else:
             print(f"   {enemy_var.get_name()} attacks with brute force!")
             hit_damage = calculate_melee_hit(enemy_var, None) 
        apply_damage_to_target(character_var, hit_damage, enemy_var.get_name())

    print('------------------------------')
    if character_var.get_health_points() > 0:
        print(f"Your current Health is now {character_var.get_health_points()}/{character_var.get_hp_limit()}")
    else:
        pass 


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
    inventory.loot_add(character_var, enemy_var)

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

            if equipped_melee_dict is None:
                 print("   You attack unarmed!")
                 hit_damage = calculate_melee_hit(character_var, None)
            elif is_item_broken(equipped_melee_dict):
                print(f"   Your {get_item_property(equipped_melee_dict, 'name', 'Weapon')} is broken!")
                hit_damage = 0
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
                 print(f"   You fire your {get_item_property(equipped_gun_dict, 'name', 'Gun')}!")
                 print(f"DEBUG: Gun: {get_item_property(equipped_gun_dict, 'name', 'N/A')}, "
                       f"Damage Attr: {get_item_attribute(equipped_gun_dict, 'damage', 'N/A')}, "
                       f"Current Dur: {get_item_property(equipped_gun_dict, 'current_durability', 'N/A')}, "
                       f"Ammo: {get_gun_ammo(equipped_gun_dict)}")

                 if random.randint(0, 6) < character_var.get_luck():
                     hit_damage = calculate_gun_hit(character_var, equipped_gun_dict, shots=1)
                     apply_damage_to_target(enemy_var, hit_damage, character_var.get_name())
                 else:
                     print("   Your shot missed!")
                     calculate_gun_hit(character_var, equipped_gun_dict, shots=1) 
        elif action_choice == "3" or "inventory" in action_choice.lower():
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

        else:
            print("Invalid action choice. Please try again.")
            continue 

        if enemy_var.get_health() <= 0:
            enemy_defeat(character_var, enemy_var)
            print("===== BATTLE END =====")
            break

        if action_taken and character_var.get_health_points() > 0:
             print("\n>> Enemy Turn <<")
             enemy_attack(character_var, enemy_var)

        if character_var.get_health_points() <= 0:
            print("===== BATTLE END =====")
            game_over(character_var) # Call game over logic
            break

    print('------------------------------')
    if character_var.get_health_points() > 0 and enemy_var.get_health() <= 0:
         pass 
    print(f"Your final health: {character_var.get_health_points()}/{character_var.get_hp_limit()}")
    print(f"Your current Score is {character_var.get_exp()}")