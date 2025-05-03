def get_item_attribute(item_dict, attribute_name, default=0):
    if isinstance(item_dict, dict) and isinstance(item_dict.get("attributes"), dict):
        return item_dict["attributes"].get(attribute_name, default)
    return default

def get_item_property(item_dict, property_name, default=None):
    if isinstance(item_dict, dict):
        return item_dict.get(property_name, default)
    return default

def decrease_item_durability(item_dict, loss_amount):
    """Decreases item durability (dict['current_durability']) safely."""
    if not isinstance(item_dict, dict) or loss_amount <= 0:
        return False
    
    current_dur = item_dict.get("current_durability", 0)
    new_dur = max(0, current_dur - loss_amount)
    item_dict["current_durability"] = new_dur 
    return True 

def is_item_broken(item_dict):
    """Checks if an item's 'current_durability' is 0 or less."""
    if isinstance(item_dict, dict):
        return item_dict.get("current_durability", 0) <= 0
    return True

def get_gun_ammo(gun_dict):
    """Gets the current ammo count for a gun dictionary. Initializes if needed."""
    if not isinstance(gun_dict, dict):
        return 0
    if 'current_ammo' not in gun_dict:
         clip_size = get_item_attribute(gun_dict, 'clip_size', 0)
         gun_dict['current_ammo'] = clip_size 
    return gun_dict.get('current_ammo', 0)

def set_gun_ammo(gun_dict, new_ammo_count):
    """Sets the current ammo count for a gun dictionary."""
    if isinstance(gun_dict, dict):
        clip_size = get_item_attribute(gun_dict, 'clip_size', 0)
        gun_dict['current_ammo'] = max(0, min(new_ammo_count, clip_size))
        return True
    return False