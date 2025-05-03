"""
Input Management System for A Sound of Distant Thunder
Provides advanced input handling with support for both mouse and keyboard interactions.
"""
import pygame
import logging
import json
import os

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
        self.mouse_buttons_prev = [False, False, False]  # Previous state
        self.mouse_wheel_delta = 0
        self.mouse_hover_object = None
        self.last_click_time = 0
        self.double_click_threshold = 0.3  # seconds
        
        # Keyboard state
        self.keys_pressed = set()
        self.keys_just_pressed = set()
        self.keys_just_released = set()
        self.text_input_active = False
        self.text_input_buffer = ""
        
        # Input focus
        self.focused_component = None
        self.hover_component = None
        self.modal_component = None
        
        # Default keybindings (configurable)
        self.keybindings = {
            # Game Actions
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
            
            # UI Navigation
            "ui_up": pygame.K_UP,
            "ui_down": pygame.K_DOWN,
            "ui_left": pygame.K_LEFT,
            "ui_right": pygame.K_RIGHT,
            "ui_select": pygame.K_RETURN,
            "ui_cancel": pygame.K_ESCAPE,
            "ui_tab": pygame.K_TAB,
            
            # Debug
            "toggle_debug": pygame.K_F12,
        }
        
        # Reverse lookup for key names
        self.key_names = {v: k for k, v in self.keybindings.items()}
        
        # Cursor images
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
        
        # Tooltip state
        self.tooltip_timer = 0
        self.tooltip_threshold = 0.8  # seconds hover before showing tooltip
        self.tooltip_object = None
        
        # Load user keybindings if available
        self._load_keybindings()
        
        logger.info("Input Manager initialized")
    
    def update(self):
        """Update input state for the current frame"""
        # Store previous mouse buttons state
        self.mouse_buttons_prev = self.mouse_buttons.copy()
        
        # Update mouse position
        self.mouse_position = pygame.mouse.get_pos()
        
        # Update mouse buttons
        self.mouse_buttons = list(pygame.mouse.get_pressed(3))
        
        # Reset wheel delta and just pressed/released keys
        self.mouse_wheel_delta = 0
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        
        # Process events
        for event in pygame.event.get():
            self._process_event(event)
            
        # Update tooltip timer
        current_time = pygame.time.get_ticks() / 1000.0
        
        if self.hover_component != self.tooltip_object:
            # Hover object changed, reset timer
            self.tooltip_timer = current_time
            self.tooltip_object = self.hover_component
        elif current_time - self.tooltip_timer > self.tooltip_threshold:
            # Threshold exceeded, should show tooltip
            self._trigger_tooltip(self.tooltip_object)
    
    def _process_event(self, event):
        """
        Process a single pygame event.
        
        Args:
            event (pygame.event.Event): Event to process
        """
        if event.type == pygame.QUIT:
            self.game_engine.handle_event("game_exit")
        
        elif event.type == pygame.KEYDOWN:
            self.keys_pressed.add(event.key)
            self.keys_just_pressed.add(event.key)
            
            # Handle text input if active
            if self.text_input_active:
                if event.key == pygame.K_BACKSPACE:
                    self.text_input_buffer = self.text_input_buffer[:-1]
                elif event.key == pygame.K_RETURN:
                    self._trigger_text_input_complete()
                elif event.unicode and ord(event.unicode) >= 32:
                    self.text_input_buffer += event.unicode
            
            # Check if this key matches any keybinding
            if event.key in self.key_names:
                action = self.key_names[event.key]
                self._trigger_action(action)
            
            # Send event to focused component
            if self.focused_component:
                self._dispatch_to_component(self.focused_component, "handle_key_press", event)
            
            # If no component handled, send to game engine
            elif hasattr(self.game_engine, "handle_key_press"):
                self.game_engine.handle_key_press(event)
        
        elif event.type == pygame.KEYUP:
            if event.key in self.keys_pressed:
                self.keys_pressed.remove(event.key)
            self.keys_just_released.add(event.key)
            
            # Send event to focused component
            if self.focused_component:
                self._dispatch_to_component(self.focused_component, "handle_key_release", event)
        
        elif event.type == pygame.MOUSEMOTION:
            # Handle mouse movement
            prev_hover = self.hover_component
            self.hover_component = self._find_component_at_position(event.pos)
            
            # Send mouse exit/enter events if hover changed
            if prev_hover != self.hover_component:
                if prev_hover:
                    self._dispatch_to_component(prev_hover, "handle_mouse_exit", event)
                if self.hover_component:
                    self._dispatch_to_component(self.hover_component, "handle_mouse_enter", event)
            
            # Send movement event to hover component
            if self.hover_component:
                self._dispatch_to_component(self.hover_component, "handle_mouse_movement", event)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Handle mouse press
            if event.button <= 3:  # Main buttons (left, middle, right)
                # Check for double click
                current_time = pygame.time.get_ticks() / 1000.0
                is_double_click = (current_time - self.last_click_time < self.double_click_threshold)
                self.last_click_time = current_time
                
                # Find component under click and focus it
                clicked_component = self._find_component_at_position(event.pos)
                
                # Update focus if clicking on a focusable component
                if clicked_component:
                    if hasattr(clicked_component, "focusable") and clicked_component.focusable:
                        self._set_focus(clicked_component)
                else:
                    # Clicked on nothing, clear focus
                    self._set_focus(None)
                
                # Dispatch event
                if is_double_click:
                    self._dispatch_mouse_event("handle_double_click", event)
                else:
                    self._dispatch_mouse_event("handle_mouse_click", event)
            
            elif event.button == 4:  # Mouse wheel up
                self.mouse_wheel_delta = 1
                self._dispatch_mouse_event("handle_mouse_wheel", event)
            
            elif event.button == 5:  # Mouse wheel down
                self.mouse_wheel_delta = -1
                self._dispatch_mouse_event("handle_mouse_wheel", event)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            # Handle mouse release
            if event.button <= 3:  # Main buttons
                self._dispatch_mouse_event("handle_mouse_release", event)
    
    def _dispatch_mouse_event(self, handler_name, event):
        """
        Dispatch a mouse event to appropriate components.
        
        Args:
            handler_name (str): Name of handler method to call
            event (pygame.event.Event): Event to dispatch
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        # Modal component gets priority
        if self.modal_component:
            if self._dispatch_to_component(self.modal_component, handler_name, event):
                return True
        
        # Then check component under mouse
        component = self._find_component_at_position(event.pos)
        if component:
            if self._dispatch_to_component(component, handler_name, event):
                return True
        
        # If no component handled it, try the game engine
        engine_handler = getattr(self.game_engine, handler_name, None)
        if engine_handler and callable(engine_handler):
            return engine_handler(event)
        
        return False
    
    def _dispatch_to_component(self, component, handler_name, event):
        """
        Dispatch an event to a specific component.
        
        Args:
            component: UI component to receive the event
            handler_name (str): Name of handler method to call
            event (pygame.event.Event): Event to dispatch
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        handler = getattr(component, handler_name, None)
        if handler and callable(handler):
            try:
                return handler(event)
            except Exception as e:
                logger.error(f"Error in component event handler: {e}")
        return False
    
    def _find_component_at_position(self, position):
        """
        Find the topmost UI component at the given position.
        
        Args:
            position (tuple): Mouse position (x, y)
            
        Returns:
            Component or None: UI component at position, or None if none found
        """
        # Check modal component first
        if self.modal_component and hasattr(self.modal_component, "rect"):
            if self.modal_component.rect.collidepoint(position):
                return self.modal_component
        
        # Then check UI components from top to bottom
        ui_manager = getattr(self.game_engine, "ui_manager", None)
        if ui_manager and hasattr(ui_manager, "ui_components"):
            # Reverse order to check top components first
            for name in reversed(list(ui_manager.ui_components.keys())):
                component = ui_manager.ui_components[name]
                if (getattr(component, "visible", False) and 
                    hasattr(component, "rect") and 
                    component.rect.collidepoint(position)):
                    return component
        
        # Then check scene objects
        scene_manager = getattr(self.game_engine, "scene_manager", None)
        if scene_manager and scene_manager.current_scene:
            obj = scene_manager.current_scene.get_object_at(position)
            if obj:
                # Return scene as component
                return scene_manager.current_scene
        
        return None
    
    def _set_focus(self, component):
        """
        Set input focus to the given component.
        
        Args:
            component: UI component to focus, or None to clear focus
        """
        if component == self.focused_component:
            return
            
        old_focus = self.focused_component
        self.focused_component = component
        
        # Notify components about focus change
        if old_focus and hasattr(old_focus, "handle_focus_lost"):
            old_focus.handle_focus_lost()
            
        if component and hasattr(component, "handle_focus_gained"):
            component.handle_focus_gained()
    
    def _set_modal(self, component):
        """
        Set a component as modal, receiving all input events first.
        
        Args:
            component: UI component to make modal, or None to clear
        """
        self.modal_component = component
    
    def _trigger_action(self, action):
        """
        Trigger a keybinding action.
        
        Args:
            action (str): Action name from keybindings
        """
        # Handle verb selection
        if action.startswith("verb_"):
            verb = action[5:]  # Remove "verb_" prefix
            self.game_engine.event_system.emit("verb_selected", {"verb": verb})
        
        # Handle UI actions
        elif action == "inventory":
            self.game_engine.event_system.emit("toggle_inventory", {})
        elif action == "map":
            self.game_engine.event_system.emit("toggle_map", {})
        elif action == "character":
            self.game_engine.event_system.emit("toggle_character", {})
        elif action == "journal":
            self.game_engine.event_system.emit("toggle_journal", {})
        elif action == "pause":
            self.game_engine.event_system.emit("toggle_pause", {})
        elif action == "skip_dialog":
            self.game_engine.event_system.emit("skip_dialog", {})
        elif action == "toggle_debug":
            self.game_engine.handle_event("toggle_debug")
    
    def _trigger_tooltip(self, component):
        """
        Trigger tooltip display for the given component.
        
        Args:
            component: UI component to show tooltip for
        """
        if component and hasattr(component, "handle_tooltip"):
            component.handle_tooltip()
    
    def _trigger_text_input_complete(self):
        """Trigger text input completion event"""
        if self.text_input_active:
            self.game_engine.event_system.emit("text_input_complete", {
                "text": self.text_input_buffer
            })
            self.text_input_active = False
            self.text_input_buffer = ""
    
    def start_text_input(self, initial_text=""):
        """
        Start text input mode.
        
        Args:
            initial_text (str): Initial text to put in buffer
        """
        self.text_input_active = True
        self.text_input_buffer = initial_text
    
    def stop_text_input(self):
        """Stop text input mode without completing"""
        self.text_input_active = False
        self.text_input_buffer = ""
    
    def set_cursor(self, cursor_name):
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
    
    def is_key_just_released(self, key):
        """
        Check if a key was just released in the current frame.
        
        Args:
            key: pygame key constant or string key name
            
        Returns:
            bool: True if key was just released, False otherwise
        """
        if isinstance(key, str):
            # Convert string key name to pygame constant
            key_const = getattr(pygame, f"K_{key.upper()}", None)
            if key_const is None:
                return False
            key = key_const
            
        return key in self.keys_just_released
    
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
    
    def is_mouse_button_just_pressed(self, button):
        """
        Check if a mouse button was just pressed in the current frame.
        
        Args:
            button (int): Button index (0=left, 1=middle, 2=right)
            
        Returns:
            bool: True if button was just pressed, False otherwise
        """
        if 0 <= button < len(self.mouse_buttons):
            return self.mouse_buttons[button] and not self.mouse_buttons_prev[button]
        return False
    
    def is_mouse_button_just_released(self, button):
        """
        Check if a mouse button was just released in the current frame.
        
        Args:
            button (int): Button index (0=left, 1=middle, 2=right)
            
        Returns:
            bool: True if button was just released, False otherwise
        """
        if 0 <= button < len(self.mouse_buttons):
            return not self.mouse_buttons[button] and self.mouse_buttons_prev[button]
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
            
            # Update reverse lookup
            self.key_names = {v: k for k, v in self.keybindings.items()}
            
            return True
        return False
    
    def get_key_name(self, key):
        """
        Get the display name for a key.
        
        Args:
            key: pygame key constant
            
        Returns:
            str: Human-readable key name
        """
        key_name = pygame.key.name(key)
        
        # Clean up key names
        key_name = key_name.upper()
        if key_name.startswith('[') and key_name.endswith(']'):
            key_name = key_name[1:-1]
            
        return key_name
    
    def get_action_key_name(self, action):
        """
        Get the display name for an action's key.
        
        Args:
            action (str): Action name
            
        Returns:
            str: Human-readable key name or empty string if not found
        """
        key = self.get_action_key(action)
        if key is None:
            return ""
        return self.get_key_name(key)
    
    def _load_keybindings(self, filename="keybindings.cfg"):
        """
        Load key bindings from a file.
        
        Args:
            filename (str): Path to configuration file
        """
        try:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    data = json.load(f)
                    
                # Update keybindings with loaded values
                for action, key in data.items():
                    if action in self.keybindings:
                        self.keybindings[action] = key
                
                # Update reverse lookup
                self.key_names = {v: k for k, v in self.keybindings.items()}
                
                logger.info(f"Loaded keybindings from {filename}")
        except Exception as e:
            logger.error(f"Error loading keybindings: {e}")
    
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
                json.dump(self.keybindings, f, indent=2)
            logger.info(f"Saved keybindings to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving keybindings: {e}")
            return False