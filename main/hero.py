# --- main/hero.py ---

import random
import sys
import os
# import data_loader # Not directly needed here
import copy

# Removed logging import - wasn't used in this version, can add back if needed

class Hero:
    def __init__(self, dp, strength, gun_skill, luck, charm, stealth, game_items_data):
        self.name = 'Alex'
        self.exp = 0
        self.lvl = 0
        self.hp = 65
        self.hp_limit = 65
        self.status_effects = []
        self.inventory = []
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
        # --- Using self.location consistently ---
        self.location = None # Stores the current location ID string
        # self.current_location_id = None # Removed redundant attribute
        # --- End location attribute ---
        self.visited_locations = set() # Stores IDs of visited locations

        # Add starting med pack
        basic_med_pack_data = game_items_data.get("basic_med_pack")
        if basic_med_pack_data:
            self.inventory.append(copy.deepcopy(basic_med_pack_data))
        else:
            # Consider using logging here if it's set up in game.py
            print("Warning: 'basic_med_pack' data not found. Starting without med pack.")

    # --- Getters ---
    def get_name(self):
        return self.name

    def get_exp(self):
        return self.exp

    def get_lvl(self):
        return self.lvl

    def get_status(self):
        return self.status_effects

    def get_inventory(self):
        return self.inventory

    def get_inventory_limit(self):
        return self.inventory_limit

    def get_equipped_gun(self):
        return self.equipped_gun

    def get_equipped_melee(self):
        return self.equipped_melee

    def get_equipped_armour(self):
        return self.equipped_armour

    def get_health_points(self):
        return self.hp

    def get_hp_limit(self):
        return self.hp_limit

    def get_defence_points(self):
        return self.defence_points

    def get_strength_attribute(self):
        return self.strength_attribute

    def get_gun_skill(self):
        return self.gun_skill_attribute

    def get_luck(self):
        return self.luck_attribute

    def get_charm_attribute(self):
        return self.charm_attribute

    def get_stealth_attribute(self):
        return self.stealth_attribute

    def get_location(self):
        """Returns the current location ID (string)."""
        return self.location

    # --- Setters / Modifiers ---
    def set_exp(self, updated_exp):
        self.exp = updated_exp

    def up_lvl(self):
        """Increments the level by 1."""
        self.lvl += 1

    def set_status(self, effect):
        """Adds a status effect string to the list."""
        if isinstance(effect, str):
             self.status_effects.append(effect)
        else:
             print(f"Warning: Tried to add non-string status effect: {effect}")

    def del_status(self, item):
        """Removes a specific status effect string from the list."""
        try:
            self.status_effects.remove(item)
        except ValueError:
            print(f"Warning: Status effect '{item}' not found to remove.")

    def add_inventory(self, item_dict):
        """Adds an item dictionary to the inventory if space allows."""
        if len(self.inventory) < self.inventory_limit:
            if isinstance(item_dict, dict):
                self.inventory.append(item_dict)
                # Print message handled by calling code for context
                return True # Indicate success
            else:
                print(f"Error: Attempted to add a non-dictionary item to inventory: {item_dict}")
                # Consider logging
                return False
        else:
            # Print message handled by calling code
            return False # Indicate failure (inventory full)

    def del_inventory(self, item_index):
        """Deletes an item from the inventory by its list index."""
        try:
            if 0 <= item_index < len(self.inventory):
                removed_item = self.inventory.pop(item_index)
                # Print handled by calling code
                return removed_item # Return the removed item
            else:
                print(f"Error: Invalid item index for deletion: {item_index}")
                return None
        except IndexError:
            print(f"Error: Index out of bounds for inventory deletion: {item_index}")
            return None

    def set_inventory_limit(self, new_limit):
        """Sets the inventory limit directly."""
        self.inventory_limit = new_limit

    def set_equipped_gun(self, gun_dict):
        """Equips a gun (dictionary) or None."""
        if gun_dict is None or isinstance(gun_dict, dict):
            self.equipped_gun = gun_dict
        else:
            print(f"Error: Tried equipping invalid gun item: {gun_dict}")

    def set_equipped_melee(self, melee_dict):
        """Equips a melee weapon (dictionary) or None."""
        if melee_dict is None or isinstance(melee_dict, dict):
            self.equipped_melee = melee_dict
        else:
            print(f"Error: Tried equipping invalid melee item: {melee_dict}")

    def set_equipped_armour(self, armour_dict):
        """Equips armour (dictionary) or None."""
        if armour_dict is None or isinstance(armour_dict, dict):
            self.equipped_armour = armour_dict
        else:
            print(f"Error: Tried equipping invalid armour item: {armour_dict}")

    def set_health_points(self, updated_health):
        """Sets current HP, clamped between 0 and hp_limit."""
        self.hp = max(0, min(updated_health, self.hp_limit))

    def set_hp_limit(self, new_limit):
        """Sets the maximum HP limit."""
        self.hp_limit = max(1, new_limit)
        self.hp = min(self.hp, self.hp_limit) # Adjust current HP if necessary

    def set_defence_points(self, dp):
        """Sets Defense points, applying cap."""
        self.defence_points = min(dp, 7) # Adjust cap if needed

    def set_strength_attribute(self, strength):
        """Sets Strength attribute, applying cap."""
        self.strength_attribute = min(strength, 35)

    def set_gun_skill(self, gun_skill):
        """Sets Gun Skill attribute, applying cap."""
        self.gun_skill_attribute = min(gun_skill, 35)

    def set_luck_attribute(self, luck):
        """Sets Luck attribute, applying cap."""
        self.luck_attribute = min(luck, 7)

    def set_charm_attribute(self, charm):
        """Sets Charm attribute, applying cap."""
        self.charm_attribute = min(charm, 7)

    # --- Corrected set_stealth_attribute ---
    def set_stealth_attribute(self, stealth):
        """Sets Stealth attribute, applying cap."""
        self.stealth_attribute = min(stealth, 7) # Correctly sets stealth
    # --- End Correction ---

    def set_location(self, location_id):
        """Sets the player's current location ID."""
        if isinstance(location_id, str):
            self.location = location_id
        else:
            print(f"Error: Tried setting invalid location ID type: {location_id}")
            # Consider logging

    # --- Location History Methods ---
    def add_visited_location(self, location_id):
        """Adds a location ID to the set of visited locations."""
        if isinstance(location_id, str):
            self.visited_locations.add(location_id)

    # --- has_visited METHOD NOW INDENTED CORRECTLY ---
    def has_visited(self, location_id):
        """Checks if the given location ID has been visited."""
        return location_id in self.visited_locations
    # --- End of Hero Class ---


# --- Class Selection Function (defined outside the class) ---
def class_selection(game_items_data):
    # Ensure random, sys, os are imported at the top of the file
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
        a_lower = a.lower() # Convert to lowercase once for efficiency
        hero_instance = None

        if a_lower == "merc" or a == "1":
            hero_instance = Hero(random.randint(3, 6), random.randint(2, 5), random.randint(20, 25), random.randint(2, 4),
                                 random.randint(1, 3), random.randint(5, 7), game_items_data)
        elif a_lower == "soldier" or a == "2":
            hero_instance = Hero(random.randint(5, 8), random.randint(10, 15), random.randint(10, 15), random.randint(2, 4),
                                 random.randint(1, 5), random.randint(1, 5), game_items_data)
        elif a_lower == "ranger" or a == "3":
            hero_instance = Hero(random.randint(4, 7), random.randint(20, 25), random.randint(4, 7), random.randint(2, 4),
                                 random.randint(1, 5), random.randint(3, 6), game_items_data)
        elif a_lower == "spy" or a == "4":
            hero_instance = Hero(random.randint(1, 4), random.randint(4, 7), random.randint(4, 7), random.randint(5, 7),
                                 random.randint(5, 7), random.randint(4, 7), game_items_data)
        elif a_lower == "random" or a == "5":
            hero_instance = Hero(random.randint(1, 7), random.randint(4, 20), random.randint(4, 20), random.randint(1, 7),
                                 random.randint(1, 7), random.randint(1, 7), game_items_data)

        # If a valid class was chosen, return the instance
        if hero_instance:
            return hero_instance

        # Handle help and quit options separately
        elif a_lower == "help" or a == "6":
            # --- Included Full Help Text ---
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
            # --- End Help Text ---
        elif a_lower == "quit" or a == "7":
            print("Quitting character selection.")
            sys.exit() # Or return None if title_screen should handle exit
        else:
            print("Invalid Input. Type class name, number (1-5), 'Help', or 'Quit'.")