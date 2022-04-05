# a sound of distant thunder
# by christopher manning

import time
import cmd
import textwrap
import sys
import os
import random
import math

screen_width = 100
time_remaining = 10080

# ____ player setup ____
class Player:
    def __init__(self):
        self.name = 'Alex'
        self.hp = 100
        self.dp = 7
        self.mp = 10
        self.str = 17
        self.status_effects = []
        self.location = 'Boat'


myPlayer = Player()


# _____enemies _____
class BasicGoblin(object):
    name = "Beta Goblin"
    hp = 25
    dp = 3
    mp = 4
    str = 13


class MediumGoblin(object):
    name = "Large Beta Goblin"
    hp = 50
    dp = 6
    mp = 7
    str = 14

class HardGoblin(object):
    name = "Alpha Goblin"
    hp = 100
    dp = 7
    mp = 10
    str = 17


def enemy_select(basic_goblin, mediumgoblin, hardgoblin):
    enemylist = [basic_goblin, mediumgoblin, hardgoblin]
    chance = random.randint(0, 2)
    return enemylist[chance]


def loot():
    loot = ["potion", "sword", "shield"]
    chance = random.randint(0, 2)
    return loot[chance]

def battlestate():
    enemy = enemy_select(BasicGoblin, MediumGoblin, HardGoblin)
    print("A ", enemy.name, " appears")
    print("you have 3 options")
    while enemy.hp > 0:
        option = input("1. Attack \n2. Magic\n3. Flee\n> ")
        if option == "1":
            print("You swing your sword attacking the", enemy.name)
            hit_chance = random.randint(0, 10)
            hit_back = random.randint(0, 10)
            if hit_chance > 3:
                enemy.hp = enemy.hp - myPlayer.str
                print("You hit the ", enemy.name, "their health is now ", enemy.hp)
                if enemy.hp > 0:
                    if hit_back > 4:
                        updated_player_hp = myPlayer.hp - (enemy.str / myPlayer.dp)
                        myPlayer.hp = math.floor(updated_player_hp)
                        print("The ", enemy.name, " struck back.\nYour health is now", myPlayer.hp)
                else:
                    enemy_reset(enemy)
                    loot_chance = random.randint(0, 10)
                    if loot_chance > 4:
                        loot_drop = loot()
                        print("It appears to have dropped a ", loot_drop, ".")
                        break
                    else:
                        break
            else:
                print("You did not hit the ", enemy.name)
                hit_back = random.randint(0, 10)
                if hit_back > 3:
                    myPlayer.hp = myPlayer.hp - enemy.str
                    print("However the ", enemy.name, "was able to strike you.\nYour health is now ", myPlayer.hp, ".")

        elif option == "2":
            print("You cast a spell attacking the", enemy.name)
            hit_chance = random.randint(0, 10)
            hit_back = random.randint(0, 10)
            if hit_chance > 4:
                enemy.hp = enemy.hp - myPlayer.mp
                print("You hit the ", enemy.name, "their health is now ", enemy.hp)
                if enemy.hp > 0:
                    if hit_back > 4:
                        updated_player_hp = myPlayer.hp - (enemy.str / myPlayer.dp)
                        myPlayer.hp = math.floor(updated_player_hp)
                        print("The ", enemy.name, " struck back.\nYour health is now", myPlayer.hp)
                else:
                    enemy_reset(enemy)
                    loot_chance = random.randint(0, 10)
                    if loot_chance > 4:
                        loot_drop = loot()
                        print("It appears to have dropped a ", loot_drop, ".")
                        break
                    else:
                        break
            else:
                print("You did not hit the ", enemy.name)
                hit_back = random.randint(0, 10)
                if hit_back > 3:
                    myPlayer.hp = myPlayer.hp - enemy.str
                    print("However the ", enemy.name, "was able to strike you.\nYour health is now ", myPlayer.hp, ".")
        elif option == "3":
            escap_chance = random.randint(0, 10)
            if escap_chance > 7:
                print("You escape battle with the ", enemy.name)
                break
            else:
                myPlayer.hp = myPlayer.hp - enemy.str
                print("You were unable to escape battle. \nHowever the", enemy.name, "was able to strike.\n"
                                                                                     "Your health is now ", myPlayer.hp)
        else:



def enemy_reset(enemy):
    if enemy.name == "Beta Goblin":
        enemy.hp = 25
    elif enemy.name == "Large Beta Goblin":
        enemy.hp = 50
    elif enemy.name == "Alpha Goblin":
        enemy.hp = 100
    print("You defeated the ", enemy.name, ".")


# ____ title screen ____
def title_screen_selections():
    option = input("> ")
    if option.lower() == ("play"):
        battlestate()
        battlestate()
        battlestate()
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
    print('- "Attach <someone/thing>    -')
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


# _____ game functionality _____
# def start_game():

# _____ map _____
NAVIGATE = 'go to'
LOOK = 'look at'
TAKE = "take"

title_screen()

