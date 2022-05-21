import enemy
import items


class Zone:
    def __init__(self, zone_name, desc, char, zone_items):
        self.name = zone_name
        self.description = desc
        self.characters = char
        self.items = zone_items

    def get_name(self):
        return self.name

    def set_name(self, new_name):
        self.name = new_name

    def get_description(self):
        return self.description

    def set_description(self, new_desc):
        self.description = new_desc

    def get_characters(self):
        return self.characters

    def set_characters(self, update_char):
        self.characters = update_char

    def add_character(self, add_char):
        self.characters.append(add_char)

    def del_character(self, del_char):
        del self.characters[del_char]

    def get_items(self):
        return self.items

    def set_items(self, update_items):
        self.items = update_items

    def add_items(self, add_items):
        self.items.append(add_items)

    def del_items(self, del_items):
        del self.items[del_items]


class StoryZone(Zone):
    def __init__(self, zone_name, desc, char, zone_items, zone_control, zone_missions, zone_affiliation):
        super().__init__(zone_name, desc, char, zone_items)
        self.control = zone_control
        self.missions = zone_missions
        self.affiliation = zone_affiliation

    def get_zone_control(self):
        return self.control

    def set_zone_control(self, new_zone_control):
        self.control = new_zone_control

    def get_zone_missions(self):
        return self.missions

    def set_zone_missions(self, update_zone_missions):
        self.missions = update_zone_missions

    def add_zone_missions(self, add_zone_missions):
        self.missions.append(add_zone_missions)

    def del_zone_missions(self, del_zone_missions):
        del self.missions[del_zone_missions]

    def get_affiliation(self):
        return self.affiliation

    def set_affiliation(self, new_affiliation):
        self.affiliation = new_affiliation


def boat_start():
    desc = {"initial":
            """That sound of distant thunder was low and ominous. Like some kind of a warning. It was clearly 
telling me to turn back. Was I going to listen? Hell no. The money was speaking louder than the thunder. Money 
can make you do stupid things. Like board a creaky dirty old ship at 9pm on a Thursday evening. A Thursday 
evening that seemed intent on levying some kind of storm upon all of us. I should be home drinking. Instead I’m 
here on the deck of a ship heading toward the thunder. Suffice is to say this gig came up last minute and the 
paycheck is insane. Some money people want me to get control of this  island. Some kind of manufacturing 
facility. The dossier here has the details. For this kind of money, I'm more than willing to oblige. Seems easy 
enough. However I'm a firm believer that  if its too good to be true it probably is. It's looking like  we're 
getting pretty close. The captain is approaching. Looks like its time to disembark.""",
            "dossier":
                """A brief Dossier put together by my boss. 
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
information as to what the hell is going on.""",
            "surroundings": """This boat or ship rather is pretty beat up. I'm guessing this was all we could get with
such short notice."""
            }
    boat_characters = [enemy.boat_captain(), enemy.deck_hand01(), enemy.deck_hand02()]
    boat_item = [items.basic_pistol(), items.basic_knife(), items.basic_med_pack(), items.small_ammo_box()]
    return Zone("Boat", desc, boat_characters, boat_item)


def lighthouse():
    desc = {
        "initial": ""
    }
    lighthouse_characters = [enemy.light_house_keeper(), enemy.basic_goblin(), enemy.basic_goblin()]
    items = []
    return Zone("Lighthouse", desc, lighthouse_characters, items)


def dock():
    desc = {
        "initial": """"""
    }
