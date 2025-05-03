"""
Scene System for A Sound of Distant Thunder
Handles rendering and input for game locations.
Uses a data-driven approach to reduce complexity and improve maintainability.
"""
import pygame
import logging
import random
from enum import Enum

# Configure logging
logger = logging.getLogger("SceneSystem")

class SceneObjectType(Enum):
    """Enumeration of scene object types for better code clarity"""
    OBJECT = "object"
    NPC = "npc"
    EXIT = "exit"
    AREA = "area"

class SceneObject:
    """Base class for all interactive objects in scenes"""
    def __init__(self, obj_id, name, description, position, image=None, actions=None):
        """
        Initialize a scene object.
        
        Args:
            obj_id (str): Object identifier
            name (str): Display name
            description (str): Object description
            position (tuple): Position (x, y) on screen
            image (pygame.Surface, optional): Object image
            actions (list, optional): List of supported actions
        """
        self.id = obj_id
        self.name = name
        self.description = description
        self.position = position
        self.image = image
        self.actions = actions or []
        self.state = {}
        self.hover = False
        
        # Create rect for hit testing
        if image:
            self.rect = image.get_rect(topleft=position)
        else:
            # Default size if no image provided
            self.rect = pygame.Rect(position[0], position[1], 64, 64)
    
    def contains_point(self, point):
        """
        Check if the object contains the given point.
        
        Args:
            point (tuple): Point coordinates (x, y)
            
        Returns:
            bool: True if point is inside object, False otherwise
        """
        return self.rect.collidepoint(point)
    
    def update(self, dt):
        """
        Update object state.
        
        Args:
            dt (float): Time delta in seconds
        """
        pass
    
    def render(self, surface):
        """
        Render the object to the given surface.
        
        Args:
            surface (pygame.Surface): Surface to render on
        """
        if self.image:
            surface.blit(self.image, self.position)
            
            # Draw highlight when hovered (if debug mode is on)
            if self.hover and hasattr(pygame, 'gfxdraw'):
                pygame.gfxdraw.rectangle(
                    surface, 
                    self.rect,
                    (255, 255, 0, 128)
                )
    
    def can_perform_action(self, action):
        """
        Check if the object can perform the given action.
        
        Args:
            action (str): Action to check
            
        Returns:
            bool: True if action is supported, False otherwise
        """
        return action in self.actions
    
    def get_object_data(self):
        """
        Get object data for event handling.
        
        Returns:
            dict: Object data
        """
        return {
            "type": SceneObjectType.OBJECT.value,
            "id": self.id,
            "name": self.name
        }


class NPCObject(SceneObject):
    """Visual representation of an NPC in the game world"""
    def __init__(self, obj_id, name, description, position, image, model, animation_frames=None):
        """
        Initialize an NPC object.
        
        Args:
            obj_id (str): NPC identifier
            name (str): Display name
            description (str): NPC description
            position (tuple): Position (x, y) on screen
            image (pygame.Surface): NPC image
            model: NPC data model from game state
            animation_frames (dict, optional): Animation frames by state
        """
        super().__init__(obj_id, name, description, position, image, ["look", "talk", "use"])
        
        self.model = model
        self.animation_frames = animation_frames or {}
        
        # Animation state
        self.current_animation = "idle"
        self.frame = 0
        self.animation_timer = 0
        
        # Movement
        self.target_position = None
        self.movement_speed = 100  # Pixels per second
    
    def update(self, dt):
        """
        Update NPC animation and position.
        
        Args:
            dt (float): Time delta in seconds
        """
        # Update animation
        self.animation_timer += dt
        if self.animation_timer >= 0.1:  # 10 FPS animation
            self.animation_timer = 0
            self.frame = (self.frame + 1) % max(1, len(self._get_animation_frames()))
        
        # Move towards target position if set
        if self.target_position:
            dx = self.target_position[0] - self.position[0]
            dy = self.target_position[1] - self.position[1]
            distance = (dx**2 + dy**2)**0.5
            
            if distance < 5:
                # Close enough, snap to target
                self.position = self.target_position
                self.target_position = None
                self.current_animation = "idle"
            else:
                # Move towards target
                move_distance = self.movement_speed * dt
                if distance > 0:
                    self.position = (
                        self.position[0] + dx * move_distance / distance,
                        self.position[1] + dy * move_distance / distance
                    )
                    self.current_animation = "walk"
            
            # Update rect position
            self.rect.topleft = self.position
        
        # Update behavior based on NPC state
        self._update_behavior(dt)
    
    def _update_behavior(self, dt):
        """
        Update based on NPC behavior.
        
        Args:
            dt (float): Time delta in seconds
        """
        # Get behavior from model if available
        behavior = getattr(self.model, "behavior_type", None)
        
        if behavior == "wary":
            # Occasionally look around
            if random.random() < 0.01:
                self.current_animation = "look_around"
        elif behavior == "hostile":
            # Appear nervous
            self.current_animation = "nervous"
        elif behavior == "assimilated":
            # Occasionally show subtle different behavior
            if random.random() < 0.005:
                self.current_animation = "strange"
                # Reset after a moment
                self.animation_timer = 0
        else:
            # Default idle behavior if not moving
            if not self.target_position and self.current_animation != "look_around":
                self.current_animation = "idle"
    
    def render(self, surface):
        """
        Render the NPC to the given surface.
        
        Args:
            surface (pygame.Surface): Surface to render on
        """
        # Get the current animation frame
        frame_image = self._get_current_frame()
        if frame_image:
            surface.blit(frame_image, self.position)
        else:
            # Fallback to static image
            surface.blit(self.image, self.position)
        
        # Show name on hover
        if self.hover:
            font = pygame.font.Font(None, 24)
            name_text = font.render(self.name, True, (255, 255, 255))
            text_pos = (self.position[0], self.position[1] - 20)
            surface.blit(name_text, text_pos)
    
    def _get_animation_frames(self):
        """
        Get frames for the current animation.
        
        Returns:
            list: List of frames or empty list if no animation
        """
        return self.animation_frames.get(self.current_animation, [])
    
    def _get_current_frame(self):
        """
        Get the current animation frame.
        
        Returns:
            pygame.Surface or None: Current animation frame or None if not animated
        """
        frames = self._get_animation_frames()
        if frames and self.frame < len(frames):
            return frames[self.frame]
        return self.image
    
    def set_target_position(self, position):
        """
        Set a target position for the NPC to move to.
        
        Args:
            position (tuple): Target position (x, y)
        """
        self.target_position = position
        self.current_animation = "walk"
    
    def get_object_data(self):
        """
        Get object data for event handling.
        
        Returns:
            dict: Object data
        """
        return {
            "type": SceneObjectType.NPC.value,
            "id": self.id,
            "name": self.name
        }


class ExitArea(SceneObject):
    """Represents an exit to another location"""
    def __init__(self, direction, target_location, rect, name=None):
        """
        Initialize an exit area.
        
        Args:
            direction (str): Exit direction
            target_location (str): Target location ID
            rect (pygame.Rect): Rectangle for the exit area
            name (str, optional): Display name
        """
        description = f"Exit to {target_location}"
        position = (rect.left, rect.top)
        super().__init__(f"exit_{direction}", name or f"Exit ({direction})", description, position)
        
        self.direction = direction
        self.target_location = target_location
        self.rect = rect
    
    def render(self, surface):
        """
        Render the exit area (debug only).
        
        Args:
            surface (pygame.Surface): Surface to render on
        """
        # Exit areas are invisible unless debugging or hovered
        if self.hover or getattr(self, "debug_mode", False):
            pygame.draw.rect(surface, (255, 0, 0, 128), self.rect, 1)
    
    def get_object_data(self):
        """
        Get object data for event handling.
        
        Returns:
            dict: Object data
        """
        return {
            "type": SceneObjectType.EXIT.value,
            "direction": self.direction,
            "target": self.target_location
        }


class InteractiveArea(SceneObject):
    """Represents an area that can be interacted with"""
    def __init__(self, obj_id, name, description, rect, actions=None):
        """
        Initialize an interactive area.
        
        Args:
            obj_id (str): Area identifier
            name (str): Display name
            description (str): Area description
            rect (pygame.Rect): Rectangle defining the area
            actions (list, optional): List of supported actions
        """
        position = (rect.left, rect.top)
        super().__init__(obj_id, name, description, position, actions=actions)
        self.rect = rect
    
    def render(self, surface):
        """
        Render the interactive area (debug only).
        
        Args:
            surface (pygame.Surface): Surface to render on
        """
        # Interactive areas are invisible unless debugging or hovered
        if self.hover or getattr(self, "debug_mode", False):
            pygame.draw.rect(surface, (0, 255, 0, 128), self.rect, 1)
    
    def get_object_data(self):
        """
        Get object data for event handling.
        
        Returns:
            dict: Object data
        """
        return {
            "type": SceneObjectType.AREA.value,
            "id": self.id,
            "name": self.name
        }


class Scene:
    """Base class for game scenes"""
    def __init__(self, game_engine, asset_manager):
        """
        Initialize a scene.
        
        Args:
            game_engine: GameEngine instance
            asset_manager: AssetManager instance
        """
        self.game_engine = game_engine
        self.asset_manager = asset_manager
        self.objects = []
        self.debug_mode = getattr(game_engine, "debug_mode", False)
    
    def update(self, dt):
        """
        Update scene state.
        
        Args:
            dt (float): Time delta in seconds
        """
        # Update all objects
        for obj in self.objects:
            obj.update(dt)
    
    def render(self, surface):
        """
        Render the scene to the given surface.
        
        Args:
            surface (pygame.Surface): Surface to render on
        """
        # Base implementation does nothing
        pass
    
    def handle_mouse_movement(self, event):
        """
        Handle mouse movement events.
        
        Args:
            event (pygame.event.Event): Mouse movement event
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        # Update hover state for all objects
        mouse_pos = event.pos
        for obj in self.objects:
            obj.hover = obj.contains_point(mouse_pos)
        
        return False
    
    def handle_mouse_click(self, event):
        """
        Handle mouse click events.
        
        Args:
            event (pygame.event.Event): Mouse click event
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        # Default implementation does nothing
        return False
    
    def handle_key_press(self, event):
        """
        Handle keyboard events.
        
        Args:
            event (pygame.event.Event): Key press event
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        # Default implementation does nothing
        return False
    
    def get_object_at(self, position):
        """
        Get the object at the given position.
        
        Args:
            position (tuple): Mouse position (x, y)
            
        Returns:
            dict or None: Object data or None if no object at position
        """
        # Check all objects in reverse order (top-to-bottom)
        for obj in reversed(self.objects):
            if obj.contains_point(position):
                return obj.get_object_data()
        
        return None


class LocationScene(Scene):
    """Scene representing a game location"""
    def __init__(self, game_engine, asset_manager, location_id):
        """
        Initialize a location scene.
        
        Args:
            game_engine: GameEngine instance
            asset_manager: AssetManager instance
            location_id (str): Location identifier
        """
        super().__init__(game_engine, asset_manager)
        self.location_id = location_id
        self.background = None
        
        # Set debug mode
        self.debug_mode = getattr(game_engine, "debug_mode", False)
        
        # Load location data
        self._load_location()
        
        logger.info(f"Location scene created: {location_id}")
    
    def _load_location(self):
        """Load location data and assets"""
        location_data = self.game_engine.data_manager.get_data("locations", self.location_id)
        if not location_data:
            logger.error(f"Location data not found: {self.location_id}")
            return
        
        # Load background
        bg_key = f"bg_{self.location_id}"
        self.background = self.asset_manager.get_image(bg_key)
        
        # Load interactive objects
        self._load_objects(location_data)
        
        # Load NPCs
        self._load_npcs(location_data)
        
        # Create exit areas
        self._load_exits(location_data)
        
        # Load interactive areas
        self._load_areas(location_data)
    
    def _load_objects(self, location_data):
        """
        Load interactive objects from location data.
        
        Args:
            location_data (dict): Location data
        """
        for obj_data in location_data.get("objects", []):
            try:
                obj_id = obj_data["id"]
                
                # Get basic object properties
                name = obj_data.get("name", obj_id)
                description = obj_data.get("description", "")
                position = obj_data.get("position", (0, 0))
                
                # Get supported actions
                actions = obj_data.get("actions", [])
                if isinstance(actions, dict):
                    # Convert from dict to list if needed
                    actions = list(actions.keys())
                
                # Load object image
                image = self.asset_manager.get_image(f"obj_{obj_id}")
                
                # Check for custom hotspot
                hotspot_rect = None
                if "hotspot" in obj_data:
                    hotspot_data = obj_data["hotspot"]
                    hotspot_rect = pygame.Rect(
                        hotspot_data.get("x", position[0]),
                        hotspot_data.get("y", position[1]),
                        hotspot_data.get("width", image.get_width()),
                        hotspot_data.get("height", image.get_height())
                    )
                
                # Create scene object
                obj = SceneObject(obj_id, name, description, position, image, actions)
                
                # Apply custom hotspot if defined
                if hotspot_rect:
                    obj.rect = hotspot_rect
                
                # Add object to scene
                self.objects.append(obj)
                logger.debug(f"Loaded object: {obj_id}")
            except KeyError as e:
                logger.error(f"Error loading object, missing key: {e}")
            except Exception as e:
                logger.error(f"Error loading object: {e}")
    
    def _load_npcs(self, location_data):
        """
        Load NPCs from location data.
        
        Args:
            location_data (dict): Location data
        """
        for npc_id in location_data.get("npcs", []):
            try:
                # Get NPC data
                npc_data = self.game_engine.data_manager.get_data("npcs", npc_id)
                if not npc_data:
                    logger.warning(f"NPC data not found: {npc_id}")
                    continue
                
                # Get NPC model from game state
                npc_model = self.game_engine.game_state.get_npc(npc_id)
                if not npc_model:
                    logger.warning(f"NPC model not found in game state: {npc_id}")
                    continue
                
                # Get basic properties
                name = npc_data.get("name", npc_id)
                description = npc_data.get("description", "")
                position = npc_data.get("position", (0, 0))
                
                # Load NPC image
                image = self.asset_manager.get_image(f"npc_{npc_id}")
                
                # Load animation frames if available
                animation_frames = {}
                for anim_type in ["idle", "walk", "look_around", "nervous", "strange"]:
                    anim_key = f"npc_{npc_id}_{anim_type}"
                    if anim_key in self.asset_manager.animations:
                        animation_frames[anim_type] = self.asset_manager.animations[anim_key]
                
                # Create NPC object
                npc = NPCObject(
                    npc_id,
                    name,
                    description,
                    position,
                    image,
                    npc_model,
                    animation_frames
                )
                
                # Add NPC to scene
                self.objects.append(npc)
                logger.debug(f"Loaded NPC: {npc_id}")
            except Exception as e:
                logger.error(f"Error loading NPC {npc_id}: {e}")
    
    def _load_exits(self, location_data):
        """
        Load exit areas from location data.
        
        Args:
            location_data (dict): Location data
        """
        exits = location_data.get("exits", {})
        if not exits:
            return
        
        # Get background dimensions for positioning exits
        if self.background:
            width, height = self.background.get_size()
        else:
            width, height = 800, 600  # Default size
        
        # Create exit areas for all directions
        for direction, target_location in exits.items():
            # Skip if direction or target is not valid
            if not direction or not target_location:
                continue
            
            # Create a rect based on the direction
            rect = self._create_exit_rect(direction, width, height)
            
            # Create exit area
            exit_area = ExitArea(direction, target_location, rect)
            exit_area.debug_mode = self.debug_mode
            
            # Add to scene
            self.objects.append(exit_area)
            logger.debug(f"Created exit to {target_location} ({direction})")
    
    def _create_exit_rect(self, direction, width, height):
        """
        Create a rectangle for an exit area based on direction.
        
        Args:
            direction (str): Exit direction
            width (int): Screen width
            height (int): Screen height
            
        Returns:
            pygame.Rect: Rectangle for the exit area
        """
        # Standard cardinal directions
        if direction == "north":
            return pygame.Rect(0, 0, width, 50)
        elif direction == "south":
            return pygame.Rect(0, height - 50, width, 50)
        elif direction == "east":
            return pygame.Rect(width - 50, 0, 50, height)
        elif direction == "west":
            return pygame.Rect(0, 0, 50, height)
        
        # Named exits
        if ":" in direction:
            parts = direction.split(":")
            if len(parts) >= 5:
                try:
                    # Format: "exit:x:y:width:height"
                    _, x, y, w, h = parts
                    return pygame.Rect(int(x), int(y), int(w), int(h))
                except (ValueError, IndexError):
                    logger.warning(f"Invalid exit format: {direction}")
        
        # Default small exit in the center
        return pygame.Rect(width // 2 - 25, height // 2 - 25, 50, 50)
    
    def _load_areas(self, location_data):
        """
        Load interactive areas from location data.
        
        Args:
            location_data (dict): Location data
        """
        for area_data in location_data.get("areas", []):
            try:
                # Get basic properties
                area_id = area_data["id"]
                name = area_data.get("name", area_id)
                description = area_data.get("description", "")
                
                # Get area rect
                rect_data = area_data.get("rect", {})
                if not rect_data:
                    logger.warning(f"Area {area_id} has no rect defined")
                    continue
                
                rect = pygame.Rect(
                    rect_data.get("x", 0),
                    rect_data.get("y", 0),
                    rect_data.get("width", 100),
                    rect_data.get("height", 100)
                )
                
                # Get supported actions
                actions = area_data.get("actions", [])
                if isinstance(actions, dict):
                    # Convert from dict to list if needed
                    actions = list(actions.keys())
                
                # Create interactive area
                area = InteractiveArea(area_id, name, description, rect, actions)
                area.debug_mode = self.debug_mode
                
                # Add to scene
                self.objects.append(area)
                logger.debug(f"Created interactive area: {area_id}")
            except KeyError as e:
                logger.error(f"Error loading area, missing key: {e}")
            except Exception as e:
                logger.error(f"Error loading area: {e}")
    
    def update(self, dt):
        """
        Update scene state.
        
        Args:
            dt (float): Time delta in seconds
        """
        # Update all objects
        super().update(dt)
    
    def render(self, surface):
        """
        Render the scene to the given surface.
        
        Args:
            surface (pygame.Surface): Surface to render on
        """
        # Render background
        if self.background:
            surface.blit(self.background, (0, 0))
        else:
            # Fallback to black background
            surface.fill((0, 0, 0))
        
        # Sort objects by Y position for proper layering
        sorted_objects = sorted(self.objects, key=lambda obj: obj.position[1])
        
        # Render all objects
        for obj in sorted_objects:
            obj.render(surface)
    
    def handle_mouse_click(self, event):
        """
        Handle mouse click events.
        
        Args:
            event (pygame.event.Event): Mouse click event
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        # Get interaction system
        interaction_system = getattr(self.game_engine, "interaction_system", None)
        if not interaction_system:
            logger.error("No interaction system available")
            return False
        
        # Find object at click position
        obj_data = self.get_object_at(event.pos)
        if not obj_data:
            # Click on empty area - could handle "go" verb here
            return False
        
        # Handle different object types
        obj_type = obj_data.get("type")
        
        if obj_type == SceneObjectType.OBJECT.value:
            # Interact with object
            obj_id = obj_data.get("id")
            verb = getattr(interaction_system, "selected_verb", "look")
            
            interaction_system.interact_with_object(obj_id, verb)
            return True
            
        elif obj_type == SceneObjectType.NPC.value:
            # Interact with NPC
            npc_id = obj_data.get("id")
            verb = getattr(interaction_system, "selected_verb", "talk")
            
            interaction_system.interact_with_npc(npc_id, verb)
            return True
            
        elif obj_type == SceneObjectType.EXIT.value:
            # Navigate to target location
            target = obj_data.get("target")
            if target:
                # Get navigation system
                navigation_system = getattr(self.game_engine, "navigation_system", None)
                if navigation_system:
                    navigation_system.navigate_to_location(target)
                    return True
            
        elif obj_type == SceneObjectType.AREA.value:
            # Interact with area as if it's an object
            area_id = obj_data.get("id")
            verb = getattr(interaction_system, "selected_verb", "look")
            
            interaction_system.interact_with_object(area_id, verb)
            return True
        
        return False
    
    def get_object_at(self, position):
        """
        Get the object at the given position.
        
        Args:
            position (tuple): Mouse position (x, y)
            
        Returns:
            dict or None: Object data or None if no object at position
        """
        # Check all objects in reverse order (top-to-bottom)
        for obj in reversed(self.objects):
            if obj.contains_point(position):
                return obj.get_object_data()
        
        return None


class SceneManager:
    """Manages game scenes and transitions"""
    def __init__(self, game_engine, asset_manager):
        """
        Initialize the scene manager.
        
        Args:
            game_engine: GameEngine instance
            asset_manager: AssetManager instance
        """
        self.game_engine = game_engine
        self.asset_manager = asset_manager
        self.current_scene = None
        
        # Transition state
        self.transition_active = False
        self.transition_progress = 0
        self.transition_target = None
        self.transition_type = None
        
        # Fade surface for transitions
        self.fade_surface = None
        
        # Register event listeners
        self.game_engine.event_system.subscribe("location_changed", self._on_location_changed)
        
        logger.info("Scene Manager initialized")
    
    def _on_location_changed(self, data):
        """
        Handle location changed event.
        
        Args:
            data (dict): Event data with new location
        """
        new_location = data.get("new_location")
        if not new_location:
            return
            
        # Check if we should use a transition
        if "transition" in data:
            # Start transition
            self.start_transition(new_location, data.get("transition", "fade"))
        else:
            # Immediate change
            self._change_scene(new_location)
    
    def start_transition(self, target_location, transition_type="fade"):
        """
        Start a scene transition.
        
        Args:
            target_location (str): Target location ID
            transition_type (str): Type of transition effect
        """
        # Only start if not already transitioning
        if self.transition_active:
            return
        
        self.transition_active = True
        self.transition_progress = 0
        self.transition_target = target_location
        self.transition_type = transition_type
        
        # Initialize fade surface if needed
        if not self.fade_surface and self.game_engine.ui_manager:
            screen_size = self.game_engine.ui_manager.screen.get_size()
            self.fade_surface = pygame.Surface(screen_size, pygame.SRCALPHA)
        
        logger.info(f"Started transition to {target_location} ({transition_type})")
    
    def _change_scene(self, location_id):
        """
        Change to a new scene.
        
        Args:
            location_id (str): New location ID
        """
        # Create new scene
        self.current_scene = LocationScene(
            self.game_engine,
            self.asset_manager,
            location_id
        )
        
        logger.info(f"Changed scene to {location_id}")
    
    def update(self, dt):
        """
        Update scene state.
        
        Args:
            dt (float): Time delta in seconds
        """
        if self.transition_active:
            # Update transition
            self.transition_progress += dt * 2  # Transition speed
            
            if self.transition_progress >= 1:
                # Transition complete
                self.transition_active = False
                self._change_scene(self.transition_target)
                self.transition_target = None
        elif self.current_scene:
            # Update current scene
            self.current_scene.update(dt)
    
    def render(self, surface):
        """
        Render the current scene.
        
        Args:
            surface (pygame.Surface): Surface to render on
        """
        if not self.current_scene:
            # No scene to render
            surface.fill((0, 0, 0))
            return
        
        # Render current scene
        self.current_scene.render(surface)
        
        # Render transition effect if active
        if self.transition_active:
            self._render_transition(surface)
    
    def _render_transition(self, surface):
        """
        Render the current transition effect.
        
        Args:
            surface (pygame.Surface): Surface to render on
        """
        if not self.fade_surface:
            # Initialize fade surface if needed
            self.fade_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        
        # Different transition types
        if self.transition_type == "fade":
            # Simple fade to black
            alpha = int(self.transition_progress * 255)
            self.fade_surface.fill((0, 0, 0, alpha))
            surface.blit(self.fade_surface, (0, 0))
            
        elif self.transition_type == "slide_left":
            # Slide out to the left
            width = surface.get_width()
            offset = int(self.transition_progress * width)
            surface.scroll(dx=-offset)
            pygame.draw.rect(
                surface,
                (0, 0, 0),
                (width - offset, 0, offset, surface.get_height())
            )
            
        elif self.transition_type == "slide_right":
            # Slide out to the right
            width = surface.get_width()
            offset = int(self.transition_progress * width)
            surface.scroll(dx=offset)
            pygame.draw.rect(
                surface,
                (0, 0, 0),
                (0, 0, offset, surface.get_height())
            )
            
        elif self.transition_type == "dissolve":
            # Random pixel dissolve
            if self.transition_progress < 0.5:
                # First half: dissolve to black
                progress = self.transition_progress * 2
                self.fade_surface.fill((0, 0, 0, int(progress * 255)))
                
                # Add noise to fade
                for _ in range(int(progress * 1000)):
                    x = random.randint(0, surface.get_width() - 1)
                    y = random.randint(0, surface.get_height() - 1)
                    
                    # Draw random pixels with varying alpha
                    alpha = random.randint(100, 255)
                    pygame.draw.rect(
                        self.fade_surface,
                        (0, 0, 0, alpha),
                        (x, y, 2, 2)
                    )
                    
                surface.blit(self.fade_surface, (0, 0))
        else:
            # Fallback to simple fade
            alpha = int(self.transition_progress * 255)
            self.fade_surface.fill((0, 0, 0, alpha))
            surface.blit(self.fade_surface, (0, 0))
    
    def handle_mouse_click(self, event):
        """
        Handle mouse click events.
        
        Args:
            event (pygame.event.Event): Mouse click event
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        if self.transition_active:
            return False  # Ignore clicks during transitions
            
        if self.current_scene:
            return self.current_scene.handle_mouse_click(event)
        
        return False
    
    def handle_mouse_movement(self, event):
        """
        Handle mouse movement events.
        
        Args:
            event (pygame.event.Event): Mouse movement event
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        if self.transition_active:
            return False  # Ignore movement during transitions
            
        if self.current_scene:
            return self.current_scene.handle_mouse_movement(event)
        
        return False
    
    def handle_key_press(self, event):
        """
        Handle keyboard events.
        
        Args:
            event (pygame.event.Event): Key press event
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        if self.transition_active:
            # Skip transition when pressing a key
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.transition_progress = 1.0
                return True
            return False
            
        if self.current_scene:
            return self.current_scene.handle_key_press(event)
        
        return False
    
    def get_object_at(self, position):
        """
        Get the object at the given position.
        
        Args:
            position (tuple): Mouse position (x, y)
            
        Returns:
            dict or None: Object data or None if no object at position
        """
        if self.transition_active or not self.current_scene:
            return None
            
        return self.current_scene.get_object_at(position)