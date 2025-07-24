#!/usr/bin/env python3
"""
Test script for the IRA chat interface.

This script tests the IRA chat interface with various inputs to verify that
the fixes we've made are working correctly.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ira.chat_interface import IRAChatInterface

def test_chat_interface():
    """Test the IRA chat interface with various inputs."""
    print("Creating chat interface...")
    chat_interface = IRAChatInterface()
    
    # Test conversational phrases
    print("\n=== Testing conversational phrases ===")
    test_inputs = [
        "hi",
        "hello",
        "how are you",
        "who are you",
        "what can you do",
        "can you talk"
    ]
    
    for input_text in test_inputs:
        print(f"\nTesting input: '{input_text}'")
        chat_interface.default(input_text)
    
    # Test concept queries
    print("\n=== Testing concept queries ===")
    test_inputs = [
        "what is a lion?",
        "what is a dog?",
        "what is a cat?",
        "what is a golden retriever?",
        "what is a computer?",
        "what is Python?"
    ]
    
    for input_text in test_inputs:
        print(f"\nTesting input: '{input_text}'")
        chat_interface.default(input_text)
    
    # Test unknown concept queries
    print("\n=== Testing unknown concept queries ===")
    test_inputs = [
        "what is a unicorn?",
        "what is a dragon?",
        "what is quantum physics?"
    ]
    
    for input_text in test_inputs:
        print(f"\nTesting input: '{input_text}'")
        chat_interface.default(input_text)
    
    # Test teaching the system
    print("\n=== Testing teaching the system ===")
    test_inputs = [
        "a unicorn is a mythical creature",
        "unicorns have a horn on their forehead",
        "unicorns are magical beings"
    ]
    
    for input_text in test_inputs:
        print(f"\nTesting input: '{input_text}'")
        chat_interface.default(input_text)
    
    # Test querying the newly taught concept
    print("\n=== Testing querying the newly taught concept ===")
    chat_interface.default("what is a unicorn?")
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    test_chat_interface()