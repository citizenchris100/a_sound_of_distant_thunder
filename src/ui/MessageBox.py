"""
Message Box Component for A Sound of Distant Thunder
Displays text messages, descriptions, and notifications to the player.
"""
import pygame
import logging
import textwrap

# Configure logging
logger = logging.getLogger("MessageBox")

class MessageBox:
    """
    UI component for displaying text messages.
    Handles word wrapping, text scrolling, and animations.
    """
    def __init__(self, game_engine, asset_manager, max_width=600, max_height=300):
        """
        Initialize the message box.
        
        Args:
            game_engine: GameEngine instance
            asset_manager: AssetManager instance
            max_width (int): Maximum width of the box
            max_height (int): Maximum height of the box
        """
        self.game_engine = game_engine
        self.asset_manager = asset_manager
        self.max_width = max_width
        self.max_height = max_height
        
        # Message state
        self.messages = []
        self.current_message = None
        self.text_reveal_index = 0
        self.text_reveal_speed = 30  # Characters per second
        self.text_reveal_timer = 0
        self.visible = False
        self.auto_hide_timer = 0
        self.scroll_offset = 0
        
        # Position is centered by default
        self.rect = pygame.Rect(0, 0, max_width, max_height)
        self.centered = True
        self.centered_y_offset = 50  # Distance from center in y-axis
        
        # Visual elements
        self.font = None
        self.background_color = (0, 0, 0, 200)  # Semi-transparent black
        self.text_color = (255, 255, 255)  # White
        self.border_color = (200, 200, 200)  # Light gray
        
        # Register event listeners
        game_engine.event_system.subscribe("message_displayed", self._on_message_displayed)
        game_engine.event_system.subscribe("description_displayed", self._on_description_displayed)
        
        logger.info("Message Box initialized")
    
    def _on_message_displayed(self, data):
        """
        Handle message displayed event.
        
        Args:
            data (dict): Event data with message text
        """
        text = data.get("text", "")
        if text:
            self.show_message(text, message_type="message")
    
    def _on_description_displayed(self, data):
        """
        Handle description displayed event.
        
        Args:
            data (dict): Event data with description text
        """
        text = data.get("text", "")
        if text:
            self.show_message(text, message_type="description")
    
    def show_message(self, text, message_type="message", auto_hide=True, auto_hide_delay=5.0):
        """
        Show a message in the message box.
        
        Args:
            text (str): Message text
            message_type (str): Type of message (affects appearance)
            auto_hide (bool): Whether to hide message after delay
            auto_hide_delay (float): Delay in seconds before hiding
        """
        # Initialize font if not done yet
        if not self.font:
            self.font = self.asset_manager.get_font("dialog") or pygame.font.Font(None, 20)
        
        # Reset state
        self.visible = True
        self.text_reveal_index = 0
        self.text_reveal_timer = 0
        self.scroll_offset = 0
        
        # Add message to queue
        self.messages.append({
            "text": text,
            "type": message_type,
            "auto_hide": auto_hide,
            "auto_hide_delay": auto_hide_delay,
            "wrapped_lines": self._wrap_text(text)
        })
        
        # If no current message, show this one
        if not self.current_message:
            self._next_message()
    
    def _wrap_text(self, text):
        """
        Wrap text to fit within the message box.
        
        Args:
            text (str): Text to wrap
            
        Returns:
            list: List of wrapped lines
        """
        if not text:
            return []
            
        # Calculate maximum characters per line
        # This is an approximation, as character widths vary
        char_width = self.font.size("A")[0]
        chars_per_line = (self.max_width - 40) // char_width
        
        # Wrap text
        lines = []
        for paragraph in text.split("\n"):
            if not paragraph:
                lines.append("")
            else:
                lines.extend(textwrap.wrap(paragraph, width=chars_per_line))
        
        return lines
    
    def _next_message(self):
        """Show the next message in the queue"""
        if not self.messages:
            self.current_message = None
            self.visible = False
            return
            
        self.current_message = self.messages.pop(0)
        self.text_reveal_index = 0
        self.text_reveal_timer = 0
        self.auto_hide_timer = 0
        self.scroll_offset = 0
    
    def update(self, dt):
        """
        Update message box state.
        
        Args:
            dt (float): Time delta in seconds
        """
        if not self.visible or not self.current_message:
            return
            
        # Update centered position if needed
        if self.centered:
            screen_width, screen_height = pygame.display.get_surface().get_size()
            self.rect.centerx = screen_width // 2
            self.rect.centery = screen_height // 2 + self.centered_y_offset
        
        # Update text reveal animation
        wrapped_lines = self.current_message.get("wrapped_lines", [])
        full_text = "\n".join(wrapped_lines)
        
        if self.text_reveal_index < len(full_text):
            self.text_reveal_timer += dt
            chars_to_reveal = int(self.text_reveal_speed * self.text_reveal_timer)
            if chars_to_reveal > 0:
                self.text_reveal_timer = 0
                self.text_reveal_index = min(
                    self.text_reveal_index + chars_to_reveal,
                    len(full_text)
                )
        else:
            # Text fully revealed, update auto-hide timer
            if self.current_message.get("auto_hide", True):
                self.auto_hide_timer += dt
                if self.auto_hide_timer >= self.current_message.get("auto_hide_delay", 5.0):
                    self._next_message()
    
    def render(self, surface):
        """
        Render the message box to the given surface.
        
        Args:
            surface (pygame.Surface): Surface to render on
        """
        if not self.visible or not self.current_message:
            return
            
        # Create background surface with transparency
        background = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        background.fill(self.background_color)
        
        # Draw border
        pygame.draw.rect(background, self.border_color, background.get_rect(), 2)
        
        # Get wrapped lines
        wrapped_lines = self.current_message.get("wrapped_lines", [])
        
        # Calculate what portion of text to show (for reveal animation)
        remaining_chars = self.text_reveal_index
        visible_lines = []
        
        for line in wrapped_lines:
            if remaining_chars <= 0:
                break
            
            if remaining_chars >= len(line):
                visible_lines.append(line)
                remaining_chars -= len(line) + 1  # +1 for the newline
            else:
                visible_lines.append(line[:remaining_chars])
                remaining_chars = 0
        
        # Render text
        line_height = self.font.get_linesize()
        text_y = 20 - self.scroll_offset * line_height
        
        for line in visible_lines:
            if line:
                text_surface = self.font.render(line, True, self.text_color)
                background.blit(text_surface, (20, text_y))
            text_y += line_height
            
            # Stop rendering if outside box
            if text_y > self.rect.height - 20:
                break
        
        # Draw scroll indicators if needed
        if len(wrapped_lines) * line_height > self.rect.height - 40:
            # Up arrow
            if self.scroll_offset > 0:
                arrow_up = pygame.Surface((20, 10), pygame.SRCALPHA)
                pygame.draw.polygon(arrow_up, self.text_color, [(0, 10), (10, 0), (20, 10)])
                background.blit(arrow_up, (self.rect.width - 30, 10))
                
            # Down arrow
            if self.scroll_offset < len(wrapped_lines) - (self.rect.height - 40) // line_height:
                arrow_down = pygame.Surface((20, 10), pygame.SRCALPHA)
                pygame.draw.polygon(arrow_down, self.text_color, [(0, 0), (10, 10), (20, 0)])
                background.blit(arrow_down, (self.rect.width - 30, self.rect.height - 20))
        
        # Blit message box to screen
        surface.blit(background, self.rect)
    
    def handle_mouse_click(self, event):
        """
        Handle mouse click events.
        
        Args:
            event (pygame.event.Event): Mouse click event
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        if not self.visible or not self.current_message:
            return False
            
        if not self.rect.collidepoint(event.pos):
            return False
            
        # Check if text is still revealing
        wrapped_lines = self.current_message.get("wrapped_lines", [])
        full_text = "\n".join(wrapped_lines)
        
        if self.text_reveal_index < len(full_text):
            # Skip to end of text
            self.text_reveal_index = len(full_text)
            return True
        else:
            # Text fully revealed, go to next message
            self._next_message()
            return True
        
        return False
    
    def handle_mouse_wheel(self, event):
        """
        Handle mouse wheel events for scrolling.
        
        Args:
            event (pygame.event.Event): Mouse wheel event
            
        Returns:
            bool: True if event was handled, False otherwise
        """
        if not self.visible or not self.current_message:
            return False
            
        if not self.rect.collidepoint(pygame.mouse.get_pos()):
            return False
            
        # Get wrapped lines
        wrapped_lines = self.current_message.get("wrapped_lines", [])
        
        # Scroll limit
        max_scroll = max(0, len(wrapped_lines) - (self.rect.height - 40) // self.font.get_linesize())
        
        # Adjust scroll offset
        if hasattr(event, "y"):
            # Pygame 2.0+ wheel event
            self.scroll_offset = max(0, min(max_scroll, self.scroll_offset - event.y))
        elif hasattr(event, "button"):
            # Older style mouse button event (4=up, 5=down)
            if event.button == 4:  # Scroll up
                self.scroll_offset = max(0, self.scroll_offset - 1)
            elif event.button == 5:  # Scroll down
                self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
                
        return True
    
    def hide(self):
        """Hide the message box"""
        self.visible = False
        self.current_message = None
        self.messages = []