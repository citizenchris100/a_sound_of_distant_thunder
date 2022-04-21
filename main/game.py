# a sound of distant thunder
# by christopher manning

import sys
import os
import textwrap
import hero
import zone
import battle_system


def use_textwrap(value):
    wrapper = textwrap.TextWrapper(width=100)
    word_list = wrapper.wrap(text=value)
    for element in word_list:
        print(element)


def start(character):
    os.system('cls' if os.name == 'nt' else 'clear')
    boat = zone.boat_start()
    use_textwrap(boat.get_description()["initial"])
    print('------------------------------')
    print('------------------------------')
    boat_zone(character)


def boat_zone(character):
    prompt = input("1. Read Dossier\n2. Speak to the Captain\n3. Look Around the Ship\n4. Inventory\n5. Help\n> ")
    boat = zone.boat_start()
    if "read" in prompt.lower() or prompt == "1":
        os.system('cls' if os.name == 'nt' else 'clear')
        use_textwrap(boat.get_description()["dossier"])
        print('------------------------------')
        boat_zone(character)
    elif "speak" in prompt.lower() or prompt == "2":
        speak_to_captain(character, boat)
    elif "look" in prompt.lower() or prompt == "3":
        os.system('cls' if os.name == 'nt' else 'clear')
        use_textwrap(boat.get_description()["surroundings"])
        print('------------------------------')
        boat_prompt = input("1. Look at the Case\n2. Speak to the Captain\n3. Inventory\n4. Return\n5. Help\n> ")
        if "look" in boat_prompt.lower() or boat_prompt == "1":
            print("As I approach the case one of the deck hands stops what he's doing to speak to me.")
            print("Deck Hand: \"Your agency had us prepare this for you.\nThey weren't specific about what was"
                  "needed. So its just our general survival kit. Take a look.\"\n"
                  "The deck hand opens the case.\nInside there appears to be pretty much what he said.\n"
                  "Standard med kit and a 9mm pistol and hunting knife.\n")
            print('------------------------------')
            option = input("Would you like to add the items from the case to your Inventory?\n1. Yes \n2. No\n> ")
            if option.lower() == "yes" or option == "1":
                character.get_inventory().extend(boat.get_items())
                print("The case items have been added to your inventory.\nYou can view your inventory by"
                      "choosing the 'Inventory' prompt.")
                boat_zone(character)
            elif option.lower() == "no" or option == "2":
                print("Maybe I don't need this stuff")
                boat_zone(character)
            else:
                print("Invalid Option")
                boat_zone(character)
    elif "inventory" in prompt.lower() or prompt == "4":
        battle_system.inventory(character)
        boat_zone(character)
    elif "help" in prompt.lower() or prompt == "5":
        help_menu()
        boat_zone(character)
    else:
        print("Invalid Option")
        boat_zone(character)


def speak_to_captain(character, boat):
    captain = boat.get_characters()[0]
    deck_hand_01 = boat.get_characters()[1]
    deck_hand_02 = boat.get_characters()[2]
    os.system('cls' if os.name == 'nt' else 'clear')
    print('Alex: "Looks like we\'re nearly there Captain"')
    print('Captain: "Indeed we are. That dock is in no condition for a ship of this size.\nYou\'ll have to '
          'disembark on one of our small inflatable crafts.\nLet me know when you\'re ready to head out\n'
          'or if you have any other questions."')
    print('------------------------------')
    speak = input("1. Disembark\n2. The Storm\n3. The Island\n4. Attack\n5. Return\n6. Help\n> ")
    if "disembark" in speak.lower() or speak == "1":
        print(captain.get_dialog()["Disembark"])
        print('------------------------------')
        small_boat = """I board the small inflatable craft the Captain prepared for me. It did in fact have a small
        4 stroke motor. Which should be enough to get me to the Island from here. However in the distance I can 
        see a light house. Which had it been functioning would be useful on a pitch black night such as this.
        Sort of makes you wonder how bad things could have gone on this island for the light house to just be
        sitting there like that. No light, no nothing. In any case, I have a decision to make. Head to the dock
        or check out this ominous Light House."""
        use_textwrap(small_boat)
        disembark(boat, character)
    elif "storm" in speak.lower() or speak == "2":
        print(captain.get_dialog()["Storm"])
        boat_zone(character)
    elif "island" in speak.lower() or speak == "3":
        print(captain.get_dialog()["Island"])
        boat_zone(character)
    elif "attack" in speak.lower() or speak == "4":
        battle_system.battle_state(character, captain, False)
        print('------------------------------')
        battle_system.battle_state(character, deck_hand_01, True)
        print('------------------------------')
        battle_system.battle_state(character, deck_hand_02, True)
        print('------------------------------')
        disembark(boat, character)
    else: 
        print("Invalid Option")
        speak_to_captain(captain, boat)


def disembark(boat, character):
    option = input("1. Light House\n2. Dock\n3. Return\n4. Help\n> ")
    if "light" in option.lower() or option == "1":
        os.system('cls' if os.name == 'nt' else 'clear')
        use_textwrap(zone.lighthouse().get_description()["initial"])
        print('------------------------------')
        print('------------------------------')
        light_house(character)
    elif "dock" in option.lower() or option == "1":
        os.system('cls' if os.name == 'nt' else 'clear')
        use_textwrap(zone.dock().get_description()["initial"])
        print('------------------------------')
        print('------------------------------')
        dock(character)
    elif "return" in option.lower() or option == "3":
        speak_to_captain(character, boat)
    elif "help" in option.lower() or option == "4":
        help_menu()
        speak_to_captain(character, boat)
    else:
        print("Invalid Option")


def light_house(character):
    print("foo")
    
    
def dock(character):
    print("bar")


def title_screen_selections():
    option = input("> ")
    if option.lower() == "play" or option == "1":
        hero.create_class_screen()
        character = hero.class_selection()
        start(character)
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
    print('- "(Weapon) Attack":         -')
    print('-  Attack a person or thing  -')
    print('-  with the corresponding    -')
    print('-  weapon                    -')
    print('------------------------------')
    print('- "Inventory":               -')
    print('-  view your current         -')
    print('-  inventory to either use or-')
    print('-  equip items               -')
    print('------------------------------')
    print('- "Flee":                    -')
    print('-   Attempt to retreat       -')
    print('-   from battle / attack     -')
    print('------------------------------')
    print('- "Return":                  -')
    print('-   Go back to the previous  -')
    print('-   set of prompts           -')
    print('------------------------------')
    print('------------------------------')


title_screen()
