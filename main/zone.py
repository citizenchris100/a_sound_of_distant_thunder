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
    desc_value = """A creaky old dirty ship like this is not my ideal method of travel. I guess I shouldn't complain
    though. This gig came up last minute and the paycheck is insane. However I'm a firm believer that if its too 
    good to be true it probably is. Some money people want me to get control of this island. Some kind of manufacturing
    facility. The dossier here has the details. It's looking like we're getting pretty close. The captain is 
    approaching. Looks like its time to disembark."""
    captain = enemy.npc()
    boat_items = [items.basic_med_pack(), items.basic_pistol(), items.basic_knife()]
    return Zone("Boat", desc_value, captain, boat_items)



