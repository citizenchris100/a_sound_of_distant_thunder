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

screen_width = 100
time_remaining = 10080


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


def loot():
    loot = ["potion", "sword", "shield"]
    chance = random.randint(0, 2)
    return loot[chance]


def game_over(character, score):
    if character.hp < 1:
        print("You have been defeated.")
        print("You Final score is ", score, sep='')
        name = input("Enter your Name : ")
        write_score(score, name)
        display_score()


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


def enemy_hit_back(character, enemy, hit, chance, score):
    hit_back = random.randint(0, 10)
    if hit:
        print("You hit the ", enemy.name, " their health is now ", enemy.hp, ".", sep='')
    else:
        print("You did not hit the ", enemy.name, ".", sep='')
    if hit_back > chance:
        if hit:
            print("The Enemy was able to strike back.")
            character.hp = math.floor(character.hp - (enemy.strength_attribute / character.defence_points))
        else:
            print("However they were able to strike you.")
            character.hp = character.hp - enemy.strength_attribute
        if character.hp > 0:
            print("Your health is now ", character.hp, ".", sep='')
        else:
            game_over(character, score)


def enemy_reset(enemy, score):
    if enemy.name == "Beta Goblin":
        enemy.hp = 25
        print("You defeated the ", enemy.name, ".", sep='')
        return score + 10
    elif enemy.name == "Large Beta Goblin":
        enemy.hp = 50
        print("You defeated the ", enemy.name, ".", sep='')
        return score + 30
    elif enemy.name == "Alpha Goblin":
        enemy.hp = 100
        print("You defeated the ", enemy.name, ".", sep='')
        return score + 55


def battle_state(character, enemy, score):
    vowel = 'aeiou'
    if enemy.name[0].lower() in vowel:
        start = "An "
    else:
        start = "A "
    print(start, enemy.name, " appears.", sep='')
    print("You have 3 options.")
    while enemy.hp > 0:
        option = input("1. Attack \n2. Magic\n3. Flee\n> ")
        if option == "1":
            print("You swing your sword attacking the ", enemy.name, ".", sep='')
            hit_chance = random.randint(0, 10)
            if hit_chance > 3:
                enemy.hp = enemy.hp - character.strength_attribute
                if enemy.hp > 0:
                    enemy_hit_back(character, enemy, True, 4, score)
                else:
                    score = enemy_reset(enemy, score)
                    loot_chance = random.randint(0, 10)
                    if loot_chance > 1:
                        loot_add(character)
                        break
                    else:
                        break
            else:
                enemy_hit_back(character, enemy, False, 3, score)
        elif option == "2":
            print("You cast a spell attacking the ", enemy.name, ".", sep='')
            hit_chance = random.randint(0, 10)
            if hit_chance > 4:
                enemy.hp = enemy.hp - character.gun_skill_attribute
                if enemy.hp > 0:
                    enemy_hit_back(character, enemy, True, 6, score)
                else:
                    score = enemy_reset(enemy, score)
                    loot_chance = random.randint(0, 10)
                    if loot_chance > 4:
                        loot_add(character)
                        break
                    else:
                        break
            else:
                enemy_hit_back(character, enemy, False, 3, score)
        elif option == "3":
            escape_chance = random.randint(0, 10)
            if escape_chance > 7:
                print("You escape battle with the ", enemy.name, ".", sep='')
                break
            else:
                character.hp = character.hp - enemy.strength_attribute
                print("You were unable to escape battle. \nHowever the ", enemy.name,
                      " was able to strike you.", sep='')
                if character.hp > 0:
                    print("Your health is now ", character.hp, ".", sep='')
                else:
                    game_over(character, score)
        else:
            print("Option not allowed please choose either 1, 2 or 3.")
    print("Your current Score is ", score, sep='')
    return score


def loot_add(character):
    loot_drop = loot()
    print("It appears to have dropped a ", loot_drop, ".", sep='')
    print("Would you like to add ", loot_drop, " to your Inventory?", sep='')
    option = input("Yes \nNo\n> ")
    if option.lower() == "yes":
        character.inventory.append(loot_drop)
        print(loot_drop, " was added to your inventory.", sep='')


# ____ title screen ____
def title_screen_selections(score):
    option = input("> ")
    if option.lower() == ("play"):
        class_data = hero.create_class_screen()
        character = hero.Hero(class_data[0], class_data[1], class_data[2], class_data[3], class_data[4])
        battle_state(character, enemy_select(BasicGoblin, BetaGoblin, AlphaGoblin), score)
    elif option.lower() == ("help"):
        help_menu()
        title_screen_selections(score)
    elif option.lower() == ("quit"):
        sys.exit()
    else:
        print("Type 'Play' to play the game. "
              "\n 'Quit' to exit"
              "\n You can type 'Help' at any time for assistance.")
        title_screen_selections(score)

def title_screen(score):
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
    title_screen_selections(score)

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


my_score = 0
title_screen(my_score)
