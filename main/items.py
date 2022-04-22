
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


def basic_med_pack():
    return Item("Basic Med Pack", 20, "hp")


def medium_med_pack():
    return Item("Medium Med Pack", 40, "hp")


def advanced_med_pack():
    return Item("Advanced Med Pack", 80, "hp")


def pop_gun():
    return Item("Pop Gun", 1, "gun")


def basic_pistol():
    return Item("Basic Pistol", 5, "gun")


def medium_pistol():
    return Item("Medium Pistol", 7, "gun")


def advanced_pistol():
    return Item("Advanced Pistol", 10, "gun")


def large_revolver():
    return Item("Large Revolver", 15, "gun")


def basic_knife():
    return Item("Basic Knife", 5, "melee")


def medium_knife():
    return Item("Basic Knife", 7, "melee")


def large_knife():
    return Item("large Knife", 10, "melee")


def machete():
    return Item("Machete", 15, "melee")


def cologne():
    return Item("Cologne", 2, "charm")


def charm():
    return Item("Charm", 2, "luck")


def basic_body_armour():
    return Item("Basic Body Armour", 2, "armour")


