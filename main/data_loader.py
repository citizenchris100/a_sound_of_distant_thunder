import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError

def load_items_data(schema_path="main/data/schemas/items_schema.json", data_path="main/data/items.json"):
    """
    Loads item data from a JSON file and validates it against a JSON schema.

    Args:
        schema_path (str, optional): Path to the JSON schema file. Defaults to "main/data/schemas/items_schema.json".
        data_path (str, optional): Path to the JSON data file. Defaults to "main/data/items.json".

    Returns:
        dict: A dictionary where keys are item_ids and values are item data dictionaries,
              or None if loading or validation fails.
    """
    try:
        with open(schema_path, 'r') as schema_file:
            items_schema = json.load(schema_file)
    except FileNotFoundError:
        print(f"Error: Schema file not found at {schema_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in schema file at {schema_path}")
        return None

    try:
        with open(data_path, 'r') as data_file:
            items_data_list = json.load(data_file)
    except FileNotFoundError:
        print(f"Error: Data file not found at {data_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in data file at {data_path}")
        return None

    try:
        validate(instance=items_data_list, schema=items_schema)
        print("Item data validated successfully against schema.")  # Success message
    except ValidationError as e:
        print("Error: Item data failed schema validation:")
        print(e)
        return None

    items_data_dict = {}
    for item_data in items_data_list:
        item_id = item_data.get("item_id")
        if item_id:
            items_data_dict[item_id] = item_data
        else:
            print("Warning: Item data missing 'item_id'. Skipping item.")

    return items_data_dict

# Example usage (for testing - you can remove this later):
if __name__ == "__main__":
    item_data = load_items_data()
    if item_data:
        print("\nLoaded Item Data (First 3 items):")
        item_ids = list(item_data.keys())[:3] # Get IDs of first 3 items
        for item_id in item_ids:
            print(f"- {item_id}: {item_data[item_id].get('name')}")
    else:
        print("Item data loading failed.")