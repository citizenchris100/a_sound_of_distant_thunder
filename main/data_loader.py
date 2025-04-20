import os 
import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError
import logging 

logger = logging.getLogger(__name__) 


def load_items_data(item_data_path): # Expects path like "main/data/items"
    """Loads all item JSON files from the specified directory."""
    item_data = {}
    if not os.path.isdir(item_data_path):
        # Print the custom error AND log it before returning empty dict
        error_detail = f"[Errno 2] No such file or directory: '{item_data_path}'"
        print(f"ERROR: Item data directory not found. Check paths. Details: {error_detail}")
        logging.error(f"Item data directory not found: {item_data_path}")
        return item_data # Return empty dict (safer than None)

    logging.info(f"Loading item data from: {item_data_path}")
    for filename in os.listdir(item_data_path):
        if filename.endswith(".json"):
            filepath = os.path.join(item_data_path, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    item_id = data.get('id') # Assuming items also have an 'id' field

                    if not item_id:
                        logging.warning(f"Skipping item file {filename}: Missing 'id' key.")
                        continue

                    # TODO: Add JSON schema validation here if desired (using items_schema.json)

                    if item_id in item_data:
                        logging.warning(f"Duplicate item ID '{item_id}' found in {filename}. Overwriting previous entry.")

                    item_data[item_id] = data
                    logging.debug(f"Loaded item: {item_id} from {filename}")

            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON from {filepath}: {e}")
            except Exception as e:
                logging.error(f"Error loading item file {filepath}: {e}")
    logging.info(f"Finished loading {len(item_data)} items.")
    return item_data # Return the dictionary

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

def load_npc_data(npc_data_path):
    """Loads all NPC JSON files from the specified directory."""
    npc_data = {}
    if not os.path.isdir(npc_data_path):
        logging.error(f"NPC data directory not found: {npc_data_path}")
        return npc_data # Return empty if directory doesn't exist

    logging.info(f"Loading NPC data from: {npc_data_path}")
    for filename in os.listdir(npc_data_path):
        if filename.endswith(".json"):
            filepath = os.path.join(npc_data_path, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    npc_id = data.get('id')

                    if not npc_id:
                        logging.warning(f"Skipping NPC file {filename}: Missing 'id' key.")
                        continue

                    # TODO: Add JSON schema validation here later if you create npcs_schema.json
                    # try:
                    #     jsonschema.validate(instance=data, schema=npc_schema)
                    # except jsonschema.ValidationError as e:
                    #     logging.error(f"NPC file {filename} failed schema validation: {e.message}")
                    #     continue

                    if npc_id in npc_data:
                        logging.warning(f"Duplicate NPC ID '{npc_id}' found in {filename}. Overwriting previous entry.")

                    npc_data[npc_id] = data
                    logging.debug(f"Loaded NPC: {npc_id} from {filename}")

            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON from {filepath}: {e}")
            except Exception as e:
                logging.error(f"Error loading NPC file {filepath}: {e}")
    logging.info(f"Finished loading {len(npc_data)} NPCs.")
    return npc_data

def load_all_data(base_data_path="main/data"):
    """Loads all game data (locations, items, NPCs) from subdirectories."""
    logging.info("--- Starting Full Data Load ---")

    # Define paths to data subdirectories
    locations_path = os.path.join(base_data_path, "locations")
    items_path = os.path.join(base_data_path, "items")
    npcs_path = os.path.join(base_data_path, "npcs")

    # Call load functions WITH paths and store results in a single dictionary
    all_data = {
        "locations": load_location_data(locations_path),
        "items": load_items_data(items_path),
        "npcs": load_npc_data(npcs_path)
    }

    # Optional: Add checks here to ensure critical data loaded successfully
    # Using .get() is safer in case a load function returned None or empty
    if not all_data.get("locations"):
        logging.critical("Failed to load any location data! Check path and files.")
        # Consider returning None or raising an exception if essential data fails
    if not all_data.get("items"):
        logging.critical("Failed to load any item data! Check path and files.")
    if not all_data.get("npcs"):
        logging.warning("No NPC data loaded. Check path or this might be expected.")

    logging.info("--- Full Data Load Finished ---")
    # Return the single dictionary containing all loaded data
    return all_data

