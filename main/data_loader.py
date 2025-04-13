import os 
import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import logging 

logger = logging.getLogger(__name__) 


def load_items_data(schema_path="main/data/schemas/items_schema.json", data_path="main/data/items.json"):
    try:
        items_data_dict = {}
        items_data_list = [] 
        with open(data_path, 'r') as data_file: 
             items_data_list = json.load(data_file)
        with open(schema_path, 'r') as schema_file:
             items_schema = json.load(schema_file)
        validate(instance=items_data_list, schema=items_schema) 

        for item_data in items_data_list:
            item_id = item_data.get("item_id")
            if item_id:
                items_data_dict[item_id] = item_data
            else:
                logger.warning("Item data missing 'item_id'. Skipping item: %s", item_data.get('name', 'N/A'))
        logger.info("Successfully loaded and validated %d items from %s", len(items_data_dict), data_path)
        return items_data_dict
    except FileNotFoundError as e:
        logger.error("Error loading item data: File not found - %s", e)
        print(f"ERROR: Item data file or schema not found. Check paths. Details: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error("Error decoding JSON for items: %s", e)
        print(f"ERROR: Invalid JSON format in item data or schema. Details: {e}")
        return None
    except ValidationError as e:
        logger.error("Item data schema validation failed: %s", e)
        print(f"ERROR: Items data validation failed. Check data format against schema.")
        print(f"Path: {list(e.path)}, Message: {e.message}")
        return None
    except Exception as e:
        logger.exception("An unexpected error occurred during item loading:")
        print(f"ERROR: An unexpected error occurred loading items.")
        return None

def load_location_data(directory_path="main/data/locations", schema_path="main/data/schemas/locations_schema.json"):
    """
    Loads all location JSON files from a directory, validates each against a schema,
    and returns a dictionary keyed by location_id.

    Args:
        directory_path (str): Path to the directory containing location JSON files.
        schema_path (str): Path to the JSON schema file for a single location object.

    Returns:
        dict: Dictionary of location objects keyed by location_id, or None if critical error.
    """
    try:
        with open(schema_path, 'r') as schema_file:
            location_schema = json.load(schema_file)
        logger.debug("Location schema loaded successfully from %s", schema_path)
    except FileNotFoundError:
        logger.error("Location schema file not found at %s", schema_path)
        print(f"ERROR: Location schema file not found at {schema_path}")
        return None
    except json.JSONDecodeError as e:
        logger.error("Error decoding JSON in location schema file %s: %s", schema_path, e)
        print(f"ERROR: Invalid JSON in location schema: {schema_path}")
        return None
    except Exception as e:
        logger.exception("Unexpected error loading location schema:")
        print(f"ERROR: Unexpected error loading location schema.")
        return None

    locations_dict = {}
    try:
        logger.info("Scanning for location files in: %s", directory_path)
        filenames = os.listdir(directory_path)
    except FileNotFoundError:
        logger.error("Locations directory not found at %s", directory_path)
        print(f"ERROR: Locations directory not found at {directory_path}")
        return None 
    except Exception as e:
        logger.exception("Unexpected error listing location directory:")
        print(f"ERROR: Unexpected error accessing locations directory.")
        return None

    loaded_count = 0
    error_count = 0
    for filename in filenames:
        if filename.endswith(".json"):
            file_path = os.path.join(directory_path, filename)
            try:
                with open(file_path, 'r') as data_file:
                    location_data = json.load(data_file) 
                validate(instance=location_data, schema=location_schema)
                location_id = location_data.get("location_id")
                if location_id:
                    if location_id in locations_dict:
                        logger.warning("Duplicate location_id '%s' found in file %s. Overwriting previous.", location_id, filename)
                    locations_dict[location_id] = location_data
                    loaded_count += 1
                else:
                    logger.warning("Location file %s is missing 'location_id'. Skipping.", filename)
                    error_count += 1
            except FileNotFoundError: 
                logger.error("Location file %s listed but not found during load.", file_path)
                error_count += 1
            except json.JSONDecodeError as e:
                logger.error("Error decoding JSON in location file %s: %s", file_path, e)
                print(f"ERROR: Invalid JSON in location file: {filename}")
                error_count += 1
            except ValidationError as e:
                logger.error("Location data schema validation failed for file %s: %s", filename, e.message)
                print(f"ERROR: Validation failed for {filename}. Path: {list(e.path)}, Message: {e.message}")
                error_count += 1
            except Exception as e:
                 logger.exception("Unexpected error processing location file '%s':", filename)
                 print(f"ERROR: Unexpected error loading {filename}.")
                 error_count += 1

    logger.info("Location loading finished. Loaded: %d, Errors/Skipped: %d", loaded_count, error_count)
    if loaded_count == 0 and error_count > 0:
         print("Warning: No locations were loaded successfully.")
    return locations_dict

def load_all_data():
    """Loads all primary game data types (items, locations, etc.)."""
    logger.info("--- Starting Full Data Load ---")
    all_game_data = {}

    items_data = load_items_data()
    if items_data is not None:
        all_game_data["items"] = items_data
    else:
        logger.error("ITEM LOADING FAILED.")
       
    locations_data = load_location_data()
    if locations_data is not None:
        all_game_data["locations"] = locations_data
    else:
        logger.error("LOCATION LOADING FAILED.")

    # --- TODO: Add calls to load other data types ---
    # all_game_data["npcs"] = load_npc_data()
    # all_game_data["dialogue"] = load_dialogue_data()
    # all_game_data["classes"] = load_class_data()
    # ---

    logger.info("--- Full Data Load Finished ---")
    if "items" not in all_game_data or "locations" not in all_game_data:
         print("CRITICAL ERROR: Failed to load essential game data (Items or Locations). Cannot continue.")
         return None

    return all_game_data

