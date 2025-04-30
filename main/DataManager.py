import os
import json
import logging
import jsonschema

class DataManager:
    """
    Manages loading, validation, and access to game data files.
    """
    def __init__(self, data_path="./data/"):
        self.data_path = data_path
        self.cache = {}
        self.logger = logging.getLogger("DataManager")
        
        # Create necessary directories if they don't exist
        os.makedirs(os.path.join(data_path, "npcs"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "locations"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "items"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "dialogs"), exist_ok=True)
        os.makedirs(os.path.join(data_path, "quests"), exist_ok=True)
    
    def get_data(self, data_type, data_id=None):
        """
        Get data of specified type and optional ID.
        
        Args:
            data_type (str): Type of data to retrieve ('npcs', 'locations', etc.)
            data_id (str, optional): Specific ID of data to retrieve
            
        Returns:
            dict or list: Requested data
        """
        if data_type not in self.cache:
            self._load_data_type(data_type)
        
        if data_id:
            return self.cache[data_type].get(data_id)
        return self.cache[data_type]
    
    def _load_data_type(self, data_type):
        """
        Load all data files of a specific type.
        
        Args:
            data_type (str): Type of data to load
        """
        self.logger.info(f"Loading {data_type} data...")
        self.cache[data_type] = {}
        
        data_dir = os.path.join(self.data_path, data_type)
        if not os.path.exists(data_dir):
            self.logger.warning(f"Data directory not found: {data_dir}")
            return
            
        for filename in os.listdir(data_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(data_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        
                    # Basic validation
                    if 'id' not in data:
                        self.logger.warning(f"Missing ID in {file_path}, skipping")
                        continue
                        
                    self.cache[data_type][data['id']] = data
                    self.logger.debug(f"Loaded {data_type} data: {data['id']}")
                except json.JSONDecodeError:
                    self.logger.error(f"Invalid JSON in {file_path}")
                except Exception as e:
                    self.logger.error(f"Error loading {file_path}: {e}")
    
    def reload_data(self):
        """Clear cache and reload all data"""
        self.cache = {}
        
    def get_all_ids(self, data_type):
        """Get all IDs for a specific data type"""
        if data_type not in self.cache:
            self._load_data_type(data_type)
        return list(self.cache[data_type].keys())
    
def _load_data_type(self, data_type):
        """Load all data files of a specific type with schema validation"""
        self.logger.info(f"Loading {data_type} data...")
        self.cache[data_type] = {}
        
        # Load schema first
        schema_path = os.path.join(self.data_path, "schemas", f"{data_type}.schema.json")
        schema = None
        
        if os.path.exists(schema_path):
            try:
                with open(schema_path, 'r') as f:
                    schema = json.load(f)
                self.logger.debug(f"Loaded schema for {data_type}")
            except Exception as e:
                self.logger.error(f"Error loading schema: {e}")
        
        # Load data files
        data_dir = os.path.join(self.data_path, data_type)
        if not os.path.exists(data_dir):
            self.logger.warning(f"Data directory not found: {data_dir}")
            return
            
        for filename in os.listdir(data_dir):
            if filename.endswith('.json'):
                file_path = os.path.join(data_dir, filename)
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                    
                    # Validate against schema if available
                    if schema:
                        try:
                            jsonschema.validate(data, schema)
                        except jsonschema.exceptions.ValidationError as e:
                            self.logger.error(f"Schema validation failed for {file_path}: {e}")
                            continue
                    
                    # Basic validation if no schema
                    if 'id' not in data:
                        self.logger.warning(f"Missing ID in {file_path}, skipping")
                        continue
                    
                    self.cache[data_type][data['id']] = data
                    self.logger.debug(f"Loaded {data_type} data: {data['id']}")
                except json.JSONDecodeError:
                    self.logger.error(f"Invalid JSON in {file_path}")
                except Exception as e:
                    self.logger.error(f"Error loading {file_path}: {e}")