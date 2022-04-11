import random
import sys
import os
import items


class Hero:
    def __init__(self, dp, strength, gun_skill, luck, charm):
        self.name = 'Alex'
        self.exp = 0
        self.hp = 85
        self.status_effects = []
        self.inventory = [items.basic_med_pack(), items.basic_med_pack()]
        self.equipped_gun = ""
        self.equipped_melee = ""
        self.equipped_armour = ""
        self.defence_points = dp
        self.strength_attribute = strength
        self.gun_skill_attribute = gun_skill
        self.luck_attribute = luck
        self.charm_attribute = charm

    def get_name(self):
        return self.name

    def get_exp(self):
        return self.exp

    def set_exp(self, updated_exp):
        self.exp = updated_exp

    def get_status(self):
        return self.status_effects

    def set_status(self, effect):
        self.status_effects.append(effect)

    def del_status(self, item):
        self.status_effects.remove(item)

    def get_inventory(self):
        return self.inventory

    def add_inventory(self, item):
        if len(self.inventory) < 5:
            self.inventory.append(item)
        else:
            print("Your Inventory is Full. You can drop Items to make room if you so choose")

    def del_inventory(self, item):
        self.inventory.remove(item)

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
        self.hp = updated_health

    def get_defence_points(self):
        return self.defence_points

    def set_defence_points(self, dp):
        self.defence_points = dp

    def get_strength_attribute(self):
        return self.strength_attribute

    def set_strength_attribute(self, strength):
        self.strength_attribute = strength

    def get_gun_skill(self):
        return self.gun_skill_attribute

    def set_gun_skill(self, gun_skill):
        self.gun_skill_attribute = gun_skill

    def get_luck_attribute(self):
        return self.luck_attribute

    def set_luck_attribute(self, luck):
        self.luck_attribute = luck

    def get_charm_attribute(self):
        return self.charm_attribute

    def set_charm_attribute(self, charm):
        self.charm_attribute = charm


def create_class_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    print('------------------------------')
    print('-  Choose a Character Class  -')
    print('------------------------------')
    print('------------------------------')
    print('-           Merc             -')
    print('-           Soldier          -')
    print('-           Ranger           -')
    print('-           Spy              -')
    print('------------------------------')
    print('------------------------------')
    print('-           help             -')
    print('-           quit             -')
    print('------------------------------')
    return create_class_selections()


# TODO there is a bug in the else part of this
def create_class_selections():
    a = input("> ")
    if a.lower() == "merc":
        return Hero(random.randint(3, 6), random.randint(2, 5), random.randint(20, 25), random.randint(1, 7),
                    random.randint(1, 3))
    elif a.lower() == "soldier":
        return Hero(random.randint(5, 8), random.randint(10, 15), random.randint(10, 15), random.randint(1, 7),
                    random.randint(1, 5))
    elif a.lower() == "ranger":
        hero_defence = 7
        hero_strength = 25
        hero_gun = 7
        hero_luck = random.randint(1, 7)
        hero_charm = 5
        return [hero_defence, hero_strength, hero_gun, hero_luck, hero_charm]
    elif a.lower() == "spy":
        hero_defence = 6
        hero_strength = 7
        hero_gun = 7
        hero_luck = random.randint(5, 8)
        hero_charm = 7
        return [hero_defence, hero_strength, hero_gun, hero_luck, hero_charm]
    elif a.lower() == "help":
        help_menu()
        create_class_selections()
    elif a.lower() == "quit":
        sys.exit()
    else:
        print("Type the name of the Character Class you would like to play."
              "\n'Quit' to exit"
              "\nYou can type 'Help' to get details on the Character Classes.")
        create_class_selections()


def help_menu():
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
    print('------------------------------')
