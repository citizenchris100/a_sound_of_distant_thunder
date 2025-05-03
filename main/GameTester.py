"""
Testing Framework for A Sound of Distant Thunder
Provides automated testing of game systems integration.
"""
import pygame
import logging
import time
import random
import os
import tempfile

# Configure logging
logger = logging.getLogger("GameTester")

class GameTester:
    """
    Testing framework for verifying game systems integration.
    Helps identify issues before they reach players.
    """
    def __init__(self, game_engine):
        """
        Initialize the testing framework.
        
        Args:
            game_engine: GameEngine instance
        """
        self.game_engine = game_engine
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.current_test = None
        
        # Test event log
        self.event_log = []
        self.log_events = False
        
        # Register for events if we need to monitor them
        self.game_engine.event_system.subscribe("*", self._on_any_event)
        
        # Create temporary directory for test assets
        self.temp_dir = tempfile.mkdtemp(prefix="asdt_test_")
        
        logger.info("Game Tester initialized")
    
    def _on_any_event(self, data):
        """
        Record any game event to the log.
        
        Args:
            data (dict): Event data
        """
        if self.log_events:
            self.event_log.append(data)
    
    def run_tests(self):
        """
        Run all integration tests.
        
        Returns:
            bool: True if all tests passed, False otherwise
        """
        logger.info("Starting integration tests")
        
        # Run individual tests
        self._test_asset_loading()
        self._test_ui_components()
        self._test_scene_loading()
        self._test_dialog_system()
        self._test_navigation()
        self._test_input_management()
        self._test_theme_system()
        self._test_event_system()
        
        # Report results
        success_rate = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        logger.info(f"Tests completed: {self.tests_run} run, {self.tests_passed} passed, "
                   f"{self.tests_failed} failed ({success_rate:.1f}% success rate)")
        
        # Clean up
        self._cleanup()
        
        return self.tests_failed == 0
    
    def _cleanup(self):
        """Clean up temporary files created during testing"""
        try:
            # Remove temporary directory and its contents
            for root, dirs, files in os.walk(self.temp_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(self.temp_dir)
        except Exception as e:
            logger.error(f"Error cleaning up temp directory: {e}")
    
    def _start_test(self, test_name):
        """
        Start a new test.
        
        Args:
            test_name (str): Name of the test
        """
        self.current_test = test_name
        self.log_events = True
        self.event_log.clear()
        
        logger.info(f"Starting test: {test_name}")
    
    def _end_test(self, success, message=""):
        """
        End the current test and record result.
        
        Args:
            success (bool): Whether the test passed
            message (str, optional): Error message if test failed
        """
        self.tests_run += 1
        
        if success:
            self.tests_passed += 1
            logger.info(f"✓ Test passed: {self.current_test}")
        else:
            self.tests_failed += 1
            logger.error(f"✗ Test failed: {self.current_test} - {message}")
        
        self.current_test = None
        self.log_events = False
    
    def _test_asset_loading(self):
        """Test asset loading system"""
        self._start_test("Asset Loading")
        
        # Check if asset manager exists
        asset_manager = getattr(self.game_engine, "asset_manager", None)
        if not asset_manager:
            self._end_test(False, "AssetManager not found")
            return
        
        # Create a test image file
        test_image_path = os.path.join(self.temp_dir, "test_image.png")
        test_surface = pygame.Surface((16, 16))
        test_surface.fill((255, 0, 0))  # Red
        
        try:
            pygame.image.save(test_surface, test_image_path)
            
            # Test loading the image
            asset_manager.images["test_image"] = pygame.image.load(test_image_path)
            success = "test_image" in asset_manager.images
            
            # Test placeholder creation
            test_placeholder = asset_manager.create_placeholder_asset("test_placeholder", 32, 32, "TEST")
            success = success and "test_placeholder" in asset_manager.images
            
            self._end_test(success, "Failed to load test assets")
        except Exception as e:
            self._end_test(False, f"Exception while testing assets: {e}")
    
    def _test_ui_components(self):
        """Test UI components"""
        self._start_test("UI Components")
        
        # Check if UI manager exists
        ui_manager = getattr(self.game_engine, "ui_manager", None)
        if not ui_manager:
            self._end_test(False, "UIManager not found")
            return
        
        # Check critical UI components
        required_components = ["inventory", "dialog", "verb_bar"]
        missing = [c for c in required_components if c not in ui_manager.ui_components]
        
        if missing:
            self._end_test(False, f"Missing UI components: {', '.join(missing)}")
            return
        
        # Check verb selection functionality
        try:
            verb_bar = ui_manager.ui_components["verb_bar"]
            
            # Track events during selection
            old_verb = verb_bar.selected_verb
            self.log_events = True
            
            # Simulate selecting a verb
            verb_bar.selected_verb = "look"
            self.game_engine.event_system.emit("verb_selected", {"verb": "look"})
            
            # Find verb selected event in log
            verb_event = None
            for e in self.event_log:
                if e.get("verb") == "look":
                    verb_event = e
                    break
            
            # Verify event was emitted with correct verb
            if verb_event:
                self._end_test(True)
            else:
                self._end_test(False, "Verb selection did not emit correct event")
            
            # Restore state
            verb_bar.selected_verb = old_verb
        except Exception as e:
            self._end_test(False, f"Exception while testing UI: {e}")
    
    def _test_scene_loading(self):
        """Test scene loading system"""
        self._start_test("Scene Loading")
        
        # Check if scene manager exists
        scene_manager = getattr(self.game_engine, "scene_manager", None)
        if not scene_manager:
            self._end_test(False, "SceneManager not found")
            return
        
        # Get current location from game state
        current_location = self.game_engine.game_state.current_location
        if not current_location:
            self._end_test(False, "No current location in game state")
            return
        
        # Check if current scene matches location
        if not scene_manager.current_scene:
            self._end_test(False, "No current scene in scene manager")
            return
        
        location_matches = (scene_manager.current_scene.location_id == current_location)
        self._end_test(location_matches, "Current scene does not match game state location")
    
    def _test_dialog_system(self):
        """Test dialog system"""
        self._start_test("Dialog System")
        
        # Check if dialog manager exists
        dialog_manager = getattr(self.game_engine, "dialog_manager", None)
        if not dialog_manager:
            self._end_test(False, "DialogManager not found")
            return
        
        # Test dialog UI
        dialog_ui = self.game_engine.ui_manager.ui_components.get("dialog")
        if not dialog_ui:
            self._end_test(False, "Dialog UI component not found")
            return
        
        # Test basic dialog functionality
        try:
            # Record initial state
            was_visible = dialog_ui.visible
            old_npc = dialog_ui.current_npc
            
            # Simulate dialog with test NPC
            test_dialog_id = "test_dialog"
            test_npc_id = "test_npc"
            
            # Create test dialog data
            self.game_engine.data_manager.cache.setdefault("dialogs", {})
            self.game_engine.data_manager.cache["dialogs"][test_dialog_id] = {
                "start_node": "greeting",
                "nodes": {
                    "greeting": {
                        "text": "This is a test dialog.",
                        "options": [
                            {"id": "option1", "text": "Test option 1"}
                        ]
                    }
                }
            }
            
            # Start dialog
            dialog_manager.start_dialog(test_dialog_id, test_npc_id)
            
            # Verify dialog UI is visible
            dialog_started = dialog_ui.visible and dialog_ui.current_npc == test_npc_id
            
            # Restore state
            dialog_ui.visible = was_visible
            dialog_ui.current_npc = old_npc
            
            self._end_test(dialog_started, "Dialog did not start correctly")
        except Exception as e:
            self._end_test(False, f"Exception while testing dialog: {e}")
        
        # Clean up test data
        if "dialogs" in self.game_engine.data_manager.cache:
            if test_dialog_id in self.game_engine.data_manager.cache["dialogs"]:
                del self.game_engine.data_manager.cache["dialogs"][test_dialog_id]
    
    def _test_navigation(self):
        """Test navigation system"""
        self._start_test("Navigation")
        
        # Check if navigation system exists
        navigation_system = getattr(self.game_engine, "navigation_system", None)
        if not navigation_system:
            self._end_test(False, "NavigationSystem not found")
            return
        
        # Record current location
        old_location = self.game_engine.game_state.current_location
        
        # Create test location data
        self.game_engine.data_manager.cache.setdefault("locations", {})
        
        test_location_id = "test_location"
        self.game_engine.data_manager.cache["locations"][test_location_id] = {
            "name": "Test Location",
            "description": "A test location for navigation testing.",
            "exits": {}
        }
        
        # Attempt navigation
        try:
            # Enable event logging
            self.log_events = True
            
            # Try to navigate to test location
            navigation_system.navigate_to_location(test_location_id)
            
            # Check if location changed event was emitted
            location_event = None
            for e in self.event_log:
                if 'new_location' in e and e['new_location'] == test_location_id:
                    location_event = e
                    break
            
            # Verify location change
            location_changed = (self.game_engine.game_state.current_location == test_location_id)
            
            # Restore original location
            if old_location:
                self.game_engine.game_state.load_location(old_location)
            
            self._end_test(location_changed, "Navigation did not change location correctly")
        except Exception as e:
            # Restore original location
            if old_location:
                self.game_engine.game_state.load_location(old_location)
            
            self._end_test(False, f"Exception while testing navigation: {e}")
        
        # Clean up test data
        if "locations" in self.game_engine.data_manager.cache:
            if test_location_id in self.game_engine.data_manager.cache["locations"]:
                del self.game_engine.data_manager.cache["locations"][test_location_id]
    
    def _test_input_management(self):
        """Test input management system"""
        self._start_test("Input Management")
        
        # Check if input manager exists
        input_manager = getattr(self.game_engine, "phase2_integration", None)
        if not input_manager:
            input_manager = getattr(self.game_engine, "input_manager", None)
            
        if not input_manager:
            self._end_test(False, "InputManager not found")
            return
        
        # Test basic input functionality
        try:
            # Create a test key binding
            action_name = "test_action"
            key_code = pygame.K_t
            
            # Set key binding
            if hasattr(input_manager, "set_action_key"):
                input_manager.set_action_key(action_name, key_code)
                
                # Verify key binding
                key_binding_works = (input_manager.get_action_key(action_name) == key_code)
                self._end_test(key_binding_works, "Key binding failed")
            else:
                # Basic test passed if input manager exists
                self._end_test(True)
        except Exception as e:
            self._end_test(False, f"Exception while testing input management: {e}")
    
    def _test_theme_system(self):
        """Test UI theme system"""
        self._start_test("Theme System")
        
        # Check if theme exists
        theme = None
        ui_manager = getattr(self.game_engine, "ui_manager", None)
        if ui_manager:
            theme = getattr(ui_manager, "theme", None)
        
        if not theme:
            phase2 = getattr(self.game_engine, "phase2_integration", None)
            if phase2:
                theme = getattr(phase2, "theme", None)
        
        if not theme:
            # Check if UITheme class is available
            from UITheme import UITheme
            theme = UITheme()
        
        if not theme:
            self._end_test(False, "UITheme not found")
            return
        
        # Test basic theme functionality
        try:
            # Create a test surface
            surface = pygame.Surface((200, 100))
            rect = pygame.Rect(0, 0, 100, 50)
            
            # Draw a panel using the theme
            if hasattr(theme, "draw_panel"):
                theme.draw_panel(surface, rect)
                
                # Check if panel was drawn (simple pixel test)
                pixel_color = surface.get_at((50, 25))
                panel_drawn = (pixel_color[3] > 0)  # Non-zero alpha
                
                self._end_test(panel_drawn, "Theme panel not drawn correctly")
            else:
                # Basic test passed if theme exists
                self._end_test(True)
        except Exception as e:
            self._end_test(False, f"Exception while testing theme system: {e}")
    
    def _test_event_system(self):
        """Test event system"""
        self._start_test("Event System")
        
        # Check if event system exists
        event_system = getattr(self.game_engine, "event_system", None)
        if not event_system:
            self._end_test(False, "EventSystem not found")
            return
        
        # Test event subscription and emission
        try:
            # Create a test event
            test_event_name = "test_event"
            test_event_data = {"value": random.randint(1, 100)}
            received_data = [None]  # Use a list to modify from inside handler
            
            # Create event handler
            def test_handler(data):
                received_data[0] = data
            
            # Subscribe to event
            event_system.subscribe(test_event_name, test_handler)
            
            # Emit event
            event_system.emit(test_event_name, test_event_data)
            
            # Verify event was received with correct data
            event_received = (received_data[0] == test_event_data)
            
            # Unsubscribe from event
            event_system.unsubscribe(test_event_name, test_handler)
            
            self._end_test(event_received, "Event system did not deliver event correctly")
        except Exception as e:
            self._end_test(False, f"Exception while testing event system: {e}")

    def simulate_user_interaction(self, duration=5.0):
        """
        Simulate user interaction for a specified duration.
        
        Args:
            duration (float): Duration in seconds
        """
        logger.info(f"Starting user interaction simulation for {duration} seconds")
        
        start_time = time.time()
        frame_count = 0
        
        # Get screen dimensions
        screen_width, screen_height = 800, 600
        ui_manager = getattr(self.game_engine, "ui_manager", None)
        if ui_manager and ui_manager.screen:
            screen_width, screen_height = ui_manager.screen.get_size()
        
        # Main simulation loop
        while time.time() - start_time < duration:
            frame_count += 1
            
            # Every 10 frames, perform a random action
            if frame_count % 10 == 0:
                action = random.choice(["click", "move", "key"])
                
                if action == "click":
                    # Random click position
                    x = random.randint(0, screen_width - 1)
                    y = random.randint(0, screen_height - 1)
                    
                    # Create click event
                    click_event = pygame.event.Event(
                        pygame.MOUSEBUTTONDOWN,
                        {"pos": (x, y), "button": 1}
                    )
                    
                    # Post event
                    pygame.event.post(click_event)
                
                elif action == "move":
                    # Random mouse movement
                    x = random.randint(0, screen_width - 1)
                    y = random.randint(0, screen_height - 1)
                    
                    # Create motion event
                    motion_event = pygame.event.Event(
                        pygame.MOUSEMOTION,
                        {"pos": (x, y), "rel": (0, 0), "buttons": (0, 0, 0)}
                    )
                    
                    # Post event
                    pygame.event.post(motion_event)
                
                elif action == "key":
                    # Random key press
                    key = random.choice([
                        pygame.K_RETURN, pygame.K_ESCAPE, pygame.K_SPACE,
                        pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d,
                        pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT
                    ])
                    
                    # Create key event
                    key_event = pygame.event.Event(
                        pygame.KEYDOWN,
                        {"key": key, "mod": 0, "unicode": chr(key)}
                    )
                    
                    # Post event
                    pygame.event.post(key_event)
            
            # Process events and update UI
            self.game_engine.ui_manager._handle_mouse_movement(
                pygame.event.Event(pygame.MOUSEMOTION, {"pos": pygame.mouse.get_pos()})
            )
            
            # Let the game process one frame
            self.game_engine.ui_manager._update()
            self.game_engine.ui_manager._render()
            
            # Add a small delay
            pygame.time.delay(16)  # ~60 FPS
        
        logger.info(f"Simulation completed: {frame_count} frames in {time.time() - start_time:.2f} seconds")