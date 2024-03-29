import random
import sys
import os
import items


class Hero:
    def __init__(self, dp, strength, gun_skill, luck, charm, stealth):
        self.name = 'Alex'
        self.exp = 0
        self.lvl = 0
        self.hp = 65
        self.hp_limit = 65
        self.status_effects = []
        self.inventory = [items.basic_med_pack()]
        self.inventory_limit = 5
        self.equipped_gun = None
        self.equipped_melee = None
        self.equipped_armour = None
        self.defence_points = dp
        self.strength_attribute = strength
        self.gun_skill_attribute = gun_skill
        self.luck_attribute = luck
        self.charm_attribute = charm
        self.stealth_attribute = stealth
        self.location = None

    def get_name(self):
        return self.name

    def get_exp(self):
        return self.exp

    def set_exp(self, updated_exp):
        self.exp = updated_exp

    def get_lvl(self):
        return self.lvl

    def up_lvl(self):
        self.lvl = self.lvl + 1

    def get_status(self):
        return self.status_effects

    def set_status(self, effect):
        self.status_effects.append(effect)

    def del_status(self, item):
        self.status_effects.remove(item)

    def get_inventory(self):
        return self.inventory

    def add_inventory(self, item):
        if len(self.inventory) < self.inventory_limit:
            self.inventory.append(item)
            print('------------------------------')
            print(item.get_item_name(), " added to your inventory.", sep='')
        else:
            print('------------------------------')
            print("Your Inventory is Full. You can discard Items to make room if you so choose")

    def del_inventory(self, item):
        del self.inventory[item]

    def get_inventory_limit(self):
        return self.inventory_limit

    def set_inventory_limit(self, new_limit):
        self.inventory_limit = self.inventory_limit + new_limit

    def get_equipped_gun(self):
        return self.equipped_gun

    def set_equipped_gun(self, gun):
        self.equipped_gun = gun

    def get_equipped_melee(self):
        return self.equipped_melee

    def set_equipped_melee(self, melee):
        self.equipped_melee = melee

    def get_equipped_armour(self):
        return self.equipped_armour

    def set_equipped_armour(self, armour):
        self.equipped_armour = armour

    def get_health_points(self):
        return self.hp

    def set_health_points(self, updated_health):
        self.hp = min(updated_health, self.hp_limit)

    def get_hp_limit(self):
        return self.hp_limit

    def set_hp_limit(self, new_limit):
        self.hp_limit = new_limit

    def get_defence_points(self):
        return self.defence_points

    def set_defence_points(self, dp):
        self.defence_points = min(dp, 7)

    def get_strength_attribute(self):
        return self.strength_attribute

    def set_strength_attribute(self, strength):
        self.strength_attribute = min(strength, 35)

    def get_gun_skill(self):
        return self.gun_skill_attribute

    def set_gun_skill(self, gun_skill):
        self.gun_skill_attribute = min(gun_skill, 35)

    def get_luck(self):
        return self.luck_attribute

    def set_luck_attribute(self, luck):
        self.luck_attribute = min(luck, 7)

    def get_charm_attribute(self):
        return self.charm_attribute

    def set_charm_attribute(self, charm):
        self.charm_attribute = min(charm, 7)

    def get_stealth_attribute(self):
        return self.stealth_attribute

    def set_stealth_attribute(self, stealth):
        self.charm_attribute = min(stealth, 7)

    def get_location(self):
        return self.location

    def set_location(self, new_location):
        self.location = new_location


def class_selection():
    os.system('cls' if os.name == 'nt' else 'clear')
    while True:
        print('------------------------------')
        print('-  Choose a Character Class  -')
        print('------------------------------')
        print('------------------------------')
        print('-          1. Merc           -')
        print('-          2. Soldier        -')
        print('-          3. Ranger         -')
        print('-          4. Spy            -')
        print('-          5. Random         -')
        print('------------------------------')
        print('------------------------------')
        print('-          6. help           -')
        print('-          7. quit           -')
        print('------------------------------')
        print('------------------------------')
        a = input("> ")
        if a.lower() == "merc" or a == "1":
            return Hero(random.randint(3, 6), random.randint(2, 5), random.randint(20, 25), random.randint(2, 4),
                             random.randint(1, 3), random.randint(5, 7))
        elif a.lower() == "soldier" or a == "2":
            return Hero(random.randint(5, 8), random.randint(10, 15), random.randint(10, 15), random.randint(2, 4),
                             random.randint(1, 5), random.randint(1, 5))
        elif a.lower() == "ranger" or a == "3":
            return Hero(random.randint(4, 7), random.randint(20, 25), random.randint(4, 7), random.randint(2, 4),
                             random.randint(1, 5), random.randint(3, 6))
        elif a.lower() == "spy" or a == "4":
            return Hero(random.randint(1, 4), random.randint(4, 7), random.randint(4, 7), random.randint(5, 7),
                             random.randint(5, 7), random.randint(4, 7))
        elif a.lower() == "random" or a == "5":
            return Hero(random.randint(1, 7), random.randint(4, 20), random.randint(4, 20), random.randint(1, 7),
                             random.randint(1, 7), random.randint(1, 7))
        elif a.lower() == "help" or a == "6":
            print('------------------------------')
            print('-About the Character Classes -')
            print('------------------------------')
            print('------------------------------')
            print('-Merc: balanced more towards -')
            print('-the use of Guns.            -')
            print('------------------------------')
            print('-Soldier: less focussed and  -')
            print('-more well rounded           -')
            print('------------------------------')
            print('-Ranger: balanced towards    -')
            print('-the use of Melee weapons.   -')
            print('------------------------------')
            print('-Spy: relies more upon wit   -')
            print('-and charm                   -')
            print('------------------------------')
            print('-Random: a character build   -')
            print('-with somewhat random stats  -')
            print('------------------------------')
            print('------------------------------')
        elif a.lower() == "quit" or a == "7":
            sys.exit()
        else:
            print("Type the name of the Character Class you would like to play."
                  "\n'Quit' to exit"
                  "\nYou can type 'Help' to get details on the Character Classes.")
