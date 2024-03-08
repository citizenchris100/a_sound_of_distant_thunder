# a sound of distant thunder
# by christopher manning

# TODO consequence of killing the captain will be bad ending  no way back.

from Util import use_textwrap
import sys
import os
import hero
import battle_system
import inventory
import NPC
import random
import dialog
import dialog_system
import items
def boat_zone(character):
    while True:
        print('------------------------------')
        prompt = input("1. Read Dossier\n2. Speak to the Captain\n3. Look Around the Ship\n4. Inventory\n5. Help\n> ")
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
            speak_to_captain(character)
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
                        character.get_inventory().extend([items.basic_pistol(), items.basic_knife(), items.basic_med_pack(), items.small_ammo_box()])
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


def speak_to_captain(character):
    hd1 = [dialog.HeroDialog(False,"Nearly there", """Looks like we\'re nearly there Captain""",None),
           dialog.HeroDialog(False,"The Storm","""Looks like we have a pretty bas system headed
our way.""",None),
           dialog.HeroDialog(False,"The Island?","""What can you tell me
about this island Captain?""",None),
           dialog.HeroDialog(False,"Attack","""I'm sorry to have to do this Captain.""",None),
           dialog.HeroDialog(False,"Disembark","""I think
I'm ready to head out Captain.""",None)]
    rsp1 = [dialog.HeroDialog(False,"Nearly there", """Indeed we are. That dock is in no condition for a
ship of this size. You\'ll have to disembark on one of our small inflatable crafts. Let me know when you\'re ready to 
head out or if you have any other questions.""",None),
           dialog.HeroDialog(False,"The Storm","""This system has been heading our way from the east. 
It's looking to be a bad one. Whatever you have to do on that Island. I'd suggest doing it fast. You won't want to be 
out here once this torm hits.""",None),
            dialog.HeroDialog(False,"The Island?","""Don't know much about it. A buddy of mine was 
making pretty good money ferrying people to and from the island.\nHe mentioned that he stopped getting ferry jobs 
about a month ago.""",None),
            dialog.HeroDialog(False,"Attack","""What the hell do you think you're doing?""",None),
            dialog.HeroDialog(False,"Disembark","""You're ready? Ok. So we're going to get you onto one of our small inflatable crafts. 
Don't worry it has a motor. I'd suggest you take care of it. We will be back to the precise coordinates we drop 
you off at to pick you back up in aproximately 12 hours. We can wait for you, but not forever. You need to be 
back here in 12 hours or find another ride home.""",None)]
    dialog_system.conversation_system(character,NPC.boat_captain(),hd1,rsp1,[
        {"label" : "Attack",
         "action": disembark,
         "op1": True,
         },
        {"label": "Disembark",
         "action": disembark,
         "op1": False,
         }
    ])


def disembark(character, attack):
    print('------------------------------')
    if attack:
        battle_system.battle_state(character, NPC.boat_captain(), False, False)
        print('------------------------------')
        battle_system.battle_state(character, NPC.deck_hand01(), True, False)
        print('------------------------------')
        battle_system.battle_state(character, NPC.deck_hand02(), True, False)
        print('------------------------------')
        use_textwrap("""Confidentiality is always of paramount concern on these assignments. Though The Captain seemed
to know very little about the client's facility. It was enough. He and the crew had to go. 
I board the small inflatable craft the Captain prepared for me. It did in fact have a small 4 
stroke motor. Which should be enough to get me to the Island dock from here. However in the distance I can see a light house.
Which had it been functioning would be useful on a pitch black night such as this.Sort of makes you wonder how bad 
things could have gone on this island for the light house to just be sitting there like that. No light, no nothing. 
In any case, I have a decision to make. Head to the dock or check out this ominous Light House.""")
    else:
        use_textwrap("""I board the small inflatable craft the Captain prepared for me. It did in fact have a small 4 
stroke motor. Which should be enough to get me to the Island dock from here. However in the distance I can see a light house.
Which had it been functioning would be useful on a pitch black night such as this.Sort of makes you wonder how bad 
things could have gone on this island for the light house to just be sitting there like that. No light, no nothing. 
In any case, I have a decision to make. Head to the dock or check out this ominous Light House.""")
    option = input("1. Light House\n2. Dock\n3. Help\n> ")
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
        use_textwrap("dock description")
        dock(character, True)
    elif "help" in option.lower() or option == "4":
        help_menu()
        speak_to_captain(character)
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
        battle_system.battle_state(character, NPC.basic_goblin(), True,False)
        print('------------------------------')
        battle_system.battle_state(character, NPC.basic_goblin(), True,False)
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
            lighthouse_inside(character, True)
        elif "explore" in option.lower() or option == "2":
            print('------------------------------')
            use_textwrap("""There is a path nearby that most likely leads to the dock.""")
            print('------------------------------')
            option2 = input("1. Take Path to Dock\n2. Enter Lighthouse\n3. Inventory\n4. Help\n> ")
            if "enter" in option2.lower() or option2 == "2":
                lighthouse_inside(character, True)
            elif "take" in option2.lower() or option2 == "1":
                use_textwrap("""The path to the dock is about as dark and dreary as the rest of this place. It's just
as inviting as well.""")
                if random.randint(0, 12) < character.get_luck():
                    print('------------------------------')
                    battle_system.battle_state(character, NPC.basic_goblin(), True,False)
                    print('------------------------------')
                    battle_system.battle_state(character, NPC.basic_goblin(), True,False)
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


def lighthouse_inside(character, first):
    if first:
        explore = False
        print('------------------------------')
        use_textwrap("""I attempt to turn the handle to the lighthouse door. It's locked. Of course it is.
I'm a crafty sort so picking this lock shouldn't be an issue. However I do not have anything to pick it with. So that's 
not really an option. Just left of the door is a small intercom box. I press the button which makes a kind of buzzing 
sound as I press it.
Lighthouse Keeper: Who is it? What do you want? Go away!
Alex: Look I just got here. My name is Alex. I was sent by the people 
that fund this facility. I'm kind of in need of some assistance. 
Lighthouse Keeper: A company man eh?
Alex: Not exactly. They hired me to...see what was happening here. Or rather they opened a contract with my 
agency and my agency gave me the gig. Could you let me in. I was just attacked by some...I don't know what...a couple 
things and...
Lighthouse Keeper: Attacked? Oh why didn't you say so. Come on in.
The door buzzes. I open it and enter into the foyer. Whoever the voice was on the other end of that intercom wasn't
the tidiest of fellows. It's a mess in here. Junk is everywhere. Though some of it does appear like it could be useful.
The rest is just trash. In the center of the foyer is a spiral staircase. That must be where he's lurking. From the 
looks of it he just discards his trash down here. One giant trash can.""")
        while True:
            print('------------------------------')
            option = input("1. Ascend Staircase\n2. Explore\n3. Inventory\n4. Return\n5. Help\n> ")
            if "ascend" in option.lower() or option == "1":
                print('------------------------------')
                lighthouse_den(character,True)
            elif "explore" in option.lower() or option == "2":
                print('------------------------------')
                if not explore:
                    use_textwrap("""In hopes of finding something useful amongst all this junk I begin to dig around. I 
carefully sift through the trash that seems to cover the entire floor of the foyer.""")
                    if random.randint(0, 12) < character.get_luck():
                        use_textwrap("""Wouldn't you know it. This wasn't such a bad idea after all. I found
something.""")
                        NPC.add_loot(character)
                    else:
                        use_textwrap("""Of course there isn't anything to be found in this garbage. Normally I'd 
console myself by saying 'It can't hurt to look'. However in this case I'm pretty certain I could have caught a 
disease from that crap. Probably a good idea to just move on.""")
                    explore = True
                else:
                    use_textwrap("I've already rummaged through this crap enough. Doubtful I'll find anything.")
            elif "inventory" in option.lower() or option == "3":
                inventory.inventory(character)
            elif "help" in option.lower() or option == "5":
                help_menu()
            elif "return" in option.lower() or option == "4":
                lighthouse_exterior(character, False)
            else:
                use_textwrap("""Not a valid entry. Please choose from the following options by entering the command
                            or entering the corresponding number.""")
    else:
        print("not ready yet")
        
def lighthouse_den(character, first):
    hd1 = [dialog.HeroDialog(False,"I need help.", """Like I said earlier I was just attacked by some 
kind of ...thing. My boats motor is on the fritz. Maybe you have some parts that could help me fix it?""",0),
           dialog.HeroDialog(False, "Let me in now!", """Come on old timer let me in now! 
This isn't a game I was just attacked and in need of some assistance.""", 1),
           dialog.HeroDialog(False, "Let me in or I'll bust this door down!",
                             """This is stupid. I just told you I was attacked. Open up now or I might just 
 have to bust this door down""", 2)
           ]
    res1 = dialog.responses(
        dialog.ResponseDialog(False, "Come on in", """Alright I'll let you in. But no funny business.""",
                              None),
        dialog.ResponseDialog(False,"Fuck you", """Hah! Fuck you. I look out for one person. Me!. Also
let me tell you something right now. If you have any intentions of making it off this island alive you had 
better work on your manners. Because you're not doing it without my help I'll tell you that.""",
                              [dialog.HeroDialog(False, "I'm sorry", """Look, you're right.
I do need you're help ok. I'm sorry. I've been through a lot. What with getting 
attacked by that...purple goblin thing. I guess you could say I'm a tad rattled.""", 0),
                               dialog.HeroDialog(False, "Give me a break.", """Come on man. Look
I get it. You're in a position to fuck with me. I need you more than you need me 
yadda yadda yadda. Would you just let me in for gods sakes.""", 1),
                               dialog.HeroDialog(False,"Fuck You!", """Fuck me? Fuck you Old Man!
You're dead.""",2)])
    )
    res2 = dialog.responses(
        dialog.ResponseDialog(False, "Come on in", """Alright I'll let you in. But no funny business.""",
                              None),
        dialog.ResponseDialog(False, "Come on in", """Well Sonny Boy I guess I'm just going ot have to 
come out there and kill you..""",
                              None),
    )
    lhk = NPC.light_house_keeper()
    if first:
        explore = False
        print('------------------------------')
        use_textwrap("""With each step up that creaky old spiral stair case I questioned my judgement more and more. 
What the hell was I doing here? No amount of money is worth this. Is it? At the top of the stairs was a small 
landing filled with, you guessed it, more trash. A single door sat in the middle of the far wall of the landing.
It looked to be a pretty heavy duty wooden door. With all manor of what could only be described as claw marks
all along the surface. As if some animal or maybe those purple goblins had been trying desperately to get in.
Obviously the door was stirdy and those things not strong enough to bust it down. I aproach""")
        while True:
            print('------------------------------')
            option = input("1. Knock on door\n2. Explore\n3. Inventory\n4. Return\n5. Help\n> ")
            if "knock" in option.lower() or option == "1":
                print('------------------------------')
                use_textwrap("""I'm guessing whomever I spoke to on that intercom downstairs has to be behind this door.
I approach causiously amd lightly knock on the door.""")
                s1 =dialog_system.persuasion_system(character, lhk, hd1, res1, 6)
                if s1 is None:
                    break
                elif s1["succeed"]:
                    print('------------------------------')
                    print("You have successfully made it in")
                else:
                    print('------------------------------')
                    s2 = dialog_system.persuasion_system(character, lhk, s1["hero_responses"], res2, s1["score"])
                    if s2["succeed"]:
                        print("You have successfully made it in")
                    else:
                        print('------------------------------')
                        battle_system.battle_state(character, lhk, True, False)
                        print('------------------------------')
                        print('------------------------------')
                        print("Game Over")
                        print('------------------------------')
                        print('------------------------------')
            elif "explore" in option.lower() or option == "2":
                print('------------------------------')
                if not explore:
                    use_textwrap("""In hopes of finding something useful amongst all this junk I begin to dig around. I 
carefully sift through the trash that seems to cover the entire floor of the landing.""")
                    if random.randint(0, 12) < character.get_luck():
                        use_textwrap("""Wouldn't you know it. This wasn't such a bad idea after all. I found
something.""")
                        NPC.add_loot(character)
                    else:
                        use_textwrap("""Of course there isn't anything to be found in this garbage. Normally I'd 
console myself by saying 'It can't hurt to look'. However in this case I'm pretty certain I could have caught a 
disease from that crap. Probably a good idea to just move on.""")
                    explore = True
                else:
                    use_textwrap("I've already rummaged through this crap enough. Doubtful I'll find anything.")
            elif "inventory" in option.lower() or option == "3":
                inventory.inventory(character)
            elif "help" in option.lower() or option == "5":
                help_menu()
            elif "return" in option.lower() or option == "4":
                lighthouse_inside(character, False)
            else:
                use_textwrap("""Not a valid entry. Please choose from the following options by entering the command
or entering the corresponding number.""")


def dock(character, first):
    if first:
        use_textwrap(boat_broke)
        use_textwrap("dock text")
        use_textwrap("""""")


def title_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    print('------------------------------')
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
    while True:
        option = input("> ")
        if option.lower() == "play" or option == "1":
            character = hero.class_selection()
            print('------------------------------')
            print('------------------------------')
            print('--Your Character\'s Stats-----')
            print('-Health: ', character.get_health_points())
            print('-Defence: ', character.get_defence_points())
            print('-Melee Attack: ', character.get_strength_attribute())
            print('-Gun Skill: ', character.get_gun_skill())
            print('-Luck: ', character.get_luck())
            print('-Charm: ', character.get_charm_attribute())
            print('-Stealth: ', character.get_stealth_attribute())
            print('------------------------------')
            print('------------------------------')
            print('-         Chapter 1          -')
            print('------------------------------')
            print('------------------------------')
            use_textwrap("""That sound of distant thunder was low and ominous. Like some kind of a warning. It was clearly 
telling me to turn back. Was I going to listen? Hell no. The money was speaking louder than the thunder. Money 
can make you do stupid things. Like board a creaky dirty old ship at 9pm on a Thursday evening. A Thursday 
evening that seemed intent on levying some kind of storm upon all of us. I should be home drinking. Instead I’m 
here on the deck of a ship heading toward the thunder. Suffice is to say this gig came up last minute and the 
paycheck is insane. Some money people want me to get control of this  island. Some kind of manufacturing 
facility. The dossier here has the details. For this kind of money, I'm more than willing to oblige. Seems easy 
enough. However I'm a firm believer that  if its too good to be true it probably is. It's looking like  we're 
getting pretty close. The captain is approaching. Looks like its time to disembark.""")
            print('------------------------------')
            print('------------------------------')
            boat_zone(character)
        elif option.lower() == "help" or option == "2":
            help_menu()
        elif option.lower() == "quit" or option == "3":
            sys.exit()
        else:
            print("Type '1' or 'Play' to play the game. "
                  "\n You can type '2' or 'Help' for assistance."
                  "\n '3' or 'Quit' to exit")


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
