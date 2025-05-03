# src/core/EventSystem.py
"""
Enhanced Event System for A Sound of Distant Thunder.
Provides a robust publish/subscribe event mechanism with priority support.
"""
import logging
import time
import threading
from collections import defaultdict

logger = logging.getLogger("EventSystem")

class EventSystem:
    """
    Event system using publish/subscribe pattern.
    Supports event priorities and wildcard subscriptions.
    """
    
    # Priority levels
    PRIORITY_HIGH = 0
    PRIORITY_NORMAL = 1
    PRIORITY_LOW = 2
    
    def __init__(self):
        """Initialize the event system."""
        # Dictionary of event types to lists of subscribers
        # Key: event_type, Value: list of (callback, priority) tuples
        self.listeners = defaultdict(list)
        
        # Wildcard listeners that receive all events
        self.wildcard_listeners = []
        
        # Mutex for thread safety
        self.mutex = threading.RLock()
        
        # Event statistics
        self.stats = {
            "events_emitted": 0,
            "subscriptions": 0,
            "most_frequent_events": defaultdict(int)
        }
        
        logger.info("EventSystem initialized")
    
    def subscribe(self, event_type, callback, priority=PRIORITY_NORMAL):
        """
        Subscribe to an event type.
        
        Args:
            event_type (str): Event type to subscribe to or "*" for all events
            callback (callable): Function to call when event is emitted
            priority (int): Subscription priority (lower numbers = higher priority)
            
        Returns:
            bool: True if subscription successful
        """
        if not callable(callback):
            logger.error(f"Callback must be callable: {callback}")
            return False
        
        with self.mutex:
            if event_type == "*":
                # Wildcard subscription
                if (callback, priority) not in self.wildcard_listeners:
                    self.wildcard_listeners.append((callback, priority))
                    self.wildcard_listeners.sort(key=lambda x: x[1])  # Sort by priority
                    
                    self.stats["subscriptions"] += 1
                    logger.debug(f"Subscribed to all events with priority {priority}")
                return True
            else:
                # Normal subscription
                if (callback, priority) not in self.listeners[event_type]:
                    self.listeners[event_type].append((callback, priority))
                    self.listeners[event_type].sort(key=lambda x: x[1])  # Sort by priority
                    
                    self.stats["subscriptions"] += 1
                    logger.debug(f"Subscribed to event: {event_type} with priority {priority}")
                return True
    
    def unsubscribe(self, event_type, callback):
        """
        Unsubscribe from an event type.
        
        Args:
            event_type (str): Event type to unsubscribe from or "*" for all events
            callback (callable): Function to unsubscribe
            
        Returns:
            bool: True if unsubscription successful
        """
        with self.mutex:
            if event_type == "*":
                # Wildcard unsubscription
                for i, (cb, _) in enumerate(self.wildcard_listeners):
                    if cb == callback:
                        del self.wildcard_listeners[i]
                        
                        self.stats["subscriptions"] -= 1
                        logger.debug(f"Unsubscribed from all events")
                        return True
            else:
                # Normal unsubscription
                for i, (cb, _) in enumerate(self.listeners[event_type]):
                    if cb == callback:
                        del self.listeners[event_type][i]
                        
                        self.stats["subscriptions"] -= 1
                        logger.debug(f"Unsubscribed from event: {event_type}")
                        return True
            
            return False
    
    def unsubscribe_all(self, callback):
        """
        Unsubscribe a callback from all event types.
        
        Args:
            callback (callable): Function to unsubscribe
            
        Returns:
            int: Number of unsubscriptions
        """
        count = 0
        
        with self.mutex:
            # Remove from wildcard listeners
            for i, (cb, _) in enumerate(self.wildcard_listeners):
                if cb == callback:
                    del self.wildcard_listeners[i]
                    count += 1
            
            # Remove from normal listeners
            for event_type in list(self.listeners.keys()):
                for i, (cb, _) in enumerate(self.listeners[event_type]):
                    if cb == callback:
                        del self.listeners[event_type][i]
                        count += 1
        
        self.stats["subscriptions"] -= count
        logger.debug(f"Unsubscribed from {count} events")
        return count
    
    def emit(self, event_type, data=None):
        """
        Emit an event to all listeners.
        
        Args:
            event_type (str): Type of event to emit
            data (dict, optional): Event data
        """
        if data is None:
            data = {}
        
        # Add event type to data for convenience
        data["event_type"] = event_type
        
        start_time = time.time()
        
        with self.mutex:
            # Update statistics
            self.stats["events_emitted"] += 1
            self.stats["most_frequent_events"][event_type] += 1
            
            # Call specific listeners
            if event_type in self.listeners:
                for callback, _ in self.listeners[event_type]:
                    try:
                        callback(data)
                    except Exception as e:
                        logger.error(f"Error in event handler for {event_type}: {e}")
            
            # Call wildcard listeners
            for callback, _ in self.wildcard_listeners:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error in wildcard handler for {event_type}: {e}")
        
        # Log slow event handling
        duration = time.time() - start_time
        if duration > 0.1:  # Log if handling takes more than 100ms
            logger.warning(f"Slow event handling for {event_type}: {duration:.3f}s")
        
        logger.debug(f"Emitted event: {event_type}")
    
    def emit_delayed(self, event_type, data=None, delay=1.0):
        """
        Emit an event after a delay.
        
        Args:
            event_type (str): Type of event to emit
            data (dict, optional): Event data
            delay (float): Delay in seconds
        """
        if delay <= 0:
            self.emit(event_type, data)
            return
        
        def delayed_emit():
            time.sleep(delay)
            self.emit(event_type, data)
        
        threading.Thread(target=delayed_emit).start()
        logger.debug(f"Scheduled delayed event: {event_type} in {delay}s")
    
    def get_stats(self):
        """
        Get event system statistics.
        
        Returns:
            dict: Event system statistics
        """
        with self.mutex:
            stats = self.stats.copy()
            stats["listener_count"] = len(self.wildcard_listeners)
            
            for event_type in self.listeners:
                stats["listener_count"] += len(self.listeners[event_type])
            
            # Get top 5 most frequent events
            top_events = sorted(
                stats["most_frequent_events"].items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            stats["top_events"] = dict(top_events)
            
            return stats
    
    def has_listeners(self, event_type):
        """
        Check if an event type has listeners.
        
        Args:
            event_type (str): Event type to check
            
        Returns:
            bool: True if event type has listeners, False otherwise
        """
        with self.mutex:
            return event_type in self.listeners and len(self.listeners[event_type]) > 0
    
    def clear(self):
        """Clear all listeners."""
        with self.mutex:
            self.listeners.clear()
            self.wildcard_listeners.clear()
            logger.info("EventSystem cleared")