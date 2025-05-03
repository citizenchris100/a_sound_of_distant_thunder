# src/game/NPCBehaviorSystem.py
"""
NPC Behavior System for A Sound of Distant Thunder.
Manages NPC behaviors, reactions, and state changes.
"""
import logging
import random
from enum import Enum

logger = logging.getLogger("NPCBehaviorSystem")

class BehaviorType(Enum):
    """Types of NPC behavior"""
    NEUTRAL = "neutral"
    FRIENDLY = "friendly"
    WARY = "wary"
    HOSTILE = "hostile"
    ASSIMILATED = "assimilated"

class NPCBehaviorSystem:
    """Manages NPC behaviors and reactions."""
    
    def __init__(self, game_state, event_system):
        """
        Initialize NPC behavior system.
        
        Args:
            game_state: GameState instance
            event_system: EventSystem instance
        """
        self.game_state = game_state
        self.event_system = event_system
    
    def update_npc_suspicion(self, npc_id, amount):
        """
        Update an NPC's suspicion of the player.
        
        Args:
            npc_id (str): ID of the NPC
            amount (int): Amount to change suspicion by (positive increases suspicion)
            
        Returns:
            str or None: Behavior change if suspicion threshold crossed, None otherwise
        """
        npc = self.game_state.get_npc(npc_id)
        if not npc:
            logger.error(f"NPC not found: {npc_id}")
            return None
        
        old_suspicion = getattr(npc, "suspicion", 0)
        new_suspicion = max(0, min(100, old_suspicion + amount))
        
        # Update NPC suspicion
        npc.suspicion = new_suspicion
        
        # Check for behavior changes
        behavior_change = None
        
        if new_suspicion >= 80 and old_suspicion < 80:
            # Become hostile
            npc.behavior_type = BehaviorType.HOSTILE.value
            behavior_change = "became_hostile"
        elif new_suspicion >= 50 and old_suspicion < 50:
            # Become wary
            npc.behavior_type = BehaviorType.WARY.value
            behavior_change = "became_wary"
        elif new_suspicion < 50 and old_suspicion >= 50:
            # Return to neutral
            npc.behavior_type = BehaviorType.NEUTRAL.value
            behavior_change = "became_neutral"
        
        # Emit event if behavior changed
        if behavior_change:
            self.event_system.emit("npc_behavior_changed", {
                "npc_id": npc_id,
                "change": behavior_change,
                "old_suspicion": old_suspicion,
                "new_suspicion": new_suspicion
            })
        
        return behavior_change
    
    def update_npc_trust(self, npc_id, amount):
        """
        Update an NPC's trust of the player.
        
        Args:
            npc_id (str): ID of the NPC
            amount (int): Amount to change trust by (positive increases trust)
            
        Returns:
            str or None: Relationship change if trust threshold crossed, None otherwise
        """
        npc = self.game_state.get_npc(npc_id)
        if not npc:
            logger.error(f"NPC not found: {npc_id}")
            return None
        
        old_trust = getattr(npc, "trust_level", 0)
        new_trust = max(0, min(100, old_trust + amount))
        
        # Update NPC trust
        npc.trust_level = new_trust
        
        # Check for relationship changes
        relationship_change = None
        
        if new_trust >= 80 and old_trust < 80:
            relationship_change = "became_ally"
        elif new_trust >= 50 and old_trust < 50:
            relationship_change = "became_friendly"
        elif new_trust < 30 and old_trust >= 30:
            relationship_change = "became_unfriendly"
        
        # Emit event if relationship changed
        if relationship_change:
            self.event_system.emit("npc_relationship_changed", {
                "npc_id": npc_id,
                "change": relationship_change,
                "old_trust": old_trust,
                "new_trust": new_trust
            })
        
        return relationship_change
    
    def would_join_coalition(self, npc_id):
        """
        Check if an NPC would join the player's coalition.
        
        Args:
            npc_id (str): ID of the NPC
            
        Returns:
            bool: True if NPC would join, False otherwise
        """
        npc = self.game_state.get_npc(npc_id)
        if not npc:
            logger.error(f"NPC not found: {npc_id}")
            return False
        
        # Assimilated NPCs might pretend to join (deception)
        if getattr(npc, "is_assimilated", False):
            # Higher suspicion reduces chance of successful deception
            suspicion = getattr(npc, "suspicion", 0)
            deception_chance = 0.9 - (suspicion / 200)
            return random.random() < deception_chance
        else:
            # Non-assimilated join based on trust
            trust_level = getattr(npc, "trust_level", 0)
            return trust_level >= 60
    
    def add_observed_behavior(self, npc_id, behavior):
        """
        Add an observed behavior to an NPC's history.
        
        Args:
            npc_id (str): ID of the NPC
            behavior (str): Description of observed behavior
            
        Returns:
            bool: True if behavior is unusual, False otherwise
        """
        npc = self.game_state.get_npc(npc_id)
        if not npc:
            logger.error(f"NPC not found: {npc_id}")
            return False
        
        # Get game time for timestamp
        timestamp = self.game_state.time.copy()
        
        # Create observation record
        observation = {
            "behavior": behavior,
            "timestamp": timestamp
        }
        
        # Initialize observed_behaviors if not present
        if not hasattr(npc, "observed_behaviors"):
            npc.observed_behaviors = []
        
        # Add observation
        npc.observed_behaviors.append(observation)
        
        # Check if behavior is unusual
        is_unusual = self._is_behavior_unusual(npc, behavior)
        
        if is_unusual:
            # Initialize unusual_behaviors if not present
            if not hasattr(npc, "unusual_behaviors"):
                npc.unusual_behaviors = 0
                
            npc.unusual_behaviors += 1
            
            # Emit behavior observed event
            self.event_system.emit("unusual_behavior_observed", {
                "npc_id": npc_id,
                "behavior": behavior
            })
        
        return is_unusual
    
    def _is_behavior_unusual(self, npc, behavior):
        """
        Check if a behavior is unusual for an NPC.
        
        Args:
            npc: NPC instance
            behavior (str): Behavior to check
            
        Returns:
            bool: True if behavior is unusual, False otherwise
        """
        # Assimilated NPCs sometimes show unusual behaviors
        if getattr(npc, "is_assimilated", False):
            # Base chance for assimilated NPCs to show unusual behavior
            if random.random() < 0.2:
                return True
        
        # List of known unusual behaviors
        unusual_behaviors = [
            "avoided_questions_about_past",
            "spoke_with_unusual_cadence",
            "showed_no_emotion",
            "stared_blankly",
            "met_secretly_with_others",
            "accessed_restricted_area",
            "collected_unusual_materials",
            "observed_strange_eating_habits",
            "unusual_reaction_to_stimuli",
            "communication_with_unknown_entities"
        ]
        
        return behavior in unusual_behaviors
    
    def get_assimilation_evidence(self, npc_id):
        """
        Get evidence level for NPC being assimilated based on observations.
        
        Args:
            npc_id (str): ID of the NPC
            
        Returns:
            float: Evidence level from 0.0 to 1.0
        """
        npc = self.game_state.get_npc(npc_id)
        if not npc:
            logger.error(f"NPC not found: {npc_id}")
            return 0.0
        
        # Get observed behaviors
        observed_behaviors = getattr(npc, "observed_behaviors", [])
        if not observed_behaviors:
            return 0.0
        
        # Get unusual behaviors count
        unusual_behaviors = getattr(npc, "unusual_behaviors", 0)
        
        # Calculate evidence level
        evidence = unusual_behaviors / max(5, len(observed_behaviors))
        return min(1.0, evidence)
    
    def get_current_behavior(self, npc_id, game_time=None):
        """
        Get NPC's current behavior action based on time and state.
        
        Args:
            npc_id (str): ID of the NPC
            game_time (dict, optional): Current game time
            
        Returns:
            str or None: Behavior action, or None if no specific behavior
        """
        npc = self.game_state.get_npc(npc_id)
        if not npc:
            logger.error(f"NPC not found: {npc_id}")
            return None
        
        # Use provided game time or get from game state
        if game_time is None:
            game_time = self.game_state.time
        
        # Behavior depends on NPC type and suspicion level
        behavior_type = getattr(npc, "behavior_type", BehaviorType.NEUTRAL.value)
        
        if behavior_type == BehaviorType.HOSTILE.value:
            return "avoid_player"
        
        if behavior_type == BehaviorType.WARY.value:
            if random.random() < 0.3:
                return "observe_player"
            return None
        
        if getattr(npc, "is_assimilated", False):
            # Assimilated NPCs sometimes meet with other assimilated
            hour = game_time.get("hour", 12)
            if hour >= 22 or hour <= 4:  # Late night
                if random.random() < 0.4:
                    return "secret_meeting"
            
            # Try to assimilate others if undetected
            suspicion = getattr(npc, "suspicion", 0)
            if suspicion < 30 and random.random() < 0.1:
                return "attempt_assimilation"
        
        return None