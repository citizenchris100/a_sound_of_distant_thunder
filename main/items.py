
class Item:
    def __init__(self, item_name, item_value, item_attribute):
        self.name = item_name
        self.value = item_value
        self.attribute = item_attribute

    def get_item_name(self):
        return self.name

    def set_item_name(self, new_item_name):
        self.name = new_item_name

    def get_item_value(self):
        return self.value

    def set_item_value(self, new_item_value):
        self.value = new_item_value

    def get_item_attribute(self):
        return self.attribute

    def set_item_attribute(self, new_item_attribute):
        self.attribute = new_item_attribute


class Firearm(Item):
    def __init__(self, item_name, item_value, item_attribute, rounds, cap):
        super().__init__(item_name, item_value, item_attribute)
        self.ammo = rounds
        self.limit = cap

    def get_ammo(self):
        return self.ammo

    def set_ammo(self, add):
        self.ammo = min(add, self.limit)

    def get_limit(self):
        return self.limit

    def set_limit(self, up):
        self.limit = up


def small_ns_pack():
    return Item("Small Pack of Night Shadow", 1, "ns")


def medium_ns_pack():
    return Item("Medium Pack of Night Shadow", 5, "ns")


def large_ns_pack():
    return Item("Large Pack of Night Shadow", 25, "ns")


def basic_med_pack():
    return Item("Basic Med Pack", 20, "hp")


def medium_med_pack():
    return Item("Medium Med Pack", 40, "hp")


def advanced_med_pack():
    return Item("Advanced Med Pack", 80, "hp")


def small_ammo_box():
    return Item("Small Ammo Box", 6, "ammo")


def med_ammo_box():
    return Item("Medium Ammo Box", 12, "ammo")


def large_ammo_box():
    return Item("Large Ammo Box", 24, "ammo")


def pop_gun():
    return Firearm("Pop Gun", 1, "gun", 1, 1)


def basic_pistol():
    return Firearm("Basic Pistol", 15, "gun", 6, 6)


def medium_pistol():
    return Firearm("Medium Pistol", 17, "gun", 6, 6)


def advanced_pistol():
    return Firearm("Advanced Pistol", 20, "gun", 16, 16)


def large_revolver():
    return Firearm("Large Revolver", 25, "gun", 6, 6)


def basic_knife():
    return Item("Basic Knife", 10, "melee")


def medium_knife():
    return Item("Basic Knife", 14, "melee")


def large_knife():
    return Item("large Knife", 20, "melee")


def machete():
    return Item("Machete", 30, "melee")


def cologne1():
    return Item("Cologne", 1, "charm")


def cologne2():
    return Item("Fancy Cologne", 2, "charm")


def cologne3():
    return Item("Very Fancy Cologne", 3, "charm")


def charm1():
    return Item("rabbits foot", 1, "luck")


def charm2():
    return Item("four leaf clover", 2, "luck")


def charm3():
    return Item("horseshoe", 3, "luck")


def basic_body_armour():
    return Item("Basic Body Armour", 1, "armour")


def medium_body_armour():
    return Item("Medium Body Armour", 2, "armour")


def advanced_body_armour():
    return Item("Advanced Body Armour", 3, "armour")


def epic_body_armour():
    return Item("Epic Body Armour", 5, "armour")
