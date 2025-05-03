"""
Input Management System for A Sound of Distant Thunder
Provides advanced input handling with support for both mouse and keyboard interactions.
"""
import pygame
import logging

# Configure logging
logger = logging.getLogger("InputManager")

class InputManager:
    """
    Manages input state and provides higher-level input events.
    Supports mouse and keyboard for better accessibility.
    """
    def __init__(self, game_engine):
        """
        Initialize the input manager.
        
        Args:
            game_engine: GameEngine instance
        """
        self.game_engine = game_engine
        
        # Mouse state
        self.mouse_position = (0, 0)
        self.mouse_buttons = [False, False, False]  # Left, Middle, Right
        self.mouse_hover_object = None
        self.last_click_time = 0
        self.double_click_threshold = 0.3  # seconds
        
        # Keyboard state
        self.keys_pressed = set()
        self.keys_just_pressed = set()
        self.keys_just_released = set()
        
        # Input focus
        self.focus_component = None
        
        # Default keybindings (configurable)
        self.keybindings = {
            "inventory": pygame.K_i,
            "map": pygame.K_m,
            "character": pygame.K_c,
            "journal": pygame.K_j,
            "pause": pygame.K_ESCAPE,
            "interact": pygame.K_SPACE,
            "skip_dialog": pygame.K_SPACE,
            # Verb shortcuts
            "verb_look": pygame.K_l,
            "verb_talk": pygame.K_t,
            "verb_take": pygame.K_g,  # 'g' for 'get'
            "verb_use": pygame.K_u,
            "verb_go": pygame.K_o,
            # Dialog navigation
            "dialog_next": pygame.K_RETURN,
            "dialog_prev": pygame.K_BACKSPACE,
        }
        
        # Cursor images - could be loaded from asset manager
        self.cursors = {
            "default": pygame.SYSTEM_CURSOR_ARROW,
            "hand": pygame.SYSTEM_CURSOR_HAND,
            "text": pygame.SYSTEM_CURSOR_IBEAM,
            "wait": pygame.SYSTEM_CURSOR_WAIT,
            "crosshair": pygame.SYSTEM_CURSOR_CROSSHAIR,
            "not_allowed": pygame.SYSTEM_CURSOR_NO,
            "size": pygame.SYSTEM_CURSOR_SIZENS,
        }
        self.current_cursor = "default"
        
        logger.info("Input Manager initialized")
    
    def update(self):
        """Update input state for the current frame"""
        # Update mouse position
        self.mouse_position = pygame.mouse.get_pos()
        
        # Update mouse buttons (store previous state)
        prev_buttons = self.mouse_buttons.copy()
        self.mouse_buttons = list(pygame.mouse.get_pressed(3))
        
        # Detect mouse button changes
        mouse_just_pressed = [self.mouse_buttons[i] and not prev_buttons[i] for i in range(3)]
        mouse_just_released = [not self.mouse_buttons[i] and prev_buttons[i] for i in range(3)]
        
        # Clear keyboard state for this frame
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_engine.handle_event("game_exit")
            
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                self.keys_just_pressed.add(event.key)
                self._handle_key_press(event)
            
            elif event.type == pygame.KEYUP:
                if event.key in self.keys_pressed:
                    self.keys_pressed.remove(event.key)
                self.keys_just_released.add(event.key)
            
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_movement(event)
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # Check for double click
                    current_time = pygame.time.get_ticks() / 1000
                    if current_time - self.last_click_time < self.double_click_threshold:
                        self._handle_double_click(event)
                    else:
                        self._handle_mouse_click(event)
                    self.last_click_time = current_time
                elif event.button == 3:  # Right click
                    self._handle_right_click(event)
                elif event.button == 4 or event.button == 5:  # Mouse wheel
                    self._handle_mouse_wheel(event)
        
        # Check for hovering
        self._update_hover()
    
    def _update_hover(self):
        """Update hover state based on mouse position"""
        # Create a mock event for compatibility with existing handlers
        mock_event = pygame.event.Event(pygame.MOUSEMOTION, {"pos": self.mouse_position})
        self._handle_mouse_movement(mock_event)
    
    def _handle_mouse_movement(self, event):
        """
        Handle mouse movement events.
        
        Args:
            event (pygame.event.Event): Mouse movement event
        """
        # Check UI components first (they have priority)
        ui_manager = getattr(self.game_engine, "ui_manager", None)
        if ui_manager:
            for component in ui_manager.ui_components.values():
                if hasattr(component, "handle_mouse_movement") and component.visible:
                    if component.handle_mouse_movement(event):
                        self.mouse_hover_object = {"type": "ui", "component": component.name if hasattr(component, "name") else "ui"}
                        return
        
        # Then check scene objects
        scene_manager = getattr(self.game_engine, "scene_manager", None)
        if scene_manager and scene_manager.current_scene:
            hover_obj = scene_manager.current_scene.get_object_at(event.pos)
            if hover_obj:
                self.mouse_hover_object = hover_obj
                # Set appropriate cursor based on object type
                self._set_cursor_for_object(hover_obj)
                return
        
        # No hover object
        self.mouse_hover_object = None
        self._set_cursor("default")
    
    def _set_cursor_for_object(self, obj):
        """
        Set appropriate cursor based on hover object type.
        
        Args:
            obj (dict): Object data with type and other properties
        """
        obj_type = obj.get("type")
        selected_verb = None
        
        # Get current verb if available
        verb_bar = self.game_engine.ui_manager.ui_components.get("verb_bar")
        if verb_bar:
            selected_verb = verb_bar.selected_verb
        
        if obj_type == "npc":
            if selected_verb == "look":
                self._set_cursor("crosshair")
            elif selected_verb == "talk":
                self._set_cursor("text")
            elif selected_verb == "attack":
                self._set_cursor("not_allowed")
            else:
                self._set_cursor("hand")
        elif obj_type == "object":
            if selected_verb == "look":
                self._set_cursor("crosshair")
            elif selected_verb == "take":
                self._set_cursor("hand")
            elif selected_verb == "use":
                self._set_cursor("hand")
            else:
                self._set_cursor("hand")
        elif obj_type == "exit":
            self._set_cursor("hand")
        else:
            # Default cursor
            self._set_cursor("default")
    
    def _set_cursor(self, cursor_name):
        """
        Set the current mouse cursor.
        
        Args:
            cursor_name (str): Name of cursor to use
        """
        if self.current_cursor != cursor_name:
            self.current_cursor = cursor_name
            
            # Set the cursor
            cursor = self.cursors.get(cursor_name, self.cursors["default"])
            pygame.mouse.set_cursor(cursor)
    
    def _handle_mouse_click(self, event):
        """
        Handle mouse click event.
        
        Args:
            event (pygame.event.Event): Mouse click event
        """
        # Check UI components first
        ui_manager = getattr(self.game_engine, "ui_manager", None)
        if ui_manager:
            for component in ui_manager.ui_components.values():
                if hasattr(component, "handle_mouse_click") and component.visible:
                    if component.handle_mouse_click(event):
                        return
        
        # Then check scene
        scene_manager = getattr(self.game_engine, "scene_manager", None)
        if scene_manager and scene_manager.current_scene:
            # Let scene handle the click
            scene_manager.current_scene.handle_mouse_click(event)
    
    def _handle_double_click(self, event):
        """
        Handle mouse double-click event.
        
        Args:
            event (pygame.event.Event): Mouse click event
        """
        # First try to handle in UI components
        ui_manager = getattr(self.game_engine, "ui_manager", None)
        if ui_manager:
            for component in ui_manager.ui_components.values():
                if hasattr(component, "handle_double_click") and component.visible:
                    if component.handle_double_click(event):
                        return
        
        # Then try scene
        scene_manager = getattr(self.game_engine, "scene_manager", None)
        if scene_manager and scene_manager.current_scene:
            if hasattr(scene_manager.current_scene, "handle_double_click"):
                scene_manager.current_scene.handle_double_click(event)
            else:
                # Double click on object/NPC is equivalent to "Use" verb
                # Get object at position
                obj = scene_manager.current_scene.get_object_at(event.pos)
                if obj:
                    # Create a mock event with the "use" verb selected
                    old_verb = None
                    verb_bar = ui_manager.ui_components.get("verb_bar")
                    if verb_bar:
                        old_verb = verb_bar.selected_verb
                        verb_bar.selected_verb = "use"
                    
                    # Forward to scene's click handler
                    scene_manager.current_scene.handle_mouse_click(event)
                    
                    # Restore verb
                    if verb_bar:
                        verb_bar.selected_verb = old_verb
    
    def _handle_right_click(self, event):
        """
        Handle mouse right-click event.
        
        Args:
            event (pygame.event.Event): Mouse click event
        """
        # First try to handle in UI components
        ui_manager = getattr(self.game_engine, "ui_manager", None)
        if ui_manager:
            for component in ui_manager.ui_components.values():
                if hasattr(component, "handle_right_click") and component.visible:
                    if component.handle_right_click(event):
                        return
        
        # Default right-click behavior: Show context menu with available verbs
        scene_manager = getattr(self.game_engine, "scene_manager", None)
        if scene_manager and scene_manager.current_scene:
            obj = scene_manager.current_scene.get_object_at(event.pos)
            if obj:
                # Emit event to show context menu
                self.game_engine.event_system.emit("show_context_menu", {
                    "pos": event.pos,
                    "object": obj
                })
    
    def _handle_mouse_wheel(self, event):
        """
        Handle mouse wheel event.
        
        Args:
            event (pygame.event.Event): Mouse wheel event
        """
        # First try to handle in UI components
        ui_manager = getattr(self.game_engine, "ui_manager", None)
        if ui_manager:
            for component in ui_manager.ui_components.values():
                if hasattr(component, "handle_mouse_wheel") and component.visible:
                    if component.handle_mouse_wheel(event):
                        return
        
        # Then try scene
        scene_manager = getattr(self.game_engine, "scene_manager", None)
        if scene_manager and scene_manager.current_scene:
            if hasattr(scene_manager.current_scene, "handle_mouse_wheel"):
                scene_manager.current_scene.handle_mouse_wheel(event)
    
    def _handle_key_press(self, event):
        """
        Handle keyboard shortcuts.
        
        Args:
            event (pygame.event.Event): Key press event
        """
        # First try to handle in UI components
        ui_manager = getattr(self.game_engine, "ui_manager", None)
        if ui_manager:
            for component in ui_manager.ui_components.values():
                if hasattr(component, "handle_key_press") and component.visible:
                    if component.handle_key_press(event):
                        return
        
        # Check if key matches any keybinding
        for action, bound_key in self.keybindings.items():
            if event.key == bound_key:
                if action.startswith("verb_"):
                    # Set active verb
                    verb = action[5:]  # Remove "verb_" prefix
                    self.game_engine.event_system.emit("verb_selected", {"verb": verb})
                elif action == "inventory":
                    # Toggle inventory
                    self.game_engine.event_system.emit("toggle_inventory", {})
                elif action == "skip_dialog":
                    # Skip dialog text or select option
                    dialog_ui = self.game_engine.ui_manager.ui_components.get("dialog")
                    if dialog_ui and dialog_ui.visible:
                        # Create artificial click event in the center of dialog
                        center_x = dialog_ui.rect.centerx
                        center_y = dialog_ui.rect.centery
                        click_event = pygame.event.Event(
                            pygame.MOUSEBUTTONDOWN,
                            {"pos": (center_x, center_y), "button": 1}
                        )
                        dialog_ui.handle_mouse_click(click_event)
                elif action == "pause":
                    # Pause game
                    self.game_engine.event_system.emit("toggle_pause", {})
                        
        # Then try scene
        scene_manager = getattr(self.game_engine, "scene_manager", None)
        if scene_manager and scene_manager.current_scene:
            if hasattr(scene_manager.current_scene, "handle_key_press"):
                scene_manager.current_scene.handle_key_press(event)
    
    def is_key_pressed(self, key):
        """
        Check if a key is currently pressed.
        
        Args:
            key: pygame key constant or string key name
            
        Returns:
            bool: True if key is pressed, False otherwise
        """
        if isinstance(key, str):
            # Convert string key name to pygame constant
            key_const = getattr(pygame, f"K_{key.upper()}", None)
            if key_const is None:
                return False
            key = key_const
            
        return key in self.keys_pressed
    
    def is_key_just_pressed(self, key):
        """
        Check if a key was just pressed in the current frame.
        
        Args:
            key: pygame key constant or string key name
            
        Returns:
            bool: True if key was just pressed, False otherwise
        """
        if isinstance(key, str):
            # Convert string key name to pygame constant
            key_const = getattr(pygame, f"K_{key.upper()}", None)
            if key_const is None:
                return False
            key = key_const
            
        return key in self.keys_just_pressed
    
    def is_mouse_button_pressed(self, button):
        """
        Check if a mouse button is currently pressed.
        
        Args:
            button (int): Button index (0=left, 1=middle, 2=right)
            
        Returns:
            bool: True if button is pressed, False otherwise
        """
        if 0 <= button < len(self.mouse_buttons):
            return self.mouse_buttons[button]
        return False
    
    def get_action_key(self, action):
        """
        Get the key assigned to an action.
        
        Args:
            action (str): Action name
            
        Returns:
            int or None: Key code or None if action not found
        """
        return self.keybindings.get(action)
    
    def set_action_key(self, action, key):
        """
        Set a key binding for an action.
        
        Args:
            action (str): Action name
            key: pygame key constant
            
        Returns:
            bool: True if binding was set, False otherwise
        """
        if action in self.keybindings:
            self.keybindings[action] = key
            return True
        return False
    
    def save_keybindings(self, filename="keybindings.cfg"):
        """
        Save key bindings to a file.
        
        Args:
            filename (str): Path to configuration file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(filename, 'w') as f:
                for action, key in self.keybindings.items():
                    f.write(f"{action}={key}\n")
            return True
        except Exception as e:
            logger.error(f"Error saving keybindings: {e}")
            return False
    
    def load_keybindings(self, filename="keybindings.cfg"):
        """
        Load key bindings from a file.
        
        Args:
            filename (str): Path to configuration file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    try:
                        action, key = line.split('=')
                        action = action.strip()
                        key = int(key.strip())
                        
                        if action in self.keybindings:
                            self.keybindings[action] = key
                    except ValueError:
                        logger.warning(f"Invalid keybinding line: {line}")
            return True
        except FileNotFoundError:
            logger.info(f"Keybindings file not found: {filename}")
            return False
        except Exception as e:
            logger.error(f"Error loading keybindings: {e}")
            return False