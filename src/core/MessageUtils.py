# src/core/MessageUtils.py
"""
Unified message handling utilities for A Sound of Distant Thunder.
Provides consistent message display functionality across all systems.
"""
import logging

logger = logging.getLogger("MessageUtils")

class MessageManager:
    """Centralized message handling system."""
    
    def __init__(self, event_system):
        """
        Initialize the message manager.
        
        Args:
            event_system: EventSystem instance for emitting events
        """
        self.event_system = event_system
    
    def show_message(self, text, message_type="message", auto_hide=True, auto_hide_delay=5.0):
        """
        Show a message to the player.
        
        Args:
            text (str): Message text to display
            message_type (str): Type of message (e.g., "message", "description", "warning")
            auto_hide (bool): Whether to automatically hide the message after a delay
            auto_hide_delay (float): Delay in seconds before hiding the message
        """
        if not text:
            return
            
        self.event_system.emit("message_displayed", {
            "text": text,
            "type": message_type,
            "auto_hide": auto_hide,
            "auto_hide_delay": auto_hide_delay
        })
        
        logger.debug(f"Message ({message_type}): {text}")
    
    def show_description(self, text):
        """
        Show an object or NPC description.
        
        Args:
            text (str): Description text to display
        """
        if not text:
            return
            
        self.event_system.emit("description_displayed", {
            "text": text
        })
        
        logger.debug(f"Description displayed: {text[:30]}...")
    
    def show_warning(self, text):
        """
        Show a warning message.
        
        Args:
            text (str): Warning message to display
        """
        self.show_message(text, message_type="warning", auto_hide_delay=7.0)
    
    def show_error(self, text):
        """
        Show an error message.
        
        Args:
            text (str): Error message to display
        """
        self.show_message(text, message_type="error", auto_hide_delay=10.0)