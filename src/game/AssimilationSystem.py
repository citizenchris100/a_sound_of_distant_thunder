class AssimilationSystem:
    """
    Manages the alien goo assimilation mechanics.
    """
    def __init__(self, game_state, event_system):
        self.game_state = game_state
        self.event_system = event_system
        self.logger = logging.getLogger("AssimilationSystem")
        
    def assimilate_npc(self, npc_id, method="goo_vial"):
        """
        Attempt to assimilate an NPC.
        
        Args:
            npc_id (str): ID of NPC to assimilate
            method (str): Method of assimilation
            
        Returns:
            bool: True if assimilation succeeded, False otherwise
        """
        npc = self.game_state.npcs.get(npc_id)
        if not npc or npc.is_assimilated:
            return False
            
        # Different assimilation methods have different requirements
        if method == "goo_vial":
            # Requires a vial of goo
            if not self.game_state.has_item("goo_vial"):
                return False
                
            # Use up the vial
            self.game_state.remove_item("goo_vial")
            success = True
            
        elif method == "npc_assimilation":
            # Another assimilated NPC tries to assimilate
            # Success depends on circumstances
            success_chance = 0.7  # Base chance
            
            # Modify based on location
            if self.game_state.current_location in ["secure_area", "public_space"]:
                success_chance *= 0.5  # Harder in public/secure areas
                
            success = random.random() < success_chance
            
        else:
            # Unknown method
            return False
            
        if success:
            # Perform the assimilation
            npc.is_assimilated = True
            npc.behavior_type = BehaviorType.ASSIMILATED
            
            # Emit assimilation event
            self.event_system.emit("npc_assimilated", {
                "npc_id": npc_id,
                "method": method
            })
            
            # If NPC was in coalition, they are now infiltrating
            if npc_id in self.game_state.coalition_members:
                self.event_system.emit("coalition_infiltrated", {
                    "npc_id": npc_id
                })
                
            self.logger.info(f"NPC assimilated: {npc_id}")
            return True
        else:
            # Failed assimilation may raise suspicion
            npc.update_suspicion(30)
            
            # Emit failed assimilation event
            self.event_system.emit("assimilation_failed", {
                "npc_id": npc_id,
                "method": method
            })
            
            self.logger.info(f"Assimilation failed: {npc_id}")
            return False
            
    def detect_assimilation(self, npc_id, detection_method="observation"):
        """
        Attempt to detect if an NPC is assimilated.
        
        Args:
            npc_id (str): ID of NPC to check
            detection_method (str): Method of detection
            
        Returns:
            dict: Detection result
        """
        npc = self.game_state.npcs.get(npc_id)
        if not npc:
            return {"success": False, "certainty": 0, "message": "NPC not found"}
            
        # Base result values
        result = {
            "success": False,
            "certainty": 0,
            "message": "No evidence of assimilation"
        }
        
        # Different detection methods have different accuracy
        if detection_method == "observation":
            # Based on observed behaviors
            evidence = npc.get_assimilation_evidence()
            result["certainty"] = evidence * 100
            
            if evidence > 0.8:
                result["success"] = True
                result["message"] = "Strong evidence of assimilation"
            elif evidence > 0.5:
                result["success"] = npc.is_assimilated  # Correct if assimilated
                result["message"] = "Possible evidence of assimilation"
            else:
                result["success"] = False  # Inconclusive
                result["message"] = "Inconclusive evidence"
                
        elif detection_method == "questioning":
            # Based on dialog responses
            # Raises suspicion
            npc.update_suspicion(15)
            
            # More accurate than observation
            if npc.is_assimilated:
                # 60% chance to detect if actually assimilated
                result["success"] = random.random() < 0.6
                result["certainty"] = 60 if result["success"] else 30
                result["message"] = "Inconsistencies in responses" if result["success"] else "No clear evidence"
            else:
                # 10% chance of false positive
                result["success"] = random.random() < 0.1
                result["certainty"] = 40 if result["success"] else 10
                result["message"] = "Unusual speech patterns" if result["success"] else "Responses seem normal"
                
        elif detection_method == "medical_scan":
            # Most accurate but requires medical equipment
            if not self.game_state.has_item("medical_scanner"):
                return {"success": False, "certainty": 0, "message": "No medical scanner available"}
                
            # High accuracy with scanner
            if npc.is_assimilated:
                # 90% chance to detect if actually assimilated
                result["success"] = random.random() < 0.9
                result["certainty"] = 90 if result["success"] else 20
                result["message"] = "Anomalous cellular structure detected" if result["success"] else "Scan inconclusive"
            else:
                # 5% chance of false positive
                result["success"] = random.random() < 0.05
                result["certainty"] = 80 if result["success"] else 5
                result["message"] = "Unusual readings" if result["success"] else "No anomalies detected"
        
        # Record detection attempt
        if result["success"]:
            # Add to known assimilated if high certainty
            if result["certainty"] >= 80 and npc_id not in self.game_state.known_assimilated:
                self.game_state.known_assimilated.append(npc_id)
                
        # Emit detection event
        self.event_system.emit("assimilation_detection_attempt", {
            "npc_id": npc_id,
            "method": detection_method,
            "result": result
        })
        
        return result