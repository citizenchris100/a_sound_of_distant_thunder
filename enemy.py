import random
import names


class Enemy:
    def __init__(self, en_name, health, defence, strength, luck):
        self.name = en_name
        self.hp = health
        self.dp = defence
        self.strength_attribute = strength
        self.luck_attribute = luck

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


class Human(Enemy):
    def __init__(self, en_name, health, defence, strength, luck, gun_skill):
        super().__init__(en_name, health, defence, strength, luck)

        self.inventory = []
        self.gun_skill_attribute = gun_skill
        self.equipped_gun = []
        self.equipped_melee = []
        self.equipped_armour = []
        self.happy = 0

    def get_inventory(self):
        return self.inventory

    def add_inventory(self, new):
        self.inventory.append(new)

    def del_inventory(self, item):
        self.inventory.remove(item)

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


def basic_goblin():
    goblin_name = "Goblin"
    goblin_hp = random.randint(15, 30)
    goblin_dp = random.randint(1, 3)
    goblin_strength = random.randint(5, 10)
    goblin_luck = random.randint(0, 3)
    return [goblin_name, goblin_hp, goblin_dp, goblin_strength, goblin_luck]


def beta_goblin():
    goblin_name = "Beta Goblin"
    goblin_hp = random.randint(35, 65)
    goblin_dp = random.randint(4, 6)
    goblin_strength = random.randint(10, 17)
    goblin_luck = random.randint(1, 5)
    return [goblin_name, goblin_hp, goblin_dp, goblin_strength, goblin_luck]


def alpha_goblin():
    goblin_name = "Alpha Goblin"
    goblin_hp = random.randint(75, 100)
    goblin_dp = random.randint(6, 8)
    goblin_strength = random.randint(17, 25)
    goblin_luck = random.randint(4, 7)
    return [goblin_name, goblin_hp, goblin_dp, goblin_strength, goblin_luck]


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

