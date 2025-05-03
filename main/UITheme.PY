"""
UI Theme System for A Sound of Distant Thunder
Defines consistent visual styling for all UI components.
"""
import pygame
import logging

# Configure logging
logger = logging.getLogger("UITheme")

class UITheme:
    """Defines a visual theme for UI components"""
    def __init__(self):
        # Color scheme
        self.background_color = (30, 30, 50, 220)  # Dark blue, semi-transparent
        self.text_color = (230, 230, 230)  # Light gray
        self.highlight_color = (100, 120, 200)  # Blue highlight
        self.border_color = (80, 80, 120)  # Medium blue border
        self.button_color = (60, 60, 80)  # Dark button
        self.button_hover_color = (80, 80, 100)  # Lighter when hovered
        self.disabled_color = (50, 50, 70)  # Grayed out for disabled items
        self.success_color = (40, 180, 40)  # Green for success indicators
        self.warning_color = (200, 180, 20)  # Yellow for warnings
        self.error_color = (200, 40, 40)  # Red for errors
        
        # Text properties
        self.title_font_size = 24
        self.heading_font_size = 20
        self.body_font_size = 16
        self.small_font_size = 14
        
        # Layout properties
        self.padding = 10
        self.small_padding = 5
        self.border_width = 2
        self.border_radius = 5
        self.button_height = 30
        self.tooltip_delay = 0.5  # seconds before showing tooltip
        
        # Animation properties
        self.transition_speed = 0.3  # seconds
        self.hover_alpha_change = 30  # alpha change on hover
        
    def draw_panel(self, surface, rect, with_border=True, alpha=None):
        """
        Draw a UI panel with the theme's styling.
        
        Args:
            surface (pygame.Surface): Surface to render on
            rect (pygame.Rect): Rectangle defining panel position and size
            with_border (bool): Whether to draw a border
            alpha (int, optional): Override alpha value (0-255)
        """
        # Create a rounded rect surface with transparency
        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        # Use provided alpha or default from theme
        bg_color = list(self.background_color)
        if alpha is not None:
            bg_color[3] = alpha
        
        # Fill with background color
        pygame.draw.rect(
            panel,
            tuple(bg_color),
            (0, 0, rect.width, rect.height),
            border_radius=self.border_radius
        )
        
        # Add border if requested
        if with_border:
            pygame.draw.rect(
                panel,
                self.border_color,
                (0, 0, rect.width, rect.height),
                width=self.border_width,
                border_radius=self.border_radius
            )
        
        # Blit to target surface
        surface.blit(panel, rect)
        
    def draw_button(self, surface, rect, text, font, is_hover=False, is_selected=False, 
                   is_disabled=False, icon=None, align="center"):
        """
        Draw a themed button.
        
        Args:
            surface (pygame.Surface): Surface to render on
            rect (pygame.Rect): Rectangle defining button position and size
            text (str): Button label text
            font (pygame.font.Font): Font to use for the text
            is_hover (bool): Whether the mouse is hovering over the button
            is_selected (bool): Whether the button is in selected state
            is_disabled (bool): Whether the button is disabled
            icon (pygame.Surface, optional): Icon to display
            align (str): Text alignment - "left", "center", or "right"
        """
        # Determine button color based on state
        if is_disabled:
            color = self.disabled_color
        elif is_selected:
            color = self.highlight_color
        elif is_hover:
            color = self.button_hover_color
        else:
            color = self.button_color
            
        # Create button surface
        button = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        # Draw rounded rectangle
        pygame.draw.rect(
            button,
            color,
            (0, 0, rect.width, rect.height),
            border_radius=self.border_radius
        )
        
        # Add border
        pygame.draw.rect(
            button,
            self.border_color,
            (0, 0, rect.width, rect.height),
            width=self.border_width,
            border_radius=self.border_radius
        )
        
        # Determine text position based on alignment and icon
        icon_width = 0
        if icon:
            icon_width = icon.get_width() + self.small_padding
            icon_rect = icon.get_rect(
                centery=rect.height // 2,
                left=self.small_padding
            )
            button.blit(icon, icon_rect)
        
        # Render text
        text_surface = font.render(text, True, self.text_color)
        
        if align == "left":
            text_rect = text_surface.get_rect(
                centery=rect.height // 2,
                left=self.small_padding + icon_width
            )
        elif align == "right":
            text_rect = text_surface.get_rect(
                centery=rect.height // 2,
                right=rect.width - self.small_padding
            )
        else:  # center
            text_rect = text_surface.get_rect(center=(rect.width // 2, rect.height // 2))
            if icon:
                # Adjust for icon
                text_rect.x += icon_width // 2
        
        button.blit(text_surface, text_rect)
        
        # Blit to target surface
        surface.blit(button, rect)
        
        # Return the rectangle used for event handling
        return rect
    
    def draw_text(self, surface, text, font, position, color=None, align="left", max_width=None):
        """
        Draw themed text with optional alignment and wrapping.
        
        Args:
            surface (pygame.Surface): Surface to render on
            text (str): Text to render
            font (pygame.font.Font): Font to use for the text
            position (tuple): Position (x, y) for the text
            color (tuple, optional): Text color override
            align (str): Text alignment - "left", "center", or "right"
            max_width (int, optional): Maximum width for text wrapping
            
        Returns:
            pygame.Rect: Rectangle containing all rendered text
        """
        if not text:
            return pygame.Rect(position[0], position[1], 0, 0)
            
        text_color = color or self.text_color
        x, y = position
        
        if max_width:
            # Word wrapping
            words = text.split(' ')
            space_width = font.size(' ')[0]
            current_x = x
            current_y = y
            max_x = x  # Track rightmost extent
            start_y = y  # Remember starting y
            
            for word in words:
                word_surface = font.render(word, True, text_color)
                word_width, word_height = word_surface.get_size()
                
                if current_x + word_width >= x + max_width:
                    # Wrap to next line
                    current_x = x
                    current_y += word_height + 2
                
                # Calculate horizontal position based on alignment
                if align == "center":
                    draw_x = current_x - (current_x - x) + (max_width - word_width) // 2
                elif align == "right":
                    draw_x = current_x - (current_x - x) + (max_width - word_width)
                else:  # left
                    draw_x = current_x
                
                surface.blit(word_surface, (draw_x, current_y))
                current_x += word_width + space_width
                max_x = max(max_x, draw_x + word_width)
            
            # Return rectangle covering all text
            return pygame.Rect(x, start_y, max_x - x, current_y + word_height - start_y)
        else:
            # Simple text rendering without wrapping
            text_surface = font.render(text, True, text_color)
            text_rect = text_surface.get_rect()
            
            if align == "center":
                text_rect.midtop = (x, y)
            elif align == "right":
                text_rect.topright = (x, y)
            else:  # left
                text_rect.topleft = (x, y)
                
            surface.blit(text_surface, text_rect)
            return text_rect
    
    def draw_progress_bar(self, surface, rect, value, max_value=100, color=None, show_text=True):
        """
        Draw a themed progress bar.
        
        Args:
            surface (pygame.Surface): Surface to render on
            rect (pygame.Rect): Rectangle defining bar position and size
            value (float): Current value
            max_value (float): Maximum value (100% full)
            color (tuple, optional): Bar color, or None to use theme highlight color
            show_text (bool): Whether to display percentage text
            
        Returns:
            pygame.Rect: Rectangle of the entire progress bar
        """
        if not color:
            color = self.highlight_color
            
        # Create progress bar surface
        bar = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        # Draw background
        pygame.draw.rect(
            bar, 
            (self.background_color[0], self.background_color[1], self.background_color[2], 180),
            (0, 0, rect.width, rect.height),
            border_radius=self.border_radius
        )
        
        # Calculate fill width
        fill_width = int((value / max_value) * (rect.width - 4))
        fill_width = max(0, min(fill_width, rect.width - 4))
        
        # Draw fill
        if fill_width > 0:
            pygame.draw.rect(
                bar,
                color,
                (2, 2, fill_width, rect.height - 4),
                border_radius=max(0, self.border_radius - 2)
            )
        
        # Draw border
        pygame.draw.rect(
            bar,
            self.border_color,
            (0, 0, rect.width, rect.height),
            width=self.border_width,
            border_radius=self.border_radius
        )
        
        # Add percentage text if requested
        if show_text:
            percentage = int((value / max_value) * 100)
            font = pygame.font.Font(None, min(rect.height - 4, 24))
            text = font.render(f"{percentage}%", True, self.text_color)
            text_rect = text.get_rect(center=(rect.width // 2, rect.height // 2))
            bar.blit(text, text_rect)
        
        # Blit to target surface
        surface.blit(bar, rect)
        
        return rect
    
    def draw_tooltip(self, surface, rect, text, font=None):
        """
        Draw a tooltip with the given text.
        
        Args:
            surface (pygame.Surface): Surface to render on
            rect (pygame.Rect): Rectangle for tooltip position
            text (str): Tooltip text
            font (pygame.font.Font, optional): Font to use, or None for default
            
        Returns:
            pygame.Rect: Rectangle of the tooltip
        """
        if not font:
            font = pygame.font.Font(None, self.small_font_size)
            
        # Create tooltip surface with padding
        padding = self.small_padding
        text_surface = font.render(text, True, self.text_color)
        tooltip_width = text_surface.get_width() + padding * 2
        tooltip_height = text_surface.get_height() + padding * 2
        
        # Position tooltip near the rect but ensure it stays on screen
        screen_width, screen_height = surface.get_size()
        tooltip_x = min(rect.right, screen_width - tooltip_width)
        tooltip_y = rect.bottom + 5  # 5px below the rect
        
        # If tooltip would go off the bottom, position it above the rect
        if tooltip_y + tooltip_height > screen_height:
            tooltip_y = rect.top - tooltip_height - 5  # 5px above the rect
        
        tooltip_rect = pygame.Rect(tooltip_x, tooltip_y, tooltip_width, tooltip_height)
        
        # Draw tooltip background
        self.draw_panel(surface, tooltip_rect)
        
        # Draw text
        surface.blit(text_surface, (tooltip_x + padding, tooltip_y + padding))
        
        return tooltip_rect
    
    def draw_scrollbar(self, surface, rect, scroll_position, content_size, viewport_size):
        """
        Draw a scrollbar representing the current scroll position.
        
        Args:
            surface (pygame.Surface): Surface to render on
            rect (pygame.Rect): Rectangle for scrollbar
            scroll_position (float): Current scroll position (0.0 to 1.0)
            content_size (float): Total size of scrollable content
            viewport_size (float): Size of visible viewport
            
        Returns:
            pygame.Rect: Rectangle of the scrollbar thumb
        """
        # Draw track
        pygame.draw.rect(
            surface,
            (50, 50, 70),
            rect,
            border_radius=self.border_radius
        )
        
        # Calculate thumb size and position
        visible_ratio = min(1.0, viewport_size / content_size)
        thumb_size = max(20, int(rect.height * visible_ratio))
        
        max_scroll = content_size - viewport_size
        scroll_ratio = 0 if max_scroll <= 0 else scroll_position / max_scroll
        
        # Limit scroll_ratio to 0.0-1.0 range
        scroll_ratio = max(0.0, min(1.0, scroll_ratio))
        
        # Calculate thumb position
        thumb_pos = int(scroll_ratio * (rect.height - thumb_size))
        
        # Draw thumb
        thumb_rect = pygame.Rect(
            rect.x,
            rect.y + thumb_pos,
            rect.width,
            thumb_size
        )
        
        pygame.draw.rect(
            surface,
            self.highlight_color,
            thumb_rect,
            border_radius=self.border_radius
        )
        
        return thumb_rect