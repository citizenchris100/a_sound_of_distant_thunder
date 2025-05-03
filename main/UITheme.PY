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
        
        # Text properties
        self.title_font_size = 24
        self.heading_font_size = 20
        self.body_font_size = 16
        self.small_font_size = 14
        
        # Layout properties
        self.padding = 10
        self.border_width = 2
        self.border_radius = 5
        self.button_height = 30
        
    def draw_panel(self, surface, rect, with_border=True):
        """
        Draw a UI panel with the theme's styling.
        
        Args:
            surface (pygame.Surface): Surface to render on
            rect (pygame.Rect): Rectangle defining panel position and size
            with_border (bool): Whether to draw a border
        """
        # Create a rounded rect surface with transparency
        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        
        # Fill with background color
        pygame.draw.rect(
            panel,
            self.background_color,
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
                   is_disabled=False):
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
        
        # Render text
        text_surface = font.render(text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(rect.width // 2, rect.height // 2))
        button.blit(text_surface, text_rect)
        
        # Blit to target surface
        surface.blit(button, rect)
    
    def draw_text(self, surface, text, font, position, align="left", max_width=None):
        """
        Draw themed text with optional alignment and wrapping.
        
        Args:
            surface (pygame.Surface): Surface to render on
            text (str): Text to render
            font (pygame.font.Font): Font to use for the text
            position (tuple): Position (x, y) for the text
            align (str): Text alignment - "left", "center", or "right"
            max_width (int, optional): Maximum width for text wrapping
        """
        if not text:
            return

        x, y = position
        
        if max_width:
            # Word wrapping
            words = text.split(' ')
            space_width = font.size(' ')[0]
            current_x = x
            current_y = y
            
            for word in words:
                word_surface = font.render(word, True, self.text_color)
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
        else:
            # Simple text rendering without wrapping
            text_surface = font.render(text, True, self.text_color)
            text_rect = text_surface.get_rect()
            
            if align == "center":
                text_rect.midtop = (x, y)
            elif align == "right":
                text_rect.topright = (x, y)
            else:  # left
                text_rect.topleft = (x, y)
                
            surface.blit(text_surface, text_rect)
    
    def draw_progress_bar(self, surface, rect, value, max_value=100, color=None):
        """
        Draw a themed progress bar.
        
        Args:
            surface (pygame.Surface): Surface to render on
            rect (pygame.Rect): Rectangle defining bar position and size
            value (float): Current value
            max_value (float): Maximum value (100% full)
            color (tuple, optional): Bar color, or None to use theme highlight color
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
        
        # Blit to target surface
        surface.blit(bar, rect)