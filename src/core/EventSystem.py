class EventSystem:
    """
    Event system for decoupling components through publish/subscribe pattern.
    """
    def __init__(self):
        self.listeners = {}
        self.logger = logging.getLogger("EventSystem")
        
    def subscribe(self, event_type, callback):
        """
        Subscribe to an event type.
        
        Args:
            event_type (str): Event type to subscribe to
            callback (callable): Function to call when event is emitted
        """
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        
        if callback not in self.listeners[event_type]:
            self.listeners[event_type].append(callback)
            self.logger.debug(f"Subscribed to event: {event_type}")
        
    def unsubscribe(self, event_type, callback):
        """
        Unsubscribe from an event type.
        
        Args:
            event_type (str): Event type to unsubscribe from
            callback (callable): Function to unsubscribe
        """
        if event_type in self.listeners and callback in self.listeners[event_type]:
            self.listeners[event_type].remove(callback)
            self.logger.debug(f"Unsubscribed from event: {event_type}")
            
    def emit(self, event_type, data=None):
        """
        Emit an event to all listeners.
        
        Args:
            event_type (str): Type of event to emit
            data (dict, optional): Event data
        """
        self.logger.debug(f"Emitting event: {event_type}")
        
        if event_type in self.listeners:
            # Create a copy of listeners to allow modifications during iteration
            for callback in list(self.listeners[event_type]):
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(f"Error in event handler for {event_type}: {e}")