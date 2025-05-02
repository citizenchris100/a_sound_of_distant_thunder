"""
Scene System for A Sound of Distant Thunder
Handles rendering and input for game locations.
"""
import pygame
import logging
import random

# Configure logging
logger = logging.getLogger("SceneSystem")

class GameObject:
    """Represents an interactive object in the game world"""
    def __init__(self, obj_id, name, description, image, position, actions=None, hotspot=None):
        """
        Initialize a game object.
        
        Args:
            obj_id (str): Object identifier
            name (str): Display name
            description (str): Object description
            image (pygame.Surface): Object image
            position (tuple): Position (x, y) on screen
            actions (list, optional): List of supported actions
            hotspot (pygame.Rect, optional): Custom clickable area
        """
        self.id = obj_id
        self.name = name
        self.description = description
        self.image = image
        self.position = position
        self.actions = actions or []
        self.state = {}
        
        # Create rect for hit testing
        if hotspot:
            self.rect = hotspot
        else:
            self.rect = self.image.get_rect(topleft=position)
    
    def contains_point(self, point):
        """
        Check if the object contains the given point.
        
        Args:
            point (tuple): Point coordinates (x, y)
            
        Returns:
            bool: True if point is inside object, False otherwise
        """
        return self.rect.collidepoint(point)
    
    def render(self, surface):
        """
        Render the object to the given surface.
        
        Args:
            surface (pygame.Surface): Surface to render on
        """
        surface.blit(self.image, self.position)
    
    def can_perform_action(self, action):
        """
        Check if the object can perform the given action.
        
        Args:
            action (str): Action to check
            
        Returns:
            bool: True if action is supported, False otherwise
        """
        return action in self.actions
    
    def update(self, dt):
        """
        Update object state.
        
        Args:
            dt (float): Time delta in seconds
        """
        # Default implementation does nothing
        pass


class NPCView:
    """Visual representation of an NPC in the game world"""
    def __init__(self, npc_id, name, image, position, model, animation_frames=None):
        """
        Initialize an NPC view.
        
        Args:
            npc_id (str): NPC identifier
            name (str): Display name
            image (pygame.Surface): NPC image
            position (tuple): Position (x, y) on screen
            model (object): NPC data model from game state
            animation_frames (dict, optional): Animation frames by state
        """
        self.id = npc_id
        self.name = name
        self.image = image
        self.position = position
        self.model = model
        self.animation_frames = animation_frames or {}
        
        # Create rect for hit testing
        self.rect = self.image.get_rect(topleft=position)
        
        # Animation state
        self.current_animation = "idle"
        self.frame = 0
        self.animation_timer = 0
        self.hover = False
        
        # Movement
        self.target_position = None
        self.movement_speed = 100  # Pixels per second
    
    def contains_point(self, point):
        """
        Check if the NPC contains the given point.
        
        Args:
            point (tuple): Point coordinates (x, y)
            
        Returns:
            bool: True if point is inside NPC, False otherwise
        """
        return self.rect.collidepoint(point)
    
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
        
        # Show name on hover if debug mode is enabled
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
        self.objects = {}
        self.npcs = {}
    
    def update(self, dt):
        """
        Update scene state.
        
        Args:
            dt (float): Time delta in seconds
        """
        # Update objects
        for obj in self.objects.values():
            obj.update(dt)
        
        # Update NPCs
        for npc in self.npcs.values():
            npc.update(dt)
    
    def render(self, surface):
        """
        Render the scene to the given surface.
        
        Args:
            surface (pygame.Surface): Surface to render on
        """
        # Default implementation does nothing
        pass
    
    def handle_mouse_click(self, event):
        """
        Handle mouse click events.
        
        Args:
            event (pygame.event.Event): Mouse click event
        """
        # Default implementation does nothing
        pass
    
    def handle_key_press(self, event):
        """
        Handle keyboard events.
        
        Args:
            event (pygame.event.Event): Key press event
        """
        # Default implementation does nothing
        pass
    
    def get_object_at(self, position):
        """
        Get the object at the given position.
        
        Args:
            position (tuple): Mouse position (x, y)
            
        Returns:
            dict or None: Object data or None if no object at position
        """
        # Default implementation returns None
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
        self.exit_areas = {}
        
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
        
        # Create interactive objects
        for obj_data in location_data.get("objects", []):
            obj_id = obj_data["id"]
            
            # Create game object
            position = obj_data.get("position", (0, 0))
            image = self.asset_manager.get_image(f"obj_{obj_id}")
            
            # Check for custom hotspot
            hotspot = None
            if "hotspot" in obj_data:
                hotspot_data = obj_data["hotspot"]
                hotspot = pygame.Rect(
                    hotspot_data.get("x", position[0]),
                    hotspot_data.get("y", position[1]),
                    hotspot_data.get("width", image.get_width()),
                    hotspot_data.get("height", image.get_height())
                )
            
            # Create game object
            game_object = GameObject(
                obj_id,
                obj_data["name"],
                obj_data["description"],
                image,
                position,
                obj_data.get("actions", []),
                hotspot
            )
            
            self.objects[obj_id] = game_object
        
        # Create NPCs
        for npc_id in location_data.get("npcs", []):
            npc_data = self.game_engine.data_manager.get_data("npcs", npc_id)
            if npc_data:
                # Get NPC from game state
                npc_model = self.game_engine.game_state.get_npc(npc_id)
                
                # Create NPC view
                position = npc_data.get("position", (0, 0))
                image = self.asset_manager.get_image(f"npc_{npc_id}")
                
                # Load animation frames if available
                animation_frames = {}
                for anim_type in ["idle", "walk", "look_around", "nervous", "strange"]:
                    anim_key = f"npc_{npc_id}_{anim_type}"
                    if anim_key in self.asset_manager.animations:
                        animation_frames[anim_type] = self.asset_manager.animations[anim_key]
                
                # Create NPC view
                npc_view = NPCView(
                    npc_id,
                    npc_data["name"],
                    image,
                    position,
                    npc_model,
                    animation_frames
                )
                
                self.npcs[npc_id] = npc_view
        
        # Create exit areas
        exits = location_data.get("exits", {})
        for direction, target_location in exits.items():
            # Create a clickable exit area
            # Position depends on the direction
            rect = self._create_exit_rect(direction)
            self.exit_areas[direction] = {
                "target": target_location,
                "rect": rect
            }
    
    def _create_exit_rect(self, direction):
        """
        Create a rectangle for an exit area based on direction.
        
        Args:
            direction (str): Exit direction
            
        Returns:
            pygame.Rect: Rectangle for the exit area
        """
        # Screen dimensions
        width, height = self.background.get_size()
        
        # Create exit area based on direction
        if direction == "north":
            return pygame.Rect(0, 0, width, 50)
        elif direction == "south":
            return pygame.Rect(0, height - 50, width, 50)
        elif direction == "east":
            return pygame.Rect(width - 50, 0, 50, height)
        elif direction == "west":
            return pygame.Rect(0, 0, 50, height)
        else:
            # For named exits, create a custom area
            # This would be defined in the location data
            # For now, just return a default rect
            return pygame.Rect(0, 0, 50, 50)
    
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
        
        # Render objects
        for game_object in self.objects.values():
            game_object.render(surface)
        
        # Render NPCs
        for npc in self.npcs.values():
            npc.render(surface)
        
        # Debug: render exit areas
        if getattr(self.game_engine, "debug_mode", False):
            for exit_data in self.exit_areas.values():
                pygame.draw.rect(surface, (255, 0, 0, 128), exit_data["rect"], 1)
    
    def handle_mouse_click(self, event):
        """
        Handle mouse click events.
        
        Args:
            event (pygame.event.Event): Mouse click event
        """
        # Get interaction system
        interaction_system = getattr(self.game_engine, "interaction_system", None)
        if not interaction_system:
            logger.error("No interaction system available")
            return
        
        # Check if click is on an object
        for obj in self.objects.values():
            if obj.contains_point(event.pos):
                # Get selected verb
                selected_verb = getattr(interaction_system, "selected_verb", "look")
                
                # Perform action
                interaction_system.interact_with_object(obj.id, selected_verb)
                return
        
        # Check if click is on an NPC
        for npc in self.npcs.values():
            if npc.contains_point(event.pos):
                # Get selected verb
                selected_verb = getattr(interaction_system, "selected_verb", "talk")
                
                # Perform action
                interaction_system.interact_with_npc(npc.id, selected_verb)
                return
        
        # Check if click is on an exit area
        for direction, exit_data in self.exit_areas.items():
            if exit_data["rect"].collidepoint(event.pos):
                # Navigate to the target location
                navigation_system = getattr(self.game_engine, "navigation_system", None)
                if navigation_system:
                    navigation_system.navigate_to_location(exit_data["target"])
                return
        
        # Click on empty area - walk there if "go" verb is selected
        selected_verb = getattr(interaction_system, "selected_verb", None)
        if selected_verb == "go":
            # Move player character (if implemented)
            pass
    
    def get_object_at(self, position):
        """
        Get the object at the given position.
        
        Args:
            position (tuple): Mouse position (x, y)
            
        Returns:
            dict or None: Object data or None if no object at position
        """
        # Check objects
        for obj in self.objects.values():
            if obj.contains_point(position):
                return {"type": "object", "id": obj.id, "name": obj.name}
        
        # Check NPCs
        for npc in self.npcs.values():
            if npc.contains_point(position):
                return {"type": "npc", "id": npc.id, "name": npc.name}
        
        # Check exit areas
        for direction, exit_data in self.exit_areas.items():
            if exit_data["rect"].collidepoint(position):
                return {"type": "exit", "direction": direction, "target": exit_data["target"]}
        
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
        self.transition_active = False
        self.transition_progress = 0
        self.transition_target = None
        
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
        if new_location:
            # Check if we should use a transition
            if "transition" in data:
                # Start transition
                self.transition_active = True
                self.transition_progress = 0
                self.transition_target = new_location
            else:
                # Immediate change
                self._change_scene(new_location)
    
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
        elif self.current_scene:
            # Update current scene
            self.current_scene.update(dt)
    
    def render(self, surface):
        """
        Render the current scene.
        
        Args:
            surface (pygame.Surface): Surface to render on
        """
        if self.transition_active:
            # Render transition effect
            if self.current_scene:
                # Fade out current scene
                self.current_scene.render(surface)
                
                # Apply fade effect
                fade = pygame.Surface(surface.get_size())
                fade.fill((0, 0, 0))
                fade.set_alpha(int(self.transition_progress * 255))
                surface.blit(fade, (0, 0))
        elif self.current_scene:
            # Render current scene
            self.current_scene.render(surface)
    
    def handle_mouse_click(self, event):
        """
        Handle mouse click events.
        
        Args:
            event (pygame.event.Event): Mouse click event
        """
        if not self.transition_active and self.current_scene:
            self.current_scene.handle_mouse_click(event)
    
    def handle_key_press(self, event):
        """
        Handle keyboard events.
        
        Args:
            event (pygame.event.Event): Key press event
        """
        if not self.transition_active and self.current_scene:
            self.current_scene.handle_key_press(event)
    
    def get_object_at(self, position):
        """
        Get the object at the given position.
        
        Args:
            position (tuple): Mouse position (x, y)
            
        Returns:
            dict or None: Object data or None if no object at position
        """
        if not self.transition_active and self.current_scene:
            return self.current_scene.get_object_at(position)
        return None