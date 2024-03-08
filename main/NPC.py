import random
import random_name_generator as rng
import items


class Enemy:
    def __init__(self, en_name, health, defence, strength, luck, awareness):
        self.name = en_name
        self.description = None
        self.hp = health
        self.hp_limit = health
        self.dp = defence
        self.strength_attribute = strength
        self.luck_attribute = luck
        self.inventory = []
        self.awareness_attribute = awareness

    def get_name(self):
        return self.name

    def set_name(self, new_name):
        self.name = new_name

    def get_description(self):
        return self.description

    def set_description(self, new_description):
        self.description = new_description

    def set_awareness(self, new_awareness):
        self.awareness_attribute = new_awareness

    def get_awareness(self):
        return self.awareness_attribute

    def get_health(self):
        return self.hp

    def set_health(self, new_hp):
        self.hp = new_hp

    def get_hp_limit(self):
        return self.hp_limit

    def set_hp_limit(self, new_limit):
        self.hp_limit = new_limit

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
    def __init__(self, en_name, health, defence, strength, luck, awareness, gun_skill):
        super().__init__(en_name, health, defence, strength, luck, awareness)

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
    def __init__(self, en_name, health, defence, strength, luck, awareness, gun_skill, move):
        super().__init__(en_name, health, defence, strength, luck, awareness, gun_skill)

        self.super_move = move

    def get_super_move(self):
        return self.super_move

    def set_super_move(self, new_move):
        self.super_move = new_move


class BossEnemy(Enemy):
    def __init__(self, en_name, health, defence, strength, luck, awareness, move):
        super().__init__(en_name, health, defence, strength, luck, awareness)

        self.super_move = move

    def get_super_move(self):
        return self.super_move

    def set_super_move(self, new_move):
        self.super_move = new_move


def med_pack_loot():
    return [items.medium_med_pack(), items.basic_med_pack(), items.advanced_med_pack()]


def night_shadow_loot():
    return [items.small_ns_pack(), items.medium_ns_pack(), items.large_ns_pack()]


def item_loot():
    return [items.charm1(), items.charm2(), items.cologne1(), items.cologne2(), items.charm3(), items.cologne3()]


def add_loot(enemy):
    if random.randint(0, 10) < enemy.get_luck():
        enemy.add_inventory(med_pack_loot()[random.randint(0, 2)])
    if random.randint(0, 6) < enemy.get_luck():
        enemy.add_inventory(night_shadow_loot()[random.randint(0, 2)])
    if random.randint(0, 24) < enemy.get_luck():
        enemy.add_inventory(item_loot()[random.randint(0, 5)])


def basic_goblin():
    goblin = Enemy("Goblin", random.randint(15, 30), random.randint(1, 3), random.randint(5, 10),
                   random.randint(0, 5),random.randint(1,5))
    add_loot(goblin)
    return goblin


def beta_goblin():
    goblin = Enemy("Beta Goblin", random.randint(35, 65), random.randint(4, 6), random.randint(10, 17),
                   random.randint(2, 7),random.randint(3,5))
    add_loot(goblin)
    return goblin


def alpha_goblin():
    goblin = Enemy("Alpha Goblin", random.randint(75, 100), random.randint(6, 8), random.randint(17, 25),
                   random.randint(4, 7),random.randint(5,7))
    add_loot(goblin)
    add_loot(goblin)
    return goblin


def npc(gender):
    if gender:
        npc_name = rng.generate_one(rng.Descent.ENGLISH, sex=rng.Sex.MALE)
        npc_health = random.randint(60, 100)
        npc_defence = random.randint(5, 8)
        npc_strength = random.randint(5, 25)
        if npc_strength > 16:
            npc_gun_skill = random.randint(0, 7)
        else:
            npc_gun_skill = random.randint(4, 18)
        npc_luck = random.randint(1, 7)
        return Human(npc_name, npc_health, npc_defence, npc_strength, npc_gun_skill, npc_luck,random.randint(1,7))
    else:
        npc_name = rng.generate_one(rng.Descent.ENGLISH, sex=rng.Sex.FEMALE)
        npc_health = random.randint(60, 100)
        npc_defence = random.randint(3, 6)
        npc_strength = random.randint(2, 17)
        if npc_strength > 13:
            npc_gun_skill = random.randint(0, 7)
        else:
            npc_gun_skill = random.randint(4, 18)
        npc_luck = random.randint(1, 7)
        return Human(npc_name, npc_health, npc_defence, npc_strength, npc_gun_skill, npc_luck,random.randint(1,7))


def boat_captain():
    captain = npc(True)
    captain.set_description("""A gruff older man in his mid 50\'s or there about. A no nonsense looking guy.""")
    captain.set_dialog({
        "Disembark": """Captain: You're ready? Ok. So we're going to get you onto one of our small inflatable crafts. 
Don't worry it has a motor. I'd suggest you take care of it. We will be back to the precise coordinates we drop 
you off at to pick you back up in aproximately 12 hours. We can wait for you, but not forever. You need to be 
back here in 12 hours or find another ride home.""",
        "Storm": """Captain: This system has been heading our way from the east. It's looking to be a bad one. 
Whatever you have to do on that Island. I'd suggest doing it fast. You won't want to be out here once this 
torm hits.""",
        "Island": """Captain: Don't know much about it. A buddy of mine was making pretty good money ferrying people 
to and from the island.\nHe mentioned that he stopped getting ferry jobs about a month ago."""
    })
    captain.set_equipped_gun(items.large_revolver())
    captain.set_equipped_armour(items.medium_body_armour())
    captain.set_inventory([items.medium_med_pack(), items.cologne1(), items.med_ammo_box()])
    captain.set_name("Boat Captain")
    # TODO debug health.
    captain.set_health(5)
    return captain


def deck_hand01():
    deck_hand = npc(True)
    deck_hand.set_equipped_melee(items.basic_knife())
    add_loot(deck_hand)
    deck_hand.set_name("Deck Hand 1")
    return deck_hand


def deck_hand02():
    deck_hand = npc(True)
    deck_hand.set_equipped_melee(items.basic_knife())
    add_loot(deck_hand)
    deck_hand.set_name("Deck Hand 2")
    return deck_hand


def light_house_keeper():
    light_hk = npc(True)
    light_hk.set_equipped_gun(items.large_revolver())
    light_hk.set_equipped_armour(items.epic_body_armour())
    light_hk.set_inventory([items.basic_med_pack(), items.basic_med_pack(), items.basic_med_pack(),
                            items.medium_med_pack(), items.medium_med_pack(), items.medium_med_pack(),
                            items.advanced_med_pack(), items.advanced_med_pack(), items.advanced_med_pack(),
                            items.medium_pistol(), items.advanced_pistol(), items.medium_knife(),
                            items.large_knife(), items.basic_body_armour(), items.medium_body_armour(),
                            items.advanced_body_armour(), items.cologne1(), items.charm1(), items.large_ammo_box()])
    light_hk.set_name("Lighthouse Keeper")
    return light_hk
