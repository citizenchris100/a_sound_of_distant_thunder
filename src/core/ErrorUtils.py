# src/core/ErrorUtils.py
"""
Error handling utilities for A Sound of Distant Thunder.
Provides consistent error management across all systems.
"""
import logging
import traceback
import sys

logger = logging.getLogger("ErrorUtils")

class ErrorHandler:
    """Centralized error handling system."""
    
    def __init__(self, event_system=None, message_manager=None):
        """
        Initialize error handler.
        
        Args:
            event_system: Optional EventSystem instance for emitting error events
            message_manager: Optional MessageManager instance for displaying error messages
        """
        self.event_system = event_system
        self.message_manager = message_manager
        self.error_count = 0
        self.last_error = None
    
    def handle_error(self, error, context=None, show_to_user=False):
        """
        Handle an error.
        
        Args:
            error (Exception): Error to handle
            context (str, optional): Context information
            show_to_user (bool): Whether to show error to user
            
        Returns:
            int: Error ID
        """
        # Generate error ID
        error_id = self.error_count
        self.error_count += 1
        
        # Get error details
        error_type = type(error).__name__
        error_message = str(error)
        error_traceback = traceback.format_exc()
        
        # Context string
        context_str = f" in {context}" if context else ""
        
        # Log error
        logger.error(f"Error {error_id}{context_str}: {error_type}: {error_message}\n{error_traceback}")
        
        # Store error
        self.last_error = {
            "id": error_id,
            "type": error_type,
            "message": error_message,
            "traceback": error_traceback,
            "context": context
        }
        
        # Emit error event
        if self.event_system:
            self.event_system.emit("error_occurred", {
                "error_id": error_id,
                "error_type": error_type,
                "error_message": error_message,
                "context": context
            })
        
        # Show error to user if requested
        if show_to_user and self.message_manager:
            user_message = f"Error: {error_message}"
            if context:
                user_message = f"Error in {context}: {error_message}"
                
            self.message_manager.show_error(user_message)
        
        return error_id
    
    def try_execute(self, func, args=None, kwargs=None, context=None, show_to_user=False):
        """
        Try to execute a function and handle any errors.
        
        Args:
            func (callable): Function to execute
            args (list, optional): Arguments for function
            kwargs (dict, optional): Keyword arguments for function
            context (str, optional): Context information
            show_to_user (bool): Whether to show error to user
            
        Returns:
            tuple: (result, error_id or None)
        """
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        
        try:
            result = func(*args, **kwargs)
            return result, None
        except Exception as e:
            error_id = self.handle_error(e, context, show_to_user)
            return None, error_id
    
    def assert_condition(self, condition, message, context=None, show_to_user=False):
        """
        Assert a condition, handle error if condition is false.
        
        Args:
            condition (bool): Condition to assert
            message (str): Error message if condition is false
            context (str, optional): Context information
            show_to_user (bool): Whether to show error to user
            
        Returns:
            bool: True if assertion passed, False otherwise
        """
        if condition:
            return True
        
        error = AssertionError(message)
        self.handle_error(error, context, show_to_user)
        return False