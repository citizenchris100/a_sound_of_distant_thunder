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

class_data = hero.create_class_screen()
character = hero.Hero(class_data[0], class_data[1], class_data[2], class_data[3], class_data[4])

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


def loot():
    this_loot = ["potion", "sword", "shield"]
    chance = random.randint(0, 2)
    return this_loot[chance]


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
    hit_back = random.randint(0, 10)
    if hit:
        print("You hit the ", enemy_var.name, " their health is now ", enemy_var.hp, ".", sep='')
    else:
        print("You did not hit the ", enemy_var.name, ".", sep='')
    if hit_back > chance:
        if hit:
            print("The Enemy was able to strike back.")
            character_var.hp = math.floor(character_var.hp - (enemy_var.strength_attribute / character_var.defence_points))
        else:
            print("However they were able to strike you.")
            character_var.hp = character_var.hp - enemy_var.strength_attribute
        if character_var.hp > 0:
            print("Your health is now ", character_var.hp, ".", sep='')
        else:
            game_over(character_var)


def enemy_defeat(character_var, enemy_var):
    if enemy_var.name == "Goblin":
        exp = 10
        print("You defeated the ", enemy_var.name, ".", sep='')
        character_var.exp = character_var.exp + exp
        print("You gained ", exp, " experience points.", sep='')
    elif enemy_var.name == "Beta Goblin":
        exp = 30
        print("You defeated the ", enemy_var.name, ".", sep='')
        character_var.exp = character_var.exp + exp
        print("You gained ", exp, " experience points.", sep='')
    elif enemy_var.name == "Alpha Goblin":
        exp = 55
        print("You defeated the ", enemy_var.name, ".", sep='')
        character_var.exp = character_var.exp + exp
        print("You gained ", exp, " experience points.", sep='')


def battle_state(character_var, enemy_var):
    vowel = 'aeiou'
    if enemy_var.name[0].lower() in vowel:
        start = "An "
    else:
        start = "A "
    print(start, enemy_var.name, " appears.", sep='')
    print("You have 3 options.")
    while enemy_var.hp > 0:
        option = input("1. Attack \n2. Magic\n3. Flee\n> ")
        if option == "1":
            print("You swing your sword attacking the ", enemy_var.name, ".", sep='')
            hit_chance = random.randint(0, 10)
            if hit_chance > 3:
                enemy_var.hp = enemy_var.hp - character_var.strength_attribute
                if enemy_var.hp > 0:
                    enemy_hit_back(character_var, enemy_var, True, 4)
                else:
                    enemy_defeat(character_var, enemy_var)
                    loot_chance = random.randint(0, 10)
                    if loot_chance > 1:
                        loot_add(character)
                        break
                    else:
                        break
            else:
                enemy_hit_back(character_var, enemy_var, False, 3)
        elif option == "2":
            print("You cast a spell attacking the ", enemy_var.name, ".", sep='')
            hit_chance = random.randint(0, 10)
            if hit_chance > 4:
                enemy_var.hp = enemy_var.hp - character_var.gun_skill_attribute
                if enemy_var.hp > 0:
                    enemy_hit_back(character_var, enemy_var, True, 6)
                else:
                    enemy_defeat(character_var, enemy_var)
                    loot_chance = random.randint(0, 10)
                    if loot_chance > 4:
                        loot_add(character)
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


def loot_add(character_var):
    loot_drop = loot()
    print("It appears to have dropped a ", loot_drop, ".", sep='')
    print("Would you like to add ", loot_drop, " to your Inventory?", sep='')
    option = input("Yes \nNo\n> ")
    if option.lower() == "yes":
        character_var.inventory.append(loot_drop)
        print(loot_drop, " was added to your inventory.", sep='')


def title_screen_selections(character_var, enemy_var):
    option = input("> ")
    if option.lower() == ("play"):
        battle_state(character_var, enemy_var)
    elif option.lower() == ("help"):
        help_menu()
        title_screen_selections(character_var, enemy_var)
    elif option.lower() == ("quit"):
        sys.exit()
    else:
        print("Type 'Play' to play the game. "
              "\n 'Quit' to exit"
              "\n You can type 'Help' at any time for assistance.")
        title_screen_selections(character_var, enemy_var)


def title_screen(character_var, enemy_var):
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
    title_screen_selections(character_var, enemy_var)


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


title_screen(character, enemy)
