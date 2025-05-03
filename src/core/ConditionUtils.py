# src/core/ConditionUtils.py
"""
Condition evaluation utilities for A Sound of Distant Thunder.
Provides consistent condition handling across all systems.
"""
import logging

logger = logging.getLogger("ConditionUtils")

class ConditionEvaluator:
    """Evaluates conditions based on game state."""
    
    def __init__(self, game_state):
        """
        Initialize condition evaluator.
        
        Args:
            game_state: GameState instance
        """
        self.game_state = game_state
    
    def evaluate_condition(self, condition):
        """
        Evaluate a condition against the current game state.
        
        Args:
            condition (dict or str): Condition to evaluate
            
        Returns:
            bool: True if condition is met, False otherwise
        """
        if not condition:
            return True
        
        if isinstance(condition, str):
            return self._evaluate_string_condition(condition)
        elif isinstance(condition, dict):
            return self._evaluate_dict_condition(condition)
        
        # Unknown condition format
        logger.warning(f"Unknown condition format: {condition}")
        return True
    
    def _evaluate_string_condition(self, condition):
        """
        Evaluate a string condition.
        
        Args:
            condition (str): Condition string
            
        Returns:
            bool: Evaluation result
        """
        # Common string condition formats
        if condition == "is_assimilated":
            # Check if current NPC is assimilated
            if not hasattr(self, "current_npc"):
                return False
            npc = self.game_state.get_npc(self.current_npc)
            return npc and getattr(npc, "is_assimilated", False)
        
        elif condition == "has_joined_coalition":
            # Check if current NPC is in coalition
            if not hasattr(self, "current_npc"):
                return False
            return self.current_npc in self.game_state.coalition_members
        
        elif condition.startswith("has_item:"):
            # Check if player has specific item
            item_id = condition.split(":")[1]
            return self.game_state.has_item(item_id)
        
        elif condition.startswith("has_flag:"):
            # Check if flag is set
            flag_name = condition.split(":")[1]
            return self.game_state.get_variable(flag_name, False)
        
        elif condition.startswith("visited_node:"):
            # Check if dialog node has been visited
            node_id = condition.split(":")[1]
            return node_id in getattr(self, "visited_nodes", set())
        
        # Unknown string condition
        logger.warning(f"Unknown string condition: {condition}")
        return True
    
    def _evaluate_dict_condition(self, condition):
        """
        Evaluate a dictionary condition.
        
        Args:
            condition (dict): Condition dictionary
            
        Returns:
            bool: Evaluation result
        """
        condition_type = condition.get("type")
        
        if not condition_type:
            logger.error("Condition missing type")
            return False
        
        # Handle different condition types
        if condition_type == "has_item":
            item_id = condition.get("item_id")
            return item_id and self.game_state.has_item(item_id)
        
        elif condition_type == "has_variable" or condition_type == "variable_check":
            var_name = condition.get("variable") or condition.get("name")
            expected_value = condition.get("value", True)
            actual_value = self.game_state.get_variable(var_name, False)
            return actual_value == expected_value
        
        elif condition_type == "dialog_variable":
            var_name = condition.get("variable")
            operation = condition.get("operation", "equals")
            value = condition.get("value")
            
            if not var_name or var_name not in getattr(self, "dialog_variables", {}) or value is None:
                return False
            
            current = getattr(self, "dialog_variables", {}).get(var_name)
            
            return self._compare_values(current, value, operation)
        
        elif condition_type == "variable_compare":
            var_name = condition.get("name") or condition.get("variable")
            operator = condition.get("operator", "==")
            value = condition.get("value")
            
            if var_name is None or value is None:
                return False
                
            actual_value = self.game_state.get_variable(var_name, None)
            
            return self._compare_values(actual_value, value, operator)
        
        elif condition_type == "npc_state" or condition_type == "suspicion_level" or condition_type == "trust_level":
            return self._evaluate_npc_condition(condition)
        
        elif condition_type == "game_progress":
            progress_var = condition.get("variable", "game_day")
            threshold = condition.get("threshold", 1)
            operator = condition.get("operator", ">=")
            
            current_value = self.game_state.get_variable(progress_var, 0)
            
            return self._compare_values(current_value, threshold, operator)
        
        elif condition_type == "and":
            subconditions = condition.get("conditions", [])
            return all(self.evaluate_condition(cond) for cond in subconditions)
        
        elif condition_type == "or":
            subconditions = condition.get("conditions", [])
            return any(self.evaluate_condition(cond) for cond in subconditions)
        
        elif condition_type == "not":
            subcondition = condition.get("condition")
            return not self.evaluate_condition(subcondition) if subcondition else True
        
        # Unknown condition type
        logger.warning(f"Unknown condition type: {condition_type}")
        return True
    
    def _evaluate_npc_condition(self, condition):
        """
        Evaluate an NPC-related condition.
        
        Args:
            condition (dict): NPC condition
            
        Returns:
            bool: Evaluation result
        """
        condition_type = condition.get("type")
        state_type = condition.get("state_type")
        npc_id = condition.get("npc_id", getattr(self, "current_npc", None))
        
        if not npc_id:
            return False
        
        npc = self.game_state.get_npc(npc_id)
        if not npc:
            return False
        
        if state_type == "is_assimilated" or condition_type == "npc_assimilated":
            return getattr(npc, "is_assimilated", False)
        
        elif state_type == "in_coalition" or condition_type == "npc_in_coalition":
            return npc_id in self.game_state.coalition_members
        
        elif state_type == "suspicion_level" or condition_type == "suspicion_level":
            suspicion = getattr(npc, "suspicion", 0)
            threshold = condition.get("threshold", 50)
            operator = condition.get("operator", ">=")
            
            return self._compare_values(suspicion, threshold, operator)
        
        elif state_type == "trust_level" or condition_type == "trust_level":
            trust = getattr(npc, "trust_level", 0)
            threshold = condition.get("threshold", 50)
            operator = condition.get("operator", ">=")
            
            return self._compare_values(trust, threshold, operator)
        
        return False
    
    def _compare_values(self, value1, value2, operation):
        """
        Compare two values using the specified operation.
        
        Args:
            value1: First value
            value2: Second value
            operation (str): Comparison operation
            
        Returns:
            bool: Result of the comparison
        """
        if operation in ("equals", "=="):
            return value1 == value2
        elif operation in ("not_equals", "!="):
            return value1 != value2
        elif operation in ("greater_than", ">"):
            return value1 > value2
        elif operation in ("less_than", "<"):
            return value1 < value2
        elif operation in ("greater_equal", ">="):
            return value1 >= value2
        elif operation in ("less_equal", "<="):
            return value1 <= value2
        elif operation == "contains":
            if isinstance(value1, (list, str, dict)):
                return value2 in value1
            return False
        else:
            logger.warning(f"Unknown comparison operation: {operation}")
            return value1 == value2