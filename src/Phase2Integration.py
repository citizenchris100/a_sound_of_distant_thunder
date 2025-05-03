"""
Phase 2 Integration for A Sound of Distant Thunder
Integrates UI styling, input handling, testing, and placeholders.
"""
import pygame
import logging
import os
import random

# Configure logging
logger = logging.getLogger("Phase2Integration")

class Phase2Integration:
    """
    Integrates and configures all Phase 2 components.
    Acts as a facade to simplify initialization and testing.
    """
    def __init__(self, game_engine):
        """
        Initialize Phase 2 integration.
        
        Args:
            game_engine: GameEngine instance
        """
        self.game_engine = game_engine
        self.theme = None
        self.input_manager = None
        self.tester = None
        
        logger.info("Phase 2 Integration initialized")
    
    def initialize(self):
        """Initialize all Phase 2 components"""
        # Import required modules
        from UITheme import UITheme
        from src.input.InputManager import InputManager
        from src.tests.GameTester import GameTester
        
        # Create theme first (no dependencies)
        self.theme = UITheme()
        
        # Create input manager (depends on game engine)
        self.input_manager = InputManager(self.game_engine)
        
        # Apply theme to UI components
        self._apply_theme()
        
        # Create testing framework (depends on game engine)
        self.tester = GameTester(self.game_engine)
        
        # Create initial placeholder assets
        self._create_placeholders()
        
        logger.info("Phase 2 components initialized")
    
    def _apply_theme(self):
        """Apply theme to UI components"""
        # Get UI manager
        ui_manager = getattr(self.game_engine, "ui_manager", None)
        if not ui_manager:
            logger.error("UIManager not found, cannot apply theme")
            return
        
        # Store theme in UI manager for components to access
        ui_manager.theme = self.theme
        
        # Update existing components to use theme if they support it
        for name, component in ui_manager.ui_components.items():
            if hasattr(component, "set_theme"):
                component.set_theme(self.theme)
                logger.debug(f"Applied theme to {name}")
    
    def _create_placeholders(self):
        """Create placeholder assets for testing and development"""
        # Get asset manager
        asset_manager = getattr(self.game_engine, "asset_manager", None)
        if not asset_manager:
            logger.error("AssetManager not found, cannot create placeholders")
            return
        
        # Check if asset manager has create_placeholder_asset method
        if not hasattr(asset_manager, "create_placeholder_asset"):
            logger.error("AssetManager does not have create_placeholder_asset method")
            return
        
        # Create basic placeholder assets for UI
        asset_manager.create_placeholder_asset("ui_dialog_bg", 700, 180, "Dialog", (40, 40, 60))
        asset_manager.create_placeholder_asset("ui_inventory_bg", 780, 90, "Inventory", (40, 40, 60))
        asset_manager.create_placeholder_asset("ui_verb_bg", 780, 40, "Verbs", (40, 40, 60))
        
        # Create verb icons
        for verb in ["look", "talk", "take", "use", "go"]:
            asset_manager.create_placeholder_asset(f"verb_{verb}", 50, 30, verb.upper(), (60, 60, 80))
        
        # Check for missing NPCs, objects, and items based on current location
        self._check_and_create_missing_location_assets()
    
    def _check_and_create_missing_location_assets(self):
        """Check for missing location assets and create placeholders"""
        # Get required components
        asset_manager = getattr(self.game_engine, "asset_manager", None)
        data_manager = getattr(self.game_engine, "data_manager", None)
        game_state = getattr(self.game_engine, "game_state", None)
        
        if not all([asset_manager, data_manager, game_state]):
            return
        
        # Get current location
        location_id = game_state.current_location
        if not location_id:
            return
        
        # Check location background
        bg_key = f"bg_{location_id}"
        if bg_key not in asset_manager.images:
            asset_manager.create_placeholder_asset(bg_key, 800, 600, f"Location: {location_id}", (20, 30, 50))
        
        # Get location data
        location_data = data_manager.get_data("locations", location_id)
        if not location_data:
            return
        
        # Create NPC placeholders
        for npc_id in location_data.get("npcs", []):
            npc_key = f"npc_{npc_id}"
            if npc_key not in asset_manager.images:
                asset_manager.create_placeholder_asset(npc_key, 64, 128, f"NPC: {npc_id}", (100, 150, 100))
            
            portrait_key = f"portrait_{npc_id}"
            if portrait_key not in asset_manager.images:
                asset_manager.create_placeholder_asset(portrait_key, 80, 80, "Portrait", (100, 150, 100))
        
        # Create object placeholders
        for obj_data in location_data.get("objects", []):
            obj_id = obj_data.get("id")
            if obj_id:
                obj_key = f"obj_{obj_id}"
                if obj_key not in asset_manager.images:
                    asset_manager.create_placeholder_asset(obj_key, 64, 64, f"Obj: {obj_id}", (150, 100, 100))
        
        # Create item placeholders
        item_data = data_manager.get_data("items")
        if item_data:
            for item_id, item in item_data.items():
                item_key = f"item_{item_id}"
                if item_key not in asset_manager.images:
                    # Choose color based on item type
                    item_type = item.get("item_type", "")
                    if item_type == "weapon":
                        color = (220, 50, 50)  # Red for weapons
                    elif item_type == "armor":
                        color = (50, 50, 220)  # Blue for armor
                    elif item_type == "consumable":
                        color = (50, 220, 50)  # Green for consumables
                    else:
                        color = (100, 150, 200)  # Default blue
                    
                    asset_manager.create_placeholder_asset(item_key, 64, 64, item.get("name", item_id), color)
    
    def update(self, dt):
        """
        Update Phase 2 components.
        
        Args:
            dt (float): Time delta in seconds
        """
        # Update input manager
        if self.input_manager:
            self.input_manager.update()
    
    def render_debug_overlay(self, surface):
        """
        Render debug information overlay if in debug mode.
        
        Args:
            surface (pygame.Surface): Surface to render on
        """
        if not self.game_engine.debug_mode:
            return
        
        # Create debug panel
        debug_rect = pygame.Rect(10, 10, 200, 120)
        self.theme.draw_panel(surface, debug_rect)
        
        # Add debug text
        font = pygame.font.Font(None, 18)
        
        # FPS counter
        fps = int(self.game_engine.ui_manager.clock.get_fps())
        fps_text = font.render(f"FPS: {fps}", True, self.theme.text_color)
        surface.blit(fps_text, (debug_rect.left + 10, debug_rect.top + 10))
        
        # Current location
        loc = self.game_engine.game_state.current_location
        loc_text = font.render(f"Location: {loc}", True, self.theme.text_color)
        surface.blit(loc_text, (debug_rect.left + 10, debug_rect.top + 30))
        
        # Mouse position
        mouse_pos = pygame.mouse.get_pos()
        pos_text = font.render(f"Mouse: {mouse_pos[0]}, {mouse_pos[1]}", True, self.theme.text_color)
        surface.blit(pos_text, (debug_rect.left + 10, debug_rect.top + 50))
        
        # Selected verb
        verb_bar = self.game_engine.ui_manager.ui_components.get("verb_bar")
        if verb_bar:
            verb = verb_bar.selected_verb or "None"
            verb_text = font.render(f"Verb: {verb}", True, self.theme.text_color)
            surface.blit(verb_text, (debug_rect.left + 10, debug_rect.top + 70))
        
        # Memory usage (if psutil is available)
        try:
            import psutil
            process = psutil.Process(os.getpid())
            memory = process.memory_info().rss / 1024 / 1024  # MB
            mem_text = font.render(f"Memory: {memory:.1f} MB", True, self.theme.text_color)
            surface.blit(mem_text, (debug_rect.left + 10, debug_rect.top + 90))
        except (ImportError, AttributeError):
            pass


def initialize_phase2(game_engine):
    """
    Initialize Phase 2 components for the game engine.
    
    Args:
        game_engine: GameEngine instance
        
    Returns:
        Phase2Integration: Integration instance
    """
    # Create integration instance
    integration = Phase2Integration(game_engine)
    
    # Initialize components
    integration.initialize()
    
    # Store integration in game engine
    game_engine.phase2_integration = integration
    
    return integration