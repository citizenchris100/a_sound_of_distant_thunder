# a sound of distant thunder
# by christopher manning

import time
import cmd
import textwrap
import sys
import os
import random
import math
import hero
import enemy


def display_score():
    file = open("score.txt", "r")
    for line in file:
        xline = line.split(",")
        print(xline[0], xline[1])
    exit()


def write_score(score, name):
    file = open("score.txt", "a")
    file.write(str(name))
    file.write(",")
    file.write(str(score))
    file.write(",")
    file.write("\n")
    file.close()


def game_over(character_var):
    score = character_var.exp
    if character_var.hp < 1:
        print("You have been defeated.")
        print("You Final score is ", score, sep='')
        name = input("Enter your Name : ")
        write_score(score, name)
        display_score()


def enemy_hit_back(character_var, enemy_var, hit):
    if hit:
        print("You hit the ", enemy_var.get_name(), " their health is now ", enemy_var.get_health(), ".", sep='')
    else:
        print("You did not hit the ", enemy_var.get_name(), ".", sep='')
    if enemy_var.get_luck() > random.randint(0, 6):
        if hit:
            print("The Enemy was able to strike back.")
            character_updated_health = math.floor(character_var.get_health_points() - (enemy_var.get_strength() /
                                                                                       character_var.get_defence_points()))
            character_var.set_health_points(character_updated_health)
        else:
            print("However they were able to strike you.")
            character_updated_health = character_var.get_health_points() - enemy_var.get_strength()
            character_var.set_health_points(character_updated_health)
        if character_var.hp > 0:
            print("Your health is now ", character_var.get_health_points(), ".", sep='')
        else:
            game_over(character_var)


def enemy_attack(character_var, enemy_var, chance):
    defend = random.randint(0, 10)
    start = vowel_start(enemy_var)
    if enemy_var.get_luck() > chance:
        if defend < character_var.get_luck_attribute():
            print(start, enemy_var.get_name(), " has attacked you. However you deflect some of the attack", sep='')
            character_updated_health = math.floor(character_var.get_health_points() - (enemy_var.get_strength() /
                                                                                       character_var.get_defence_points()))
            character_var.set_health_points(character_updated_health)
        else:
            print(start, enemy_var.name, " has attacked you.")
            character_updated_health = character_var.get_health_points() - enemy_var.get_strength()
            character_var.set_health_points(character_updated_health)
        if character_var.hp > 0:
            print("Your health is now ", character_var.get_health_points(), ".", sep='')
        else:
            game_over(character_var)
    else:
        print(start, enemy_var.get_name(), " has attempted a surprise attack", sep='')


def vowel_start(enemy_var):
    vowel = 'aeiou'
    if enemy_var.get_name()[0].lower() in vowel:
        start = "An "
    else:
        start = "A "
    return start


def level_up(character_var):
    if 0 <= character_var.get_lvl() <= 1:
        if 25 <= character_var.get_exp():
            upgrade_character(character_var, 1, 5)
    elif 1 <= character_var.get_lvl() <= 2:
        if 50 <= character_var.get_exp():
            character_var.up_lvl()
    elif 2 <= character_var.get_lvl() <= 3:
        if 100 <= character_var.get_exp():
            character_var.up_lvl()
    elif 3 <= character_var.get_lvl() <= 4:
        if 175 <= character_var.get_exp():
            character_var.up_lvl()
    elif 4 <= character_var.get_lvl() <= 5:
        if 275 <= character_var.get_exp():
            character_var.up_lvl()
    elif 5 <= character_var.get_lvl() <= 6:
        if 475 <= character_var.get_exp():
            character_var.up_lvl()
    elif 6 <= character_var.get_lvl() <= 7:
        if 775 <= character_var.get_exp():
            character_var.up_lvl()
    elif 7 <= character_var.get_lvl() <= 7:
        if 1775 <= character_var.get_exp():
            character_var.up_lvl()


def upgrade_character(character_var, dp, hp):
    option = input("You have leveled up.\nChoose which attribute you would like to improve.\n"
                   "1. Melee Attack\n2. Gun Skill\n3. Luck\n4. Charm\nHelp\n> ")
    if option == "1":
        character_var.set_strength_attribute(character_var.get_strength_attribute() + 1)
    elif option == "2":
        character_var.set_gun_skill(character_var.get_gun_skill() + 1)
    elif option == "3":
        character_var.set_luck_attribute(character_var.get_luck_attribute() + 1)
    elif option == "4":
        character_var.set_charm_attribute(character_var.get_charm_attribute() + 1)
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
        print("Invalid Input, please select an Attribute you wish to upgrade. If you need more information \n"
              "about the Class Attributes type \'Help\'")
    character_var.up_lvl()
    character_var.set_health_points(character_var.get_health_points() + hp)
    character_var.set_defence_points(character_var.get_defence_points() + dp)
    print("Alex is now Level ", character_var.get_lvl(), "\nYou've gained ", hp,
          " health points & ", dp, " defence point", sep='')


def enemy_defeat(character_var, enemy_var):
    chance = random.randint(0, 10)
    if "Goblin" in enemy_var.get_name():
        if chance < character_var.get_luck_attribute():
            exp = math.ceil(enemy_var.get_strength() + random.randint(0, 10))
        else:
            exp = enemy_var.get_strength()
        print("You killed the ", enemy_var.name, ".", sep='')
    else:
        if enemy_var.get_gun_skill() < enemy_var.get_strength():
            if chance < character_var.get_luck_attribute():
                exp = math.ceil(enemy_var.get_strength() + random.randint(0, 10))
            else:
                exp = enemy_var.get_strength()
        else:
            if chance < character_var.get_luck_attribute():
                exp = math.ceil(enemy_var.get_gun_skill() + random.randint(0, 10))
            else:
                exp = enemy_var.get_gun_skill()
        print("You killed ", enemy_var.name, ".", sep='')
    print("You gained ", exp, " experience points.", sep='')
    character_var.set_exp(character_var.get_exp() + exp)
    level_up(character_var)


# TODO: balance the combat mechanics
def battle_state(character_var, enemy_var, surprise):
    if surprise:
        enemy_attack(character_var, enemy_var, random.randint(0, 10))
    while enemy_var.get_health() > 0:
        option = input("1. Melee Attack \n2. Gun Attack\n3. Flee\n> ")
        if option == "1":
            print("You swing your sword attacking the ", enemy_var.get_name(), ".", sep='')
            if random.randint(0, 6) < character_var.get_luck_attribute():
                enemy_var.set_health(enemy_var.get_health() - character_var.get_strength_attribute())
                if enemy_var.get_health() > 0:
                    enemy_hit_back(character_var, enemy_var, True)
                else:
                    enemy_defeat(character_var, enemy_var)
                    loot_add(character_var, enemy_var)
                    break
            elif random.randint(0, 6) < random.randint(0, 10):
                enemy_var.set_health(math.floor(enemy_var.get_health() - (character_var.get_strength_attribute() /
                                                                          enemy_var.get_defence())))
                if enemy_var.get_health() > 0:
                    enemy_hit_back(character_var, enemy_var, True)
                else:
                    enemy_defeat(character_var, enemy_var)
                    loot_add(character_var, enemy_var)
                    break
            else:
                enemy_hit_back(character_var, enemy_var, False)
        elif option == "2":
            print("You fired your gun attacking the ", enemy_var.name, ".", sep='')
            if random.randint(0, 6) < character_var.get_luck_attribute():
                new_hp = enemy_var.get_health() - character_var.get_gun_skill()
                enemy_var.set_health(new_hp)
                if random.randint(0, 6) + character_var.get_luck_attribute() > 12:
                    print("You were able to get off another shot as well.")
                    new_hp = enemy_var.get_health() - character_var.get_gun_skill()
                    enemy_var.set_health(new_hp)
                if enemy_var.hp > 0:
                    enemy_hit_back(character_var, enemy_var, True)
                else:
                    enemy_defeat(character_var, enemy_var)
                    loot_add(character_var, enemy_var)
                    break
            else:
                enemy_hit_back(character_var, enemy_var, False)
        elif option == "3":
            if random.randint(0, 6) + character_var.get_luck_attribute() > 12:
                print("You escape battle with the ", enemy_var.name, ".", sep='')
                break
            else:
                new_hp = enemy_var.get_health() - character_var.get_strength_attribute()
                character_var.set_health_points(new_hp)
                print("You were unable to escape battle. \nHowever the ", enemy_var.name,
                      " was able to strike you.", sep='')
                if character_var.get_health_points() > 0:
                    print("Your health is now ", character_var.get_health_points(), ".", sep='')
                else:
                    game_over(character_var)
        else:
            print("Option not allowed please choose either 1, 2 or 3.")
    print("Your current Score is ", character_var.get_exp(), sep='')


# TODO: add ability to actually use inventory items
def loot_add(character_var, enemy_var):
    chance = random.randint(0, 10)
    if chance < character_var.get_luck_attribute():
        loot_drop = enemy_var.get_inventory()[0]
        print("It appears to have dropped a ", loot_drop.get_item_name(), ".", sep='')
        print("Would you like to add ", loot_drop.get_item_name(), " to your Inventory?", sep='')
        # TODO: add help and gibberish catch
        option = input("Yes \nNo\n> ")
        if option.lower() == "yes":
            character_var.add_inventory(loot_drop)
            print(loot_drop.get_item_name(), " was added to your inventory.", sep='')


def title_screen_selections():
    option = input("> ")
    if option.lower() == "play":
        hero.create_class_screen()
        character = hero.class_selection()
        print("---------------battle 1")
        battle_state(character, [enemy.basic_goblin(), enemy.beta_goblin(), enemy.alpha_goblin()]
        [random.randint(0, 2)], False)
        print("---------------battle 2")
        battle_state(character, [enemy.basic_goblin(), enemy.beta_goblin(), enemy.alpha_goblin()]
        [random.randint(0, 2)], False)
        print("---------------battle 3")
        battle_state(character, [enemy.basic_goblin(), enemy.beta_goblin(), enemy.alpha_goblin()]
        [random.randint(0, 2)], False)
    elif option.lower() == "help":
        help_menu()
        title_screen_selections()
    elif option.lower() == "quit":
        sys.exit()
    else:
        print("Type 'Play' to play the game. "
              "\n 'Quit' to exit"
              "\n You can type 'Help' at any time for assistance.")
        title_screen_selections()


def title_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    print('------------------------------')
    print('- A Sound of Distant Thunder -')
    print('------------------------------')
    print('------------------------------')
    print('-   by Christopher Manning   -')
    print('------------------------------')
    print('-           play             -')
    print('-           help             -')
    print('-           quit             -')
    print('------------------------------')
    title_screen_selections()


def help_menu():
    print('------------------------------')
    print('-         How to Play        -')
    print('------------------------------')
    print('------------------------------')
    print('-Type what you would like the-')
    print('-player to do.               -')
    print('------------------------------')
    print('-Common commands you can use -')
    print('------------------------------')
    print('- "Go to <location>"         -')
    print('-   :this will move you to a -')
    print('-    new location            -')
    print('------------------------------')
    print('- "Look at <something>"      -')
    print('-   :this will give you      -')
    print('-    details                 -')
    print('------------------------------')
    print('- "Take <something>"         -')
    print('-   :this will add the       -')
    print('-    item to your            -')
    print('-    inventory               -')
    print('------------------------------')
    print('- "Speak to <someone>"       -')
    print('-   :enter into a            -')
    print('-    conversation with       -')
    print('-    an NPC                  -')
    print('------------------------------')
    print('- "Attack <someone/thing>    -')
    print('-  with <something>"         -')
    print('-   :Attach a person         -')
    print('-    or thing                -')
    print('------------------------------')
    print('- "Defend against            -')
    print('-  <someone/thing>           -')
    print('-  with <something>"         -')
    print('-   :Defend yourself         -')
    print('-    against an attack       -')
    print('------------------------------')
    print('- "Flee"                     -')
    print('-   :Attempt to retreat      -')
    print('-    from battle / attack    -')
    print('------------------------------')


title_screen()
