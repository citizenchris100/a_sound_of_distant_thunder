import random
import names 
import copy

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
    def add_inventory(self, item_dict):
         if isinstance(item_dict, dict):
            self.inventory.append(item_dict)
         else:
            print(f"Warning: Tried to add non-dictionary item to {self.name}'s inventory.")
    def del_inventory(self, item_dict): 
        try:
            self.inventory.remove(item_dict)
        except ValueError:
            print(f"Warning: Item not found in {self.name}'s inventory for removal.")


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
    def set_equipped_gun(self, gun_dict):
        if gun_dict is None or isinstance(gun_dict, dict):
            self.equipped_gun = gun_dict
        else:
            print("Error: Tried to equip non-dictionary as gun.")
    def get_equipped_melee(self):
        return self.equipped_melee
    def set_equipped_melee(self, melee_dict):
         if melee_dict is None or isinstance(melee_dict, dict):
            self.equipped_melee = melee_dict
         else:
            print("Error: Tried to equip non-dictionary as melee.")
    def get_equipped_armour(self):
        return self.equipped_armour
    def set_equipped_armour(self, armour_dict):
         if armour_dict is None or isinstance(armour_dict, dict):
            self.equipped_armour = armour_dict
         else:
            print("Error: Tried to equip non-dictionary as armour.")
    def get_happy(self):
        return self.happy
    def set_happy(self, add, value):
        if add: self.happy += value
        else: self.happy -= value
    def get_dialog(self):
        return self.dialog
    def set_dialog(self, new_dialog):
        self.dialog = new_dialog


class BossHuman(Human): 
    def __init__(self, en_name, health, defence, strength, luck, awareness, gun_skill, move):
        super().__init__(en_name, health, defence, strength, luck, awareness, gun_skill)
        self.super_move = move
    def get_super_move(self): return self.super_move
    def set_super_move(self, new_move): self.super_move = new_move

class BossEnemy(Enemy): 
    def __init__(self, en_name, health, defence, strength, luck, awareness, move):
        super().__init__(en_name, health, defence, strength, luck, awareness)
        self.super_move = move
    def get_super_move(self): return self.super_move
    def set_super_move(self, new_move): self.super_move = new_move

def get_random_loot_id(loot_type):
    """Helper to get a random item ID for loot based on type."""
    if loot_type == "med_pack":
        ids = ["medium_med_pack", "basic_med_pack", "advanced_med_pack"]
        return random.choice(ids)
    elif loot_type == "night_shadow":
        ids = ["small_ns_pack", "medium_ns_pack", "large_ns_pack"]
        return random.choice(ids)
    elif loot_type == "misc_item":
        ids = ["charm1", "charm2", "cologne1", "cologne2", "charm3", "cologne3"]
        return random.choice(ids)
    return None

def add_loot(enemy, game_items_data):
    """Adds loot (item dictionaries) to an enemy's inventory based on luck."""
    if random.randint(0, 10) < enemy.get_luck():
        item_id = get_random_loot_id("med_pack")
        item_data = game_items_data.get(item_id)
        if item_data: 
            enemy.add_inventory(copy.deepcopy(item_data)) 
            
    if random.randint(0, 6) < enemy.get_luck():
        item_id = get_random_loot_id("night_shadow")
        item_data = game_items_data.get(item_id)
        if item_data: 
            enemy.add_inventory(copy.deepcopy(item_data)) 

    if random.randint(0, 24) < enemy.get_luck():
        item_id = get_random_loot_id("misc_item")
        item_data = game_items_data.get(item_id)
        if item_data: 
            enemy.add_inventory(copy.deepcopy(item_data)) 

def basic_goblin(game_items_data):
    goblin = Enemy("Goblin", random.randint(15, 30), random.randint(1, 3), random.randint(5, 10),
                   random.randint(0, 5), random.randint(1, 5))
    add_loot(goblin, game_items_data)
    return goblin

def beta_goblin(game_items_data):
    goblin = Enemy("Beta Goblin", random.randint(35, 65), random.randint(4, 6), random.randint(10, 17),
                   random.randint(2, 7), random.randint(3, 5))
    add_loot(goblin, game_items_data) 
    return goblin

def alpha_goblin(game_items_data):
    goblin = Enemy("Alpha Goblin", random.randint(75, 100), random.randint(6, 8), random.randint(17, 25),
                   random.randint(4, 7), random.randint(5, 7))
    add_loot(goblin, game_items_data) 
    add_loot(goblin, game_items_data) 
    return goblin


def npc(gender): 
    
    try:
        import names
    except ImportError:
        print("Error: 'names' library not found. Cannot generate NPC names.")
        return None # 

    if gender:
        npc_name = names.get_full_name(gender='male')
        npc_health = random.randint(50, 100)
        npc_defence = random.randint(5, 8)
        npc_strength = random.randint(5, 25)
        npc_gun_skill = random.randint(0, 7) if npc_strength > 16 else random.randint(4, 18)
        npc_luck = random.randint(1, 7)
        npc_awareness = random.randint(1, 7) 
        return Human(npc_name, npc_health, npc_defence, npc_strength, npc_luck, npc_awareness, npc_gun_skill)
    else:
        npc_name = names.get_full_name(gender='female')
        npc_health = random.randint(40, 80)
        npc_defence = random.randint(3, 6)
        npc_strength = random.randint(2, 17)
        npc_gun_skill = random.randint(0, 7) if npc_strength > 13 else random.randint(4, 18)
        npc_luck = random.randint(1, 7)
        npc_awareness = random.randint(1, 7) 
        return Human(npc_name, npc_health, npc_defence, npc_strength, npc_luck, npc_awareness, npc_gun_skill)


def boat_captain(game_items_data):
    captain = npc(True)
    if captain is None: return None # Handle case where npc() failed

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
        captain.set_equipped_gun(large_revolver_data) 
    else:
        print("Warning: 'large_revolver' data not found.")

    medium_body_armour_data = game_items_data.get("medium_body_armour")
    if medium_body_armour_data:
        captain.set_equipped_armour(medium_body_armour_data) 
    else:
        print("Warning: 'medium_body_armour' data not found.")

    captain_inventory_items = []
    item_ids_to_add = ["medium_med_pack", "cologne1", "med_9mm_ammo_box"] 
    for item_id in item_ids_to_add:
        item_data = game_items_data.get(item_id)
        if item_data:
            captain_inventory_items.append(copy.deepcopy(item_data)) 
        else:
            print(f"Warning: Item data for '{item_id}' not found.")

    captain.set_inventory(captain_inventory_items)
    captain.set_name("Boat Captain")
    captain.set_health(75)
    return captain


def deck_hand01(game_items_data):
    deck_hand = npc(True)
    if deck_hand is None: return None

    basic_knife_data = game_items_data.get("basic_knife")
    if basic_knife_data:
        deck_hand.set_equipped_melee(basic_knife_data) # Assign dictionary
    else:
        print("Warning: 'basic_knife' data not found.")

    add_loot(deck_hand, game_items_data) # Pass game_items_data
    deck_hand.set_name("Deck Hand 1")
    return deck_hand


def deck_hand02(game_items_data):
    deck_hand = npc(True)
    if deck_hand is None: return None

    basic_knife_data = game_items_data.get("basic_knife")
    if basic_knife_data:
        deck_hand.set_equipped_melee(basic_knife_data) # Assign dictionary
    else:
        print("Warning: 'basic_knife' data not found.")

    add_loot(deck_hand, game_items_data) # Pass game_items_data
    deck_hand.set_name("Deck Hand 2")
    return deck_hand


def light_house_keeper(game_items_data):
    light_hk = npc(True)
    if light_hk is None: return None

    large_revolver_data = game_items_data.get("large_revolver")
    if large_revolver_data:
        light_hk.set_equipped_gun(large_revolver_data) 
    else:
        print("Warning: 'large_revolver' data not found.")

    epic_body_armour_data = game_items_data.get("epic_body_armour")
    if epic_body_armour_data:
        light_hk.set_equipped_armour(epic_body_armour_data) 
    else:
        print("Warning: 'epic_body_armour' data not found.")

    light_hk_inventory_items = []
    inventory_setup = {
        "basic_med_pack": 3,
        "medium_med_pack": 3,
        "advanced_med_pack": 3,
        "medium_pistol": 1,
        "advanced_pistol": 1,
        "medium_knife": 1,
        "large_knife": 1,
        "basic_body_armour": 1,
        "medium_body_armour": 1,
        "advanced_body_armour": 1,
        "cologne1": 1,
        "charm1": 1,
        "large_9mm_ammo_box": 1 
    }

    for item_id, quantity in inventory_setup.items():
        item_data = game_items_data.get(item_id)
        if item_data:
            for _ in range(quantity):
                light_hk_inventory_items.append(copy.deepcopy(item_data))
        else:
            print(f"Warning: Item data for '{item_id}' not found for Lighthouse Keeper inventory.")

    light_hk.set_inventory(light_hk_inventory_items)
    light_hk.set_name("Lighthouse Keeper")
    return light_hk