"""
ConversationContext module for the Conversation Manager.

This module defines the ConversationContext class, which maintains the context
of a conversation in the IRA (Ideom Resolver AI) architecture.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum, auto
import uuid


class MessageType(Enum):
    """
    Enum for message types.
    """
    USER = auto()
    SYSTEM = auto()


@dataclass
class Message:
    """
    A message in a conversation.
    
    Attributes:
        id: A unique identifier for the message.
        content: The content of the message.
        type: The type of the message (user or system).
        timestamp: The time the message was created.
        metadata: Additional metadata for the message.
    """
    
    id: str
    content: str
    type: MessageType
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def create_user_message(cls, content: str, metadata: Optional[Dict[str, Any]] = None) -> 'Message':
        """
        Create a user message.
        
        Args:
            content: The content of the message.
            metadata: Additional metadata for the message.
            
        Returns:
            A new Message instance.
        """
        return cls(
            id=str(uuid.uuid4()),
            content=content,
            type=MessageType.USER,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
    
    @classmethod
    def create_system_message(cls, content: str, metadata: Optional[Dict[str, Any]] = None) -> 'Message':
        """
        Create a system message.
        
        Args:
            content: The content of the message.
            metadata: Additional metadata for the message.
            
        Returns:
            A new Message instance.
        """
        return cls(
            id=str(uuid.uuid4()),
            content=content,
            type=MessageType.SYSTEM,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )


class ConversationState(Enum):
    """
    Enum for conversation states.
    """
    ACTIVE = auto()
    IDLE = auto()
    ENDED = auto()


@dataclass
class ConversationContext:
    """
    Maintains the context of a conversation.
    
    The ConversationContext class maintains the context of a conversation,
    including the history of messages, the current state, and any relevant information.
    
    Attributes:
        id: A unique identifier for the conversation.
        messages: A list of messages in the conversation.
        state: The current state of the conversation.
        metadata: Additional metadata for the conversation.
        created_at: The time the conversation was created.
        updated_at: The time the conversation was last updated.
    """
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    messages: List[Message] = field(default_factory=list)
    state: ConversationState = ConversationState.ACTIVE
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_user_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        """
        Add a user message to the conversation.
        
        Args:
            content: The content of the message.
            metadata: Additional metadata for the message.
            
        Returns:
            The added message.
        """
        message = Message.create_user_message(content, metadata)
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def add_system_message(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Message:
        """
        Add a system message to the conversation.
        
        Args:
            content: The content of the message.
            metadata: Additional metadata for the message.
            
        Returns:
            The added message.
        """
        message = Message.create_system_message(content, metadata)
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def add_message(self, message: Message) -> Message:
        """
        Add a message to the conversation.
        
        Args:
            message: The message to add.
            
        Returns:
            The added message.
        """
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def get_messages(self, count: Optional[int] = None) -> List[Message]:
        """
        Get the messages in the conversation.
        
        Args:
            count: The number of messages to get, or None to get all messages.
            
        Returns:
            A list of messages.
        """
        if count is None:
            return self.messages.copy()
        return self.messages[-count:].copy()
    
    def get_last_message(self) -> Optional[Message]:
        """
        Get the last message in the conversation.
        
        Returns:
            The last message, or None if there are no messages.
        """
        if not self.messages:
            return None
        return self.messages[-1]
    
    def get_last_user_message(self) -> Optional[Message]:
        """
        Get the last user message in the conversation.
        
        Returns:
            The last user message, or None if there are no user messages.
        """
        for message in reversed(self.messages):
            if message.type == MessageType.USER:
                return message
        return None
    
    def get_last_system_message(self) -> Optional[Message]:
        """
        Get the last system message in the conversation.
        
        Returns:
            The last system message, or None if there are no system messages.
        """
        for message in reversed(self.messages):
            if message.type == MessageType.SYSTEM:
                return message
        return None
    
    def set_state(self, state: ConversationState) -> None:
        """
        Set the state of the conversation.
        
        Args:
            state: The new state.
        """
        self.state = state
        self.updated_at = datetime.now()
    
    def set_metadata(self, key: str, value: Any) -> None:
        """
        Set a metadata value.
        
        Args:
            key: The metadata key.
            value: The metadata value.
        """
        self.metadata[key] = value
        self.updated_at = datetime.now()
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Get a metadata value.
        
        Args:
            key: The metadata key.
            default: The default value to return if the key doesn't exist.
            
        Returns:
            The metadata value, or the default value if the key doesn't exist.
        """
        return self.metadata.get(key, default)
    
    def clear_messages(self) -> None:
        """
        Clear all messages from the conversation.
        """
        self.messages.clear()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to a dictionary.
        
        Returns:
            A dictionary representation of the conversation context.
        """
        return {
            "id": self.id,
            "messages": [
                {
                    "id": message.id,
                    "content": message.content,
                    "type": message.type.name,
                    "timestamp": message.timestamp.isoformat(),
                    "metadata": message.metadata
                }
                for message in self.messages
            ],
            "state": self.state.name,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationContext':
        """
        Create a ConversationContext instance from a dictionary.
        
        Args:
            data: A dictionary representation of a conversation context.
            
        Returns:
            A new ConversationContext instance.
        """
        context = cls(
            id=data["id"],
            state=ConversationState[data["state"]],
            metadata=data["metadata"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
        
        for message_data in data["messages"]:
            message = Message(
                id=message_data["id"],
                content=message_data["content"],
                type=MessageType[message_data["type"]],
                timestamp=datetime.fromisoformat(message_data["timestamp"]),
                metadata=message_data["metadata"]
            )
            context.messages.append(message)
        
        return context