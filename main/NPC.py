import random
from enum import Enum

class BehaviorType(Enum):
    """Types of NPC behavior"""
    NEUTRAL = "neutral"
    FRIENDLY = "friendly"
    WARY = "wary"
    HOSTILE = "hostile"
    ASSIMILATED = "assimilated"
    

class NPC:
    """
    Represents a non-player character with behavior, assimilation status, and relationships.
    """
    def __init__(self, npc_id, data):
        self.id = npc_id
        self.name = data["name"]
        self.description = data["description"]
        self.persistent = data.get("persistent", False)
        
        # Dialog references
        self.dialog_trees = data.get("dialog_trees", [])
        
        # Game mechanics attributes
        self.health = data.get("health", 100)
        self.max_health = data.get("health", 100)
        self.defense = data.get("defense", 0)
        self.strength = data.get("strength", 5)
        self.gun_skill = data.get("gun_skill", 0)
        self.luck = data.get("luck", 0)
        self.awareness = data.get("awareness", 0)
        
        # Inventory
        self.inventory = []
        for item_id in data.get("inventory", []):
            item_data = {"id": item_id}
            self.inventory.append(item_data)
            
        # Equipment
        self.equipped = {
            "weapon": data.get("equipped_weapon"),
            "armor": data.get("equipped_armor"),
            "melee": data.get("equipped_melee")
        }
        
        # Suspicion/trust system (0-100 scales)
        self.suspicion = 0
        self.trust_level = data.get("initial_trust", 0)
        
        # Behavior
        self.behavior_type = BehaviorType(data.get("behavior_pattern", "neutral"))
        
        # Assimilation
        self.is_assimilated = data.get("is_assimilated", False)
        self.assimilation_knowledge = data.get("assimilation_knowledge", {})
        
        # Schedule
        self.schedule = data.get("schedule", {})
        
        # Observation data - what player has observed
        self.observed_behaviors = []
        self.unusual_behaviors = 0
        
    def update_suspicion(self, amount):
        """
        Update suspicion level and return behavior change if threshold crossed.
        
        Args:
            amount (int): Amount to change suspicion by
            
        Returns:
            str or None: Behavior change if threshold crossed, None otherwise
        """
        old_suspicion = self.suspicion
        self.suspicion = max(0, min(100, self.suspicion + amount))
        
        # Determine behavior change based on suspicion thresholds
        if self.suspicion >= 80 and old_suspicion < 80:
            self.behavior_type = BehaviorType.HOSTILE
            return "became_hostile"
        elif self.suspicion >= 50 and old_suspicion < 50:
            self.behavior_type = BehaviorType.WARY
            return "became_wary"
        elif self.suspicion < 50 and old_suspicion >= 50:
            self.behavior_type = BehaviorType.NEUTRAL
            return "became_neutral"
        
        return None
        
    def update_trust(self, amount):
        """
        Update trust level and return relationship change if threshold crossed.
        
        Args:
            amount (int): Amount to change trust by
            
        Returns:
            str or None: Relationship change if threshold crossed, None otherwise
        """
        old_trust = self.trust_level
        self.trust_level = max(0, min(100, self.trust_level + amount))
        
        # Determine relationship change based on trust thresholds
        if self.trust_level >= 80 and old_trust < 80:
            return "became_ally"
        elif self.trust_level >= 50 and old_trust < 50:
            return "became_friendly"
        elif self.trust_level < 30 and old_trust >= 30:
            return "became_unfriendly"
        
        return None
        
    def would_join_coalition(self):
        """
        Check if NPC would join player's coalition.
        
        Returns:
            bool: True if NPC would join, False otherwise
        """
        # Assimilated NPCs might pretend to join (deception)
        if self.is_assimilated:
            # Higher suspicion reduces chance of successful deception
            deception_chance = 0.9 - (self.suspicion / 200)
            return random.random() < deception_chance
        else:
            # Non-assimilated join based on trust
            return self.trust_level >= 60
            
    def add_observed_behavior(self, behavior):
        """
        Add an observed behavior to NPC's history.
        
        Args:
            behavior (str): Description of observed behavior
            
        Returns:
            bool: True if behavior is unusual, False otherwise
        """
        timestamp = {"day": 1, "hour": 12, "minute": 0}  # TODO: Use actual game time
        
        observation = {
            "behavior": behavior,
            "timestamp": timestamp
        }
        
        self.observed_behaviors.append(observation)
        
        # Check if behavior is unusual based on NPC type
        is_unusual = self._is_behavior_unusual(behavior)
        if is_unusual:
            self.unusual_behaviors += 1
            
        return is_unusual
        
    def _is_behavior_unusual(self, behavior):
        """
        Check if a behavior is unusual for this NPC.
        
        Args:
            behavior (str): Behavior to check
            
        Returns:
            bool: True if behavior is unusual, False otherwise
        """
        # Assimilated NPCs sometimes show unusual behaviors
        if self.is_assimilated:
            # Base chance for assimilated NPCs to show unusual behavior
            if random.random() < 0.2:
                return True
                
        # Specific unusual behaviors
        unusual_behaviors = [
            "avoided_questions_about_past",
            "spoke_with_unusual_cadence",
            "showed_no_emotion",
            "stared_blankly",
            "met_secretly_with_others",
            "accessed_restricted_area",
            "collected_unusual_materials"
        ]
        
        return behavior in unusual_behaviors
        
    def get_assimilation_evidence(self):
        """
        Get evidence level for NPC being assimilated based on observations.
        
        Returns:
            float: Evidence level from 0.0 to 1.0
        """
        if len(self.observed_behaviors) == 0:
            return 0.0
            
        # Calculate evidence level based on unusual behaviors
        evidence = self.unusual_behaviors / max(5, len(self.observed_behaviors))
        return min(1.0, evidence)
        
    def get_current_location(self, game_time):
        """
        Get NPC's location based on schedule and time.
        
        Args:
            game_time (dict): Current game time
            
        Returns:
            str or None: Location ID, or None if no scheduled location
        """
        # Get time of day key
        hour = game_time["hour"]
        if 5 <= hour < 12:
            time_key = "morning"
        elif 12 <= hour < 18:
            time_key = "afternoon"
        else:
            time_key = "evening"
            
        # Return scheduled location for this time if available
        return self.schedule.get(time_key)
        
    def get_current_behavior(self, game_time):
        """
        Get NPC's current behavior action based on time and state.
        
        Args:
            game_time (dict): Current game time
            
        Returns:
            str or None: Behavior action, or None if no specific behavior
        """
        # Behavior depends on NPC type and suspicion level
        if self.behavior_type == BehaviorType.HOSTILE:
            return "avoid_player"
            
        if self.behavior_type == BehaviorType.WARY:
            if random.random() < 0.3:
                return "observe_player"
            return None
            
        if self.is_assimilated:
            # Assimilated NPCs sometimes meet with other assimilated
            hour = game_time["hour"]
            if hour >= 22 or hour <= 4:  # Late night
                if random.random() < 0.4:
                    return "secret_meeting"
            
            # Try to assimilate others if undetected
            if self.suspicion < 30 and random.random() < 0.1:
                return "attempt_assimilation"
                
        return None