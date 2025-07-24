"""
Context tracking for multi-turn conversations.

This module provides functionality for tracking conversation history,
resolving references, and maintaining conversation state.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Message:
    """Represents a single message in the conversation."""
    text: str
    sender: str  # "user" or "system"
    timestamp: datetime = field(default_factory=datetime.now)
    entities: List[Dict[str, Any]] = field(default_factory=list)


class ContextTracker:
    """
    Tracks conversation context including message history and referenced entities.
    
    This class is responsible for:
    - Maintaining a history of messages
    - Tracking entities mentioned in the conversation
    - Resolving references (like pronouns) to entities
    - Providing context for the current conversation turn
    """
    
    def __init__(self, max_history: int = 10):
        """
        Initialize the context tracker.
        
        Args:
            max_history: Maximum number of messages to keep in history
        """
        self.messages: List[Message] = []
        self.max_history = max_history
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.current_focus: Optional[str] = None
    
    def add_user_message(self, text: str) -> None:
        """
        Add a user message to the conversation history.
        
        Args:
            text: The text of the user message
        """
        message = Message(text=text, sender="user")
        self._add_message(message)
    
    def add_system_message(self, text: str) -> None:
        """
        Add a system message to the conversation history.
        
        Args:
            text: The text of the system message
        """
        message = Message(text=text, sender="system")
        self._add_message(message)
    
    def _add_message(self, message: Message) -> None:
        """
        Add a message to the history and trim if necessary.
        
        Args:
            message: The message to add
        """
        self.messages.append(message)
        if len(self.messages) > self.max_history:
            self.messages.pop(0)
    
    def add_entity(self, entity_id: str, entity_data: Dict[str, Any]) -> None:
        """
        Add or update an entity in the context.
        
        Args:
            entity_id: Unique identifier for the entity
            entity_data: Data associated with the entity
        """
        self.entities[entity_id] = entity_data
        # Set as current focus when a new entity is added
        self.current_focus = entity_id
    
    def get_last_n_messages(self, n: int) -> List[Message]:
        """
        Get the last n messages from the conversation history.
        
        Args:
            n: Number of messages to retrieve
            
        Returns:
            List of the last n messages
        """
        return self.messages[-n:] if n <= len(self.messages) else self.messages[:]
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an entity by its ID.
        
        Args:
            entity_id: The ID of the entity to retrieve
            
        Returns:
            The entity data or None if not found
        """
        return self.entities.get(entity_id)
    
    def get_current_focus(self) -> Optional[Dict[str, Any]]:
        """
        Get the entity that is currently in focus.
        
        Returns:
            The entity data for the current focus or None
        """
        if self.current_focus:
            return self.entities.get(self.current_focus)
        return None
    
    def resolve_reference(self, reference: str) -> Optional[str]:
        """
        Resolve a reference (like a pronoun) to an entity ID.
        
        Args:
            reference: The reference to resolve (e.g., "it", "they")
            
        Returns:
            The entity ID or None if the reference couldn't be resolved
        """
        # Simple implementation - just return the current focus
        # A more sophisticated implementation would use NLP to resolve references
        if reference.lower() in ["it", "this", "that"]:
            return self.current_focus
        return None
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current conversation state.
        
        Returns:
            A dictionary containing conversation summary information
        """
        return {
            "message_count": len(self.messages),
            "entities": list(self.entities.keys()),
            "current_focus": self.current_focus,
            "last_user_message": next((m.text for m in reversed(self.messages) 
                                      if m.sender == "user"), None),
            "last_system_message": next((m.text for m in reversed(self.messages) 
                                        if m.sender == "system"), None),
        }