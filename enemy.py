import random
import names
import items


class Enemy:
    def __init__(self, en_name, health, defence, strength, luck):
        self.name = en_name
        self.hp = health
        self.dp = defence
        self.strength_attribute = strength
        self.luck_attribute = luck
        self.inventory = []

    def get_name(self):
        return self.name

    def set_name(self, new_name):
        self.name = new_name

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


def npc():
    gender = bool(random.getrandbits(1))
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
        return [npc_name, npc_health, npc_defence, npc_strength, npc_gun_skill, npc_luck]
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
        return [npc_name, npc_health, npc_defence, npc_strength, npc_gun_skill, npc_luck]

