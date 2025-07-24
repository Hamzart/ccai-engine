#!/usr/bin/env python3
"""
Simple demo of the enhanced integration between the Unified Reasoning Core and the Knowledge Graph.

This script provides a minimal example of how to use the enhanced integration with the bug fixes applied.
It creates a simple knowledge graph, applies the bug fixes, and demonstrates basic functionality.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ira.core.knowledge.knowledge_graph import KnowledgeGraph
from ira.core.reasoning.ideom_network import IdeomNetwork
from ira.core.reasoning.unified_reasoning_core import UnifiedReasoningCore
from ira.core.integration.reasoning_knowledge_integration import ReasoningKnowledgeIntegration
from ira.core.integration.reasoning_knowledge_integration_bugfixes import apply_bug_fixes


def main():
    """Run the simple integration demo."""
    print("Creating a simple knowledge graph...")
    knowledge_graph = KnowledgeGraph()
    
    # Add a simple concept
    dog_concept = knowledge_graph.add_concept("dog")
    knowledge_graph.update_concept(
        dog_concept.id,
        properties={
            "type": "animal",
            "legs": "four",
            "sound": "bark"
        }
    )
    
    # Add a multi-word concept to demonstrate the bug fix
    golden_retriever_concept = knowledge_graph.add_concept("golden retriever")
    knowledge_graph.update_concept(
        golden_retriever_concept.id,
        properties={
            "type": "dog breed",
            "coat": "golden",
            "temperament": "friendly"
        }
    )
    
    # Create a relationship
    knowledge_graph.update_relation(golden_retriever_concept, dog_concept, "is_a", bidirectional=False)
    
    print("Creating the reasoning core...")
    ideom_network = IdeomNetwork()
    reasoning_core = UnifiedReasoningCore(ideom_network=ideom_network)
    
    print("Creating the integration...")
    integration = ReasoningKnowledgeIntegration(knowledge_graph, reasoning_core)
    
    print("Applying bug fixes...")
    apply_bug_fixes(integration)
    
    print("Initializing the integration...")
    integration.create_ideoms_from_concepts()
    integration.create_prefabs_from_concepts()
    
    print("\nDemonstrating the integration...")
    
    # Example 1: Basic query
    print("\nExample 1: Basic query")
    query = "What is a dog?"
    print(f"Query: {query}")
    result = integration.process_input_with_knowledge(query)
    print(f"Response: {result['reasoning_result']['primary_response']}")
    
    # Example 2: Multi-word concept handling (bug fix demonstration)
    print("\nExample 2: Multi-word concept handling")
    query = "What is a golden retriever?"
    print(f"Query: {query}")
    result = integration.process_input_with_knowledge(query)
    print(f"Response: {result['reasoning_result']['primary_response']}")
    
    # Example 3: Error handling (bug fix demonstration)
    print("\nExample 3: Error handling")
    query = ""  # Empty query to demonstrate error handling
    print(f"Query: {query} (empty query)")
    result = integration.process_input_with_knowledge(query)
    print(f"Response: {result['reasoning_result']['primary_response']}")
    
    print("\nDemo completed.")


if __name__ == "__main__":
    main()