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


def basic_goblin(game_items_data):
    goblin = Enemy("Goblin", random.randint(15, 30), random.randint(1, 3), random.randint(5, 10),
                   random.randint(0, 5), random.randint(1, 5))
    # Goblins don't have equipment in the original code, so no equipment setup here from data
    add_loot(goblin)  # Loot is still hardcoded for now
    return goblin


def beta_goblin(game_items_data):
    goblin = Enemy("Beta Goblin", random.randint(35, 65), random.randint(4, 6), random.randint(10, 17),
                   random.randint(2, 7), random.randint(3, 5))
    # Beta Goblins don't have equipment in the original code either
    add_loot(goblin)  # Loot is still hardcoded for now
    return goblin


def alpha_goblin(game_items_data):
    goblin = Enemy("Alpha Goblin", random.randint(75, 100), random.randint(6, 8), random.randint(17, 25),
                   random.randint(4, 7), random.randint(5, 7))
    # Alpha Goblins also don't have equipment in the original code
    add_loot(goblin)  # Loot is still hardcoded for now (twice)
    return goblin


def npc(gender):
    if gender:
        npc_name = rng.generate_one(rng.Descent.ENGLISH, sex=rng.Sex.MALE)
        npc_health = random.randint(50, 100)
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
        npc_health = random.randint(40, 80)
        npc_defence = random.randint(3, 6)
        npc_strength = random.randint(2, 17)
        if npc_strength > 13:
            npc_gun_skill = random.randint(0, 7)
        else:
            npc_gun_skill = random.randint(4, 18)
        npc_luck = random.randint(1, 7)
        return Human(npc_name, npc_health, npc_defence, npc_strength, npc_gun_skill, npc_luck,random.randint(1,7))


def boat_captain(game_items_data):
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
    
    large_revolver_data = game_items_data.get("large_revolver")
    if large_revolver_data:
        captain.set_equipped_gun(items.Firearm( 
            item_name=large_revolver_data.get("name"),
            item_value=large_revolver_data.get("value"),
            item_attribute=large_revolver_data.get("item_type"),
            rounds=large_revolver_data.get("attributes", {}).get("clip_size"), 
            cap=large_revolver_data.get("attributes", {}).get("clip_size") 
        ))
    else:
        print("Warning: 'large_revolver' data not found.")

    medium_body_armour_data = game_items_data.get("medium_body_armour")
    if medium_body_armour_data:
        captain.set_equipped_armour(items.Item(
            item_name=medium_body_armour_data.get("name"),
            item_value=medium_body_armour_data.get("value"),
            item_attribute=medium_body_armour_data.get("item_type")
        ))
    else:
        print("Warning: 'medium_body_armour' data not found.")

    captain_inventory_items = []
    med_med_pack_data = game_items_data.get("medium_med_pack")
    if med_med_pack_data:
        captain_inventory_items.append(items.Item(
            item_name=med_med_pack_data.get("name"),
            item_value=med_med_pack_data.get("value"),
            item_attribute=med_med_pack_data.get("item_type")
        ))
    cologne1_data = game_items_data.get("cologne1")
    if cologne1_data:
        captain_inventory_items.append(items.Item(
            item_name=cologne1_data.get("name"),
            item_value=cologne1_data.get("value"),
            item_attribute=cologne1_data.get("item_type")
        ))
    med_ammo_box_data = game_items_data.get("med_9mm_ammo_box") 
    if med_ammo_box_data:
        captain_inventory_items.append(items.Item(
            item_name=med_ammo_box_data.get("name"),
            item_value=med_ammo_box_data.get("value"),
            item_attribute=med_ammo_box_data.get("item_type")
        ))
    captain.set_inventory(captain_inventory_items)
    captain.set_name("Boat Captain")
    # TODO debug health.
    captain.set_health(75)
    return captain


def deck_hand01(game_items_data):
    deck_hand = npc(True)

    basic_knife_data = game_items_data.get("basic_knife")
    if basic_knife_data:
        deck_hand.set_equipped_melee(items.Item(
            item_name=basic_knife_data.get("name"),
            item_value=basic_knife_data.get("value"),
            item_attribute=basic_knife_data.get("item_type")
        ))
    else:
        print("Warning: 'basic_knife' data not found.")

    add_loot(deck_hand)  # Loot is still hardcoded for now, we can make loot data-driven later too
    deck_hand.set_name("Deck Hand 1")
    return deck_hand


def deck_hand02(game_items_data):
    deck_hand = npc(True)

    basic_knife_data = game_items_data.get("basic_knife")
    if basic_knife_data:
        deck_hand.set_equipped_melee(items.Item(
            item_name=basic_knife_data.get("name"),
            item_value=basic_knife_data.get("value"),
            item_attribute=basic_knife_data.get("item_type")
        ))
    else:
        print("Warning: 'basic_knife' data not found.")

    add_loot(deck_hand)  # Loot is still hardcoded for now
    deck_hand.set_name("Deck Hand 2")
    return deck_hand


def light_house_keeper(game_items_data):
    light_hk = npc(True)

    large_revolver_data = game_items_data.get("large_revolver")
    if large_revolver_data:
        light_hk.set_equipped_gun(items.Firearm(
            item_name=large_revolver_data.get("name"),
            item_value=large_revolver_data.get("value"),
            item_attribute=large_revolver_data.get("item_type"),
            rounds=large_revolver_data.get("attributes", {}).get("clip_size"),
            cap=large_revolver_data.get("attributes", {}).get("clip_size")
        ))
    else:
        print("Warning: 'large_revolver' data not found.")

    epic_body_armour_data = game_items_data.get("epic_body_armour")
    if epic_body_armour_data:
        light_hk.set_equipped_armour(items.Item(
            item_name=epic_body_armour_data.get("name"),
            item_value=epic_body_armour_data.get("value"),
            item_attribute=epic_body_armour_data.get("item_type")
        ))
    else:
        print("Warning: 'epic_body_armour' data not found.")

    light_hk_inventory_items = []
    basic_med_pack_data = game_items_data.get("basic_med_pack")
    if basic_med_pack_data:
        for _ in range(3):  # Add 3 basic med packs from data
            light_hk_inventory_items.append(items.Item(
                item_name=basic_med_pack_data.get("name"),
                item_value=basic_med_pack_data.get("value"),
                item_attribute=basic_med_pack_data.get("item_type")
            ))
    medium_med_pack_data = game_items_data.get("medium_med_pack")
    if medium_med_pack_data:
        for _ in range(3):  # Add 3 medium med packs from data
            light_hk_inventory_items.append(items.Item(
                item_name=medium_med_pack_data.get("name"),
                item_value=medium_med_pack_data.get("value"),
                item_attribute=medium_med_pack_data.get("item_type")
            ))
    advanced_med_pack_data = game_items_data.get("advanced_med_pack")
    if advanced_med_pack_data:
        for _ in range(3):  # Add 3 advanced med packs from data
            light_hk_inventory_items.append(items.Item(
                item_name=advanced_med_pack_data.get("name"),
                item_value=advanced_med_pack_data.get("value"),
                item_attribute=advanced_med_pack_data.get("item_type")
            ))
    medium_pistol_data = game_items_data.get("medium_pistol")
    if medium_pistol_data:
        light_hk_inventory_items.append(items.Firearm(
            item_name=medium_pistol_data.get("name"),
            item_value=medium_pistol_data.get("value"),
            item_attribute=medium_pistol_data.get("item_type"),
            rounds=medium_pistol_data.get("attributes", {}).get("clip_size"),
            cap=medium_pistol_data.get("attributes", {}).get("clip_size")
        ))
    advanced_pistol_data = game_items_data.get("advanced_pistol")
    if advanced_pistol_data:
        light_hk_inventory_items.append(items.Firearm(
            item_name=advanced_pistol_data.get("name"),
            item_value=advanced_pistol_data.get("value"),
            item_attribute=advanced_pistol_data.get("item_type"),
            rounds=advanced_pistol_data.get("attributes", {}).get("clip_size"),
            cap=advanced_pistol_data.get("attributes", {}).get("clip_size")
        ))
    medium_knife_data = game_items_data.get("medium_knife")
    if medium_knife_data:
        light_hk_inventory_items.append(items.Item(
            item_name=medium_knife_data.get("name"),
            item_value=medium_knife_data.get("value"),
            item_attribute=medium_knife_data.get("item_type")
        ))
    large_knife_data = game_items_data.get("large_knife")
    if large_knife_data:
        light_hk_inventory_items.append(items.Item(
            item_name=large_knife_data.get("name"),
            item_value=large_knife_data.get("value"),
            item_attribute=large_knife_data.get("item_type")
        ))
    basic_body_armour_data = game_items_data.get("basic_body_armour")
    if basic_body_armour_data:
        light_hk_inventory_items.append(items.Item(
            item_name=basic_body_armour_data.get("name"),
            item_value=basic_body_armour_data.get("value"),
            item_attribute=basic_body_armour_data.get("item_type")
        ))
    medium_body_armour_data = game_items_data.get("medium_body_armour")
    if medium_body_armour_data:
        light_hk_inventory_items.append(items.Item(
            item_name=medium_body_armour_data.get("name"),
            item_value=medium_body_armour_data.get("value"),
            item_attribute=medium_body_armour_data.get("item_type")
        ))
    advanced_body_armour_data = game_items_data.get("advanced_body_armour")
    if advanced_body_armour_data:
        light_hk_inventory_items.append(items.Item(
            item_name=advanced_body_armour_data.get("name"),
            item_value=advanced_body_armour_data.get("value"),
            item_attribute=advanced_body_armour_data.get("item_type")
        ))
    cologne1_data = game_items_data.get("cologne1")
    if cologne1_data:
        light_hk_inventory_items.append(items.Item(
            item_name=cologne1_data.get("name"),
            item_value=cologne1_data.get("value"),
            item_attribute=cologne1_data.get("item_type")
        ))
    charm1_data = game_items_data.get("charm1")
    if charm1_data:
        light_hk_inventory_items.append(items.Item(
            item_name=charm1_data.get("name"),
            item_value=charm1_data.get("value"),
            item_attribute=charm1_data.get("item_type")
        ))
    large_ammo_box_data = game_items_data.get("large_ammo_box")  # Note: You might need "large_9mm_ammo_box"
    if large_ammo_box_data:
        light_hk_inventory_items.append(items.Item(
            item_name=large_ammo_box_data.get("name"),
            item_value=large_ammo_box_data.get("value"),
            item_attribute=large_ammo_box_data.get("item_type")
        ))

    light_hk.set_inventory(light_hk_inventory_items)
    light_hk.set_name("Lighthouse Keeper")
    return light_hk
