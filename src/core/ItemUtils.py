# src/core/ItemUtils.py
"""
Item handling utilities for A Sound of Distant Thunder.
Provides consistent item operations across all systems.
"""
import logging

logger = logging.getLogger("ItemUtils")

class ItemManager:
    """Manages item operations."""
    
    def __init__(self, game_state, data_manager):
        """
        Initialize item manager.
        
        Args:
            game_state: GameState instance
            data_manager: DataManager instance
        """
        self.game_state = game_state
        self.data_manager = data_manager
    
    def get_item_attribute(self, item_dict, attribute_name, default=0):
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
    
    def get_item_property(self, item_dict, property_name, default=None):
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
    
    def decrease_item_durability(self, item_dict, loss_amount):
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
    
    def is_item_broken(self, item_dict):
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
    
    def get_gun_ammo(self, gun_dict):
        """
        Get current ammo count for a gun.
        
        Args:
            gun_dict (dict): Gun dictionary
            
        Returns:
            int: Current ammo count
        """
        if not isinstance(gun_dict, dict):
            return 0
            
        if 'current_ammo' not in gun_dict:
            clip_size = self.get_item_attribute(gun_dict, 'clip_size', 0)
            gun_dict['current_ammo'] = clip_size
            
        return gun_dict.get('current_ammo', 0)
    
    def set_gun_ammo(self, gun_dict, new_ammo_count):
        """
        Set current ammo count for a gun.
        
        Args:
            gun_dict (dict): Gun dictionary
            new_ammo_count (int): New ammo count
            
        Returns:
            bool: True if successful, False otherwise
        """
        if isinstance(gun_dict, dict):
            clip_size = self.get_item_attribute(gun_dict, 'clip_size', 0)
            gun_dict['current_ammo'] = max(0, min(new_ammo_count, clip_size))
            return True
        return False
    
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
        
        # Add item to inventory (implementation depends on game state structure)
        success = self.game_state.player.add_inventory(item_data)
        
        if success:
            # Emit item acquired event
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
        
        # Check inventory for matching item
        for item in self.game_state.player.get_inventory():
            # Check by ID if possible
            if hasattr(item, 'id') and item.id == item_id_or_name:
                return True
                
            # Check by name
            if hasattr(item, 'get_item_name'):
                if item.get_item_name().lower() == item_id_or_name.lower():
                    return True
            elif hasattr(item, 'name'):
                if item.name.lower() == item_id_or_name.lower():
                    return True
            elif isinstance(item, dict) and 'name' in item:
                if item['name'].lower() == item_id_or_name.lower():
                    return True
        
        return False