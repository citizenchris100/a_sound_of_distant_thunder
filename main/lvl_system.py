import logging 
logger = logging.getLogger(__name__)

def level_up(character_var):
    """Checks if the character has enough EXP to level up and calls upgrade_character if so."""
    current_level = character_var.get_lvl()
    current_exp = character_var.get_exp()
    exp_needed = 0
    dp_gain = 0
    hp_gain = 5 

    if current_level == 0: 
        exp_needed = 25
       
    elif current_level == 1: 
        exp_needed = 50
        dp_gain = 1 
    elif current_level == 2: 
        exp_needed = 125
        dp_gain = 0 
    elif current_level == 3: 
        exp_needed = 275
        dp_gain = 1 
    elif current_level == 4: 
        exp_needed = 375
        dp_gain = 0 
    elif current_level == 5: 
        exp_needed = 575
        dp_gain = 1 
    elif current_level == 6: 
        exp_needed = 875
        dp_gain = 0
    elif current_level == 7: 
        exp_needed = 1775 
        dp_gain = 1 
    else:
        return 

    if current_exp >= exp_needed:
        upgrade_character(character_var, dp_gain, hp_gain)
    else:
        logger.debug("Player level %d, EXP %d < %d needed for next level.", current_level, current_exp, exp_needed)


def upgrade_character(character_var, dp, hp):
    """Handles the attribute increase prompt and applies level up bonuses."""
    print("-" * 30) 
    print("          LEVEL UP!           ")
    print("-" * 30)

    total = (character_var.get_strength_attribute() +
             character_var.get_gun_skill() +
             character_var.get_luck() +
             character_var.get_charm_attribute() +
             character_var.get_stealth_attribute())

    stat_point_added = False

    if total < 84:
        while not stat_point_added: 
            print("Choose which attribute you would like to improve:")
            print("1. Melee Attack (Strength)")
            print("2. Gun Skill")
            print("3. Luck")
            print("4. Charm")
            print("5. Stealth")
            print("Help")
            option = input("> ")

            if option == "1" or "melee" in option.lower():
                if character_var.get_strength_attribute() < 35:
                    character_var.set_strength_attribute(character_var.get_strength_attribute() + 1)
                    print("Your Strength / Melee Attack is now ", character_var.get_strength_attribute(), sep='')
                    stat_point_added = True
                else:
                    print("You have reached the limit of your Strength / Melee Attack attribute.")

            elif option == "2":
                if character_var.get_gun_skill() < 35:
                    character_var.set_gun_skill(character_var.get_gun_skill() + 1)
                    print("Your Gun Skill is now ", character_var.get_gun_skill(), sep='')
                    stat_point_added = True
                else:
                    print("You have reached the limit of your Gun Skill attribute.")

            elif option == "3":
                if character_var.get_luck() < 7:
                    character_var.set_luck_attribute(character_var.get_luck() + 1)
                    print("Your Luck is now ", character_var.get_luck(), sep='') 
                    stat_point_added = True
                else:
                    print("You have reached the limit of your Luck attribute.")

            elif option == "4":
                if character_var.get_charm_attribute() < 7:
                    character_var.set_charm_attribute(character_var.get_charm_attribute() + 1)
                    print("Your Charm is now ", character_var.get_charm_attribute(), sep='') 
                    stat_point_added = True
                else:
                    print("You have reached the limit of your Charm attribute.")

            elif option == "5":
                if character_var.get_stealth_attribute() < 7:
                    character_var.set_stealth_attribute(character_var.get_stealth_attribute() + 1)
                    print("Your Stealth is now ", character_var.get_stealth_attribute(), sep='')
                    stat_point_added = True
                else:
                    print("You have reached the limit of your Stealth attribute.")

            elif option.lower() == "help":
                print('------------------------------')
                print('-About the Character         -')
                print('-Attributes                  -')
                print('------------------------------')
                print('------------------------------')
                print('-Melee Attack: affects how   -')
                print('-you use hand help weapons   -')
                print('-such as knives.             -')
                print('------------------------------')
                print('-Gun Skill: affects your     -')
                print('-ability to use hand guns    -')
                print('-and rifles.                 -')
                print('------------------------------')
                print('-Luck: can greatly affect    -')
                print('-the outcome of battles and  -')
                print('-your chance of getting loot.-')
                print('------------------------------')
                print('-Charm: affects how well     -')
                print('-you can persuade others     -')
                print('------------------------------')
                print('-Stealth: affects chance of  -')
                print('-being surprised and maybe   -')
                print('-other sneaky actions.       -')
                print('------------------------------')

            else:
                print("Invalid Input, please select an Attribute (1-5) or type 'Help'.")
            if not stat_point_added and option in ["1", "2", "3", "4", "5"]:
                 print("Please make another selection.")

    else: 
         print("You have reached the maximum potential for Str, Gun, Luck, and Charm attributes!")
         logger.info("Character %s reached combined stat cap (excluding stealth) at level %d.",
                     character_var.get_name(), character_var.get_lvl())

    character_var.up_lvl() 
    character_var.set_hp_limit(character_var.get_hp_limit() + hp) 
    character_var.set_health_points(character_var.get_hp_limit()) 
    character_var.set_defence_points(character_var.get_defence_points() + dp) 
    character_var.set_inventory_limit(character_var.get_inventory_limit() + 1) 

    print("-" * 30)
    print(f"You are now Level {character_var.get_lvl()}!")
    print(f"You gained {hp} health points (Max HP: {character_var.get_hp_limit()})")
    if dp > 0:
        print(f"You gained {dp} defence point (Defense: {character_var.get_defence_points()})")
    print(f"You gained 1 inventory slot (Capacity: {character_var.get_inventory_limit()})")
    print("-" * 30)