"""
MemoryManager module for the Conversation Manager.

This module defines the MemoryManager class, which manages the memory
of the conversation system in the IRA (Ideom Resolver AI) architecture.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Set, Tuple
import json
import os
from datetime import datetime
from .conversation_context import ConversationContext, Message, MessageType, ConversationState


@dataclass
class MemoryManager:
    """
    Manages the memory of the conversation system.
    
    The MemoryManager class is responsible for storing and retrieving
    conversation contexts and other relevant information.
    
    Attributes:
        contexts: A dictionary mapping conversation IDs to ConversationContext instances.
        active_context_id: The ID of the currently active conversation context.
        memory_file: The path to the file where memory is stored.
        max_contexts: The maximum number of conversation contexts to keep in memory.
    """
    
    contexts: Dict[str, ConversationContext] = field(default_factory=dict)
    active_context_id: Optional[str] = None
    memory_file: str = "conversation_memory.json"
    max_contexts: int = 100
    
    def create_context(self) -> ConversationContext:
        """
        Create a new conversation context.
        
        Returns:
            The new ConversationContext instance.
        """
        context = ConversationContext()
        self.contexts[context.id] = context
        self.active_context_id = context.id
        
        # If we have too many contexts, remove the oldest ones
        if len(self.contexts) > self.max_contexts:
            self._prune_contexts()
        
        return context
    
    def get_context(self, context_id: str) -> Optional[ConversationContext]:
        """
        Get a conversation context by ID.
        
        Args:
            context_id: The ID of the conversation context.
            
        Returns:
            The ConversationContext instance, or None if it doesn't exist.
        """
        return self.contexts.get(context_id)
    
    def get_active_context(self) -> Optional[ConversationContext]:
        """
        Get the currently active conversation context.
        
        Returns:
            The active ConversationContext instance, or None if there is no active context.
        """
        if self.active_context_id is None:
            return None
        return self.get_context(self.active_context_id)
    
    def set_active_context(self, context_id: str) -> bool:
        """
        Set the active conversation context.
        
        Args:
            context_id: The ID of the conversation context to set as active.
            
        Returns:
            True if the context was set as active, False if it doesn't exist.
        """
        if context_id not in self.contexts:
            return False
        self.active_context_id = context_id
        return True
    
    def delete_context(self, context_id: str) -> bool:
        """
        Delete a conversation context.
        
        Args:
            context_id: The ID of the conversation context to delete.
            
        Returns:
            True if the context was deleted, False if it doesn't exist.
        """
        if context_id not in self.contexts:
            return False
        
        del self.contexts[context_id]
        
        if self.active_context_id == context_id:
            self.active_context_id = None
        
        return True
    
    def _prune_contexts(self) -> None:
        """
        Remove the oldest conversation contexts to stay within the maximum limit.
        """
        # Sort contexts by updated_at timestamp
        sorted_contexts = sorted(
            self.contexts.items(),
            key=lambda x: x[1].updated_at
        )
        
        # Keep only the most recent max_contexts contexts
        contexts_to_keep = sorted_contexts[-self.max_contexts:]
        
        # Update the contexts dictionary
        self.contexts = {context_id: context for context_id, context in contexts_to_keep}
        
        # If the active context was pruned, set active_context_id to None
        if self.active_context_id not in self.contexts:
            self.active_context_id = None
    
    def save_memory(self) -> bool:
        """
        Save the memory to a file.
        
        Returns:
            True if the memory was saved successfully, False otherwise.
        """
        try:
            memory_data = {
                "active_context_id": self.active_context_id,
                "contexts": {
                    context_id: context.to_dict()
                    for context_id, context in self.contexts.items()
                }
            }
            
            with open(self.memory_file, "w") as f:
                json.dump(memory_data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving memory: {e}")
            return False
    
    def load_memory(self) -> bool:
        """
        Load the memory from a file.
        
        Returns:
            True if the memory was loaded successfully, False otherwise.
        """
        if not os.path.exists(self.memory_file):
            return False
        
        try:
            with open(self.memory_file, "r") as f:
                memory_data = json.load(f)
            
            self.active_context_id = memory_data.get("active_context_id")
            
            self.contexts = {}
            for context_id, context_data in memory_data.get("contexts", {}).items():
                self.contexts[context_id] = ConversationContext.from_dict(context_data)
            
            return True
        except Exception as e:
            print(f"Error loading memory: {e}")
            return False
    
    def get_all_contexts(self) -> List[ConversationContext]:
        """
        Get all conversation contexts.
        
        Returns:
            A list of all ConversationContext instances.
        """
        return list(self.contexts.values())
    
    def get_contexts_by_state(self, state: ConversationState) -> List[ConversationContext]:
        """
        Get conversation contexts by state.
        
        Args:
            state: The state to filter by.
            
        Returns:
            A list of ConversationContext instances with the specified state.
        """
        return [
            context for context in self.contexts.values()
            if context.state == state
        ]
    
    def search_contexts(self, query: str) -> List[Tuple[ConversationContext, float]]:
        """
        Search for conversation contexts containing the query.
        
        Args:
            query: The query to search for.
            
        Returns:
            A list of tuples, where each tuple contains a ConversationContext instance
            and a relevance score.
        """
        query = query.lower()
        results = []
        
        for context in self.contexts.values():
            relevance = 0.0
            
            # Check messages for the query
            for message in context.messages:
                if query in message.content.lower():
                    # Increase relevance based on the number of occurrences
                    relevance += message.content.lower().count(query) * 0.1
                    
                    # Increase relevance if the query is in a user message
                    if message.type == MessageType.USER:
                        relevance += 0.2
            
            # Check metadata for the query
            for key, value in context.metadata.items():
                if isinstance(value, str) and query in value.lower():
                    relevance += 0.3
            
            if relevance > 0.0:
                results.append((context, relevance))
        
        # Sort results by relevance score in descending order
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results
    
    def get_context_summary(self, context_id: str) -> Optional[str]:
        """
        Get a summary of a conversation context.
        
        Args:
            context_id: The ID of the conversation context.
            
        Returns:
            A summary of the conversation context, or None if it doesn't exist.
        """
        context = self.get_context(context_id)
        if context is None:
            return None
        
        # Get the first few messages
        first_messages = context.messages[:3]
        
        # Get the last few messages
        last_messages = context.messages[-3:]
        
        # Create a summary
        summary = f"Conversation {context_id}\n"
        summary += f"State: {context.state.name}\n"
        summary += f"Created: {context.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        summary += f"Updated: {context.updated_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
        summary += f"Messages: {len(context.messages)}\n\n"
        
        if first_messages:
            summary += "First messages:\n"
            for message in first_messages:
                summary += f"[{message.type.name}] {message.content[:50]}{'...' if len(message.content) > 50 else ''}\n"
            summary += "\n"
        
        if last_messages and last_messages != first_messages:
            summary += "Last messages:\n"
            for message in last_messages:
                summary += f"[{message.type.name}] {message.content[:50]}{'...' if len(message.content) > 50 else ''}\n"
        
        return summary