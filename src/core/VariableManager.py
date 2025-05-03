# src/core/VariableManager.py
"""
Variable Manager for A Sound of Distant Thunder.
Provides a consistent interface for game state variables.
"""
import logging
import json
import os

logger = logging.getLogger("VariableManager")

class VariableManager:
    """Manages game state variables."""
    
    def __init__(self, event_system=None):
        """
        Initialize variable manager.
        
        Args:
            event_system: Optional EventSystem instance for emitting events
        """
        self.variables = {}
        self.event_system = event_system
    
    def get(self, name, default=None):
        """
        Get a variable value.
        
        Args:
            name (str): Variable name
            default: Default value if variable not set
            
        Returns:
            Variable value or default
        """
        return self.variables.get(name, default)
    
    def set(self, name, value):
        """
        Set a variable value.
        
        Args:
            name (str): Variable name
            value: Variable value
        """
        old_value = self.variables.get(name, None)
        self.variables[name] = value
        
        # Emit event if event system is available
        if self.event_system and old_value != value:
            self.event_system.emit("variable_changed", {
                "name": name,
                "old_value": old_value,
                "new_value": value
            })
            
        return value
    
    def modify(self, name, operation, value, default=0):
        """
        Modify a variable with an operation.
        
        Args:
            name (str): Variable name
            operation (str): Operation to perform ("set", "add", "subtract", "multiply", "divide")
            value: Value for operation
            default: Default value if variable not set
            
        Returns:
            New variable value
        """
        current = self.get(name, default)
        
        if operation == "set":
            return self.set(name, value)
        elif operation == "add" or operation == "increment":
            return self.set(name, current + value)
        elif operation == "subtract" or operation == "decrement":
            return self.set(name, current - value)
        elif operation == "multiply":
            return self.set(name, current * value)
        elif operation == "divide" and value != 0:
            return self.set(name, current / value)
        else:
            logger.warning(f"Unknown operation: {operation}")
            return current
    
    def has(self, name):
        """
        Check if a variable exists.
        
        Args:
            name (str): Variable name
            
        Returns:
            bool: True if variable exists, False otherwise
        """
        return name in self.variables
    
    def delete(self, name):
        """
        Delete a variable.
        
        Args:
            name (str): Variable name
            
        Returns:
            bool: True if variable was deleted, False otherwise
        """
        if name in self.variables:
            old_value = self.variables[name]
            del self.variables[name]
            
            # Emit event if event system is available
            if self.event_system:
                self.event_system.emit("variable_deleted", {
                    "name": name,
                    "old_value": old_value
                })
                
            return True
        return False
    
    def clear(self):
        """Clear all variables."""
        old_variables = self.variables.copy()
        self.variables = {}
        
        # Emit event if event system is available
        if self.event_system:
            self.event_system.emit("variables_cleared", {
                "old_variables": old_variables
            })
    
    def save_to_file(self, filepath):
        """
        Save variables to a JSON file.
        
        Args:
            filepath (str): Path to save file
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(self.variables, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving variables to {filepath}: {e}")
            return False
    
    def load_from_file(self, filepath):
        """
        Load variables from a JSON file.
        
        Args:
            filepath (str): Path to load file
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    self.variables = json.load(f)
                return True
            return False
        except Exception as e:
            logger.error(f"Error loading variables from {filepath}: {e}")
            return False