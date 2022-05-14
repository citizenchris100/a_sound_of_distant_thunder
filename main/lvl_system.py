
def level_up(character_var):
    if 0 <= character_var.get_lvl() <= 1:
        if 25 <= character_var.get_exp():
            upgrade_character(character_var, 1, 5)
    elif 1 <= character_var.get_lvl() <= 2:
        if 50 <= character_var.get_exp():
            upgrade_character(character_var, 0, 5)
    elif 2 <= character_var.get_lvl() <= 3:
        if 125 <= character_var.get_exp():
            upgrade_character(character_var, 1, 5)
    elif 3 <= character_var.get_lvl() <= 4:
        if 275 <= character_var.get_exp():
            upgrade_character(character_var, 0, 5)
    elif 4 <= character_var.get_lvl() <= 5:
        if 375 <= character_var.get_exp():
            upgrade_character(character_var, 1, 5)
    elif 5 <= character_var.get_lvl() <= 6:
        if 575 <= character_var.get_exp():
            upgrade_character(character_var, 0, 5)
    elif 6 <= character_var.get_lvl() <= 7:
        if 875 <= character_var.get_exp():
            upgrade_character(character_var, 1, 5)
    elif 7 <= character_var.get_lvl() <= 7:
        if 1775 <= character_var.get_exp():
            upgrade_character(character_var, 0, 5)


def upgrade_character(character_var, dp, hp):
    total = (character_var.get_strength_attribute() + character_var.get_gun_skill() + character_var.get_luck_attribute()
             + character_var.get_charm_attribute())
    if total < 84:
        option = input("You have leveled up.\nChoose which attribute you would like to improve.\n"
                       "1. Melee Attack\n2. Gun Skill\n3. Luck\n4. Charm\nHelp\n> ")
        if option == "1" or "melee" in option.lower():
            if character_var.get_strength_attribute() < 35:
                character_var.set_strength_attribute(character_var.get_strength_attribute() + 1)
                print("Your Strength / Melee Attack is now ", character_var.get_strength_attribute(), sep='')
            else:
                print("You have reached the limit of your Strength / Melee Attack attribute. Make another selection.")
                upgrade_character(character_var, dp, hp)
        elif option == "2":
            if character_var.get_strength_attribute() < 35:
                character_var.set_gun_skill(character_var.get_gun_skill() + 1)
                print("Your Gun Skill is now ", character_var.get_gun_skill(), sep='')
            else:
                print("You have reached the limit of your Gun Skill attribute. Make another selection.")
                upgrade_character(character_var, dp, hp)
        elif option == "3":
            if character_var.get_luck_attribute() < 7:
                character_var.set_luck_attribute(character_var.get_luck_attribute() + 1)
                print("Your Luck is now ", character_var.get_gun_skill(), sep='')
            else:
                print("You have reached the limit of your Luck attribute. Make another selection.")
                upgrade_character(character_var, dp, hp)
        elif option == "4":
            if character_var.get_charm_attribute() < 7:
                character_var.set_charm_attribute(character_var.get_charm_attribute() + 1)
                print("Your Charm is now ", character_var.get_gun_skill(), sep='')
            else:
                print("You have reached the limit of your Charm attribute. Make another selection.")
                upgrade_character(character_var, dp, hp)
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
            upgrade_character(character_var, dp, hp)
        else:
            print("Invalid Input, please select an Attribute you wish to upgrade. \nIf you need more information "
                  "about the Class Attributes type \'Help\'")
            upgrade_character(character_var, dp, hp)
    character_var.up_lvl()
    character_var.set_hp_limit(character_var.get_hp_limit() + hp)
    character_var.set_health_points(character_var.get_hp_limit())
    character_var.set_defence_points(character_var.get_defence_points() + dp)
    character_var.set_inventory_limit((character_var.get_inventory_limit() + 1))
    print("You are now Level ", character_var.get_lvl(), "\nYou've gained ", hp,
          " health points & ", dp, " defence points.\nAdditionally you've gained 1 inventory slot.", sep='')