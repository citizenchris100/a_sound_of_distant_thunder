# a sound of distant thunder
# by christopher manning

# TODO refactor to NOT use zone objects
import sys
import os
import textwrap
import hero
import zone
import battle_system
import inventory
import enemy


def use_textwrap(value):
    dedented_text = textwrap.dedent(value).strip()
    print(dedented_text)


def start(character):
    boat = zone.boat_start()
    print('------------------------------')
    print('-         Chapter 1          -')
    print('------------------------------')
    use_textwrap(boat.get_description()["initial"])
    print('------------------------------')
    print('------------------------------')
    boat_zone(character)


def boat_zone(character):
    while True:
        prompt = input("1. Read Dossier\n2. Speak to the Captain\n3. Look Around the Ship\n4. Inventory\n5. Help\n> ")
        boat = zone.boat_start()
        print('------------------------------')
        if "read" in prompt.lower() or prompt == "1":
            print('------------------------------')
            use_textwrap("""A brief Dossier put together by my boss. 
The Client: Venture Capital Consortium. This is big money 
for our agency Alex, don't fuck this up. 
The Job: Our Client has put significant money into this 
small upstart Pharma company. I couldn't get much info on the company. It all looks pretty hush 
hush. What I could gather from the Client is that the company produces some kind of experimental 
pharmaceutical. The production facility is on a small Caribbean island I'd never heard of. 
Our client has lost contact with the island. Seems all communication has been cut off. Sounds like 
before things went dark there had been some drama related to unauthorized use of the pharmaceutical.
Your mission if you choose to accept it. You'd better accept it. For this kind of money you'd be 
crazy not to. In any case the ask is simple. Restore communications to the island and return with 
information as to what the hell is going on.""")
            print('------------------------------')
        elif "speak" in prompt.lower() or prompt == "2":
            speak_to_captain(character, boat)
        elif "look" in prompt.lower() or prompt == "3":
            print('------------------------------')
            use_textwrap("""This boat or ship rather is pretty beat up. I'm guessing this was all we could get with
such short notice.""")
            print('------------------------------')
            if len(battle_system.check_ammo(character)) == 0:
                use_textwrap("""There is a case near by. Probably the supplies prepared for me. Might
be a good idea to take a look. They could help""")
                print('------------------------------')
                boat_prompt = input("1. Look at the Case\n2. Return\n3. Help\n> ")
                if "look" in boat_prompt.lower() or boat_prompt == "1":
                    print('------------------------------')
                    print("As I approach the case one of the deck hands stops what he's doing to speak to me.")
                    print('------------------------------')
                    use_textwrap("""Deck Hand: Your agency had us prepare this for you. They weren't specific about what was 
needed. So its just our general survival kit. Take a look.""")
                    print('------------------------------')
                    use_textwrap("""The deck hand opens the case. Inside there appears to be pretty much what he said. Standard 
med kit and a 9mm pistol and hunting knife.""")
                    print('------------------------------')
                    option = input(
                        "Would you like to add the items from the case to your Inventory?\n1. Yes \n2. No\n> ")
                    if option.lower() == "yes" or option == "1":
                        character.get_inventory().extend(boat.get_items())
                        print('------------------------------')
                        use_textwrap("""The case items have been added to your inventory. You can view your inventory by 
choosing the 'Inventory' prompt.""")
                        print('------------------------------')
                    elif option.lower() == "no" or option == "2":
                        print("Maybe I don't need this stuff")
                    else:
                        print('------------------------------')
                        use_textwrap("""Not a valid entry. Please choose from the following options by entering the command
or entering the corresponding number.""")
                        print('------------------------------')
                elif "return" in boat_prompt.lower() or boat_prompt == "2":
                    boat_zone(character)
                elif "help" in boat_prompt.lower() or boat_prompt == "3":
                    help_menu()
                else:
                    print('------------------------------')
                    use_textwrap("""Not a valid entry. Please choose from the following options by entering the command
or entering the corresponding number.""")
                    print('------------------------------')
        elif "inventory" in prompt.lower() or prompt == "4":
            inventory.inventory(character)
        elif "help" in prompt.lower() or prompt == "5":
            help_menu()
        else:
            print('------------------------------')
            use_textwrap("""Not a valid entry. Please choose from the following options by entering the command
or entering the corresponding number.""")
            print('------------------------------')


def speak_to_captain(character, boat):
    captain = boat.get_characters()[0]
    deck_hand_01 = boat.get_characters()[1]
    deck_hand_02 = boat.get_characters()[2]
    print('------------------------------')
    print('Alex: "Looks like we\'re nearly there Captain"')
    use_textwrap("""Captain: "Indeed we are. That dock is in no condition for a ship of this size. You\'ll have to 
disembark on one of our small inflatable crafts. Let me know when you\'re ready to head out or if you have any other 
questions.""")
    while True:
        print('------------------------------')
        speak = input("1. Disembark\n2. The Storm\n3. The Island\n4. Attack\n5. Return\n6. Help\n> ")
        if "disembark" in speak.lower() or speak == "1":
            use_textwrap(captain.get_dialog()["Disembark"])
            print('------------------------------')
            use_textwrap("""I board the small inflatable craft the Captain prepared for me. It did in fact have a small 4 
stroke motor. Which should be enough to get me to the Island from here. However in the distance I can see a light house.
Which had it been functioning would be useful on a pitch black night such as this.Sort of makes you wonder how bad 
things could have gone on this island for the light house to just be sitting there like that. No light, no nothing. 
In any case, I have a decision to make. Head to the dock or check out this ominous Light House.""")
            disembark(boat, character)
        elif "storm" in speak.lower() or speak == "2":
            print(captain.get_dialog()["Storm"])
        elif "island" in speak.lower() or speak == "3":
            print(captain.get_dialog()["Island"])
        elif "attack" in speak.lower() or speak == "4":
            battle_system.battle_state(character, captain, False)
            print('------------------------------')
            battle_system.battle_state(character, deck_hand_01, True)
            print('------------------------------')
            battle_system.battle_state(character, deck_hand_02, True)
            print('------------------------------')
            disembark(boat, character)
        elif "return" in speak.lower() or speak == "5":
            boat_zone(character)
        elif "help" in speak.lower() or speak == "6":
            help_menu()
        else:
            print('------------------------------')
            use_textwrap("""Not a valid entry. Please choose from the following options by entering the command
or entering the corresponding number.""")
            print('------------------------------')


def disembark(boat, character):
    print('------------------------------')
    option = input("1. Light House\n2. Dock\n3. Return\n4. Help\n> ")
    if "light" in option.lower() or option == "1":
        os.system('cls' if os.name == 'nt' else 'clear')
        print('------------------------------')
        print('-         Chapter 2          -')
        print('------------------------------')
        lighthouse_exterior(character, True)
    elif "dock" in option.lower() or option == "1":
        print('------------------------------')
        print('-         Chapter 2          -')
        print('------------------------------')
        use_textwrap(zone.dock().get_description()["initial"])
        dock(character, True)
    elif "return" in option.lower() or option == "3":
        speak_to_captain(character, boat)
    elif "help" in option.lower() or option == "4":
        help_menu()
        speak_to_captain(character, boat)
    else:
        print("Invalid Option")


boat_broke = """As I make my way ashore the boat engine starts to make a sound that can't be good. 
I'm no mechanic but I'm guessing either I need to get this thing fixed or find another way back to the pickup point. 
Wonderful. This gig is already starting off well."""


def lighthouse_exterior(character, first):
    if first:
        print('------------------------------')
        use_textwrap(boat_broke)
        print('------------------------------')
        use_textwrap("""The light house was sitting atop a tiny peninsula about 100 feet or so above the shore.
I walked the shoreline around the peninsula until I found a stair case built into the side of the cliff wall. A couple
minutes later I'm up the stairs. Up close this place wasn't exactly the most inviting looking spot I've ever seen. 
However that hasn't ever stopped me before. 
The air is thick with humidity and a slight mist from the beach below. Moonlight is about all I have to light my way. 
It suddenly occurred to me how oddly quiet it was. I seemed to be the only living thing out and about on this island. 
Every step pierced the silence and I'd be lying if I said I didn't feel a little vulnerable out here. Everything about 
this place screams spooky vibes.
As I near what appears to be the main entrance of The Lighthouse two figures approach from left. I ready my weapon.

Alex: Hello(?) Who goes there?

I got nothing in response and as they crept nearer I decided to raise my weapon.

Alex: I'm not looking for trouble ok. My boat engine is in need of repair and...

Just that moment I got a good look at these....things. They might have been human at one point however that seems to 
have been a while ago. They were incredibly emaciated walked with a peculiar hunched posture. 
I'm not sure if it was the moonlight or what but their skin was wrinkly and almost purple. No hair to speak of.
The most disturbing quality was what appeared to be an elongated snout or jaw. Though admittedly tt was hard to make out
before the attack came.""")
        print('------------------------------')
        battle_system.battle_state(character, enemy.basic_goblin(), True)
        print('------------------------------')
        battle_system.battle_state(character, enemy.basic_goblin(), True)
        print('------------------------------')
        use_textwrap("""After I catch my breath and calm down a bit I'm able to get a better look at these...things.
Whatever they are they aren't human. Taking this job is starting to seem like a very bad idea. Regardless of how good
the money is. No amount of money is worth getting your head ripped off by some purple goblin. I continue around the
the Lighthouse until I come to what has to be the entrance.""")
        print('------------------------------')
    else:
        use_textwrap("""Outside the Lighthouse. Just as ominous and creepy as it ever was.""")
    while True:
        option = input("1. Enter Lighthouse\n2. Explore\n3. Inventory\n4. Help\n> ")
        if "enter" in option.lower() or option == "1":
            print("foo")
        elif "explore" in option.lower() or option == "2":
            use_textwrap("""There is a path nearby that most likely leads to the dock.""")
            option2 = input("1. Take Path to Dock\n2. Enter Lighthouse\n3. Inventory\n4. Help\n> ")
            if "enter" in option.lower() or option == "2":
                print("foo")
            elif "take" in option.lower() or option == "1":
                use_textwrap("""The path to the dock is about as dark and dreary as the rest of this place. It's just
as inviting as well.""")
                dock(character, False)
            elif "inventory" in option.lower() or option == "3":
                inventory.inventory(character)
            elif "help" in option.lower() or option == "4":
                help_menu()
            else:
                use_textwrap("""Not a valid entry. Please choose from the following options by entering the command
            or entering the corresponding number.""")
        elif "inventory" in option.lower() or option == "3":
            inventory.inventory(character)
        elif "help" in option.lower() or option == "4":
            help_menu()
        else:
            use_textwrap("""Not a valid entry. Please choose from the following options by entering the command
or entering the corresponding number.""")


def dock(character, first):
    if first:
        use_textwrap(boat_broke)
        use_textwrap(zone.lighthouse().get_description()["initial"])
        use_textwrap("""""")


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
