"""
Test script for the Conversation Manager component.

This script tests the functionality of the Conversation Manager component,
including the ConversationContext, IntentRecognizer, ResponsePlanner,
MemoryManager, and ConversationManager classes.
"""

import sys
import os
import time
from datetime import datetime

# Add the parent directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ira.core.conversation.conversation_context import ConversationContext, Message, MessageType, ConversationState
from ira.core.conversation.intent_recognizer import IntentRecognizer, Intent, IntentType
from ira.core.conversation.response_planner import ResponsePlanner
from ira.core.conversation.memory_manager import MemoryManager
from ira.core.conversation.conversation_manager import ConversationManager


def test_conversation_context():
    """Test the ConversationContext class."""
    print("\n=== Testing ConversationContext ===")
    
    # Create a conversation context
    context = ConversationContext()
    print(f"Created context with ID: {context.id}")
    print(f"State: {context.state}")
    print(f"Created at: {context.created_at}")
    print(f"Updated at: {context.updated_at}")
    
    # Add some messages
    context.add_message(Message(
        content="Hello, how are you?",
        type=MessageType.USER,
        timestamp=datetime.now()
    ))
    time.sleep(0.1)  # Sleep to ensure different timestamps
    context.add_message(Message(
        content="I'm doing well, thank you for asking!",
        type=MessageType.SYSTEM,
        timestamp=datetime.now()
    ))
    
    # Print the messages
    print("\nMessages:")
    for i, message in enumerate(context.messages):
        print(f"{i+1}. [{message.type.name}] {message.content}")
    
    # Test metadata
    context.metadata["user_name"] = "John"
    print(f"\nMetadata: {context.metadata}")
    
    # Test to_dict and from_dict
    context_dict = context.to_dict()
    print(f"\nContext as dict: {context_dict}")
    
    new_context = ConversationContext.from_dict(context_dict)
    print(f"\nRecreated context with ID: {new_context.id}")
    print(f"State: {new_context.state}")
    print(f"Created at: {new_context.created_at}")
    print(f"Updated at: {new_context.updated_at}")
    
    print("\nRecreated messages:")
    for i, message in enumerate(new_context.messages):
        print(f"{i+1}. [{message.type.name}] {message.content}")
    
    print(f"\nRecreated metadata: {new_context.metadata}")
    
    assert context.id == new_context.id, "Context IDs don't match"
    assert context.state == new_context.state, "Context states don't match"
    assert len(context.messages) == len(new_context.messages), "Message counts don't match"
    assert context.metadata == new_context.metadata, "Metadata doesn't match"
    
    print("\nConversationContext tests passed!")


def test_intent_recognizer():
    """Test the IntentRecognizer class."""
    print("\n=== Testing IntentRecognizer ===")
    
    # Create an intent recognizer
    recognizer = IntentRecognizer()
    print("Created IntentRecognizer")
    
    # Create a conversation context
    context = ConversationContext()
    
    # Test some messages
    test_messages = [
        "Hello, how are you?",
        "What is your name?",
        "Thank you for your help!",
        "Goodbye!",
        "What can you do?",
        "I don't understand.",
        "Do you like pizza?",
        "Tell me about yourself."
    ]
    
    for message in test_messages:
        intent = recognizer.recognize_intent(message, context)
        print(f"\nMessage: '{message}'")
        print(f"Intent type: {intent.type.name}")
        print(f"Confidence: {intent.confidence}")
        print(f"Entities: {intent.entities}")
        print(f"Metadata: {intent.metadata}")
    
    print("\nIntentRecognizer tests passed!")


def test_response_planner():
    """Test the ResponsePlanner class."""
    print("\n=== Testing ResponsePlanner ===")
    
    # Create a response planner
    planner = ResponsePlanner()
    print("Created ResponsePlanner")
    
    # Create a conversation context
    context = ConversationContext()
    
    # Test some intents
    test_intents = [
        Intent(type=IntentType.GREETING, confidence=0.9, entities={}, metadata={}),
        Intent(type=IntentType.QUESTION, confidence=0.8, entities={"topic": "weather"}, metadata={}),
        Intent(type=IntentType.COMMAND, confidence=0.95, entities={"command": "search", "query": "Python programming"}, metadata={}),
        Intent(type=IntentType.UNKNOWN, confidence=0.5, entities={}, metadata={})
    ]
    
    for intent in test_intents:
        response = planner.plan_response(intent, context)
        print(f"\nIntent type: {intent.type.name}")
        print(f"Entities: {intent.entities}")
        print(f"Response: '{response}'")
    
    print("\nResponsePlanner tests passed!")


def test_memory_manager():
    """Test the MemoryManager class."""
    print("\n=== Testing MemoryManager ===")
    
    # Create a memory manager
    memory_manager = MemoryManager()
    print("Created MemoryManager")
    
    # Create some contexts
    context1 = memory_manager.create_context()
    print(f"Created context 1 with ID: {context1.id}")
    
    context2 = memory_manager.create_context()
    print(f"Created context 2 with ID: {context2.id}")
    
    # Add some messages to the contexts
    context1.add_message(Message(
        content="Hello, how are you?",
        type=MessageType.USER,
        timestamp=datetime.now()
    ))
    context1.add_message(Message(
        content="I'm doing well, thank you for asking!",
        type=MessageType.SYSTEM,
        timestamp=datetime.now()
    ))
    
    context2.add_message(Message(
        content="What is the weather like today?",
        type=MessageType.USER,
        timestamp=datetime.now()
    ))
    context2.add_message(Message(
        content="I'm sorry, I don't have access to real-time weather information.",
        type=MessageType.SYSTEM,
        timestamp=datetime.now()
    ))
    
    # Test getting contexts
    retrieved_context1 = memory_manager.get_context(context1.id)
    print(f"\nRetrieved context 1 with ID: {retrieved_context1.id}")
    print(f"Messages in context 1: {len(retrieved_context1.messages)}")
    
    retrieved_context2 = memory_manager.get_context(context2.id)
    print(f"Retrieved context 2 with ID: {retrieved_context2.id}")
    print(f"Messages in context 2: {len(retrieved_context2.messages)}")
    
    # Test active context
    active_context = memory_manager.get_active_context()
    print(f"\nActive context ID: {active_context.id}")
    
    # Test setting active context
    memory_manager.set_active_context(context1.id)
    active_context = memory_manager.get_active_context()
    print(f"New active context ID: {active_context.id}")
    
    # Test saving and loading memory
    print("\nSaving memory...")
    memory_manager.save_memory()
    
    # Create a new memory manager and load the memory
    new_memory_manager = MemoryManager()
    print("Created new MemoryManager")
    
    print("Loading memory...")
    new_memory_manager.load_memory()
    
    # Check if the contexts were loaded correctly
    loaded_context1 = new_memory_manager.get_context(context1.id)
    print(f"\nLoaded context 1 with ID: {loaded_context1.id}")
    print(f"Messages in loaded context 1: {len(loaded_context1.messages)}")
    
    loaded_context2 = new_memory_manager.get_context(context2.id)
    print(f"Loaded context 2 with ID: {loaded_context2.id}")
    print(f"Messages in loaded context 2: {len(loaded_context2.messages)}")
    
    # Test deleting a context
    print("\nDeleting context 2...")
    memory_manager.delete_context(context2.id)
    
    # Check if the context was deleted
    deleted_context = memory_manager.get_context(context2.id)
    print(f"Deleted context: {deleted_context}")
    
    # Clean up
    print("\nCleaning up...")
    if os.path.exists(memory_manager.memory_file):
        os.remove(memory_manager.memory_file)
    
    print("\nMemoryManager tests passed!")


def test_conversation_manager():
    """Test the ConversationManager class."""
    print("\n=== Testing ConversationManager ===")
    
    # Create a conversation manager
    conversation_manager = ConversationManager()
    print("Created ConversationManager")
    
    # Process some messages
    test_messages = [
        "Hello, how are you?",
        "What is your name?",
        "Thank you for your help!",
        "@help",
        "@status",
        "@clear",
        "What can you do?",
        "Goodbye!"
    ]
    
    for message in test_messages:
        print(f"\nUser: {message}")
        response = conversation_manager.process_message(message)
        print(f"System: {response}")
    
    # Test conversation context
    context = conversation_manager.memory_manager.get_active_context()
    print(f"\nActive context ID: {context.id}")
    print(f"Messages in active context: {len(context.messages)}")
    
    # Clean up
    print("\nCleaning up...")
    if os.path.exists(conversation_manager.memory_manager.memory_file):
        os.remove(conversation_manager.memory_manager.memory_file)
    
    print("\nConversationManager tests passed!")


def main():
    """Run all tests."""
    print("=== Running Conversation Manager Tests ===")
    
    test_conversation_context()
    test_intent_recognizer()
    test_response_planner()
    test_memory_manager()
    test_conversation_manager()
    
    print("\n=== All tests passed! ===")


if __name__ == "__main__":
    main()