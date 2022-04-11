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


basic_goblin_data = enemy.basic_goblin()
BasicGoblin = enemy.Enemy(basic_goblin_data[0], basic_goblin_data[1], basic_goblin_data[2], basic_goblin_data[3],
                          basic_goblin_data[4])


basic_goblin_data = enemy.beta_goblin()
BetaGoblin = enemy.Enemy(basic_goblin_data[0], basic_goblin_data[1], basic_goblin_data[2], basic_goblin_data[3],
                         basic_goblin_data[4])


basic_goblin_data = enemy.alpha_goblin()
AlphaGoblin = enemy.Enemy(basic_goblin_data[0], basic_goblin_data[1], basic_goblin_data[2], basic_goblin_data[3],
                          basic_goblin_data[4])


def enemy_select(basic_goblin, medium_goblin, hard_goblin):
    enemy_list = [basic_goblin, medium_goblin, hard_goblin]
    chance = random.randint(0, 2)
    return enemy_list[chance]


enemy = enemy_select(BasicGoblin, BetaGoblin, AlphaGoblin)


# TODO: update to use objects
def loot():
    loot = ["potion", "sword", "shield"]
    chance = random.randint(0, 2)
    return loot[chance]


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


def enemy_hit_back(character_var, enemy_var, hit, chance):
    if hit:
        print("You hit the ", enemy_var.get_name(), " their health is now ", enemy_var.get_health(), ".", sep='')
    else:
        print("You did not hit the ", enemy_var.get_name(), ".", sep='')
    if enemy_var.get_luck() > chance:
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
    defend = random.randint(0,10)
    if enemy_var.get_luck() > chance:
        if defend < character_var.luck_attribute:
            print(enemy_var.get_name(), " has attacked you. However deflect some of the attack")
            character_updated_health = math.floor(character_var.get_health_points() - (enemy_var.get_strength() /
                                                                                       character_var.get_defence_points()))
            character_var.set_health_points(character_updated_health)
        else:
            print(enemy_var.name, " has attacked you.")
            character_updated_health = character_var.get_health_points() - enemy_var.get_strength()
            character_var.set_health_points(character_updated_health)
        if character_var.hp > 0:
            print("Your health is now ", character_var.get_health_points(), ".", sep='')
        else:
            game_over(character_var)


# TODO: do something with experience
def enemy_defeat(character_var, enemy_var):
    if enemy_var.get_name() == "Goblin":
        exp = 10
        print("You defeated the ", enemy_var.name, ".", sep='')
        character_var.exp = character_var.exp + exp
        print("You gained ", exp, " experience points.", sep='')
    elif enemy_var.get_name() == "Beta Goblin":
        exp = 30
        print("You defeated the ", enemy_var.name, ".", sep='')
        character_var.exp = character_var.exp + exp
        print("You gained ", exp, " experience points.", sep='')
    elif enemy_var.get_name() == "Alpha Goblin":
        exp = 55
        print("You defeated the ", enemy_var.name, ".", sep='')
        character_var.exp = character_var.exp + exp
        print("You gained ", exp, " experience points.", sep='')


def battle_state(character_var, enemy_var, surprise):
    if surprise:
        chance = random.randint(0,10)
        enemy_attack(character_var, enemy_var, chance)
    while enemy_var.get_health() > 0:
        option = input("1. Melee Attack \n2. Gun Attack\n3. Flee\n> ")
        if option == "1":
            print("You swing your sword attacking the ", enemy_var.get_name(), ".", sep='')
            hit_chance = random.randint(0, 10)
            if hit_chance < character_var.get_luck_attribute():
                enemy_var.hp = enemy_var.hp - character_var.strength_attribute
                if enemy_var.hp > 0:
                    enemy_hit_back(character_var, enemy_var, True, 5)
                else:
                    enemy_defeat(character_var, enemy_var)
                    loot_add(character_var)
                    break
            else:
                enemy_hit_back(character_var, enemy_var, False, 4)
        elif option == "2":
            print("You fired your gun attacking the ", enemy_var.name, ".", sep='')
            hit_chance = random.randint(0, 10)
            if hit_chance > 4:
                enemy_var.hp = enemy_var.hp - character_var.gun_skill_attribute
                if enemy_var.hp > 0:
                    enemy_hit_back(character_var, enemy_var, True, 6)
                else:
                    enemy_defeat(character_var, enemy_var)
                    loot_chance = random.randint(0, 10)
                    if loot_chance < character_var.luck_attribute:
                        loot_add(character_var)
                        break
                    else:
                        break
            else:
                enemy_hit_back(character_var, enemy_var, False, 3)
        elif option == "3":
            escape_chance = random.randint(0, 10)
            if escape_chance > 7:
                print("You escape battle with the ", enemy_var.name, ".", sep='')
                break
            else:
                character_var.hp = character_var.hp - enemy_var.strength_attribute
                print("You were unable to escape battle. \nHowever the ", enemy_var.name,
                      " was able to strike you.", sep='')
                if character_var.hp > 0:
                    print("Your health is now ", character_var.hp, ".", sep='')
                else:
                    game_over(character_var)
        else:
            print("Option not allowed please choose either 1, 2 or 3.")
    print("Your current Score is ", character_var.exp, sep='')


# TODO: add ability to actually use inventory items
def loot_add(character_var):
    chance = random.randint(0, 10)
    if chance < character_var.get_luck_attribute():
        loot_drop = loot()
        print("It appears to have dropped a ", loot_drop, ".", sep='')
        print("Would you like to add ", loot_drop, " to your Inventory?", sep='')
        option = input("Yes \nNo\n> ")
        if option.lower() == "yes":
            character_var.add_inventory(loot_drop)
            print(loot_drop, " was added to your inventory.", sep='')


def title_screen_selections():
    option = input("> ")
    if option.lower() == ("play"):
        class_data = hero.create_class_screen()
        character = hero.Hero(class_data[0], class_data[1], class_data[2], class_data[3], class_data[4])
        battle_state(character, enemy, True, 4)
    elif option.lower() == ("help"):
        help_menu()
        title_screen_selections()
    elif option.lower() == ("quit"):
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
