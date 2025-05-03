# src/core/ItemUtil.py
"""
Centralized Item Utility functions for A Sound of Distant Thunder.
Provides consistent item operations across all systems.
"""
import logging

logger = logging.getLogger("ItemUtil")

class ItemUtil:
    """
    Static utility class for item operations.
    Consolidates functionality from previous separate implementations.
    """
    
    @staticmethod
    def get_item_attribute(item_dict, attribute_name, default=0):
        """
        Get an attribute from an item dictionary.
        
        Args:
            item_dict (dict): Item dictionary
            attribute_name (str): Name of attribute to get
            default: Default value if attribute not found
            
        Returns:
            Attribute value or default
        """
        if isinstance(item_dict, dict) and isinstance(item_dict.get("attributes"), dict):
            return item_dict["attributes"].get(attribute_name, default)
        return default
    
    @staticmethod
    def get_item_property(item_dict, property_name, default=None):
        """
        Get a property from an item dictionary.
        
        Args:
            item_dict (dict): Item dictionary
            property_name (str): Name of property to get
            default: Default value if property not found
            
        Returns:
            Property value or default
        """
        if isinstance(item_dict, dict):
            return item_dict.get(property_name, default)
        return default
    
    @staticmethod
    def decrease_item_durability(item_dict, loss_amount):
        """
        Decrease an item's durability.
        
        Args:
            item_dict (dict): Item dictionary
            loss_amount (int): Amount to decrease durability by
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not isinstance(item_dict, dict) or loss_amount <= 0:
            return False
        
        current_dur = item_dict.get("current_durability", 0)
        new_dur = max(0, current_dur - loss_amount)
        item_dict["current_durability"] = new_dur
        return True
    
    @staticmethod
    def is_item_broken(item_dict):
        """
        Check if an item is broken (durability <= 0).
        
        Args:
            item_dict (dict): Item dictionary
            
        Returns:
            bool: True if item is broken, False otherwise
        """
        if isinstance(item_dict, dict):
            return item_dict.get("current_durability", 0) <= 0
        return True
    
    @staticmethod
    def get_gun_ammo(gun_dict):
        """
        Get current ammo count for a gun.
        Initializes ammo if needed based on clip_size.
        
        Args:
            gun_dict (dict): Gun dictionary
            
        Returns:
            int: Current ammo count
        """
        if not isinstance(gun_dict, dict):
            return 0
        
        if 'current_ammo' not in gun_dict:
            clip_size = ItemUtil.get_item_attribute(gun_dict, 'clip_size', 0)
            gun_dict['current_ammo'] = clip_size
            
        return gun_dict.get('current_ammo', 0)
    
    @staticmethod
    def set_gun_ammo(gun_dict, new_ammo_count):
        """
        Set current ammo count for a gun.
        Enforces limits based on clip_size.
        
        Args:
            gun_dict (dict): Gun dictionary
            new_ammo_count (int): New ammo count
            
        Returns:
            bool: True if successful, False otherwise
        """
        if isinstance(gun_dict, dict):
            clip_size = ItemUtil.get_item_attribute(gun_dict, 'clip_size', 0)
            gun_dict['current_ammo'] = max(0, min(new_ammo_count, clip_size))
            return True
        return False
    
    @staticmethod
    def repair_item(item_dict, repair_amount):
        """
        Repair an item by increasing its durability.
        
        Args:
            item_dict (dict): Item dictionary
            repair_amount (int): Amount to increase durability by
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not isinstance(item_dict, dict) or repair_amount <= 0:
            return False
        
        current_dur = item_dict.get("current_durability", 0)
        max_dur = item_dict.get("max_durability", 100)
        new_dur = min(max_dur, current_dur + repair_amount)
        item_dict["current_durability"] = new_dur
        return True
    
    @staticmethod
    def can_repair_item(item_dict):
        """
        Check if an item can be repaired.
        
        Args:
            item_dict (dict): Item dictionary
            
        Returns:
            bool: True if item can be repaired, False otherwise
        """
        if not isinstance(item_dict, dict):
            return False
        
        is_repairable = item_dict.get("is_repairable", False)
        current_dur = item_dict.get("current_durability", 0)
        max_dur = item_dict.get("max_durability", 100)
        
        return is_repairable and current_dur < max_dur
    
    @staticmethod
    def get_item_value(item_dict):
        """
        Get the value of an item.
        
        Args:
            item_dict (dict): Item dictionary
            
        Returns:
            int: Item value or 0 if not specified
        """
        return ItemUtil.get_item_property(item_dict, "value", 0)
    
    @staticmethod
    def get_item_type(item_dict):
        """
        Get the type of an item.
        
        Args:
            item_dict (dict): Item dictionary
            
        Returns:
            str or None: Item type or None if not specified
        """
        return ItemUtil.get_item_property(item_dict, "item_type")
    
    @staticmethod
    def get_item_name(item_dict):
        """
        Get the name of an item.
        
        Args:
            item_dict (dict): Item dictionary
            
        Returns:
            str: Item name or "Unknown Item" if not specified
        """
        return ItemUtil.get_item_property(item_dict, "name", "Unknown Item")
    
    @staticmethod
    def get_item_description(item_dict):
        """
        Get the description of an item.
        
        Args:
            item_dict (dict): Item dictionary
            
        Returns:
            str: Item description or empty string if not specified
        """
        return ItemUtil.get_item_property(item_dict, "description", "")
    
    @staticmethod
    def get_ammo_quantity(ammo_dict):
        """
        Get the quantity of ammunition in an ammo box.
        
        Args:
            ammo_dict (dict): Ammo dictionary
            
        Returns:
            int: Ammo quantity or 0 if not specified
        """
        return ItemUtil.get_item_attribute(ammo_dict, "quantity", 0)
    
    @staticmethod
    def get_ammo_type(item_dict):
        """
        Get the ammo type of a weapon or ammo box.
        
        Args:
            item_dict (dict): Item dictionary
            
        Returns:
            str or None: Ammo type or None if not specified
        """
        return ItemUtil.get_item_attribute(item_dict, "ammo_type")
    
    @staticmethod
    def is_ammo_compatible(gun_dict, ammo_dict):
        """
        Check if ammo is compatible with a gun.
        
        Args:
            gun_dict (dict): Gun dictionary
            ammo_dict (dict): Ammo dictionary
            
        Returns:
            bool: True if ammo is compatible, False otherwise
        """
        if not isinstance(gun_dict, dict) or not isinstance(ammo_dict, dict):
            return False
        
        gun_ammo_type = ItemUtil.get_ammo_type(gun_dict)
        ammo_type = ItemUtil.get_ammo_type(ammo_dict)
        
        return gun_ammo_type == ammo_type
    
    @staticmethod
    def get_item_durability_percentage(item_dict):
        """
        Get the durability percentage of an item.
        
        Args:
            item_dict (dict): Item dictionary
            
        Returns:
            float: Durability percentage (0-100)
        """
        if not isinstance(item_dict, dict):
            return 0.0
        
        current_dur = item_dict.get("current_durability", 0)
        max_dur = item_dict.get("max_durability", 100)
        
        if max_dur <= 0:
            return 0.0
            
        return (current_dur / max_dur) * 100.0
    
    @staticmethod
    def get_weapon_damage(weapon_dict):
        """
        Get the damage value of a weapon.
        
        Args:
            weapon_dict (dict): Weapon dictionary
            
        Returns:
            int: Weapon damage or 0 if not specified
        """
        return ItemUtil.get_item_attribute(weapon_dict, "damage", 0)
    
    @staticmethod
    def get_armor_defense(armor_dict):
        """
        Get the defense value of armor.
        
        Args:
            armor_dict (dict): Armor dictionary
            
        Returns:
            int: Armor defense or 0 if not specified
        """
        return ItemUtil.get_item_attribute(armor_dict, "defense", 0)


class ItemManager:
    """
    Instance-based item manager for game state integration.
    Provides methods that require game state access.
    """
    
    def __init__(self, game_state, data_manager):
        """
        Initialize the item manager.
        
        Args:
            game_state: GameState instance
            data_manager: DataManager instance
        """
        self.game_state = game_state
        self.data_manager = data_manager
    
    def add_item_to_inventory(self, item_id):
        """
        Add an item to player inventory.
        
        Args:
            item_id (str): ID of item to add
            
        Returns:
            bool: True if item added, False otherwise
        """
        if self.game_state.player is None:
            logger.error("Cannot add item: Player not initialized")
            return False
            
        item_data = self.data_manager.get_data("items", item_id)
        if not item_data:
            logger.error(f"Item data not found: {item_id}")
            return False
            
        # Check inventory limit
        if len(self.game_state.player.get_inventory()) >= self.game_state.player.get_inventory_limit():
            logger.debug(f"Cannot add item: Inventory full")
            return False
        
        # Add item to inventory
        success = self.game_state.player.add_inventory(item_data)
        
        if success:
            # Emit item acquired event if event system is available
            if hasattr(self.game_state, 'event_system') and self.game_state.event_system:
                self.game_state.event_system.emit("item_acquired", {
                    "item_id": item_id,
                    "item_name": item_data.get("name", item_id)
                })
            
            logger.info(f"Item added to inventory: {item_id}")
            
        return success
    
    def has_item(self, item_id_or_name):
        """
        Check if player has an item by ID or name.
        
        Args:
            item_id_or_name (str): Item ID or name
            
        Returns:
            bool: True if player has item, False otherwise
        """
        if self.game_state.player is None:
            return False
        
        # Convert to lowercase for case-insensitive comparison
        item_id_lower = item_id_or_name.lower()
        
        # Check inventory for matching item
        for item in self.game_state.player.get_inventory():
            # Check by ID if possible
            if hasattr(item, 'id') and item.id == item_id_or_name:
                return True
                
            # Check by name if the item has a get_item_name method
            if hasattr(item, 'get_item_name'):
                if item.get_item_name().lower() == item_id_lower:
                    return True
            # Check by name attribute directly
            elif hasattr(item, 'name'):
                if item.name.lower() == item_id_lower:
                    return True
            # Check dictionary format
            elif isinstance(item, dict) and 'name' in item:
                if item['name'].lower() == item_id_lower:
                    return True
            # Check by item_id property
            elif isinstance(item, dict) and 'item_id' in item:
                if item['item_id'].lower() == item_id_lower:
                    return True
        
        return False
    
    def remove_item(self, item_id_or_name):
        """
        Remove an item from player inventory.
        
        Args:
            item_id_or_name (str): Item ID or name
            
        Returns:
            bool: True if item was removed, False otherwise
        """
        if self.game_state.player is None:
            return False
            
        # Convert to lowercase for case-insensitive comparison
        item_id_lower = item_id_or_name.lower()
        
        # Find matching item in inventory
        for i, item in enumerate(self.game_state.player.get_inventory()):
            item_name = ""
            item_id = ""
            
            # Extract item name and ID based on format
            if hasattr(item, 'get_item_name'):
                item_name = item.get_item_name()
            elif hasattr(item, 'name'):
                item_name = item.name
            elif isinstance(item, dict) and 'name' in item:
                item_name = item['name']
                
            if hasattr(item, 'id'):
                item_id = item.id
            elif isinstance(item, dict) and 'item_id' in item:
                item_id = item['item_id']
            
            # Check for match
            if (item_name.lower() == item_id_lower or 
                item_id.lower() == item_id_lower):
                # Remove from inventory
                removed_item = self.game_state.player.del_inventory(i)
                
                # Emit event if event system is available
                if hasattr(self.game_state, 'event_system') and self.game_state.event_system:
                    self.game_state.event_system.emit("item_removed", {
                        "item_id": item_id,
                        "item_name": item_name
                    })
                
                logger.info(f"Item removed from inventory: {item_id}")
                return True
        
        return False
    
    def get_item_by_id(self, item_id):
        """
        Get item data from the data manager.
        
        Args:
            item_id (str): Item ID
            
        Returns:
            dict or None: Item data or None if not found
        """
        return self.data_manager.get_data("items", item_id)
    
    def reload_weapon(self, weapon_index, ammo_index):
        """
        Reload a weapon from the player's inventory.
        
        Args:
            weapon_index (int): Index of weapon in inventory
            ammo_index (int): Index of ammo in inventory
            
        Returns:
            bool: True if weapon was reloaded, False otherwise
        """
        if self.game_state.player is None:
            return False
            
        inventory = self.game_state.player.get_inventory()
        
        # Validate indices
        if (weapon_index < 0 or weapon_index >= len(inventory) or
            ammo_index < 0 or ammo_index >= len(inventory)):
            return False
            
        weapon = inventory[weapon_index]
        ammo = inventory[ammo_index]
        
        # Check if weapon is a gun
        if ItemUtil.get_item_type(weapon) != "weapon":
            return False
            
        weapon_type = ItemUtil.get_item_attribute(weapon, "weapon_type", "")
        if weapon_type != "gun":
            return False
            
        # Check if ammo is compatible
        if ItemUtil.get_item_type(ammo) != "ammo":
            return False
            
        if not ItemUtil.is_ammo_compatible(weapon, ammo):
            return False
            
        # Get ammo quantity and clip capacity
        ammo_quantity = ItemUtil.get_ammo_quantity(ammo)
        clip_size = ItemUtil.get_item_attribute(weapon, "clip_size", 0)
        current_ammo = ItemUtil.get_gun_ammo(weapon)
        
        # Calculate how much ammo to add
        ammo_needed = clip_size - current_ammo
        ammo_to_add = min(ammo_needed, ammo_quantity)
        
        if ammo_to_add <= 0:
            return False
            
        # Update ammo in weapon
        ItemUtil.set_gun_ammo(weapon, current_ammo + ammo_to_add)
        
        # Update ammo box
        remaining_ammo = ammo_quantity - ammo_to_add
        if remaining_ammo <= 0:
            # Remove empty ammo box
            self.game_state.player.del_inventory(ammo_index)
        else:
            # Update ammo quantity
            ammo["attributes"]["quantity"] = remaining_ammo
            
        # Emit event if event system is available
        if hasattr(self.game_state, 'event_system') and self.game_state.event_system:
            self.game_state.event_system.emit("weapon_reloaded", {
                "weapon_name": ItemUtil.get_item_name(weapon),
                "ammo_added": ammo_to_add,
                "current_ammo": current_ammo + ammo_to_add
            })
            
        return True