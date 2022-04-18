# a sound of distant thunder
# by christopher manning

import sys
import os
import textwrap
import hero
import enemy
import battle_system
import random
import zone


def use_textwrap(value):
    wrapper = textwrap.TextWrapper(width=100)
    word_list = wrapper.wrap(text=value)
    for element in word_list:
        print(element)


def start():
    os.system('cls' if os.name == 'nt' else 'clear')
    boat = zone.boat_start()
    use_textwrap(boat.get_description()["initial"])
    print('------------------------------')
    print('------------------------------')
    game(boat)


def game(boat):
    prompt = input("1. Read Dossier\n2. Speak to the Captain\n3. Look Around the Ship\n4. Inventory\n5. Help\n> ")
    if "read" in prompt.lower() or prompt == "1":
        use_textwrap(boat.get_description()["dossier"])
        print('------------------------------')
        game(boat)
    elif "speak" in prompt.lower() or prompt == "2":
        print('Alex: "Looks like we\'re nearly there Captain"')
        print('Captain: "Indeed we are. That dock is in no condition for a ship of this size. You\'ll have to '
              'disembark on one of our small inflatable crafts. Let me know when you\'re ready to head out '
              'or if you have any other questions."')
        print('------------------------------')
        speak = input("1. Disembark\n2. The Storm\n3. The Island")

def title_screen_selections():
    option = input("> ")
    if option.lower() == "play" or option == "1":
        hero.create_class_screen()
        character = hero.class_selection()
        start()
        #battle_system.battle_state(character, [enemy.basic_goblin(), enemy.beta_goblin(), enemy.alpha_goblin()]
        #                           [random.randint(0, 2)])
    elif option.lower() == "help" or option == "2":
        help_menu()
        title_screen_selections()
    elif option.lower() == "quit" or option == "3":
        sys.exit()
    else:
        print("Type '1' or 'Play' to play the game. "
              "\n You can type '2' or 'Help' for assistance."
              "\n '3' or 'Quit' to exit")
        title_screen_selections()


def title_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    print('------------------------------')
    print('- A Sound of Distant Thunder -')
    print('------------------------------')
    print('------------------------------')
    print('-   by Christopher Manning   -')
    print('------------------------------')
    print('------------------------------')
    print('-          1. Play           -')
    print('-          2. Help           -')
    print('-          3. Quit           -')
    print('------------------------------')
    print('------------------------------')
    title_screen_selections()


def help_menu():
    print('------------------------------')
    print('------------------------------')
    print('-         How to Play        -')
    print('------------------------------')
    print('------------------------------')
    print('- Type either the Number or  -')
    print('- the command next to the    -')
    print('- corresponding prompt.      -')
    print('------------------------------')
    print('------------------------------')
    print('- Common prompts             -')
    print('------------------------------')
    print('------------------------------')
    print('- "Go to <location>":        -')
    print('-  this will move you to a   -')
    print('-  new location              -')
    print('------------------------------')
    print('- "Look at <something>":     -')
    print('-  this will give you        -')
    print('-  details                   -')
    print('------------------------------')
    print('- "Take <something>":        -')
    print('-  this will add the item    -')
    print('-  o your inventory          -')
    print('------------------------------')
    print('- "Speak to <someone>":      -')
    print('-  enter into a              -')
    print('-  conversation with         -')
    print('-  an NPC                    -')
    print('------------------------------')
    print('- "<Weapon> Attack":         -')
    print('-  Attack a person or thing  -')
    print('-  with the corresponding    -')
    print('-  weapon                    -')
    print('------------------------------')
    print('- "Inventory":               -')
    print('-  view your current         -')
    print('-  inventory to either use or-')
    print('-  equip items               -')
    print('------------------------------')
    print('- "Flee"                     -')
    print('-   :Attempt to retreat      -')
    print('-    from battle / attack    -')
    print('------------------------------')
    print('------------------------------')


title_screen()
