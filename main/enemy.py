import random
import names
import items


class Enemy:
    def __init__(self, en_name, health, defence, strength, luck):
        self.name = en_name
        self.description = None
        self.hp = health
        self.dp = defence
        self.strength_attribute = strength
        self.luck_attribute = luck
        self.inventory = []

    def get_name(self):
        return self.name

    def set_name(self, new_name):
        self.name = new_name

    def get_description(self):
        return self.description

    def set_description(self, new_description):
        self.description = new_description

    def get_health(self):
        return self.hp

    def set_health(self, new_hp):
        self.hp = new_hp

    def get_defence(self):
        return self.dp

    def set_defence(self, new_dp):
        self.dp = new_dp

    def get_strength(self):
        return self.strength_attribute

    def set_strength(self, update_strength):
        self.strength_attribute = update_strength

    def get_luck(self):
        return self.luck_attribute

    def set_luck(self, update_luck):
        self.luck_attribute = update_luck

    def get_inventory(self):
        return self.inventory

    def set_inventory(self, new_inventory):
        self.inventory = new_inventory

    def add_inventory(self, new):
        self.inventory.append(new)

    def del_inventory(self, item):
        self.inventory.remove(item)


class Human(Enemy):
    def __init__(self, en_name, health, defence, strength, luck, gun_skill):
        super().__init__(en_name, health, defence, strength, luck)

        self.gun_skill_attribute = gun_skill
        self.equipped_gun = None
        self.equipped_melee = None
        self.equipped_armour = None
        self.happy = 0
        self.dialog = None

    def get_gun_skill(self):
        return self.gun_skill_attribute

    def set_gun_attribute(self, gun_skill):
        self.gun_skill_attribute = gun_skill

    def get_equipped_gun(self):
        return self.equipped_gun

    def set_equipped_gun(self, new_gun):
        self.equipped_gun = new_gun

    def get_equipped_melee(self):
        return self.equipped_melee

    def set_equipped_melee(self, new_melee):
        self.equipped_melee = new_melee

    def get_equipped_armour(self):
        return self.equipped_armour

    def set_equipped_armour(self, new_armour):
        self.equipped_armour = new_armour

    def get_happy(self):
        return self.happy

    def set_happy(self, add, value):
        if add:
            self.happy = self.happy + value
        else:
            self.happy = self.happy - value

    def get_dialog(self):
        return self.dialog

    def set_dialog(self, new_dialog):
        self.dialog = new_dialog


class BossHuman(Human):
    def __init__(self, en_name, health, defence, strength, luck, gun_skill, move):
        super().__init__(en_name, health, defence, strength, luck, gun_skill)

        self.super_move = move

    def get_super_move(self):
        return self.super_move

    def set_super_move(self, new_move):
        self.super_move = new_move


class BossEnemy(Enemy):
    def __init__(self, en_name, health, defence, strength, luck, move):
        super().__init__(en_name, health, defence, strength, luck)

        self.super_move = move

    def get_super_move(self):
        return self.super_move

    def set_super_move(self, new_move):
        self.super_move = new_move


def med_pack_loot():
    return [items.medium_med_pack(), items.basic_med_pack(), items.advanced_med_pack()]


# TODO : add descriptions to goblins
def basic_goblin():
    goblin = Enemy("Goblin", random.randint(15, 30), random.randint(1, 3), random.randint(5, 10), random.randint(0, 5))
    goblin.add_inventory(med_pack_loot()[random.randint(0, 2)])
    return goblin


def beta_goblin():
    goblin = Enemy("Beta Goblin", random.randint(35, 65), random.randint(4, 6), random.randint(10, 17),
                   random.randint(1, 7))
    goblin.add_inventory(med_pack_loot()[random.randint(0, 2)])
    return goblin


def alpha_goblin():
    goblin = Enemy("Alpha Goblin", random.randint(75, 100), random.randint(6, 8), random.randint(17, 25),
                   random.randint(4, 8))
    goblin.add_inventory(med_pack_loot()[random.randint(0, 2)])
    return goblin


def npc(gender):
    if gender:
        npc_name = names.get_full_name(gender='male')
        npc_health = random.randint(60, 100)
        npc_defence = random.randint(5, 8)
        npc_strength = random.randint(5, 25)
        if npc_strength > 16:
            npc_gun_skill = random.randint(0, 7)
        else:
            npc_gun_skill = random.randint(4, 18)
        npc_luck = random.randint(1, 10)
        return Human(npc_name, npc_health, npc_defence, npc_strength, npc_gun_skill, npc_luck)
    else:
        npc_name = names.get_full_name(gender='female')
        npc_health = random.randint(60, 100)
        npc_defence = random.randint(3, 6)
        npc_strength = random.randint(2, 17)
        if npc_strength > 13:
            npc_gun_skill = random.randint(0, 7)
        else:
            npc_gun_skill = random.randint(4, 18)
        npc_luck = random.randint(1, 10)
        return Human(npc_name, npc_health, npc_defence, npc_strength, npc_gun_skill, npc_luck)


def boat_captain():
    captain = npc(True)
    captain.set_description("""A gruff older man in his mid 50\'s or there about. A no nonsense looking guy.""")
    captain.set_dialog({
        "Disembark": "Captain: You're ready? Ok. So we're going to get you onto one of our small inflatable crafts. Don't worry it has a motor. I'd suggest you take care of it. We will be back to the precise coordinates we drop you off at to pick you back up in aproximately 12 hours. We can wait for you, but not forever. You need to be back here in 12 hours or find another ride home.",
        "Storm": "Captain: This system has been heading our way from the east.\nIt's looking to be a bad one. Whatever you have"
                 "to do on that Island\nI'd suggest doing it fast.\nYou won't want to be out here once this storm hits.",
        "Island": "Captain: Don't know much about it. A buddy of mine was making pretty\ngood money ferrying people to and from"
                  "the island.\nHe mentioned that he stopped getting ferry jobs about a month ago."
    })
    captain.set_equipped_gun(items.large_revolver())
    captain.set_inventory([items.medium_med_pack(), items.cologne()])
    captain.set_name("Boat Captain")
    return captain


def deck_hand01():
    deck_hand = npc(True)
    deck_hand.set_equipped_melee(items.basic_knife())
    deck_hand.set_inventory([items.basic_med_pack()])
    deck_hand.set_name("Deck Hand")
    return deck_hand


def deck_hand02():
    deck_hand = npc(True)
    deck_hand.set_equipped_melee(items.basic_knife())
    deck_hand.set_inventory([items.basic_med_pack()])
    deck_hand.set_name("Deck Hand")
    return deck_hand

def ligh_house_keeper():
    lhk = npc(True)
