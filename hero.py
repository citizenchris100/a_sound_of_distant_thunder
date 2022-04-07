import random
import time
import os
from pprint import pprint


class Hero:
    def __init__(self, hp, dp, strength, gun_skill, luck, charm):
        self.name = 'Alex'
        self.exp = 0
        self.status_effects = []
        self.inventory = []
        self.equipped_gun = ""
        self.equipped_melee = ""
        self.equipped_armour = ""
        self.health_points = hp
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

    def set_status(self, updated_status):
        self.status_effects = updated_status

    def get_inventory(self):
        return self.inventory

    def add_inventory(self, item):
        self.inventory.append(item)

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
        return self.health_points

    def set_health_points(self, updated_health):
        self.health_points = updated_health

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

    def set_luck_attribute(self, luck):
        self.luck_attribute = luck

def create_class():
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
    a = input("> ")


def help_menu():
    os.system('cls' if os.name == 'nt' else 'clear')
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







