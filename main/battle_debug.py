import logging
import copy
import random
import os
import sys
import math 


try:
    from hero import Hero, class_selection 
    from NPC import basic_goblin, beta_goblin, alpha_goblin 
    import data_loader
    import battle_system
    from ItemUtil import set_gun_ammo, is_item_broken 
except ImportError as e:
    print(f"FATAL ERROR: Failed to import necessary modules: {e}")
    print("Make sure all game modules (hero, NPC, data_loader, battle_system, ItemUtil) exist and are importable.")
    sys.exit(1)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='battle_debug.log',
    filemode='w'
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.WARNING) 
console_formatter = logging.Formatter('%(levelname)s - %(name)s - %(message)s')
console_handler.setFormatter(console_formatter)
logging.getLogger('').addHandler(console_handler) 

logging.info("--- Starting Battle Debug Session ---")

def run_battle_test():
    logging.info("Loading game data...")
    game_items_data = data_loader.load_items_data()

    if game_items_data is None:
        logging.error("Failed to load items data. Aborting test.")
        print("ERROR: Failed to load items.json. Check file path and format. See battle_debug.log for details.")
        return 

    target_level = 0 
    try:
        level_input = input(f"Enter desired starting level (0 or 1 for standard creation, max defined in lvl_system: ~8): ")
        target_level = int(level_input)
        if target_level < 0:
            target_level = 0
            print("Invalid level, defaulting to 0.")
        elif target_level > 8:
            print(f"Warning: Level {target_level} progression not explicitly defined in lvl_system.py. Stats are approximated.")
            logging.warning("Testing level %d which is beyond explicitly defined progression.", target_level)

    except ValueError:
        print("Invalid input, defaulting to level 0.")
        target_level = 0

    player = None
    if target_level <= 1: 
        logging.info("Starting character creation for Level 0/1...")
        print("\n--- Character Creation ---")
        player = class_selection(game_items_data) 
        if player is None:
             logging.error("Character creation failed or was quit. Aborting test.")
             print("Character creation quit or failed.")
             return
        logging.info("Character '%s' created via class selection (Level %d).", player.get_name(), player.lvl)

    else: 
        logging.info("Creating manual Hero for testing (Level %d target).", target_level)
        print(f"\n--- Creating Simulated Level {target_level} Character ---")

        BASE_HP = 65
        BASE_DEF = 6
        BASE_STR = 13
        BASE_GUN = 12
        BASE_LUCK = 3
        BASE_CHARM = 3
        BASE_STEALTH = 3
       
        levels_gained = target_level 

        hp_gain = levels_gained * 5
        simulated_hp_limit = BASE_HP + hp_gain

       
        dp_gain = target_level // 2 
        simulated_dp = min(7, BASE_DEF + dp_gain) 

        current_total_stats = BASE_STR + BASE_GUN + BASE_LUCK + BASE_CHARM
        points_available = levels_gained
        points_allocatable = max(0, 84 - current_total_stats) 
        points_to_add = min(points_available, points_allocatable) 

        gun_skill_gain = points_to_add
        simulated_gun = min(35, BASE_GUN + gun_skill_gain)

        simulated_str = BASE_STR
        simulated_luck = BASE_LUCK
        simulated_charm = BASE_CHARM
     
        simulated_stealth = BASE_STEALTH
  
        player = Hero(dp=simulated_dp, strength=simulated_str, gun_skill=simulated_gun,
                      luck=simulated_luck, charm=simulated_charm, stealth=simulated_stealth,
                      game_items_data=game_items_data) 
        player.name = f"DebugHeroLvl{target_level}"
        player.lvl = target_level 
        player.set_hp_limit(simulated_hp_limit) 
        player.set_health_points(simulated_hp_limit) 
        player.set_inventory_limit(5 + levels_gained)

        logging.info("Manual Hero created with approximated stats: Def:%d Str:%d Gun:%d Luck:%d HP:%d/%d InvCap:%d",
                     player.get_defence_points(), player.get_strength_attribute(), player.get_gun_skill(), player.get_luck(),
                     player.get_health_points(), player.get_hp_limit(), player.get_inventory_limit())

    print("--- Character Ready ---")
    print(f"- Name: {player.get_name()} (Level {player.lvl})")
    print(f"- HP: {player.get_health_points()}/{player.get_hp_limit()}")
    print(f"- Def: {player.get_defence_points()}")
    print(f"- Str: {player.get_strength_attribute()}")
    print(f"- Gun: {player.get_gun_skill()}")
    print(f"- Luck: {player.get_luck()}")
    print(f"- Charm: {player.get_charm_attribute()}")
    print(f"- Stealth: {player.get_stealth_attribute()}")
    print(f"- Inv Cap: {player.get_inventory_limit()}")
    print("-------------------------")

    logging.info("Adding standard starting gear (Boat Case items).")
    print("Adding starting gear...")
    pistol_id = "basic_pistol"
    knife_id = "basic_knife"
    ammo_id = "small_9mm_ammo_box"
    pistol_data = game_items_data.get(pistol_id)
    knife_data = game_items_data.get(knife_id)
    ammo_data = game_items_data.get(ammo_id)
    equipped_pistol_instance = None

    if pistol_data:
        pistol_instance = copy.deepcopy(pistol_data)
        player.set_equipped_gun(pistol_instance)
        equipped_pistol_instance = pistol_instance
        logging.info("Equipped: %s", pistol_id)
    else: logging.warning("Item data for '%s' not found. Cannot equip.", pistol_id)

    if knife_data:
        knife_instance = copy.deepcopy(knife_data)
        player.set_equipped_melee(knife_instance)
        logging.info("Equipped: %s", knife_id)
    else: logging.warning("Item data for '%s' not found. Cannot equip.", knife_id)

    if ammo_data:
        ammo_instance = copy.deepcopy(ammo_data)
        player.add_inventory(ammo_instance) 
        logging.info("Added to inventory: %s", ammo_id)
    else: logging.warning("Item data for '%s' not found. Cannot add to inventory.", ammo_id)

    if equipped_pistol_instance:
        try:
            if 'set_gun_ammo' in globals() or 'set_gun_ammo' in locals():
                 clip_size = equipped_pistol_instance.get('attributes', {}).get('clip_size', 6)
                 set_gun_ammo(equipped_pistol_instance, clip_size)
                 logging.info("Set starting ammo for %s to %d", pistol_id, clip_size)
                 print(f"Loaded {player.get_equipped_gun().get('name', 'pistol')} with {clip_size} rounds.")
            else:
                 logging.warning("set_gun_ammo function not available. Pistol not loaded.")
        except Exception as e:
            logging.error("Error setting gun ammo: %s", e)
            print(f"ERROR setting gun ammo - see log.")

    logging.info("Creating enemy instances...")
    enemies_to_fight = {
        "Basic Goblin": basic_goblin(game_items_data),
        "Beta Goblin": beta_goblin(game_items_data),
        "Alpha Goblin": alpha_goblin(game_items_data)
    }
    print("Created enemies for testing.")

    for enemy_type, current_enemy in enemies_to_fight.items():
        if player.get_health_points() <= 0:
            logging.info("Player already defeated before fighting %s. Stopping.", enemy_type)
            print("\nPlayer has been defeated. Cannot continue fight sequence.")
            break 

        if not current_enemy:
            logging.error("Failed to create %s instance. Skipping battle.", enemy_type)
            print(f"ERROR: Could not create {enemy_type}. Skipping fight.")
            continue

        # --- Optional: Health reset is commented out, per user request ---
        # current_hp = player.get_health_points()
        # max_hp = player.get_hp_limit()
        # if current_hp < max_hp:
        #     logging.info("Resetting player health to %d for next fight.", max_hp)
        #     player.set_health_points(max_hp)
        # --- End Optional Reset ---

        logging.info("Starting battle: %s (Lvl %d) vs %s (%s)", player.get_name(), player.lvl, current_enemy.get_name(), enemy_type)
        print(f"\n--- Starting Battle: {player.get_name()} (Lvl {player.lvl} | HP: {player.get_health_points()}/{player.get_hp_limit()}) vs {current_enemy.get_name()} ({enemy_type}) ---")
        enemy_weapon = current_enemy.get_equipped_melee()
        if enemy_weapon:
            print(f"--- {current_enemy.get_name()} is armed with: {enemy_weapon.get('name')} ---")
        else:
            print(f"--- {current_enemy.get_name()} is unarmed ---")
        input("Press Enter to start battle...")


        battle_system.battle_state(player, current_enemy) 

        if player.get_health_points() <= 0:
             
             logging.warning("Player defeated during battle against %s. Ending test sequence.", current_enemy.get_name())
            
             break

        logging.info("Battle finished against %s.", enemy_type)
        print(f"--- Battle against {enemy_type} finished. ---")
        input("Press Enter to fight next enemy (if any)...")


    logging.info("--- Battle Debug Session Ended ---")
    print("\n--- All Battle Tests Finished (or Player Defeated) ---")


if __name__ == "__main__":
    try:
        run_battle_test()
    except NameError as ne:
         print(f"\nFATAL NameError: {ne}. Ensure all necessary functions/classes are imported correctly.")
         logging.exception("Fatal NameError during script execution.")
    except Exception as e:
         print(f"\nAn unexpected error occurred: {e}")
         logging.exception("An unexpected error occurred during script execution.")