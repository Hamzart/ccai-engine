#!/usr/bin/env python3
"""
Test script for the IRA system.
"""

import sys
import os
import nltk

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    print("Downloading punkt tokenizer...")
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    print("Downloading punkt_tab tokenizer...")
    # The punkt_tab resource is part of the 'all' package
    nltk.download('all')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("Downloading stopwords...")
    nltk.download('stopwords')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    print("Downloading wordnet...")
    nltk.download('wordnet')

# Ensure punkt is properly downloaded
if not nltk.download('punkt', quiet=True):
    print("Warning: Failed to download punkt tokenizer. Some functionality may not work.")

from ira.core.ira_system import IRASystem
from ira.core.knowledge.knowledge_graph import KnowledgeGraph
from ira.core.reasoning.ideom_network import IdeomNetwork
from ira.core.reasoning.unified_reasoning_core import UnifiedReasoningCore
from ira.core.integration.reasoning_knowledge_integration import ReasoningKnowledgeIntegration
from ira.core.integration.reasoning_knowledge_integration_bugfixes import apply_bug_fixes

def test_ira_system():
    """Test the IRA system."""
    print("Testing IRA system...")
    
    # Initialize the components
    knowledge_graph = KnowledgeGraph()
    ideom_network = IdeomNetwork()
    reasoning_core = UnifiedReasoningCore(ideom_network=ideom_network)
    reasoning_integration = ReasoningKnowledgeIntegration(
        knowledge_graph,
        reasoning_core
    )
    
    # Apply bug fixes to the reasoning integration
    apply_bug_fixes(reasoning_integration)
    
    # Initialize the IRA system
    ira = IRASystem(
        knowledge_graph=knowledge_graph,
        ideom_network=ideom_network,
        reasoning_core=reasoning_core,
        reasoning_integration=reasoning_integration
    )
    
    # Add some test concepts
    dog_concept = knowledge_graph.add_concept("dog")
    knowledge_graph.update_concept(
        dog_concept.id,
        properties={
            "type": "animal",
            "legs": "four",
            "sound": "bark"
        }
    )
    
    cat_concept = knowledge_graph.add_concept("cat")
    knowledge_graph.update_concept(
        cat_concept.id,
        properties={
            "type": "animal",
            "legs": "four",
            "sound": "meow"
        }
    )
    
    # Create ideoms and prefabs from concepts
    reasoning_integration.create_ideoms_from_concepts()
    reasoning_integration.create_prefabs_from_concepts()
    
    # Test processing a message
    test_queries = [
        "What is a dog?",
        "What sound does a cat make?",
        "How many legs does a dog have?",
        "Is a cat an animal?"
    ]
    
    print("\nTesting message processing:")
    for query in test_queries:
        response = ira.process_message(query)
        print(f"Query: {query}")
        print(f"Response: {response}")
        print()

if __name__ == "__main__":
    print("=== Testing IRA System ===\n")
    test_ira_system()