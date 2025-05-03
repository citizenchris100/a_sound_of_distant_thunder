"""
Core UI Framework for A Sound of Distant Thunder
Provides the main UI infrastructure for the SCUMM-like point-and-click adventure game.
"""
import pygame
import logging
import os
import random

# Configure logging
logger = logging.getLogger("UIFramework")

class UIManager:
    """
    Main UI manager class that handles rendering, input, and UI components.
    """
    def __init__(self, game_engine, screen_width=800, screen_height=600):
        """
        Initialize the UI manager.
        
        Args:
            game_engine: GameEngine instance
            screen_width (int): Width of the game window
            screen_height (int): Height of the game window
        """
        self.game_engine = game_engine
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("A Sound of Distant Thunder")
        
        # UI state
        self.active_scene = None
        self.ui_components = {}
        self.mouse_position = (0, 0)
        self.hover_object = None
        self.is_dialog_active = False
        
        # Theme system - will be set by Phase2Integration
        self.theme = None
        
        # Asset management
        self.asset_manager = AssetManager("./assets/")
        
        # Create clock for tracking frame rate
        self.clock = pygame.time.Clock()
        self.target_fps = 60
        
        # Register event listeners
        self.game_engine.event_system.subscribe("location_changed", self._on_location_changed)
        self.game_engine.event_system.subscribe("dialog_started", self._on_dialog_started)
        self.game_engine.event_system.subscribe("dialog_ended", self._on_dialog_ended)
        
        logger.info("UI Manager initialized")
    
    def initialize(self):
        """Initialize the UI system"""
        # Load common assets
        self.asset_manager.load_common_assets()
        
        # Create UI components
        self._create_ui_components()
        
        # Set initial scene based on game state
        self._update_scene()
        
        logger.info("UI initialized")
    
    def _create_ui_components(self):
        """Create all UI components"""
        # Create inventory UI at the bottom of the screen
        self.ui_components["inventory"] = InventoryUI(
            self.game_engine,
            self.asset_manager,
            pygame.Rect(10, self.screen_height - 100, self.screen_width - 20, 90)
        )
        
        # Create dialog UI in the middle-bottom of the screen
        self.ui_components["dialog"] = DialogUI(
            self.game_engine,
            self.asset_manager,
            pygame.Rect(50, 400, self.screen_width - 100, 180)
        )
        self.ui_components["dialog"].visible = False
        
        # Create verb bar above the inventory
        self.ui_components["verb_bar"] = VerbBarUI(
            self.game_engine,
            self.asset_manager,
            pygame.Rect(10, self.screen_height - 150, self.screen_width - 20, 40)
        )
        
        # Create status bar at the top
        self.ui_components["status_bar"] = StatusBarUI(
            self.game_engine,
            self.asset_manager,
            pygame.Rect(10, 10, self.screen_width - 20, 30)
        )
        
        logger.debug("UI components created")
    
    def _update_scene(self):
        """Update the current scene based on game state"""
        location_id = self.game_engine.game_state.current_location
        if location_id and location_id != getattr(self.active_scene, "location_id", None):
            # Load assets for the new location
            self.asset_manager.load_location_assets(location_id)
            
            # Create new scene
            self.active_scene = LocationScene(
                self.game_engine,
                self.asset_manager,
                location_id
            )
            
            logger.info(f"Scene updated: {location_id}")
    
    def run(self):
        """Run the main game loop"""
        running = True
        
        while running:
            # Check for input manager
            input_manager = None
            phase2 = getattr(self.game_engine, "phase2_integration", None)
            if phase2 and hasattr(phase2, "input_manager"):
                input_manager = phase2.input_manager
            
            # Handle events
            if input_manager:
                # Use advanced input handling
                input_manager.update()
                
                # Get current mouse position for consistency
                self.mouse_position = input_manager.mouse_position
                
                # Check for exit event
                if not pygame.get_init():
                    running = False
            else:
                # Fallback to original event handling
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.MOUSEMOTION:
                        self.mouse_position = event.pos
                        self._handle_mouse_movement(event)
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        self._handle_mouse_click(event)
                    elif event.type == pygame.KEYDOWN:
                        self._handle_key_press(event)
            
            # Update game state with delta time
            dt = self.clock.get_time() / 1000.0  # Convert milliseconds to seconds
            
            # Update Phase2 integration if available
            if phase2 and hasattr(phase2, "update"):
                phase2.update(dt)
            
            # Update active scene
            if self.active_scene:
                self.active_scene.update(dt)
            
            # Update UI components
            for component in self.ui_components.values():
                if hasattr(component, "update") and component.visible:
                    component.update(dt)
            
            # Render frame
            self._render()
            
            # Cap the frame rate
            self.clock.tick(self.target_fps)
        
        # Clean up
        pygame.quit()
    
    def _render(self):
        """Render the current frame"""
        # Clear screen
        self.screen.fill((0, 0, 0))  # Black background
        
        # Render active scene
        if self.active_scene:
            self.active_scene.render(self.screen)
        
        # Render UI components in order
        # First the always visible components
        for name, component in self.ui_components.items():
            if name not in ["dialog"] and hasattr(component, "render") and component.visible:
                component.render(self.screen)
        
        # Then dialog on top if active
        if self.is_dialog_active and "dialog" in self.ui_components:
            self.ui_components["dialog"].render(self.screen)
        
        # Debug info (optional)
        if self.game_engine.debug_mode:
            # Use the game engine's debug info renderer
            if hasattr(self.game_engine, "_render_debug_info"):
                self.game_engine._render_debug_info(self.screen)
            else:
                # Fallback to simple debug info
                self._render_debug_info()
        
        # Update display
        pygame.display.flip()
    
    def _render_debug_info(self):
        """Render debug information (if debug mode is enabled)"""
        font = pygame.font.Font(None, 20)
        fps_text = font.render(f"FPS: {int(self.clock.get_fps())}", True, (255, 255, 255))
        self.screen.blit(fps_text, (5, 5))
        
        # Mouse position
        pos_text = font.render(f"Mouse: {self.mouse_position}", True, (255, 255, 255))
        self.screen.blit(pos_text, (5, 25))
        
        # Hover info
        if self.hover_object:
            hover_text = font.render(f"Hover: {self.hover_object}", True, (255, 255, 255))
            self.screen.blit(hover_text, (5, 45))
    
    def apply_theme(self, theme):
        """
        Apply a theme to all UI components that support it.
        
        Args:
            theme: UITheme instance
        """
        if not theme:
            return
            
        self.theme = theme
        
        # Apply theme to components that support it
        for name, component in self.ui_components.items():
            if hasattr(component, "set_theme"):
                component.set_theme(theme)
                logger.debug(f"Applied theme to {name}")
    
    def _handle_mouse_movement(self, event):
        """Handle mouse movement events"""
        # Update hover object
        self.hover_object = None
        
        # First check UI components (they have priority)
        for component in self.ui_components.values():
            if hasattr(component, "handle_mouse_movement") and component.visible:
                if component.handle_mouse_movement(event):
                    return
        
        # Then check scene objects
        if self.active_scene:
            self.hover_object = self.active_scene.get_object_at(event.pos)
            
            # Update cursor based on hover
            if self.hover_object:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    
    def _handle_mouse_click(self, event):
        """Handle mouse click events"""
        # First check UI components (they have priority)
        for component in self.ui_components.values():
            if hasattr(component, "handle_mouse_click") and component.visible:
                if component.handle_mouse_click(event):
                    return
        
        # Then check scene objects
        if self.active_scene and not self.is_dialog_active:
            self.active_scene.handle_mouse_click(event)
    
    def _handle_key_press(self, event):
        """Handle keyboard events"""
        # First check UI components (they have priority)
        for component in self.ui_components.values():
            if hasattr(component, "handle_key_press") and component.visible:
                if component.handle_key_press(event):
                    return
        
        # Then check scene
        if self.active_scene:
            self.active_scene.handle_key_press(event)
    
    def _on_location_changed(self, data):
        """Handle location changed event"""
        self._update_scene()
    
    def _on_dialog_started(self, data):
        """Handle dialog started event"""
        self.is_dialog_active = True
        self.ui_components["dialog"].visible = True
        self.ui_components["dialog"].start_dialog(data["dialog_id"], data["npc_id"])
    
    def _on_dialog_ended(self, data):
        """Handle dialog ended event"""
        self.is_dialog_active = False
        self.ui_components["dialog"].visible = False


class AssetManager:
    """
    Manages game assets including images, audio, and animations.
    """
    def __init__(self, asset_path="./assets/"):
        """
        Initialize the asset manager.
        
        Args:
            asset_path (str): Path to the assets directory
        """
        self.asset_path = asset_path
        
        # Asset collections
        self.images = {}
        self.sounds = {}
        self.music = {}
        self.animations = {}
        self.fonts = {}
        
        # Ensure asset directories exist
        self._create_directories()
        
        logger.info(f"Asset Manager initialized: {asset_path}")
    
    def _create_directories(self):
        """Create necessary asset directories if they don't exist"""
        directories = [
            "",  # Base directory
            "ui",
            "locations",
            "npcs",
            "items",
            "fonts",
            "sounds",
            "music"
        ]
        
        for directory in directories:
            os.makedirs(os.path.join(self.asset_path, directory), exist_ok=True)
    
    def load_common_assets(self):
        """Load common assets used across multiple scenes"""
        # Load UI elements
        self._load_image("ui_dialog_bg", os.path.join("ui", "dialog_bg.png"))
        self._load_image("ui_inventory_bg", os.path.join("ui", "inventory_bg.png"))
        self._load_image("ui_verb_bg", os.path.join("ui", "verb_bg.png"))
        
        # Load verb icons
        for verb in ["look", "talk", "take", "use", "go"]:
            self._load_image(f"verb_{verb}", os.path.join("ui", f"verb_{verb}.png"))
        
        # Load fonts
        self._load_font("dialog", os.path.join("fonts", "dialog.ttf"), 18)
        self._load_font("dialog_option", os.path.join("fonts", "dialog.ttf"), 16)
        self._load_font("ui", os.path.join("fonts", "ui.ttf"), 14)
        
        # Load common sounds
        self._load_sound("click", os.path.join("sounds", "click.wav"))
        self._load_sound("select", os.path.join("sounds", "select.wav"))
        
        logger.info("Common assets loaded")
    
    def load_location_assets(self, location_id):
        """
        Load assets for a specific location.
        
        Args:
            location_id (str): ID of the location
        """
        # Load background
        self._load_image(f"bg_{location_id}", os.path.join("locations", location_id, "background.png"))
        
        # Load objects and NPCs based on location data
        if hasattr(self, "game_engine") and self.game_engine:
            # Load location data
            location_data = self.game_engine.data_manager.get_data("locations", location_id)
            if location_data:
                # Load object images
                for obj in location_data.get("objects", []):
                    obj_id = obj["id"]
                    self._load_image(f"obj_{obj_id}", os.path.join("locations", location_id, "objects", f"{obj_id}.png"))
                
                # Load NPC images
                for npc_id in location_data.get("npcs", []):
                    self._load_image(f"npc_{npc_id}", os.path.join("npcs", f"{npc_id}.png"))
                    self._load_image(f"portrait_{npc_id}", os.path.join("npcs", f"{npc_id}_portrait.png"))
        
        # Load location music if available
        music_file = os.path.join("locations", location_id, "music.mp3")
        if os.path.exists(os.path.join(self.asset_path, music_file)):
            self._load_music(f"music_{location_id}", music_file)
        
        logger.info(f"Location assets loaded: {location_id}")
    
    def create_placeholder_asset(self, key, width, height, label=None, color=(200, 200, 200)):
        """
        Create a placeholder asset with optional text label.
        
        Args:
            key (str): Asset key
            width (int): Width of placeholder
            height (int): Height of placeholder
            label (str, optional): Text to display on placeholder
            color (tuple, optional): Background color (r, g, b)
            
        Returns:
            pygame.Surface: Created placeholder surface
        """
        # Create surface with transparency
        placeholder = pygame.Surface((width, height), pygame.SRCALPHA)
        placeholder.fill((*color, 220))  # Semi-transparent
        
        # Draw border
        pygame.draw.rect(placeholder, (100, 100, 100), placeholder.get_rect(), 2)
        
        # Add label if provided
        if label:
            try:
                font = pygame.font.Font(None, min(height // 3, 24))  # Scale font to fit
                text = font.render(label, True, (50, 50, 50))
                text_rect = text.get_rect(center=(width // 2, height // 2))
                placeholder.blit(text, text_rect)
            except Exception:
                # Ignore text rendering errors
                pass
        
        # Add to images collection
        self.images[key] = placeholder
        
        return placeholder
    
    def _load_image(self, key, file_path):
        """
        Load an image asset.
        
        Args:
            key (str): Key for retrieving the image
            file_path (str): Path to the image file relative to assets directory
        """
        full_path = os.path.join(self.asset_path, file_path)
        try:
            if os.path.exists(full_path):
                self.images[key] = pygame.image.load(full_path).convert_alpha()
                logger.debug(f"Loaded image: {key}")
            else:
                # Create a placeholder image
                placeholder = pygame.Surface((64, 64))
                placeholder.fill((200, 200, 200))  # Gray
                pygame.draw.rect(placeholder, (100, 100, 100), placeholder.get_rect(), 2)  # Border
                self.images[key] = placeholder
                logger.warning(f"Image not found, using placeholder: {file_path}")
        except Exception as e:
            logger.error(f"Error loading image {file_path}: {e}")
            # Create error placeholder
            placeholder = pygame.Surface((64, 64))
            placeholder.fill((255, 0, 0))  # Red for error
            self.images[key] = placeholder
    
    def _load_sound(self, key, file_path):
        """
        Load a sound asset.
        
        Args:
            key (str): Key for retrieving the sound
            file_path (str): Path to the sound file relative to assets directory
        """
        full_path = os.path.join(self.asset_path, file_path)
        try:
            if os.path.exists(full_path):
                self.sounds[key] = pygame.mixer.Sound(full_path)
                logger.debug(f"Loaded sound: {key}")
            else:
                logger.warning(f"Sound not found: {file_path}")
        except Exception as e:
            logger.error(f"Error loading sound {file_path}: {e}")
    
    def _load_music(self, key, file_path):
        """
        Load a music asset.
        
        Args:
            key (str): Key for retrieving the music
            file_path (str): Path to the music file relative to assets directory
        """
        full_path = os.path.join(self.asset_path, file_path)
        try:
            if os.path.exists(full_path):
                self.music[key] = full_path  # Store the path for pygame.mixer.music.load()
                logger.debug(f"Loaded music: {key}")
            else:
                logger.warning(f"Music not found: {file_path}")
        except Exception as e:
            logger.error(f"Error loading music {file_path}: {e}")
    
    def _load_font(self, key, file_path, size):
        """
        Load a font asset.
        
        Args:
            key (str): Key for retrieving the font
            file_path (str): Path to the font file relative to assets directory
            size (int): Font size
        """
        full_path = os.path.join(self.asset_path, file_path)
        try:
            if os.path.exists(full_path):
                self.fonts[key] = pygame.font.Font(full_path, size)
                logger.debug(f"Loaded font: {key}")
            else:
                # Use system font as fallback
                self.fonts[key] = pygame.font.Font(None, size)
                logger.warning(f"Font not found, using default: {file_path}")
        except Exception as e:
            logger.error(f"Error loading font {file_path}: {e}")
            # Use system font as fallback
            self.fonts[key] = pygame.font.Font(None, size)
    
    def get_image(self, key):
        """
        Get an image by key.
        
        Args:
            key (str): Image key
            
        Returns:
            pygame.Surface: The image or a placeholder if not found
        """
        if key in self.images:
            return self.images[key]
        
        # Return placeholder for missing image
        logger.warning(f"Image key not found: {key}")
        placeholder = pygame.Surface((64, 64))
        placeholder.fill((255, 0, 255))  # Magenta for missing
        return placeholder
    
    def get_sound(self, key):
        """
        Get a sound by key.
        
        Args:
            key (str): Sound key
            
        Returns:
            pygame.mixer.Sound or None: The sound or None if not found
        """
        return self.sounds.get(key)
    
    def get_music(self, key):
        """
        Get music path by key.
        
        Args:
            key (str): Music key
            
        Returns:
            str or None: Path to music file or None if not found
        """
        return self.music.get(key)
    
    def get_font(self, key):
        """
        Get a font by key.
        
        Args:
            key (str): Font key
            
        Returns:
            pygame.font.Font: The font or a default font if not found
        """
        if key in self.fonts:
            return self.fonts[key]
        
        # Return default font if not found
        logger.warning(f"Font key not found: {key}")
        return pygame.font.Font(None, 18)  # Default system font


class UIComponent:
    """Base class for UI components"""
    def __init__(self, game_engine, asset_manager, rect):
        self.game_engine = game_engine
        self.asset_manager = asset_manager
        self.rect = rect
        self.visible = True
        self.theme = None
    
    def update(self, dt):
        """Update component state"""
        pass
    
    def render(self, surface):
        """Render component to the given surface"""
        pass
    
    def handle_mouse_movement(self, event):
        """
        Handle mouse movement events.
        
        Returns:
            bool: True if event was handled, False otherwise
        """
        return False
    
    def handle_mouse_click(self, event):
        """
        Handle mouse click events.
        
        Returns:
            bool: True if event was handled, False otherwise
        """
        return False
    
    def handle_key_press(self, event):
        """
        Handle keyboard events.
        
        Returns:
            bool: True if event was handled, False otherwise
        """
        return False
    
    def set_theme(self, theme):
        """
        Set component theme.
        
        Args:
            theme: UITheme instance
        """
        self.theme = theme


class Scene:
    """Base class for game scenes"""
    def __init__(self, game_engine, asset_manager):
        self.game_engine = game_engine
        self.asset_manager = asset_manager
        self.objects = {}
        self.npcs = {}
    
    def update(self, dt):
        """Update scene state"""
        pass
    
    def render(self, surface):
        """Render the scene to the given surface"""
        pass
    
    def handle_mouse_click(self, event):
        """Handle mouse click events"""
        pass
    
    def handle_key_press(self, event):
        """Handle keyboard events"""
        pass
    
    def get_object_at(self, position):
        """
        Get the object at the given position.
        
        Args:
            position (tuple): Mouse position (x, y)
            
        Returns:
            dict or None: Object data or None if no object at position
        """
        return None


class LocationScene(Scene):
    """Scene representing a game location"""
    def __init__(self, game_engine, asset_manager, location_id):
        super().__init__(game_engine, asset_manager)
        self.location_id = location_id
        self.background = None
        self.exit_areas = {}
        
        # Load location data
        self._load_location()
    
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
            
            game_object = GameObject(
                obj_id,
                obj_data["name"],
                obj_data["description"],
                image,
                position,
                obj_data.get("actions", [])
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
                
                npc_view = NPCView(
                    npc_id,
                    npc_data["name"],
                    image,
                    position,
                    npc_model
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
    
    def update(self, dt):
        """Update scene state"""
        # Update NPCs
        for npc in self.npcs.values():
            npc.update(dt)
    
    def render(self, surface):
        """Render the scene to the given surface"""
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
        if self.game_engine.debug_mode:
            for exit_data in self.exit_areas.values():
                pygame.draw.rect(surface, (255, 0, 0, 128), exit_data["rect"], 1)
    
    def handle_mouse_click(self, event):
        """Handle mouse click events"""
        # Check if click is on an object
        for obj in self.objects.values():
            if obj.contains_point(event.pos):
                # Get selected verb
                verb = self.game_engine.ui_manager.ui_components["verb_bar"].selected_verb or "look"
                
                # Perform action
                self.game_engine.interaction_system.interact_with_object(obj.id, verb)
                return
        
        # Check if click is on an NPC
        for npc in self.npcs.values():
            if npc.contains_point(event.pos):
                # Get selected verb
                verb = self.game_engine.ui_manager.ui_components["verb_bar"].selected_verb or "talk"
                
                # Perform action
                self.game_engine.interaction_system.interact_with_npc(npc.id, verb)
                return
        
        # Check if click is on an exit area
        for direction, exit_data in self.exit_areas.items():
            if exit_data["rect"].collidepoint(event.pos):
                # Navigate to the target location
                self.game_engine.navigation_system.navigate_to_location(exit_data["target"])
                return
        
        # Click on empty area - walk there if "go" verb is selected
        verb = self.game_engine.ui_manager.ui_components["verb_bar"].selected_verb
        if verb == "go":
            # Movement logic would go here
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


class GameObject:
    """Represents an interactive object in the game world"""
    def __init__(self, obj_id, name, description, image, position, actions=None):
        self.id = obj_id
        self.name = name
        self.description = description
        self.image = image
        self.position = position
        self.rect = image.get_rect(topleft=position)
        self.actions = actions or []
        self.state = {}
    
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


class NPCView:
    """Visual representation of an NPC in the game world"""
    def __init__(self, npc_id, name, image, position, npc_model):
        self.id = npc_id
        self.name = name
        self.image = image
        self.position = position
        self.rect = image.get_rect(topleft=position)
        self.model = npc_model
        
        # Animation state
        self.current_animation = "idle"
        self.frame = 0
        self.animation_timer = 0
        self.hover = False
    
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
            dt (float): Time since last update in seconds
        """
        # Update animation
        self.animation_timer += dt
        if self.animation_timer >= 0.1:  # 10 FPS animation
            self.animation_timer = 0
            self.frame = (self.frame + 1) % 4  # Assume 4 frames per animation
            
        # Update behavior
        behavior = getattr(self.model, "behavior_type", None)
        if behavior:
            self._update_behavior(behavior, dt)
    
    def _update_behavior(self, behavior, dt):
        """
        Update based on NPC behavior.
        
        Args:
            behavior: NPC behavior
            dt (float): Time since last update in seconds
        """
        if behavior == "wary":
            # Occasionally look around
            if random.random() < 0.01:
                self.current_animation = "look_around"
        elif behavior == "hostile":
            # Move away if player is nearby
            self.current_animation = "nervous"
        elif behavior == "assimilated":
            # Show subtle different behavior
            if random.random() < 0.005:
                self.current_animation = "strange"
        else:
            # Default idle behavior
            self.current_animation = "idle"
    
    def render(self, surface):
        """
        Render the NPC to the given surface.
        
        Args:
            surface (pygame.Surface): Surface to render on
        """
        # Get animation frame
        frame_image = self._get_animation_frame()
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
    
    def _get_animation_frame(self):
        """
        Get the current animation frame.
        
        Returns:
            pygame.Surface or None: Current animation frame or None if not animated
        """
        # In a real implementation, this would retrieve the correct frame
        # from a sprite sheet or animation dictionary
        return self.image


class VerbBarUI(UIComponent):
    """UI component for displaying and selecting verbs"""
    def __init__(self, game_engine, asset_manager, rect):
        super().__init__(game_engine, asset_manager, rect)
        
        # Verb state
        self.verbs = ["look", "talk", "take", "use", "go"]
        self.selected_verb = None
        self.verb_width = 70
        self.verb_height = 30
        self.verb_padding = 10
        
        # Visual elements
        self.background = asset_manager.get_image("ui_verb_bg")
        self.verb_images = {
            verb: asset_manager.get_image(f"verb_{verb}")
            for verb in self.verbs
        }
        
        # Create verb rectangles
        self.verb_rects = {}
        self._update_verb_rects()
    
    def _update_verb_rects(self):
        """Update verb rectangle positions"""
        start_x = self.rect.left + (self.rect.width - (len(self.verbs) * (self.verb_width + self.verb_padding))) // 2
        
        for i, verb in enumerate(self.verbs):
            # Calculate verb position
            verb_x = start_x + i * (self.verb_width + self.verb_padding)
            verb_y = self.rect.top + (self.rect.height - self.verb_height) // 2
            
            # Create verb rect
            self.verb_rects[verb] = pygame.Rect(verb_x, verb_y, self.verb_width, self.verb_height)
    
    def render(self, surface):
        """Render the verb bar UI to the given surface"""
        if not self.visible:
            return
        
        # Draw background using theme if available
        if self.theme:
            self.theme.draw_panel(surface, self.rect)
        elif self.background:
            surface.blit(self.background, self.rect)
        else:
            pygame.draw.rect(surface, (50, 50, 80), self.rect, 0)
        
        # Draw verbs
        for verb, verb_rect in self.verb_rects.items():
            # Determine colors based on theme or defaults
            if self.theme:
                bg_color = self.theme.highlight_color if verb == self.selected_verb else self.theme.button_color
                text_color = self.theme.text_color
            else:
                bg_color = (100, 100, 255) if verb == self.selected_verb else (50, 50, 80)
                text_color = (255, 255, 255)
            
            # Draw verb background
            if self.theme:
                self.theme.draw_button(
                    surface, 
                    verb_rect, 
                    verb.capitalize(), 
                    self.asset_manager.get_font("ui"),
                    is_selected=(verb == self.selected_verb)
                )
            else:
                # Fallback to original implementation
                pygame.draw.rect(surface, bg_color, verb_rect, 0)
                
                # Draw verb image if available
                if verb in self.verb_images and self.verb_images[verb]:
                    image = self.verb_images[verb]
                    image_rect = image.get_rect(center=verb_rect.center)
                    surface.blit(image, image_rect)
                else:
                    # Fallback to text
                    font = self.asset_manager.get_font("ui")
                    text = font.render(verb.capitalize(), True, text_color)
                    text_rect = text.get_rect(center=verb_rect.center)
                    surface.blit(text, text_rect)
    
    def handle_mouse_movement(self, event):
        """Handle mouse movement over verbs"""
        if not self.visible or not self.rect.collidepoint(event.pos):
            return False
        
        # Check if mouse is over any verb
        for verb, verb_rect in self.verb_rects.items():
            if verb_rect.collidepoint(event.pos):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                return True
        
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        return False
    
    def handle_mouse_click(self, event):
        """Handle mouse click on verbs"""
        if not self.visible or not self.rect.collidepoint(event.pos):
            return False
        
        # Check if click was on a verb
        for verb, verb_rect in self.verb_rects.items():
            if verb_rect.collidepoint(event.pos):
                # Toggle selection
                if self.selected_verb == verb:
                    self.selected_verb = None
                else:
                    self.selected_verb = verb
                
                # Play sound
                sound = self.asset_manager.get_sound("click")
                if sound:
                    sound.play()
                
                # Emit verb selected event
                self.game_engine.event_system.emit("verb_selected", {
                    "verb": self.selected_verb
                })
                
                return True
        
        return False


class InventoryUI(UIComponent):
    """UI component for displaying and managing inventory"""
    def __init__(self, game_engine, asset_manager, rect):
        super().__init__(game_engine, asset_manager, rect)
        
        # Inventory state
        self.selected_item = None
        self.items_per_row = 8
        self.item_size = 64
        self.item_padding = 4
        
        # Visual elements
        self.background = asset_manager.get_image("ui_inventory_bg")
        
        # Register events
        game_engine.event_system.subscribe("item_acquired", self._on_item_acquired)
        game_engine.event_system.subscribe("item_removed", self._on_item_removed)
    
    def _on_item_acquired(self, data):
        """Handle item acquired event"""
        # Update the UI
        pass
    
    def _on_item_removed(self, data):
        """Handle item removed event"""
        # Update the UI
        pass
    
    def render(self, surface):
        """Render the inventory UI to the given surface"""
        if not self.visible:
            return
        
        # Draw background using theme if available
        if self.theme:
            self.theme.draw_panel(surface, self.rect)
        elif self.background:
            surface.blit(self.background, self.rect)
        else:
            pygame.draw.rect(surface, (30, 30, 50), self.rect, 0)
        
        # Get inventory items
        inventory = self.game_engine.game_state.player.get_inventory()
        
        # Draw items
        for i, item in enumerate(inventory):
            row = i // self.items_per_row
            col = i % self.items_per_row
            
            # Calculate item position
            item_x = self.rect.left + col * (self.item_size + self.item_padding) + 10
            item_y = self.rect.top + row * (self.item_size + self.item_padding) + 10
            
            # Get item image
            item_name = item.get("name", "Unknown")
            item_id = item.get("id", "unknown")
            item_image = self.asset_manager.get_image(f"item_{item_id}")
            
            # Draw item
            item_rect = pygame.Rect(item_x, item_y, self.item_size, self.item_size)
            if item_image:
                surface.blit(item_image, item_rect)
            else:
                # Fallback if image not found
                pygame.draw.rect(surface, (100, 100, 100), item_rect, 0)
                
                # Draw item name
                font = self.asset_manager.get_font("ui")
                text = font.render(item_name[:10], True, (255, 255, 255))
                text_rect = text.get_rect(center=(item_x + self.item_size // 2, item_y + self.item_size // 2))
                surface.blit(text, text_rect)
            
            # Draw selection highlight
            if self.selected_item == i:
                if self.theme:
                    pygame.draw.rect(surface, self.theme.highlight_color, item_rect, 2)
                else:
                    pygame.draw.rect(surface, (255, 255, 0), item_rect, 2)
    
    def handle_mouse_click(self, event):
        """Handle mouse click on inventory items"""
        if not self.visible or not self.rect.collidepoint(event.pos):
            return False
        
        # Get inventory items
        inventory = self.game_engine.game_state.player.get_inventory()
        
        # Check which item was clicked
        for i, _ in enumerate(inventory):
            row = i // self.items_per_row
            col = i % self.items_per_row
            
            # Calculate item position
            item_x = self.rect.left + col * (self.item_size + self.item_padding) + 10
            item_y = self.rect.top + row * (self.item_size + self.item_padding) + 10
            
            # Create item rect
            item_rect = pygame.Rect(item_x, item_y, self.item_size, self.item_size)
            
            if item_rect.collidepoint(event.pos):
                # Toggle selection
                if self.selected_item == i:
                    self.selected_item = None
                else:
                    self.selected_item = i
                
                # Emit item selected event
                self.game_engine.event_system.emit("item_selected", {
                    "item_index": self.selected_item
                })
                
                # Play sound
                sound = self.asset_manager.get_sound("click")
                if sound:
                    sound.play()
                
                return True
        
        return False


class DialogUI(UIComponent):
    """UI component for displaying dialogs"""
    def __init__(self, game_engine, asset_manager, rect):
        super().__init__(game_engine, asset_manager, rect)
        
        # Dialog state
        self.current_npc = None
        self.current_text = ""
        self.current_options = []
        self.selected_option = -1
        
        # Animation
        self.text_reveal_index = 0
        self.text_reveal_speed = 30  # Characters per second
        self.text_reveal_timer = 0
        
        # Visual elements
        self.background = asset_manager.get_image("ui_dialog_bg")
        self.npc_portrait = None
        self.player_portrait = None  # Could load player portrait here
        
        # Register events
        game_engine.event_system.subscribe("dialog_node_updated", self._on_dialog_node_updated)
    
    def start_dialog(self, dialog_id, npc_id):
        """
        Start a dialog.
        
        Args:
            dialog_id (str): ID of the dialog to start
            npc_id (str): ID of the NPC
        """
        self.visible = True
        self.current_npc = npc_id
        
        # Load NPC portrait
        self.npc_portrait = self.asset_manager.get_image(f"portrait_{npc_id}")
        
        # Reset animation
        self.text_reveal_index = 0
        self.text_reveal_timer = 0
        
        # Start dialog in dialog manager
        self.game_engine.dialog_manager.start_dialog(dialog_id, npc_id)
    
    def _on_dialog_node_updated(self, data):
        """Handle dialog node updated event"""
        self.current_text = data.get("text", "")
        self.current_options = data.get("options", [])
        self.selected_option = -1
        
        # Reset text reveal animation
        self.text_reveal_index = 0
        self.text_reveal_timer = 0
    
    def update(self, dt):
        """Update dialog UI state"""
        if not self.visible:
            return
        
        # Update text reveal animation
        if self.text_reveal_index < len(self.current_text):
            self.text_reveal_timer += dt
            chars_to_reveal = int(self.text_reveal_speed * self.text_reveal_timer)
            if chars_to_reveal > 0:
                self.text_reveal_timer = 0
                self.text_reveal_index = min(
                    self.text_reveal_index + chars_to_reveal,
                    len(self.current_text)
                )
    
    def render(self, surface):
        """Render the dialog UI to the given surface"""
        if not self.visible:
            return
        
        # Draw background using theme if available
        if self.theme:
            self.theme.draw_panel(surface, self.rect)
        elif self.background:
            surface.blit(self.background, self.rect)
        else:
            pygame.draw.rect(surface, (30, 30, 50), self.rect, 0)
        
        # Draw portraits
        if self.npc_portrait:
            portrait_rect = pygame.Rect(self.rect.left + 10, self.rect.top + 10, 80, 80)
            surface.blit(self.npc_portrait, portrait_rect)
        
        # Draw text
        revealed_text = self.current_text[:self.text_reveal_index]
        text_rect = pygame.Rect(
            self.rect.left + 100,
            self.rect.top + 10,
            self.rect.width - 110,
            80
        )
        
        if self.theme:
            self.theme.draw_text(
                surface, 
                revealed_text, 
                self.asset_manager.get_font("dialog"),
                (text_rect.left, text_rect.top),
                max_width=text_rect.width
            )
        else:
            self._render_text(surface, revealed_text, text_rect)
        
        # Draw options if text is fully revealed
        if self.text_reveal_index >= len(self.current_text):
            self._render_options(surface)
    
    def _render_text(self, surface, text, rect):
        """
        Render dialog text with word wrapping.
        
        Args:
            surface (pygame.Surface): Surface to render on
            text (str): Text to render
            rect (pygame.Rect): Rectangle to contain the text
        """
        font = self.asset_manager.get_font("dialog")
        
        # Word wrap implementation
        words = text.split(' ')
        space_width = font.size(' ')[0]
        x, y = rect.left, rect.top
        
        for word in words:
            word_surface = font.render(word, True, (255, 255, 255))
            word_width, word_height = word_surface.get_size()
            
            if x + word_width >= rect.right:
                x = rect.left
                y += word_height
                
            surface.blit(word_surface, (x, y))
            x += word_width + space_width
    
    def _render_options(self, surface):
        """Render dialog options"""
        if not self.current_options:
            return
        
        option_font = self.asset_manager.get_font("dialog_option")
        option_height = 25
        option_padding = 5
        
        # Calculate starting position
        start_y = self.rect.bottom - (len(self.current_options) * (option_height + option_padding)) - 10
        
        for i, option in enumerate(self.current_options):
            # Create option rectangle
            option_rect = pygame.Rect(
                self.rect.left + 20,
                start_y + i * (option_height + option_padding),
                self.rect.width - 40,
                option_height
            )
            
            # Draw option using theme if available
            option_text = option["text"]
            
            if self.theme:
                self.theme.draw_button(
                    surface,
                    option_rect,
                    option_text,
                    option_font,
                    is_hover=(i == self.selected_option),
                    is_selected=(i == self.selected_option)
                )
            else:
                # Fallback to original implementation
                if i == self.selected_option:
                    pygame.draw.rect(surface, (100, 100, 255), option_rect, 0)
                    text_color = (255, 255, 255)
                else:
                    pygame.draw.rect(surface, (50, 50, 80), option_rect, 0)
                    text_color = (200, 200, 200)
                
                # Draw option text
                option_text_surf = option_font.render(option_text, True, text_color)
                text_rect = option_text_surf.get_rect(midleft=(option_rect.left + 10, option_rect.centery))
                surface.blit(option_text_surf, text_rect)
    
    def handle_mouse_movement(self, event):
        """Handle mouse movement over dialog options"""
        if not self.visible or not self.rect.collidepoint(event.pos) or not self.current_options:
            return False
        
        if self.text_reveal_index < len(self.current_text):
            return False
        
        # Check if mouse is over any option
        option_height = 25
        option_padding = 5
        start_y = self.rect.bottom - (len(self.current_options) * (option_height + option_padding)) - 10
        
        for i, _ in enumerate(self.current_options):
            option_rect = pygame.Rect(
                self.rect.left + 20,
                start_y + i * (option_height + option_padding),
                self.rect.width - 40,
                option_height
            )
            
            if option_rect.collidepoint(event.pos):
                self.selected_option = i
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                return True
        
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        return False
    
    def handle_mouse_click(self, event):
        """Handle mouse click on dialog options"""
        if not self.visible or not self.rect.collidepoint(event.pos):
            return False
        
        # Skip text reveal on click
        if self.text_reveal_index < len(self.current_text):
            self.text_reveal_index = len(self.current_text)
            return True
        
        # Check if click was on an option
        if self.selected_option >= 0 and self.selected_option < len(self.current_options):
            self._select_option(self.selected_option)
            
            # Play sound
            sound = self.asset_manager.get_sound("select")
            if sound:
                sound.play()
            
            return True
        
        return False
    
    def _select_option(self, option_index):
        """
        Select a dialog option.
        
        Args:
            option_index (int): Index of the option to select
        """
        if option_index < 0 or option_index >= len(self.current_options):
            return
        
        option = self.current_options[option_index]
        option_id = option["id"]
        
        # Forward to dialog manager
        self.game_engine.dialog_manager.select_option(option_id)


class StatusBarUI(UIComponent):
    """UI component for displaying game status"""
    def __init__(self, game_engine, asset_manager, rect):
        super().__init__(game_engine, asset_manager, rect)
        
        # Status bar state
        self.update_timer = 0
        self.update_interval = 1.0  # Update every second
        
        # Font for status text
        self.font = asset_manager.get_font("ui")
    
    def update(self, dt):
        """Update status bar"""
        self.update_timer += dt
        if self.update_timer >= self.update_interval:
            self.update_timer = 0
            # Status bar only needs periodic updates
    
    def render(self, surface):
        """Render the status bar UI to the given surface"""
        if not self.visible:
            return
        
        # Draw background using theme if available
        if self.theme:
            self.theme.draw_panel(surface, self.rect)
        else:
            pygame.draw.rect(surface, (30, 30, 50), self.rect, 0)
        
        # Get current location name
        location_id = self.game_engine.game_state.current_location
        location_data = self.game_engine.data_manager.get_data("locations", location_id)
        location_name = location_data.get("name", "Unknown Location") if location_data else "Unknown Location"
        
        # Get game time
        game_time = self.game_engine.game_state.time
        time_str = f"Day {game_time['day']} - {game_time['hour']:02d}:{game_time['minute']:02d}"
        
        # Get coalition status
        coalition_size = len(self.game_engine.game_state.coalition_members)
        
        # Render text
        text_color = self.theme.text_color if self.theme else (255, 255, 255)
        location_text = self.font.render(location_name, True, text_color)
        time_text = self.font.render(time_str, True, text_color)
        coalition_text = self.font.render(f"Coalition: {coalition_size}", True, text_color)
        
        # Position text
        surface.blit(location_text, (self.rect.left + 10, self.rect.centery - 8))
        surface.blit(time_text, (self.rect.centerx - 40, self.rect.centery - 8))
        surface.blit(coalition_text, (self.rect.right - 100, self.rect.centery - 8))